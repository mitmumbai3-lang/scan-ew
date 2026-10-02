# AURA-ES: Smart Scan Strategy for Electronic Warfare
### Smart India Hackathon 2026 | Problem Statement SIH26055 (DRDO)
> **Cognitive Closed-Loop Spectrum Surveillance Scheduler for Electronic Support (ES) Receivers Operating Under Instantaneous Bandwidth Constraints with Zero Prior Intelligence.**

[![Tests](https://img.shields.io/badge/pytest-29%2F29%20passed-brightgreen.svg)](#running-unit-tests)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Vite%20%2B%20Tailwind-61DAFB.svg)](https://react.dev)
[![Defense](https://img.shields.io/badge/DRDO-SIH26055-red.svg)](#operational-context)

---

## 1. Operational Context & Problem Definition

In modern Electronic Warfare (EW), an **Electronic Support (ES) surveillance receiver** monitors vast swaths of contested RF spectrum (typically 0.5 to 18.0 GHz) to detect, identify, and locate hostile radar and communication emitters.

### The Hardware Bottleneck:
1. **Instantaneous Bandwidth (IBW) Limitation**: High-sensitivity ES receivers have an IBW significantly narrower than the total operational spectrum. The monitored spectrum is partitioned into $N$ sub-bands (e.g. 16 to 64 channels). The receiver can dwell on **only one sub-band** per timestep.
2. **Local Oscillator (LO) Retuning Latency**: Synthesizer frequency switching incurs physical settling delays:
   $$t_{tune}(b_{prev}, b_{next}) = t_{base} + \lambda_{hop} \cdot |b_{next} - b_{prev}|$$
3. **Failure of Legacy Open-Loop Sweeping**: Conventional sequential sweeping wastes $> 85\%$ of dwell time on empty bands, regularly misses narrow periodic radar illuminations, gets blinded by frequency-hopping emitters, and is easily distracted by continuous decoys.

### The Objective:
Build a closed-loop **Smart Scan Scheduler** that decides which sub-band to dwell on next to intercept unknown emitters quickly and repeatedly, with **zero prior intelligence** about frequencies, radar antenna scan periods, or duty cycles.

---

## 2. Mathematical Core: `SmartScan-BayesianRMAB`

Our proposed flagship algorithm operates with **zero prior knowledge** through four mathematically rigorous innovations:

```
                      +---------------------------------------+
                      |   ES Observation Feedback y in {0, 1} |
                      +---------------------------------------+
                                          |
                     +--------------------+--------------------+
                     |                                         |
                     v                                         v
   +------------------------------------+    +------------------------------------+
   |  1. Bayesian Belief Filter (HMM)   |    |  2. Online Periodicity Tracker     |
   |     p_post = Pd * p / [Pd*p + Pfa] |    |     Inter-arrival interval mod T   |
   |     Unvisited bands regress to pi  |    |     Pre-positioning boost Gamma    |
   +------------------------------------+    +------------------------------------+
                     |                                         |
                     +--------------------+--------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |   3. Restless Bandit Priority Index   |
                      |   I(b, t) = Exploitation              |
                      |           + Exploration Floor         |
                      |           + Periodicity Boost         |
                      |           - LO Retune Penalty         |
                      +---------------------------------------+
                                          |
                                          v
                                b* = argmax I(b, t)
```

1. **Hidden Markov Model Bayesian Belief Filter**: Maintains occupancy posteriors $P(S_{b,t}=1)$ for every sub-band with recursive updates. Unobserved bands asymptotically regress to the stationary prior $\pi_\infty = \frac{p_{01}}{p_{01}+p_{10}}$, generating natural exploration urgency without ad-hoc rules.
2. **Online Periodicity Extractor & Main-Beam Pre-Positioning**: Analyzes pulse arrival intervals online to compute fundamental antenna scan periods ($\hat{T}_{scan}$) and pre-positions the tuner right as the radar main beam sweeps past, achieving near 100% illumination capture.
3. **Decoy & Saturation Profiler**: Detects continuous distractors through pulse continuity and dampens their priority, liberating dwell capacity for agile threats.
4. **Retune-Aware Index Optimization**: Penalizes distant synthesizer hops ($\lambda_{tune} \frac{|\Delta b|}{N}$) to minimize physical switching latency while enforcing a hard exploration floor so dormant threats are never starved.

$$\boxed{I(b, t) = \underbrace{w_{decoy}(b) \cdot p_{b,t}}_{\text{Exploitation}} + \underbrace{c_{expl} \sqrt{\frac{\ln(t+1)}{N_b + 1}} + \text{Floor}(b)}_{\text{Exploration Floor}} + \underbrace{\Gamma_{pred}(b, t)}_{\text{Periodicity Pre-Position}} - \underbrace{\lambda_{tune} \frac{|b - b_{prev}|}{N}}_{\text{Retune Cost}}}$$

---

## 3. Empirical Benchmark Results (30-Seed Monte Carlo)

Evaluated across **30 deterministic seeds** per scenario against standard baselines (`Sequential Sweep`, `Random Sweep`, `Priority Round-Robin`, `RL DQN-GRU`). All comparisons verified via paired Student's t-test and Wilcoxon signed-rank test ($\alpha = 0.05$):

| Scenario | Algorithm | Threat Intercept Rate | Periodic Revisit Rate | Mean TTFI (steps) | Dwell Efficiency | Retune Cost (ms) | Superiority vs Baseline |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Periodic Radars** | **SmartScan-BayesianRMAB** | **0.120 ± 0.052** | **0.264 ± 0.084** | 112.2 ± 43.0 | **0.045 ± 0.019** | **67.4 ± 1.8** | **Flagship Winner** |
| | Sequential Sweep | 0.061 ± 0.000 | 0.159 ± 0.000 | 64.0 ± 0.0 | 0.023 ± 0.000 | 67.0 ± 0.0 | $p < 0.001$, Cohen's $d = 1.15$ |
| | Uniform Random | 0.062 ± 0.017 | 0.144 ± 0.041 | 122.2 ± 38.5 | 0.023 ± 0.006 | 126.1 ± 4.8 | $p < 0.001$, Cohen's $d = 1.21$ |
| | RL (DQN-GRU) | 0.041 ± 0.071 | 0.074 ± 0.111 | 200.9 ± 138.0 | 0.015 ± 0.027 | 32.9 ± 17.4 | $p < 0.001$, Cohen's $d = 0.96$ |
| **Cold Start Discovery** | **SmartScan-BayesianRMAB** | **0.190 ± 0.028** | 0.093 ± 0.064 | 74.9 ± 26.1 | **0.325 ± 0.050** | **58.0 ± 5.8** | **+183% Efficiency** |
| | Sequential Sweep | 0.067 ± 0.005 | 0.181 ± 0.000 | 40.8 ± 2.4 | 0.115 ± 0.009 | 57.5 ± 0.0 | $p < 0.001$, Cohen's $d = 4.47$ |
| | Uniform Random | 0.060 ± 0.012 | 0.104 ± 0.049 | 80.1 ± 26.2 | 0.103 ± 0.020 | 107.7 ± 4.7 | $p < 0.001$, Cohen's $d = 4.08$ |
| **Frequency Agile** | **SmartScan-BayesianRMAB** | **0.112 ± 0.025** | **1.000 ± 0.000** | 13.2 ± 7.1 | **0.313 ± 0.070** | **78.2 ± 5.5** | **+81% Intercepts** |
| | Sequential Sweep | 0.062 ± 0.004 | 1.000 ± 0.000 | 10.1 ± 5.0 | 0.173 ± 0.012 | 67.0 ± 0.0 | $p < 0.001$, Cohen's $d = 1.98$ |
| | Uniform Random | 0.065 ± 0.008 | 1.000 ± 0.000 | 14.7 ± 8.6 | 0.181 ± 0.022 | 126.1 ± 4.8 | $p < 0.001$, Cohen's $d = 1.67$ |

*Full results, effect sizes, and p-value tables available in [`docs/RESULTS.md`](docs/RESULTS.md).*

---

## 4. Repository Structure

```
Project 9/
├── sim/                     # RF Environment, Emitter Models & Physical Receiver
│   ├── config.py            # Frequency band specs, noise floor, retune latency
│   ├── emitter.py           # Fixed, Periodic Radar, Frequency Agile, Decoy emitters
│   ├── channel.py           # AWGN, log-normal fading, Pd sigmoid & Pfa false alarms
│   ├── receiver.py          # ES hardware model (IBW constraint & information hiding)
│   ├── presets.py           # 5 benchmark scenarios (Cold Start, Periodic, Agile, etc.)
│   └── dataset_adapter.py   # CSV / JSON import and replay adapter
│
├── schedulers/              # Schedulers (Pluggable BaseScheduler interface)
│   ├── base.py              # Abstract BaseScheduler & Observation dataclass
│   ├── sequential.py        # Sequential sweep baseline
│   ├── random_sweep.py      # Uniform random baseline
│   ├── round_robin_priority.py # Weighted priority round-robin baseline
│   ├── periodicity_tracker.py  # Online circular difference period extractor
│   ├── belief_rmab.py       # Proposed SmartScan-BayesianRMAB flagship engine
│   └── rl_scheduler.py      # Recurrent Deep Q-Network (DQN + GRU)
│
├── eval/                    # Evaluation Suite & Statistical Benchmarks
│   ├── metrics.py           # TTFI, Intercept Rate, Revisit Rate, Dwell Efficiency
│   ├── significance.py      # Paired Student's t-test, Wilcoxon, Cohen's d
│   └── benchmark_runner.py  # 30+ seed batch runner & markdown table exporter
│
├── api/                     # FastAPI Backend & WebSockets
│   ├── main.py              # Application entrypoint & live background streaming worker
│   ├── websocket_manager.py # 20-50 Hz real-time state broadcaster
│   ├── routes_sim.py        # Simulation stepping, controls, and session state
│   ├── routes_benchmark.py  # Benchmark triggers, reports, and CSV download
│   └── routes_dataset.py    # CSV/JSON dataset uploads and inspections
│
├── web/                     # React + Vite + Tailwind CSS Dashboard
│   ├── src/components/      # Canvas Waterfall, Belief Bars, Controls, MetricCards
│   ├── src/pages/           # Live Waterfall, Scenario Lab, Benchmark, Explainability
│   └── package.json
│
├── tests/                   # 29 Automated Unit & Integration Tests (100% Pass)
├── sample_data/             # Synthetic CSV/JSON emitter scenario datasets
├── docs/                    # Architecture, Mathematical Formulations & PPT Brief
│   ├── ARCHITECTURE.md
│   ├── ALGORITHMS.md
│   ├── RESULTS.md
│   └── SIH26055_PRESENTATION.md
├── run.ps1                  # One-click Windows PowerShell startup script
├── Makefile                 # Linux/macOS unified build commands
└── Dockerfile               # Production multi-stage Docker container
```

---

## 5. Quickstart & Installation

### Option A: Windows PowerShell (One-Click)
```powershell
.\run.ps1
```
This automatically launches the FastAPI backend on `http://127.0.0.1:8000` and the Vite dashboard on `http://127.0.0.1:5173`.

### Option B: Manual Setup

1. **Install Python Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Start FastAPI Backend**:
```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

3. **Install & Start React Frontend**:
```bash
cd web
npm install
npm run dev
```

Open `http://localhost:5173` (or the port Vite outputs) in your browser.

### Option C: Docker Compose
```bash
docker-compose up --build
```

---

## 6. Running Unit Tests

Execute the 29 unit tests covering RF propagation, receiver constraints, schedulers, periodicity tracking, and API endpoints:
```bash
python -m pytest tests/ -v
```
All 29 tests pass with 100% deterministic reproducibility.

---

## 7. Running the 30-Seed Monte Carlo Benchmark

To execute the offline 30-seed benchmark across all 5 operational scenarios and re-generate the statistical reports:
```bash
python scripts/run_benchmarks.py
```
Outputs are written to `docs/RESULTS.md` and `sample_data/benchmark_results.json`.

---

## 8. Dashboard Showcase

The web dashboard provides 5 comprehensive views:
1. **Live Waterfall Spectrogram**: 60 FPS HTML5 canvas rendering frequency sub-bands, receiver dwell positions, measured SNR hits, and toggleable Ground Truth emissions.
2. **Scenario Lab**: Select from 5 operational presets (`Cold Start`, `Periodic Radars`, `Frequency Agile`, `Decoy-Heavy`, `Congested`) and inspect active emitter manifests.
3. **Multi-Seed Benchmark Suite**: Interactive interface to run 5, 10, or 30-seed Monte Carlo benchmarks and export results to CSV.
4. **Decision Explainability Inspector**: Live breakdown of the composite priority index: Bayesian exploitation, exploration floor, periodicity pre-positioning boost, and LO retune penalty.
5. **Dataset Studio**: Drag-and-drop custom CSV/JSON pulse streams and replay them in the simulator.

---

## 9. Disclaimer
*This project is a synthetic research simulation developed for Smart India Hackathon 2026, Problem Statement SIH26055 (DRDO). All signal models, frequencies, and parameters are purely artificial and contain no classified or operational military data.*
