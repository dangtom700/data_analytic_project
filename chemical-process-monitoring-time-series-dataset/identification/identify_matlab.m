function identify_matlab(varargin)
% IDENTIFY_MATLAB  Two-zone subspace state-space identification via the
% System Identification Toolbox, as the reference against Controller-Toolbox.
%
% Counterpart to identify_ctrl_toolbox.py. Both read the SAME matrices written by
% prepare_id_data.py and write the SAME JSON schema, so compare_models.py can diff
% them on realisation-invariant quantities.
%
%   identify_matlab()                       % defaults
%   identify_matlab('orders', [1 2 3 4], 'iHorizon', 20)
%
% Requires: System Identification Toolbox (n4sid).
%
% Why MOESP weighting
% -------------------
% ctrl_toolbox's n4sid() defaults to MOESP weighting (its SubspaceMethod.MOESP
% "reproduces n4sid() exactly"). n4sidOptions('N4Weight','MOESP') selects the same
% variant here, so the two tools are solving the same problem rather than two
% differently-weighted ones. This is the single most important setting for making
% the comparison meaningful.
%
% Orientation trap
% ----------------
% iddata wants time DOWN ROWS (N-by-p, N-by-m). ctrl_toolbox wants the transpose
% (p-by-N, channels in rows). Neither errors on the wrong one.
%
% Metric conventions -- identical to identify_ctrl_toolbox.py
% ----------------------------------------------------------
% fit_pct = 100 * (1 - norm(y-yhat)/norm(y-mean(y)))
% r2      = 1 - SSE/SST
% Primary metric is FREE-RUN simulation with x0 = 0, computed by the explicit loop
% in localSimulate() rather than by sim()/compare(), so the definition is provably
% the same on both sides. A bias-removed variant (one free DC term per record)
% is reported alongside, because each reactor in a zone sits at a slightly
% different absolute operating point.

ip = inputParser;
ip.addParameter('idData',   fullfile(fileparts(mfilename('fullpath')), 'id_data'));
ip.addParameter('out',      fullfile(fileparts(mfilename('fullpath')), 'results_matlab.json'));
% Orders capped at 4 deliberately: rho(A) crosses 0.9 at order 5 (zone A) and
% reaches 0.9975 by order 6 (zone B). Poles that close to the unit circle on a
% noise-fitted model make free-run simulation numerically sensitive, and
% bias-removed holdout fit degrades monotonically with order anyway.
ip.addParameter('orders',   [1 2 3 4]);
ip.addParameter('iHorizon', 20);
ip.parse(varargin{:});
opt = ip.Results;

if isempty(ver('ident'))
    error('identify_matlab:noToolbox', ...
          'System Identification Toolbox not found -- n4sid is unavailable.');
end

manPath = fullfile(opt.idData, 'prep_manifest.json');
assert(isfile(manPath), 'missing %s -- run prepare_id_data.py first', manPath);
man = jsondecode(fileread(manPath));

Ts    = man.Ts;
ucols = cellstr(man.u_cols);
ycols = cellstr(man.y_cols);

results = struct();
results.tool            = 'matlab';
results.matlab_version  = version;
results.Ts              = Ts;
results.u_cols          = ucols;
results.y_cols          = ycols;
results.i_horizon       = opt.iHorizon;
results.n4_weight       = 'MOESP';
results.zones           = struct();

