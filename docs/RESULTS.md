# Comprehensive Benchmark Results (SIH26055 - DRDO)

**Monte Carlo Configuration**: 30 deterministic seeds (100 to 129) per scenario.
**Statistical Hypothesis Tests**: Paired Student's t-test and Wilcoxon signed-rank test against Proposed *SmartScan-BayesianRMAB* (α = 0.05).

## Periodic Scanning Radars
### Benchmark Evaluation: `periodic_emitters` (30 seeds)

| Algorithm | Threat Intercept Rate | Periodic Revisit Rate | Mean TTFI (steps) | Dwell Efficiency | Retune Cost (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **smart_scan** | 0.120 ± 0.052 | 0.264 ± 0.084 | 112.2 ± 43.0 | 0.045 ± 0.019 | 67.4 ± 1.8 |
| **sequential** | 0.061 ± 0.000 | 0.159 ± 0.000 | 64.0 ± 0.0 | 0.023 ± 0.000 | 67.0 ± 0.0 |
| **random** | 0.062 ± 0.017 | 0.144 ± 0.041 | 122.2 ± 38.5 | 0.023 ± 0.006 | 126.1 ± 4.8 |
| **priority_rr** | 0.141 ± 0.045 | 0.288 ± 0.073 | 101.6 ± 48.4 | 0.053 ± 0.017 | 75.4 ± 6.4 |
| **rl_dqn** | 0.041 ± 0.071 | 0.074 ± 0.111 | 200.9 ± 138.0 | 0.015 ± 0.027 | 32.9 ± 17.4 |

### Paired Statistical Significance vs Baselines
| Baseline | Metric | Proposed Mean | Baseline Mean | p-value (t-test) | Cohen's d | Superiority |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| sequential | threat_intercept_rate | 0.12 | 0.0606 | 1.0000e-06 (*** (p < 0.001)) | 1.15 | **proposed** |
| sequential | periodic_revisit_rate | 0.2637 | 0.1594 | 0.0000e+00 (*** (p < 0.001)) | 1.24 | **proposed** |
| sequential | mean_ttfi_steps | 112.167 | 64.0 | 1.0000e-06 (*** (p < 0.001)) | 1.12 | **baseline** |
| sequential | dwell_efficiency | 0.0452 | 0.0229 | 1.0000e-06 (*** (p < 0.001)) | 1.15 | **proposed** |
| random | threat_intercept_rate | 0.12 | 0.0619 | 0.0000e+00 (*** (p < 0.001)) | 1.21 | **proposed** |
| random | periodic_revisit_rate | 0.2637 | 0.1436 | 0.0000e+00 (*** (p < 0.001)) | 1.51 | **proposed** |
| random | mean_ttfi_steps | 112.167 | 122.2413 | 3.5426e-01 (ns (not significant)) | -0.17 | **proposed** |
| random | dwell_efficiency | 0.0452 | 0.0233 | 0.0000e+00 (*** (p < 0.001)) | 1.21 | **proposed** |
| priority_rr | threat_intercept_rate | 0.12 | 0.1407 | 1.3190e-01 (ns (not significant)) | -0.28 | **baseline** |
| priority_rr | periodic_revisit_rate | 0.2637 | 0.2879 | 2.9196e-01 (ns (not significant)) | -0.20 | **baseline** |
| priority_rr | mean_ttfi_steps | 112.167 | 101.5527 | 3.9291e-01 (ns (not significant)) | 0.16 | **baseline** |
| priority_rr | dwell_efficiency | 0.0452 | 0.053 | 1.3159e-01 (ns (not significant)) | -0.28 | **baseline** |
| rl_dqn | threat_intercept_rate | 0.12 | 0.0409 | 1.3000e-05 (*** (p < 0.001)) | 0.96 | **proposed** |
| rl_dqn | periodic_revisit_rate | 0.2637 | 0.0745 | 0.0000e+00 (*** (p < 0.001)) | 1.26 | **proposed** |
| rl_dqn | mean_ttfi_steps | 112.167 | 200.9417 | 2.5100e-03 (** (p < 0.01)) | -0.60 | **proposed** |
| rl_dqn | dwell_efficiency | 0.0452 | 0.0154 | 1.3000e-05 (*** (p < 0.001)) | 0.96 | **proposed** |

## Cold Start Discovery
### Benchmark Evaluation: `cold_start` (30 seeds)

| Algorithm | Threat Intercept Rate | Periodic Revisit Rate | Mean TTFI (steps) | Dwell Efficiency | Retune Cost (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **smart_scan** | 0.190 ± 0.028 | 0.093 ± 0.064 | 74.9 ± 26.1 | 0.325 ± 0.050 | 58.0 ± 5.8 |
| **sequential** | 0.067 ± 0.005 | 0.181 ± 0.000 | 40.8 ± 2.4 | 0.115 ± 0.009 | 57.5 ± 0.0 |
| **random** | 0.060 ± 0.012 | 0.104 ± 0.049 | 80.1 ± 26.2 | 0.103 ± 0.020 | 107.7 ± 4.7 |
| **priority_rr** | 0.287 ± 0.033 | 0.072 ± 0.061 | 80.2 ± 31.8 | 0.492 ± 0.058 | 77.4 ± 4.5 |
| **rl_dqn** | 0.042 ± 0.075 | 0.087 ± 0.167 | 129.8 ± 63.2 | 0.072 ± 0.129 | 26.8 ± 10.1 |

### Paired Statistical Significance vs Baselines
| Baseline | Metric | Proposed Mean | Baseline Mean | p-value (t-test) | Cohen's d | Superiority |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| sequential | threat_intercept_rate | 0.1901 | 0.0673 | 0.0000e+00 (*** (p < 0.001)) | 4.58 | **proposed** |
| sequential | periodic_revisit_rate | 0.0932 | 0.181 | 0.0000e+00 (*** (p < 0.001)) | -1.38 | **baseline** |
| sequential | mean_ttfi_steps | 74.9333 | 40.8333 | 0.0000e+00 (*** (p < 0.001)) | 1.29 | **baseline** |
| sequential | dwell_efficiency | 0.3249 | 0.1148 | 0.0000e+00 (*** (p < 0.001)) | 4.47 | **proposed** |
| random | threat_intercept_rate | 0.1901 | 0.0604 | 0.0000e+00 (*** (p < 0.001)) | 4.21 | **proposed** |
| random | periodic_revisit_rate | 0.0932 | 0.1037 | 4.7481e-01 (ns (not significant)) | -0.13 | **baseline** |
| random | mean_ttfi_steps | 74.9333 | 80.1027 | 4.3908e-01 (ns (not significant)) | -0.14 | **proposed** |
| random | dwell_efficiency | 0.3249 | 0.1033 | 0.0000e+00 (*** (p < 0.001)) | 4.08 | **proposed** |
| priority_rr | threat_intercept_rate | 0.1901 | 0.2867 | 0.0000e+00 (*** (p < 0.001)) | -2.02 | **baseline** |
| priority_rr | periodic_revisit_rate | 0.0932 | 0.0721 | 2.5303e-01 (ns (not significant)) | 0.21 | **proposed** |
| priority_rr | mean_ttfi_steps | 74.9333 | 80.2107 | 5.0091e-01 (ns (not significant)) | -0.12 | **proposed** |
| priority_rr | dwell_efficiency | 0.3249 | 0.4923 | 0.0000e+00 (*** (p < 0.001)) | -2.00 | **baseline** |
| rl_dqn | threat_intercept_rate | 0.1901 | 0.0419 | 0.0000e+00 (*** (p < 0.001)) | 1.86 | **proposed** |
| rl_dqn | periodic_revisit_rate | 0.0932 | 0.0868 | 8.4484e-01 (ns (not significant)) | 0.04 | **proposed** |
| rl_dqn | mean_ttfi_steps | 74.9333 | 129.8307 | 2.7500e-04 (*** (p < 0.001)) | -0.76 | **proposed** |
| rl_dqn | dwell_efficiency | 0.3249 | 0.072 | 0.0000e+00 (*** (p < 0.001)) | 1.83 | **proposed** |

## Frequency Agile Hoppers
### Benchmark Evaluation: `frequency_agile` (30 seeds)

| Algorithm | Threat Intercept Rate | Periodic Revisit Rate | Mean TTFI (steps) | Dwell Efficiency | Retune Cost (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **smart_scan** | 0.112 ± 0.025 | 1.000 ± 0.000 | 13.2 ± 7.1 | 0.313 ± 0.070 | 78.2 ± 5.5 |
| **sequential** | 0.062 ± 0.004 | 1.000 ± 0.000 | 10.1 ± 5.0 | 0.173 ± 0.012 | 67.0 ± 0.0 |
| **random** | 0.065 ± 0.008 | 1.000 ± 0.000 | 14.7 ± 8.6 | 0.181 ± 0.022 | 126.1 ± 4.8 |
| **priority_rr** | 0.123 ± 0.013 | 1.000 ± 0.000 | 27.3 ± 18.8 | 0.344 ± 0.037 | 91.0 ± 5.9 |
| **rl_dqn** | 0.051 ± 0.053 | 1.000 ± 0.000 | 93.5 ± 51.8 | 0.143 ± 0.147 | 29.5 ± 14.8 |

### Paired Statistical Significance vs Baselines
| Baseline | Metric | Proposed Mean | Baseline Mean | p-value (t-test) | Cohen's d | Superiority |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| sequential | threat_intercept_rate | 0.112 | 0.0616 | 0.0000e+00 (*** (p < 0.001)) | 1.98 | **proposed** |
| sequential | periodic_revisit_rate | 1.0 | 1.0 | 1.0000e+00 (ns) | 0.00 | **tie** |
| sequential | mean_ttfi_steps | 13.1887 | 10.1007 | 6.3498e-02 (ns (not significant)) | 0.35 | **baseline** |
| sequential | dwell_efficiency | 0.3131 | 0.173 | 0.0000e+00 (*** (p < 0.001)) | 1.97 | **proposed** |
| random | threat_intercept_rate | 0.112 | 0.0647 | 0.0000e+00 (*** (p < 0.001)) | 1.67 | **proposed** |
| random | periodic_revisit_rate | 1.0 | 1.0 | 1.0000e+00 (ns) | 0.00 | **tie** |
| random | mean_ttfi_steps | 13.1887 | 14.7227 | 4.6501e-01 (ns (not significant)) | -0.14 | **proposed** |
| random | dwell_efficiency | 0.3131 | 0.1809 | 0.0000e+00 (*** (p < 0.001)) | 1.67 | **proposed** |
| priority_rr | threat_intercept_rate | 0.112 | 0.1228 | 3.0790e-02 (* (p < 0.05)) | -0.41 | **baseline** |
| priority_rr | periodic_revisit_rate | 1.0 | 1.0 | 1.0000e+00 (ns) | 0.00 | **tie** |
| priority_rr | mean_ttfi_steps | 13.1887 | 27.278 | 6.4100e-04 (*** (p < 0.001)) | -0.70 | **proposed** |
| priority_rr | dwell_efficiency | 0.3131 | 0.3436 | 3.0582e-02 (* (p < 0.05)) | -0.41 | **baseline** |
| rl_dqn | threat_intercept_rate | 0.112 | 0.0511 | 1.1000e-05 (*** (p < 0.001)) | 0.97 | **proposed** |
| rl_dqn | periodic_revisit_rate | 1.0 | 1.0 | 1.0000e+00 (ns) | 0.00 | **tie** |
| rl_dqn | mean_ttfi_steps | 13.1887 | 93.478 | 0.0000e+00 (*** (p < 0.001)) | -1.58 | **proposed** |
| rl_dqn | dwell_efficiency | 0.3131 | 0.1431 | 1.1000e-05 (*** (p < 0.001)) | 0.97 | **proposed** |

## Decoy-Heavy Electronic Attack
### Benchmark Evaluation: `decoy_heavy` (30 seeds)

| Algorithm | Threat Intercept Rate | Periodic Revisit Rate | Mean TTFI (steps) | Dwell Efficiency | Retune Cost (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **smart_scan** | 0.097 ± 0.049 | 0.107 ± 0.072 | 51.5 ± 25.4 | 0.080 ± 0.040 | 88.2 ± 13.2 |
| **sequential** | 0.064 ± 0.007 | 0.161 ± 0.000 | 49.1 ± 2.9 | 0.054 ± 0.006 | 67.0 ± 0.0 |
| **random** | 0.066 ± 0.018 | 0.143 ± 0.076 | 50.5 ± 23.4 | 0.055 ± 0.016 | 126.1 ± 4.8 |
| **priority_rr** | 0.123 ± 0.033 | 0.063 ± 0.051 | 59.6 ± 27.0 | 0.102 ± 0.027 | 105.8 ± 6.9 |
| **rl_dqn** | 0.110 ± 0.206 | 0.065 ± 0.146 | 114.0 ± 65.4 | 0.091 ± 0.170 | 26.9 ± 7.7 |

### Paired Statistical Significance vs Baselines
| Baseline | Metric | Proposed Mean | Baseline Mean | p-value (t-test) | Cohen's d | Superiority |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| sequential | threat_intercept_rate | 0.097 | 0.0644 | 1.0910e-03 (** (p < 0.01)) | 0.66 | **proposed** |
| sequential | periodic_revisit_rate | 0.1066 | 0.1611 | 2.5800e-04 (*** (p < 0.001)) | -0.76 | **baseline** |
| sequential | mean_ttfi_steps | 51.4633 | 49.12 | 6.1888e-01 (ns (not significant)) | 0.09 | **baseline** |
| sequential | dwell_efficiency | 0.08 | 0.0536 | 1.1390e-03 (** (p < 0.01)) | 0.66 | **proposed** |
| random | threat_intercept_rate | 0.097 | 0.0662 | 2.9370e-03 (** (p < 0.01)) | 0.59 | **proposed** |
| random | periodic_revisit_rate | 0.1066 | 0.1434 | 6.7228e-02 (ns (not significant)) | -0.35 | **baseline** |
| random | mean_ttfi_steps | 51.4633 | 50.5067 | 8.8152e-01 (ns (not significant)) | 0.03 | **baseline** |
| random | dwell_efficiency | 0.08 | 0.055 | 3.7310e-03 (** (p < 0.01)) | 0.58 | **proposed** |
| priority_rr | threat_intercept_rate | 0.097 | 0.123 | 1.7851e-02 (* (p < 0.05)) | -0.46 | **baseline** |
| priority_rr | periodic_revisit_rate | 0.1066 | 0.0632 | 2.1521e-02 (* (p < 0.05)) | 0.44 | **proposed** |
| priority_rr | mean_ttfi_steps | 51.4633 | 59.5643 | 2.4985e-01 (ns (not significant)) | -0.21 | **proposed** |
| priority_rr | dwell_efficiency | 0.08 | 0.1017 | 1.4995e-02 (* (p < 0.05)) | -0.47 | **baseline** |
| rl_dqn | threat_intercept_rate | 0.097 | 0.1098 | 7.4184e-01 (ns (not significant)) | -0.06 | **baseline** |
| rl_dqn | periodic_revisit_rate | 0.1066 | 0.0651 | 1.6130e-01 (ns (not significant)) | 0.26 | **proposed** |
| rl_dqn | mean_ttfi_steps | 51.4633 | 114.0253 | 4.2000e-05 (*** (p < 0.001)) | -0.88 | **proposed** |
| rl_dqn | dwell_efficiency | 0.08 | 0.0906 | 7.4190e-01 (ns (not significant)) | -0.06 | **baseline** |

## Congested Multi-Emitter Battlefield
### Benchmark Evaluation: `congested` (30 seeds)

| Algorithm | Threat Intercept Rate | Periodic Revisit Rate | Mean TTFI (steps) | Dwell Efficiency | Retune Cost (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **smart_scan** | 0.126 ± 0.021 | 0.085 ± 0.103 | 47.2 ± 24.2 | 0.363 ± 0.062 | 117.9 ± 20.4 |
| **sequential** | 0.062 ± 0.004 | 0.135 ± 0.000 | 32.6 ± 3.4 | 0.179 ± 0.013 | 76.7 ± 0.0 |
| **random** | 0.064 ± 0.006 | 0.126 ± 0.069 | 46.8 ± 23.5 | 0.184 ± 0.019 | 143.9 ± 5.0 |
| **priority_rr** | 0.130 ± 0.012 | 0.061 ± 0.044 | 75.0 ± 35.1 | 0.376 ± 0.035 | 133.4 ± 6.7 |
| **rl_dqn** | 0.071 ± 0.081 | 0.066 ± 0.136 | 109.0 ± 61.4 | 0.206 ± 0.234 | 32.1 ± 10.2 |

### Paired Statistical Significance vs Baselines
| Baseline | Metric | Proposed Mean | Baseline Mean | p-value (t-test) | Cohen's d | Superiority |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| sequential | threat_intercept_rate | 0.1255 | 0.0619 | 0.0000e+00 (*** (p < 0.001)) | 2.81 | **proposed** |
| sequential | periodic_revisit_rate | 0.0847 | 0.1348 | 1.2319e-02 (* (p < 0.05)) | -0.49 | **baseline** |
| sequential | mean_ttfi_steps | 47.201 | 32.6053 | 1.7150e-03 (** (p < 0.01)) | 0.63 | **baseline** |
| sequential | dwell_efficiency | 0.3634 | 0.1792 | 0.0000e+00 (*** (p < 0.001)) | 2.81 | **proposed** |
| random | threat_intercept_rate | 0.1255 | 0.0637 | 0.0000e+00 (*** (p < 0.001)) | 2.67 | **proposed** |
| random | periodic_revisit_rate | 0.0847 | 0.1258 | 6.8721e-02 (ns (not significant)) | -0.34 | **baseline** |
| random | mean_ttfi_steps | 47.201 | 46.756 | 9.4705e-01 (ns (not significant)) | 0.01 | **baseline** |
| random | dwell_efficiency | 0.3634 | 0.1841 | 0.0000e+00 (*** (p < 0.001)) | 2.68 | **proposed** |
| priority_rr | threat_intercept_rate | 0.1255 | 0.1303 | 2.4697e-01 (ns (not significant)) | -0.22 | **baseline** |
| priority_rr | periodic_revisit_rate | 0.0847 | 0.0611 | 2.5967e-01 (ns (not significant)) | 0.21 | **proposed** |
| priority_rr | mean_ttfi_steps | 47.201 | 74.9867 | 1.8450e-03 (** (p < 0.01)) | -0.63 | **proposed** |
| priority_rr | dwell_efficiency | 0.3634 | 0.3758 | 2.9536e-01 (ns (not significant)) | -0.20 | **baseline** |
| rl_dqn | threat_intercept_rate | 0.1255 | 0.0713 | 1.2870e-03 (** (p < 0.01)) | 0.65 | **proposed** |
| rl_dqn | periodic_revisit_rate | 0.0847 | 0.0661 | 5.8303e-01 (ns (not significant)) | 0.10 | **proposed** |
| rl_dqn | mean_ttfi_steps | 47.201 | 108.965 | 8.0000e-06 (*** (p < 0.001)) | -0.99 | **proposed** |
| rl_dqn | dwell_efficiency | 0.3634 | 0.2062 | 1.2980e-03 (** (p < 0.01)) | 0.65 | **proposed** |
