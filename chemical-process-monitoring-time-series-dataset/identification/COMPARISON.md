# Two-zone identification: MATLAB vs Controller-Toolbox

Result files present: ctrl_toolbox, matlab

- Sample time `Ts = 60.0 s`
- Inputs `['coolant_flow_rate', 'feed_flow_rate', 'agitator_speed_rpm', 'ambient_temp_effect']`
- Outputs `['reactor_temp', 'reactor_pressure']`

## Zone A

Linearisation point: `coolant_flow_rate=79.1016`, `feed_flow_rate=99.9922`, `agitator_speed_rpm=300.0021`, `ambient_temp_effect=4.4798`, `reactor_temp=181.1432`, `reactor_pressure=15.7092`

Identification record: `A_R2`

### Order selection

- **ctrl_toolbox**: largest sv ratio within first 10 = **1.146** at order 1; `sv[10]/sv[0] = 0.727`; knee_present = **False**
  - unrestricted max-ratio search returns order 20 (ratio 2.565) -- the spectrum's numerical tail, not a real knee
  - `suggest_order(max_order=-1)` -> **20**, capped -> 1
- **matlab**: largest sv ratio within first 10 = **1.147** at order 1; `sv[10]/sv[0] = 0.726`; knee_present = **False**
  - unrestricted max-ratio search returns order 20 (ratio 2.564) -- the spectrum's numerical tail, not a real knee

### Fit per order (free-run simulation, x0 = 0)

| order | tool | rho(A) | ident reactor_temp | ident reactor_pressure | holdout reactor_temp (bias-rm) | holdout reactor_pressure (bias-rm) |
|---|---|---|---|---|---|---|
| 1 | ctrl_toolbox | 0.0786 | 2.09% | 0.03% | -144.1% (3.80%) | -15.2% (0.04%) |
| 1 | matlab | 0.0800 | 1.84% | 0.01% | -144.2% (3.59%) | -16.6% (0.03%) |
| 2 | ctrl_toolbox | 0.3775 | 2.10% | 0.03% | -144.1% (3.80%) | -15.2% (0.04%) |
| 2 | matlab | 0.3616 | 1.87% | 0.01% | -144.2% (3.56%) | -15.3% (0.04%) |
| 3 | ctrl_toolbox | 0.6277 | 2.10% | 0.03% | -144.1% (3.79%) | -15.2% (0.04%) |
| 3 | matlab | 0.6309 | 1.88% | 0.02% | -144.2% (3.56%) | -15.3% (0.04%) |
| 4 | ctrl_toolbox | 0.7844 | 2.10% | 0.03% | -144.1% (3.79%) | -15.2% (0.04%) |
| 4 | matlab | 0.7883 | 0.62% | 0.01% | -144.3% (3.44%) | -15.3% (0.04%) |
| 5 | ctrl_toolbox | 0.9108 | 2.10% | 0.03% | -144.1% (3.79%) | -15.2% (0.04%) |
| 5 | matlab | 0.9085 | -3930955.02% | -241298.26% | -915358.5% (-915358.49%) | -56510.8% (-56510.81%) |
| 6 | ctrl_toolbox | 0.9141 | 2.09% | 0.03% | -144.1% (3.75%) | -15.2% (0.04%) |
| 6 | matlab | 0.9141 | -3785560.29% | -230257.77% | -881499.3% (-881499.23%) | -53921.7% (-53921.73%) |
| 8 | ctrl_toolbox | 0.9614 | 2.00% | 0.02% | -144.1% (3.70%) | -15.3% (0.04%) |
| 8 | matlab | 0.9616 | -26737591.26% | -3418099.74% | -6226535.9% (-6226535.85%) | -801509.5% (-801509.49%) |

Holdout columns are averaged over the two held-out reactors; the parenthesised value removes a constant per-record offset, separating gain/dynamic error from operating-point bias.

### Do the two tools agree?

| order | max |d(eig)| | DC-gain rel. diff | step-resp rel. diff |
|---|---|---|---|
| 1 | 1.430e-03 | 1.860e-01 | n/a |
| 2 | 1.590e-02 | 1.426e-01 | n/a |
| 3 | 8.210e-03 | 2.812e-01 | n/a |
| 4 | 3.303e-02 | 2.016e-01 | n/a |
| 5 | 1.205e+00 | 1.013e-01 | n/a |
| 6 | 1.565e+00 | 8.697e-02 | n/a |
| 8 | 1.817e+00 | 1.318e-01 | n/a |

Agreement here means both implementations extracted the same system. Disagreement on a dataset with no deterministic subspace is expected: each tool is fitting its own noise direction, so the invariants are not pinned down by the data.

## Zone B