zoneNames = fieldnames(man.zones);
for zi = 1:numel(zoneNames)
    z     = zoneNames{zi};
    zinfo = man.zones.(z);
    fprintf('\n================ zone %s ================\n', z);

    [Yi, Ui] = localLoad(opt.idData, zinfo.ident.file, ucols, ycols);
    nVal = numel(zinfo.validation);
    valTags = cell(nVal,1); valY = cell(nVal,1); valU = cell(nVal,1);
    for v = 1:nVal
        vinfo = zinfo.validation(v);
        if iscell(vinfo), vinfo = vinfo{1}; end
        valTags{v} = vinfo.tag;
        [valY{v}, valU{v}] = localLoad(opt.idData, vinfo.file, ucols, ycols);
    end
    fprintf('ident %s: Y[%d x %d] U[%d x %d]   val %s\n', zinfo.ident.tag, ...
            size(Yi,1), size(Yi,2), size(Ui,1), size(Ui,2), strjoin(valTags', ', '));

    datIdent = iddata(Yi, Ui, Ts);          % N-by-p, N-by-m
    datIdent.OutputName = ycols;
    datIdent.InputName  = ucols;

    zres = struct();
    zres.ident_tag       = zinfo.ident.tag;
    zres.operating_point = zinfo.operating_point;
    zres.models          = struct();

    for n = opt.orders(:)'
        if opt.iHorizon < n + 1
            fprintf('  order %d: skipped (i_horizon %d < n+1)\n', n, opt.iHorizon);
            continue
        end
        key = sprintf('order_%d', n);
        try
            n4opt = n4sidOptions('N4Weight', 'MOESP', 'Focus', 'prediction', ...
                                 'EnforceStability', false);
            n4opt.N4Horizon = [opt.iHorizon opt.iHorizon opt.iHorizon];
            % 'Feedthrough' is ESSENTIAL here, not cosmetic. n4sid defaults to
            % D = 0 (no input-output feedthrough), but in this dataset the entire
            % input->output relationship is instantaneous -- the cross-correlation
            % peaks at lag 0 -- so all of it belongs in D. Forbidden from using D,
            % n4sid must approximate an instantaneous response through
            % C(zI-A)^-1 B, which needs a huge B: measured max|B| reached 1e6-1.5e7
            % at order >= 5 and free-run simulation fit collapsed to -4e6 %.
            % ctrl_toolbox estimates D freely, so this also makes the two
            % comparable instead of solving different problems.
            mdl = n4sid(datIdent, n, 'Feedthrough', true(1, numel(ucols)), n4opt);
        catch ME
            fprintf('  order %d: FAILED -- %s\n', n, ME.message);
            zres.models.(key) = struct('success', false, 'message', ME.message);
            continue
        end

        [A, B, C, D, K] = idssdata(mdl);

        e = struct();
        e.success = true;
        e.n_order = n;
        e.A = A;  e.B = B;  e.C = C;  e.D = D;
        e.Ts = Ts;
        e.kalman_gain = K;
        if ~isempty(mdl.NoiseVariance)
            e.innov_cov = mdl.NoiseVariance;
        end

        invs = localInvariants(A, B, C, D);
        for f = fieldnames(invs)', e.(f{1}) = invs.(f{1}); end

        e.fit_ident = localScore(Yi, localSimulate(A,B,C,D,Ui));
        fv = struct();
        for v = 1:nVal
            fv.(matlab.lang.makeValidName(valTags{v})) = ...
                localScore(valY{v}, localSimulate(A,B,C,D,valU{v}));
        end
        e.fit_val = fv;
        zres.models.(key) = e;

        fprintf('  order %d: rho(A)=%7.4f   ident', n, e.spectral_radius);
        for o = 1:numel(ycols)
            fprintf('  %s=%7.2f%%', ycols{o}, e.fit_ident(o).fit_pct);
        end
        fprintf('\n');
        for v = 1:nVal
            s = fv.(matlab.lang.makeValidName(valTags{v}));
            fprintf('            holdout %s:', valTags{v});
            for o = 1:numel(ycols)
                fprintf('  %s=%8.2f%%(bias-rm %6.2f%%)', ycols{o}, ...
                        s(o).fit_pct, s(o).fit_pct_bias_removed);
            end
            fprintf('\n');
        end

    end

    % Singular-value spectrum for the knee test. n4sid does NOT expose the subspace
    % singular values programmatically (its second output is x0, and the order-
    % selection spectrum only reaches the plot), so they are computed here from the
    % same MOESP projection ctrl_toolbox uses. That makes the two spectra directly
    % comparable instead of comparing against something MATLAB never returned.
    svRecorded = localSingularValues(Yi, Ui, opt.iHorizon);

    if ~isempty(svRecorded)
        zres.singular_values = svRecorded;
        zres.sv_diagnostics  = localSvDiagnostics(svRecorded);
        d = zres.sv_diagnostics;
        fprintf('  largest sv ratio (first %d) = %.3f at order %d  ->  knee_present=%d\n', ...
                d.candidate_limit, d.max_ratio, d.argmax_ratio_order, d.knee_present);
    else
        fprintf('  singular-value spectrum unavailable (record too short).\n');
    end

    results.zones.(z) = zres;
end

fid = fopen(opt.out, 'w');
assert(fid > 0, 'cannot open %s for writing', opt.out);
fprintf(fid, '%s', jsonencode(results, 'PrettyPrint', true));
fclose(fid);
fprintf('\nwrote %s\n', opt.out);
end

% =========================================================================
function [Y, U] = localLoad(dir_, fname, ucols, ycols)
T = readtable(fullfile(dir_, fname), 'VariableNamingRule', 'preserve');
Y = zeros(height(T), numel(ycols));
U = zeros(height(T), numel(ucols));
for i = 1:numel(ycols), Y(:,i) = T.(ycols{i}); end
for i = 1:numel(ucols), U(:,i) = T.(ucols{i}); end
assert(~any(isnan(Y(:))) && ~any(isnan(U(:))), '%s: NaNs present', fname);
end

% -------------------------------------------------------------------------
function Yh = localSimulate(A, B, C, D, U)
% Free-run simulation, x0 = 0. U is N-by-m; returns N-by-p.
% Deliberately an explicit loop, matching simulate() in identify_ctrl_toolbox.py.
N = size(U, 1);
x = zeros(size(A, 1), 1);
Yh = zeros(N, size(C, 1));
for k = 1:N
    uk = U(k, :)';
    Yh(k, :) = (C * x + D * uk)';
    x = A * x + B * uk;
end
end

% -------------------------------------------------------------------------
function s = localScore(Y, Yh)
% Per-output-channel fit. Mirrors score() in identify_ctrl_toolbox.py exactly.
p = size(Y, 2);
s = repmat(struct('offset',0,'fit_pct',0,'r2',0,'rmse',0, ...
                  'fit_pct_bias_removed',0,'r2_bias_removed',0, ...
                  'rmse_bias_removed',0), p, 1);
for i = 1:p
    y = Y(:, i); yh = Yh(:, i);
    off = mean(y - yh);
    s(i).offset = off;
    preds = {yh, yh + off};
    names = {'', '_bias_removed'};
    for v = 1:2
        pr  = preds{v};
        sse = sum((y - pr).^2);
        sst = sum((y - mean(y)).^2);
        s(i).(['fit_pct' names{v}]) = 100 * (1 - norm(y - pr) / norm(y - mean(y)));
        s(i).(['r2'      names{v}]) = 1 - sse / sst;
        s(i).(['rmse'    names{v}]) = sqrt(sse / numel(y));
    end
end
end

% -------------------------------------------------------------------------
function invs = localInvariants(A, B, C, D)
% A/B/C/D are basis-dependent and will NOT match between tools even for an
% identical system. These descriptors will.
n  = size(A, 1);
ev = eig(A);
[~, ord] = sort(abs(ev), 'descend');
ev = ev(ord);
invs = struct();
invs.eig_real        = real(ev);
invs.eig_imag        = imag(ev);
invs.eig_abs         = abs(ev);
invs.spectral_radius = max(abs(ev));
if rcond(eye(n) - A) > eps
    invs.dc_gain = C * ((eye(n) - A) \ B) + D;
else
    invs.dc_gain = [];
end
steps = struct();
for j = 1:size(B, 2)
    Uj = zeros(60, size(B, 2));
    Uj(:, j) = 1;
    steps.(sprintf('u%d', j - 1)) = localSimulate(A, B, C, D, Uj)';
end
invs.step_response_60 = steps;
end

% -------------------------------------------------------------------------
function d = localSvDiagnostics(sv, maxCandidate, kneeThreshold)
if nargin < 2, maxCandidate = 10;  end
if nargin < 3, kneeThreshold = 3.0; end
sv = sv(sv > 0);
d = struct('max_ratio', NaN);
if numel(sv) < 2, return; end
ratios = sv(1:end-1) ./ sv(2:end);
lim    = min(maxCandidate, numel(ratios));
head   = ratios(1:lim);
[mx, ix] = max(head);
[mxu, ixu] = max(ratios);
d.max_ratio               = mx;
d.argmax_ratio_order      = ix;
d.max_ratio_unrestricted  = mxu;
d.argmax_ratio_unrestricted = ixu;
d.candidate_limit         = lim;
d.knee_threshold          = kneeThreshold;
d.sv_normalised           = sv / sv(1);
d.decay_first_to_tenth    = sv(min(10, numel(sv))) / sv(1);
d.knee_present            = mx > kneeThreshold;
end

% -------------------------------------------------------------------------
function sv = localSingularValues(Y, U, i)
% Singular values of the MOESP oblique projection -- the same quantity
% ctrl_toolbox returns in SubspaceIDResult.singular_values.
%
% Y is N-by-p, U is N-by-m (iddata orientation); transposed here to the
% channels-in-rows form the Hankel construction needs.
Yt = Y'; Ut = U';
[p, N] = size(Yt); m = size(Ut, 1);
nc = N - 2*i + 1;
sv = [];
if nc <= (p + m) * i, return; end

Up = localHankel(Ut, 0, i, nc); Uf = localHankel(Ut, i, i, nc);
Yp = localHankel(Yt, 0, i, nc); Yf = localHankel(Yt, i, i, nc);

[Q, ~] = qr(Uf', 0);                      % project out the future inputs
Zf = Yf - (Yf * Q) * Q';
Wp = [Up; Yp] - (([Up; Yp]) * Q) * Q';
O  = Zf * pinv(Wp) * Wp;                  % onto the past data
sv = svd(O);
end

% -------------------------------------------------------------------------
function H = localHankel(sig, startBlk, rowsBlocks, ncols)
d = size(sig, 1);
H = zeros(d * rowsBlocks, ncols);
for b = 0:rowsBlocks-1
    H(b*d+1:(b+1)*d, :) = sig(:, startBlk+b+1 : startBlk+b+ncols);
end
end
