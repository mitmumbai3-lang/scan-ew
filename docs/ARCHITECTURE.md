# System Architecture: Smart Scan Strategy for Electronic Warfare (SIH26055 - DRDO)

## 1. Problem Formulation & Defense Context

An Electronic Support (ES) surveillance receiver operates in contested, high-density electromagnetic spectrum environments (typically covering 0.5 to 18.0 GHz). Modern radars, tactical datalinks, and active electronic attack (decoy/jammer) systems radiate simultaneously across this spectrum.

### The Hardware Bottleneck
While modern ES receivers possess high RF sensitivity, their instantaneous bandwidth (IBW) is fundamentally narrower than the total monitored spectrum. For example:
- **Total Monitored Spectrum**: $B_{total} = 17.5\text{ GHz}$ (0.5 – 18.0 GHz).
- **Instantaneous Bandwidth (IBW)**: $B_{IBW} \approx 500\text{ MHz} - 1.1\text{ GHz}$.
- **Sub-Band Partition**: The spectrum is discretized into $N$ contiguous sub-bands:
  $$\mathcal{B} = \{0, 1, \dots, N-1\}$$
- **Single-Band Dwell Constraint**: At any discrete dwell timestep $t$, the receiver can observe **at most one** sub-band $b_t \in \mathcal{B}$.
- **LO Retuning Delay**: Tuning the local oscillator (LO) frequency synthesizer from band $b_{t-1}$ to $b_t$ incurs a physical settling latency:
  $$t_{retune}(b_{t-1}, b_t) = t_{base} + \lambda_{hop} \cdot |b_t - b_{t-1}|$$

### The Algorithmic Challenge
The scheduler must decide which band to dwell on next in order to maximize threat detection and intercept consistency with **ZERO prior intelligence** regarding:
- Carrier frequencies
- Radar antenna scan periods ($T_{scan}$)
- Illumination beamwidths / dwell windows ($W$)
- Frequency-hopping sequences
- Distractor / decoy locations

---

## 2. High-Level Modular Architecture

```
+-------------------------------------------------------------------------------+
|                       SYNTHETIC RF ENVIRONMENT SIMULATOR                      |
|                                                                               |
|  +---------------------+   +---------------------+   +---------------------+  |
|  | Fixed Comm Emitters |   | Periodic Radars     |   | Agile Hopping Radars|  |
|  | (Continuous / Duty) |   | (Rotating Beams)    |   | (Markov / Pseudo)   |  |
|  +---------------------+   +---------------------+   +---------------------+  |
|                             \         |         /                             |
|                              v        v        v                              |
|                   +---------------------------------------+                   |
|                   |  Decoy / Continuous Barrage Jammers   |                   |
|                   +---------------------------------------+                   |
|                                       |                                       |
|                                       v                                       |
|                   +---------------------------------------+                   |
|                   |   RF Propagation & Detection Channel  |                   |
|                   |   - AWGN Noise Floor (-95 dBm)        |                   |
|                   |   - Log-Normal Fading Scintillation   |                   |
|                   |   - Sigmoidal Pd Curve & Noise Pfa    |                   |
|                   +---------------------------------------+                   |
+---------------------------------------|---------------------------------------+
                                        | (Physical Emissions)
                                        v
+-------------------------------------------------------------------------------+
|                             ES RECEIVER HARDWARE MODEL                        |
|                                                                               |
|   - Tuner LO Synthesizer: 1 Band per Dwell + Retune Settling Penalty          |
|   - Information Hiding: Strips emitter identities & false-alarm ground truth  |
|   - Output: Observation(band, hit: bool, measured_snr: float, pulse_count)    |
+---------------------------------------|---------------------------------------+
                                        | (Observation Feedback Only)
                                        v
+-------------------------------------------------------------------------------+
|                  PROPOSED ENGINE: SmartScan-BayesianRMAB                      |
|                                                                               |
|  +--------------------------------+   +------------------------------------+  |
|  | 1. Bayesian Belief Filter      |   | 2. Online Periodicity Tracker      |  |
|  |    Hidden Markov Model (HMM)   |   |    Inter-arrival histogramming &   |  |
|  |    Occupancy Posterior P(S_b=1)|   |    GCD / Autocorrelation scan T    |  |
|  +--------------------------------+   +------------------------------------+  |
|                 |                                      |                      |
|                 +------------------+-------------------+                      |
|                                    |                                          |
|                                    v                                          |
|                   +------------------------------------+                      |
|                   | 3. Restless Multi-Armed Bandit     |                      |
|                   |    Composite Priority Index I(b, t)|                      |
|                   |    - Exploitation: w_decoy * p_b   |                      |
|                   |    - Exploration: UCB non-stat     |                      |
|                   |    - Periodicity: Gamma_pred Boost |                      |
|                   |    - Synthesizer Retune Cost       |                      |
|                   |    - Hard Non-Starvation Floor     |                      |
|                   +------------------------------------+                      |
+---------------------------------------|---------------------------------------+
                                        | Next Band Choice: b* = argmax I(b, t)
                                        v (Tuning Command)
                                    [ES Tuner]
```