Linearisation point: `coolant_flow_rate=72.1894`, `feed_flow_rate=107.9882`, `agitator_speed_rpm=299.9275`, `ambient_temp_effect=-0.8879`, `reactor_temp=193.6402`, `reactor_pressure=17.5542`

Identification record: `B_R2`

### Order selection

- **ctrl_toolbox**: largest sv ratio within first 10 = **1.088** at order 3; `sv[10]/sv[0] = 0.712`; knee_present = **False**
  - unrestricted max-ratio search returns order 20 (ratio 2.436) -- the spectrum's numerical tail, not a real knee
  - `suggest_order(max_order=-1)` -> **20**, capped -> 3
- **matlab**: largest sv ratio within first 10 = **1.088** at order 3; `sv[10]/sv[0] = 0.712`; knee_present = **False**
  - unrestricted max-ratio search returns order 20 (ratio 2.436) -- the spectrum's numerical tail, not a real knee

### Fit per order (free-run simulation, x0 = 0)

| order | tool | rho(A) | ident reactor_temp | ident reactor_pressure | holdout reactor_temp (bias-rm) | holdout reactor_pressure (bias-rm) |
|---|---|---|---|---|---|---|
| 1 | ctrl_toolbox | 0.8100 | 1.96% | 0.02% | -152.3% (2.33%) | -115.1% (0.01%) |
| 1 | matlab | 0.8039 | 1.47% | -0.00% | -152.6% (1.76%) | -117.0% (0.02%) |
| 2 | ctrl_toolbox | 0.7765 | 1.81% | 0.02% | -152.3% (2.17%) | -115.1% (0.01%) |
| 2 | matlab | 0.7803 | 1.50% | 0.00% | -152.5% (1.74%) | -115.0% (0.01%) |
| 3 | ctrl_toolbox | 0.9711 | 1.76% | 0.02% | -152.4% (2.08%) | -115.1% (0.01%) |
| 3 | matlab | 0.9702 | 1.39% | -0.05% | -152.6% (1.57%) | -115.0% (-0.01%) |
| 4 | ctrl_toolbox | 0.9430 | 1.75% | 0.02% | -152.3% (2.07%) | -115.1% (0.00%) |
| 4 | matlab | 0.9404 | 1.18% | -0.06% | -152.7% (1.32%) | -115.1% (-0.02%) |
| 5 | ctrl_toolbox | 0.9842 | 1.68% | 0.01% | -152.4% (2.00%) | -115.1% (0.01%) |
| 5 | matlab | 0.9839 | -9277412.46% | -5658504.07% | -9490847.9% (-9490847.94%) | -5907920.6% (-5907920.65%) |
| 6 | ctrl_toolbox | 0.9975 | 1.57% | -0.00% | -152.4% (1.90%) | -115.1% (0.01%) |
| 6 | matlab | 0.9974 | -39383701.73% | -24180687.93% | -40289753.4% (-40289753.44%) | -25246522.8% (-25246522.75%) |
| 8 | ctrl_toolbox | 0.9507 | 1.60% | 0.02% | -152.4% (1.91%) | -115.1% (0.01%) |
| 8 | matlab | 0.9512 | -49921883.53% | -40627192.09% | -51070372.0% (-51070371.98%) | -42417951.5% (-42417951.54%) |

Holdout columns are averaged over the two held-out reactors; the parenthesised value removes a constant per-record offset, separating gain/dynamic error from operating-point bias.

### Do the two tools agree?

| order | max |d(eig)| | DC-gain rel. diff | step-resp rel. diff |
|---|---|---|---|
| 1 | 6.187e-03 | 2.289e-01 | n/a |
| 2 | 4.425e-03 | 7.103e-01 | n/a |
| 3 | 1.046e-03 | 2.404e-01 | n/a |
| 4 | 5.290e-03 | 4.214e-01 | n/a |
| 5 | 5.640e-03 | 7.030e-02 | n/a |
| 6 | 7.495e-03 | 5.449e-01 | n/a |
| 8 | 1.697e+00 | 3.429e-01 | n/a |

Agreement here means both implementations extracted the same system. Disagreement on a dataset with no deterministic subspace is expected: each tool is fitting its own noise direction, so the invariants are not pinned down by the data.

## Verdict

- **Zone A**: knee_present = `False`; best ident free-run fit on `reactor_temp` = **2.10%** at order_2
- **Zone B**: knee_present = `False`; best ident free-run fit on `reactor_temp` = **1.96%** at order_1

A knee-free singular-value spectrum plus a single-digit free-run fit means the records contain no deterministic subspace to identify: the returned A/B/C/D are a fit to noise, and the poles land near the origin (no memory at Ts = 60 s). Read the numbers above as a measurement of the dataset, not of either tool.
