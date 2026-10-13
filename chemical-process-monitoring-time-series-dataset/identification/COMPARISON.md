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
| 1 | matlab | 0.0800 | 2.63% | 0.03% | -143.9% (4.19%) | -15.4% (0.04%) |
| 2 | ctrl_toolbox | 0.3775 | 2.10% | 0.03% | -144.1% (3.80%) | -15.2% (0.04%) |
| 2 | matlab | 0.3616 | 2.57% | 0.02% | -143.9% (4.16%) | -15.4% (0.04%) |
| 3 | ctrl_toolbox | 0.6277 | 2.10% | 0.03% | -144.1% (3.79%) | -15.2% (0.04%) |
| 3 | matlab | 0.6309 | -10571169.44% | -633721.12% | -2461722.3% (-2461722.26%) | -148538.6% (-148538.56%) |
| 4 | ctrl_toolbox | 0.7844 | 2.10% | 0.03% | -144.1% (3.79%) | -15.2% (0.04%) |
| 4 | matlab | 0.7883 | -7938561.04% | -415822.97% | -1848644.1% (-1848644.10%) | -97438.8% (-97438.81%) |

Holdout columns are averaged over the two held-out reactors; the parenthesised value removes a constant per-record offset, separating gain/dynamic error from operating-point bias.

### Do the two tools agree?

| order | max abs(d(eig)) | DC-gain rel. diff | step-resp rel. diff |
|---|---|---|---|
| 1 | 1.430e-03 | 8.531e-01 | 8.531e-01 |
| 2 | 1.590e-02 | 8.551e-01 | 1.098e+00 |
| 3 | 8.210e-03 | 7.428e-01 | 1.437e+00 |
| 4 | 3.303e-02 | 7.609e-01 | 1.000e+00 |

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
| 1 | matlab | 0.8039 | 2.00% | 0.03% | -152.2% (2.37%) | -115.0% (0.00%) |
| 2 | ctrl_toolbox | 0.7765 | 1.81% | 0.02% | -152.3% (2.17%) | -115.1% (0.01%) |
| 2 | matlab | 0.7803 | -6.61% | -0.09% | -157.2% (-7.24%) | -115.1% (-0.09%) |
| 3 | ctrl_toolbox | 0.9711 | 1.76% | 0.02% | -152.4% (2.08%) | -115.1% (0.01%) |
| 3 | matlab | 0.9702 | -88610610.17% | -41167650.13% | -90649160.6% (-90649160.61%) | -42982233.7% (-42982233.70%) |
| 4 | ctrl_toolbox | 0.9430 | 1.75% | 0.02% | -152.3% (2.07%) | -115.1% (0.00%) |
| 4 | matlab | 0.9404 | -79857253.31% | -25883316.21% | -81694426.6% (-81694426.58%) | -27024200.3% (-27024200.27%) |

Holdout columns are averaged over the two held-out reactors; the parenthesised value removes a constant per-record offset, separating gain/dynamic error from operating-point bias.

### Do the two tools agree?

| order | max abs(d(eig)) | DC-gain rel. diff | step-resp rel. diff |
|---|---|---|---|
| 1 | 6.187e-03 | 8.115e-01 | 9.584e-01 |
| 2 | 4.425e-03 | 4.777e-01 | 1.287e+00 |
| 3 | 1.046e-03 | 5.930e-01 | 1.365e+00 |
| 4 | 5.290e-03 | 6.027e-01 | 1.399e+00 |

Agreement here means both implementations extracted the same system. Disagreement on a dataset with no deterministic subspace is expected: each tool is fitting its own noise direction, so the invariants are not pinned down by the data.

## Verdict

- **Zone A**: knee_present = `False`; best ident free-run fit on `reactor_temp` = **2.10%** at order_2
- **Zone B**: knee_present = `False`; best ident free-run fit on `reactor_temp` = **1.96%** at order_1

A knee-free singular-value spectrum plus a single-digit free-run fit means the records contain no deterministic subspace to identify: the returned A/B/C/D are a fit to noise, and the poles land near the origin (no memory at Ts = 60 s). Read the numbers above as a measurement of the dataset, not of either tool.