---

## 3. Mathematical Engine Specifications

### 3.1 Bayesian Occupancy Posterior (Hidden Markov Model)
Each sub-band $b \in \{0, \dots, N-1\}$ has a binary hidden state $S_{b,t} \in \{0, 1\}$, where $1$ denotes that an active RF emitter is illuminating the band at step $t$.

Between timesteps, the spectral state evolves via a 2-state Markov chain:
- Transition probability $p_{01} = P(S_{b,t}=1 | S_{b,t-1}=0) = 0.05$ (birth / hop-in probability).
- Transition probability $p_{10} = P(S_{b,t}=0 | S_{b,t-1}=1) = 0.08$ (death / hop-out probability).

#### Prior Prediction (Time Update)
For all bands $b$:
$$p_{b, t|t-1} = p_{b, t-1} \cdot (1 - p_{10}) + (1 - p_{b, t-1}) \cdot p_{01}$$
Notice that as an unobserved band elapses without visits, $p_{b, t|t-1}$ asymptotically regresses to the stationary probability:
$$\pi_\infty = \frac{p_{01}}{p_{01} + p_{10}} \approx 0.385$$
This provides a natural information-theoretic exploration incentive without ad-hoc rules.

#### Posterior Measurement Update (Visited Band $b^*$)
When observation $y \in \{0, 1\}$ is received on band $b^*$:
$$p_{b^*, t} = \frac{P(y | S=1) \cdot p_{b^*, t|t-1}}{P(y | S=1) \cdot p_{b^*, t|t-1} + P(y | S=0) \cdot (1 - p_{b^*, t|t-1})}$$
Where $P(y=1 | S=1) = P_d \approx 0.95$ and $P(y=1 | S=0) = P_{fa} \approx 0.02$.

---

### 3.2 Online Periodicity Tracking & Main-Beam Pre-Positioning
Rotating radars (e.g. 2D search, 3D surveillance) exhibit recurring illuminations when their main beam sweeps across the ES receiver:
- Scan period $T_{scan} \in [8, 60]\text{ steps}$
- Main beam dwell window $W \approx 2-3\text{ steps}$

#### Online Fundamental Period Extraction
Let arrival timestamps for band $b$ be $\{\tau_1, \tau_2, \dots, \tau_K\}$.
Differences are computed: $\Delta \tau_k = \tau_k - \tau_{k-1}$.
To identify the true fundamental period $T_{cand}$ without harmonic collapse (avoiding integer sub-multiples like $T/2$ or $T/3$):
$$\text{Score}(T) = \text{MatchRate}(T) \times \left(1.0 - 0.25 \frac{\sum (k_i - 1)}{\sum k_i}\right) - 0.1 \frac{\bar{e}_T}{T}$$
Where:
- $k_i = \text{round}(\Delta \tau_i / T)$ is the implied pass count.
- $\bar{e}_T$ is the mean absolute remainder error.
- The penalty $\frac{\sum (k_i - 1)}{\sum k_i}$ prevents phantom subharmonic pulses.

#### Pre-Positioning Boost Calculation
When confidence $C_b \ge 0.5$, the scheduler computes the next arrival step $\hat{t}_{next} = \tau_{last} + k \cdot \hat{T}$.
If $current\_step \in [\hat{t}_{next} - 1, \hat{t}_{next} + 1]$, a predictive Gaussian boost is added:
$$\Gamma_{pred}(b, t) = 2.5 \cdot C_b \cdot \exp\left(-\frac{(t - \hat{t}_{next})^2}{2}\right)$$
This elevates band $b$ to the top of the priority list precisely when the radar beam sweeps past, achieving near 100% illumination capture!

---

### 3.3 Decoy Suppression & Dwell Starvation Prevention
Barrage decoys radiate continuously ($> 95\%$ duty cycle) with high power ($> 20\text{ dB SNR}$) to induce dwell starvation in greedy schedulers.
Our algorithm evaluates hit continuity:
- If consecutive hits $> 12$ and no periodic beam modulation is detected:
  $$w_{decoy}(b) = \max\left(0.15, 1.0 - 0.05 \cdot (\text{hits}_{consecutive} - 12)\right)$$
This attenuates exploitation on decoy bands, liberating receiver dwell capacity to hunt for tactical threats.

---

### 3.4 Composite Restless Bandit Priority Index
At step $t$, for each band $b \in \{0, \dots, N-1\}$:
$$\boxed{I(b, t) = \underbrace{w_{decoy}(b) \cdot p_{b,t}}_{\text{Bayesian Exploitation}} + \underbrace{c_{expl} \sqrt{\frac{\ln(t+1)}{N_b + 1}} + \text{StarveBoost}(b)}_{\text{Exploration Floor}} + \underbrace{\Gamma_{pred}(b, t)}_{\text{Periodicity Pre-Position}} - \underbrace{\lambda_{tune} \frac{|b - b_{prev}|}{N}}_{\text{LO Retune Cost}}}$$
The tuner selects:
$$b^* = \arg\max_{b \in \mathcal{B}} I(b, t)$$
