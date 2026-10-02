# Algorithmic Analysis: Electronic Warfare Schedulers

This document provides mathematical pseudocode, complexity analysis, and design rationales for the schedulers implemented in SIH26055 (DRDO).

---

## 1. Flagship: SmartScan-BayesianRMAB (Proposed)

### Design Rationale
In real-world EW operations, the surveillance receiver has no prior intelligence about threat frequencies or radar rotation periods. A pure greedy approach gets trapped by high-duty-cycle decoys or continuous emitters, whereas sequential sweeping suffers from blind spots on periodic beams and frequency agile hoppers. 

`SmartScan-BayesianRMAB` models the spectrum as a **Restless Multi-Armed Bandit (RMAB)** with Hidden Markov dynamics, augmented by an **Online Periodicity Extractor** and an **Information-Theoretic Exploration Floor**.

### Pseudocode
```python
class SmartScanScheduler:
    initialize:
        p01 = 0.05, p10 = 0.08
        pi_inf = p01 / (p01 + p10)
        beliefs = [pi_inf] * N
        visits = [0] * N
        consecutive_hits = [0] * N
        decoy_weights = [1.0] * N
        period_engine = PeriodicityEngine(N)

    function select_band(step t):
        # 1. State propagation forward in time (HMM time-update)
        for b in 0 to N-1:
            beliefs[b] = beliefs[b] * (1 - p10) + (1 - beliefs[b]) * p01
            steps_since_visit[b] += 1

        # 2. Online periodicity pre-positioning boost
        period_boosts = period_engine.get_boosts(current_step=t)

        # 3. Compute Restless Priority Index for each band
        for b in 0 to N-1:
            # A. Bayesian exploitation
            exploitation = decoy_weights[b] * beliefs[b]

            # B. Exploration bonus with non-starvation floor
            starvation = steps_since_visit[b]
            base_expl = c_expl * sqrt(ln(t + 1) / (visits[b] + 1))
            starve_boost = 0.4 * (starvation / (2 * N)) if starvation > 1.5 * N else 0.0
            exploration = base_expl + starve_boost

            # C. Periodicity boost for predicted main-beam arrival
            periodicity_boost = period_boosts[b].boost

            # D. LO synthesizer retune cost penalty
            retune_penalty = lambda_tune * abs(b - b_prev) / N

            # Composite Index
            I[b, t] = exploitation + exploration + periodicity_boost - retune_penalty

        # 4. Choose best band
        b_star = argmax_b I[b, t]
        return b_star

    function observe(Observation obs):
        band = obs.band
        hit = obs.hit
        t = obs.step

        # 1. Periodicity Engine update
        period_engine.record_observation(band, hit, t)

        # 2. Bayesian posterior update (HMM measurement-update)
        p_prior = beliefs[band]
        if hit:
            beliefs[band] = (Pd * p_prior) / [Pd * p_prior + Pfa * (1 - p_prior)]
            consecutive_hits[band] += 1
            if consecutive_hits[band] > 12:
                # Continuous distractor detected -> attenuate priority
                if not period_engine.has_periodic_modulation(band):
                    decoy_weights[band] = max(0.15, 1.0 - 0.05 * (consecutive_hits[band] - 12))
        else:
            beliefs[band] = ((1 - Pd) * p_prior) / [(1 - Pd) * p_prior + (1 - Pfa) * (1 - p_prior)]
            consecutive_hits[band] = 0
            decoy_weights[band] = min(1.0, decoy_weights[band] + 0.1)

        steps_since_visit[band] = 0
        b_prev = band
```

### Computational Complexity
- **Time Complexity per Dwell Step**: $\mathcal{O}(N)$ where $N$ is the number of sub-bands. For $N=16$ or $N=32$, selection takes under $0.05\text{ ms}$, effortlessly enabling hard real-time execution at $> 1000\text{ Hz}$.
- **Space Complexity**: $\mathcal{O}(N \cdot K)$ where $K$ is the circular timestamp buffer ($K \le 100$). Memory footprint $< 50\text{ KB}$.

---

## 2. Baselines for Comparison

### 2.1 Sequential Sweep (`SequentialScheduler`)
- **Policy**: Cycles sequentially through bands: $b_{t+1} = (b_t + 1) \bmod N$.
- **Strengths**: Deterministic, zero computational cost, predictable coverage.
- **Weaknesses**: Vulnerable to radar scan periodicity alignment (coincidental aliasing), wastes $85\%+$ of dwell time on empty bands, cannot track agile hoppers.

### 2.2 Uniform Random Sweep (`RandomSweepScheduler`)
- **Policy**: Uniform random sampling $b_t \sim \mathcal{U}(0, N-1)$.
- **Strengths**: No systematic blind spots, unbiased against pseudorandom hoppers.
- **Weaknesses**: High variance, highest synthesizer retuning cost ($126\text{ ms}$ avg), lacks cognitive memory.

### 2.3 Priority Round-Robin (`RoundRobinPriorityScheduler`)
- **Policy**: Interleaves $60\%$ dwell allocation to bands with recent hits (within 25 steps) and $40\%$ exploratory sweeps.
- **Strengths**: Good at staying on active targets once found.
- **Weaknesses**: Vulnerable to continuous decoys (gets stuck on jammer channels), lacks predictive pre-positioning.

### 2.4 Deep Q-Network + GRU (`RLScheduler`)
- **Policy**: Recurrent neural network mapping sequential state vectors (last band, hit, SNR, visit latencies) to per-band Q-values.
- **Strengths**: Can learn complex sequential dependencies.
- **Weaknesses**: Sample efficiency is low during cold start without extensive pre-training; higher inference latency than the Bayesian closed-form index.
