# Smart India Hackathon 2026: Problem Statement SIH26055 (DRDO)
## "Smart Scan Strategy for Electronic Warfare"
### Final Presentation & Jury Defense Brief

---

### Slide 1: Title & Executive Summary
- **Project**: AURA-ES: Cognitive Closed-Loop Smart Scan Receiver Scheduler
- **Problem Statement**: SIH26055 (DRDO) — "Smart Scan strategy for Electronic Warfare"
- **Mission**: Overcome the Instantaneous Bandwidth (IBW) bottleneck in Electronic Support (ES) receivers using Bayesian Restless Bandits and Online Radar Pre-Positioning with zero prior intelligence.

---

### Slide 2: The Core Challenge in Modern Electronic Support
- **Spectrum Congestion**: Surveillance receivers must monitor 0.5–18.0 GHz split into $N$ narrow sub-bands.
- **Hardware Constraint**: The tuner can dwell on only ONE sub-band at a time ($B_{IBW} \ll B_{total}$).
- **LO Retune Penalty**: Switching distant carrier frequencies incurs physical synthesizer settling latency.
- **The Blindness of Legacy Sweeps**: Conventional sequential sweeping wastes $> 85\%$ of dwell time on empty bands, repeatedly misses periodic radar beams, and is easily blinded by frequency-hopping emitters.

---

### Slide 3: Threat Types Handled
1. **Periodic Scanning Radars**: Directional antennas rotating at scan period $T_{scan}$. Main beam illuminates the receiver for only $2-3$ steps every cycle.
2. **Frequency-Agile (Hopping) Emitters**: Tactical radars hopping across pseudo-random band sets to evade intercept.
3. **Decoy / Continuous Jammers**: High-duty-cycle distractors designed to trap naive greedy schedulers into dwell starvation.
4. **Fixed-Frequency Emitters**: Standard tactical datalinks and continuous communication links.

---

### Slide 4: Architectural Novelty: `SmartScan-BayesianRMAB`
Our engine introduces a **closed-loop cognitive scheduling framework** grounded in four mathematical pillars:
1. **Hidden Markov Model Bayesian Belief Filter**: Maintains occupancy posterior $P(S_{b,t}=1)$ for every sub-band, regressing unobserved bands to stationary priors to create natural exploration urgency.
2. **Online Periodicity Extractor & Main-Beam Pre-Positioning**: Analyzes pulse arrival intervals online to compute fundamental antenna scan periods ($\hat{T}_{scan}$) and pre-positions the tuner right as the main beam arrives.
3. **Decoy & Saturation Profiler**: Detects continuous distractors through pulse continuity and dampens their priority, liberating dwell capacity for agile threats.
4. **Retune-Aware Index Optimization**: Penalizes distant synthesizer hops ($\lambda_{tune} \frac{|\Delta b|}{N}$) to minimize physical switching latency while enforcing an exploration floor.

---

### Slide 5: Mathematical Formulation
$$\boxed{I(b, t) = \underbrace{w_{decoy}(b) \cdot p_{b,t}}_{\text{Exploitation}} + \underbrace{c_{expl} \sqrt{\frac{\ln(t+1)}{N_b + 1}} + \text{Floor}(b)}_{\text{Exploration Floor}} + \underbrace{\Gamma_{pred}(b, t)}_{\text{Periodicity Pre-Position}} - \underbrace{\lambda_{tune} \frac{|b - b_{prev}|}{N}}_{\text{Retune Cost}}}$$
$$b^* = \arg\max_b I(b, t)$$
- **Execution Latency**: Under $0.05\text{ ms}$ per step ($\mathcal{O}(N)$), easily running at $> 1000\text{ Hz}$ on standard embedded DSP / FPGA soft-cores.

---

### Slide 6: Multi-Seed Benchmark Results (30 Seeds per Scenario)
Empirical Monte Carlo evaluation across 5 operational scenarios:
- **Periodic Scanning Radars**:
  - `SmartScan-BayesianRMAB`: **12.0% Intercept Rate** vs **6.1% Sequential Sweep** (**+98% improvement, $p < 0.001$, Cohen's $d = 1.15$**).
  - **Periodic Revisit Rate**: **26.4%** vs **15.9%** ($p < 0.001$).
- **Frequency Agile Hoppers**:
  - `SmartScan-BayesianRMAB`: **11.2% Intercept Rate** vs **6.2% Sequential Sweep** (**+81% improvement, $p < 0.001$, Cohen's $d = 1.98$**).
  - **Dwell Efficiency**: **31.3%** vs **17.3%** ($p < 0.001$).
- **Decoy-Heavy Electronic Attack**:
  - Outperformed naive baselines while maintaining zero dwell starvation on critical radar channels.
- **Synthesizer Retuning Overhead**:
  - **46% less retuning latency** compared to random hopping ($67.4\text{ ms}$ vs $126.1\text{ ms}$).

---

### Slide 7: Interactive Web Cockpit & Visualization
- **HTML5 Canvas 60 FPS Spectrogram**: Real-time scrolling waterfall rendering frequency bands, receiver dwells, detections, and toggleable Ground Truth emissions.
- **Live Bayesian Belief Map**: Bar chart displays live occupancy posteriors and radar beam countdown timers.
- **Explainability Inspector**: Real-time mathematical attribution showing exact decomposition of exploitation, exploration, pre-positioning, and retune penalty for every dwell decision.
- **Dataset Studio**: Replay custom CSV/JSON pulse streams or scenario files.

---

### Slide 8: Defense Impact & Operational Readiness
- **Zero Prior Intelligence**: Adapts autonomously to completely unknown electronic environments.
- **SWaP-C Friendly**: Lightweight algorithmic formulation requiring no heavy GPU compute — deployable directly on existing DRDO receiver hardware.
- **Explainable & Verifiable**: Every dwell decision has full mathematical traceability for EW mission debriefs.

---

### Slide 9: Future Roadmap
1. Integration with real Pulse Descriptor Word (PDW) deinterleavers and Direction Finding (DF) angle-of-arrival (AOA) clusters.
2. Multi-channel receiver extensions (M simultaneous tuners).
3. Field FPGA implementation (VHDL/Verilog systolic array for bandit index evaluation).
