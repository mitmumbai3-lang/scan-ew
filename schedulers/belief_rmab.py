"""
SmartScan-BayesianRMAB: Bayesian Restless Multi-Armed Bandit Scheduler with
Online Periodicity Pre-Positioning, Decoy Suppression, and Retune Optimization.
"""
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from .base import BaseScheduler
from .periodicity_tracker import PeriodicityEngine
from sim.receiver import Observation


class SmartScanScheduler(BaseScheduler):
    """
    Proposed Flagship Scheduler: SmartScan-BayesianRMAB.
    Operates with ZERO prior intelligence about emitters.

    Combines:
    1. Recursive Bayesian Belief Filter (HMM occupancy posteriors).
    2. Online Periodicity Tracking with Pre-Positioning for rotating radars.
    3. Restless Multi-Armed Bandit Index balancing exploitation & exploration.
    4. Decoy & Saturation Profiler to avoid dwell starvation.
    5. Retune-distance awareness to minimize LO synthesizer latency.
    """

    def __init__(
        self,
        num_bands: int = 16,
        p01: float = 0.05,        # Prob idle band becomes active
        p10: float = 0.08,        # Prob active band becomes idle
        pd_nominal: float = 0.95, # Assumed detector Pd
        pfa_nominal: float = 0.02,# Assumed detector Pfa
        exploration_weight: float = 0.45,
        retune_penalty_weight: float = 0.12,
        seed: Optional[int] = None,
    ):
        super().__init__(num_bands=num_bands, name="SmartScan-BayesianRMAB")
        self.p01 = p01
        self.p10 = p10
        self.pd = pd_nominal
        self.pfa = pfa_nominal
        self.c_expl = exploration_weight
        self.lambda_tune = retune_penalty_weight
        self.rng = np.random.default_rng(seed)

        # Belief posteriors P(S_b = 1)
        self.stationary_prior = self.p01 / (self.p01 + self.p10)
        self.beliefs: List[float] = [self.stationary_prior] * num_bands

        # Steps since last visit for starvation prevention
        self.steps_since_visit: List[int] = [0] * num_bands

        # Decoy / saturation detector
        self.consecutive_hits: List[int] = [0] * num_bands
        self.decoy_weights: List[float] = [1.0] * num_bands

        # Online periodicity tracker
        self.periodicity_engine = PeriodicityEngine(num_bands)

        # Explainability cache
        self.last_decision_components: Dict[int, Dict[str, float]] = {}

    def get_belief_state(self) -> List[float]:
        return [round(b, 4) for b in self.beliefs]

    def _propagate_beliefs(self):
        """Propagates HMM transition forward by 1 time step for all bands."""
        for b in range(self.num_bands):
            # p(t|t-1) = p(t-1)*(1 - p10) + (1 - p(t-1))*p01
            p_prev = self.beliefs[b]
            p_prior = p_prev * (1.0 - self.p10) + (1.0 - p_prev) * self.p01
            self.beliefs[b] = float(np.clip(p_prior, 0.01, 0.99))
            self.steps_since_visit[b] += 1

    def select_band(self, current_step: int) -> int:
        # 1. Update state predictions forward in time
        self._propagate_beliefs()

        # 2. Get periodicity pre-positioning boosts
        period_boosts = self.periodicity_engine.get_boosts(current_step)

        best_band = 0
        highest_index = -1e9
        current_components = {}

        total_steps = max(1, self.step_count)

        for b in range(self.num_bands):
            # A. Bayesian Exploitation
            belief = self.beliefs[b]
            w_decoy = self.decoy_weights[b]
            exploitation = w_decoy * belief

            # B. Exploration Bonus (UCB-style with starvation acceleration)
            visits = self.visit_counts[b]
            starvation = self.steps_since_visit[b]
            base_expl = self.c_expl * np.sqrt(np.log(total_steps + 1.0) / (visits + 1.0))
            # Starvation floor: if not visited in > 2*N steps, boost urgency
            starve_boost = 0.4 * (starvation / (2.0 * self.num_bands)) if starvation > (self.num_bands * 1.5) else 0.0
            exploration = base_expl + starve_boost

            # C. Periodicity Pre-Positioning Boost
            boost, exp_step = period_boosts.get(b, (0.0, None))
            periodicity_boost = boost

            # D. Retune Penalty (LO synthesizer switching distance)
            if self.current_band is not None:
                dist = abs(b - self.current_band) / float(self.num_bands)
                retune_penalty = self.lambda_tune * dist
            else:
                retune_penalty = 0.0

            # Composite Priority Index
            total_score = exploitation + exploration + periodicity_boost - retune_penalty

            # Add tiny random jitter to break exact ties deterministically
            total_score += self.rng.uniform(0.0, 1e-5)

            current_components[b] = {
                "total_score": round(float(total_score), 4),
                "exploitation": round(float(exploitation), 4),
                "exploration": round(float(exploration), 4),
                "periodicity_boost": round(float(periodicity_boost), 4),
                "retune_penalty": round(float(retune_penalty), 4),
                "decoy_discount": round(float(1.0 - w_decoy), 4),
                "belief": round(float(belief), 4),
                "expected_period_step": exp_step,
            }

            if total_score > highest_index:
                highest_index = total_score
                best_band = b

        self.last_decision_components = current_components
        return best_band

    def observe(self, observation: Observation):
        super().observe(observation)
        band = observation.band
        hit = observation.hit
        step = observation.step

        # 1. Update Periodicity Engine
        self.periodicity_engine.record_observation(band, hit, step)

        # 2. Bayesian Posterior Update on visited band
        p_prior = self.beliefs[band]
        if hit:
            # P(y=1 | S=1) = Pd, P(y=1 | S=0) = Pfa
            num = self.pd * p_prior
            den = (self.pd * p_prior) + (self.pfa * (1.0 - p_prior))
        else:
            # P(y=0 | S=1) = 1 - Pd, P(y=0 | S=0) = 1 - Pfa
            num = (1.0 - self.pd) * p_prior
            den = ((1.0 - self.pd) * p_prior) + ((1.0 - self.pfa) * (1.0 - p_prior))

        p_post = num / den if den > 0 else p_prior
        self.beliefs[band] = float(np.clip(p_post, 0.01, 0.99))
        self.steps_since_visit[band] = 0

        # 3. Decoy & Saturation Profiling
        if hit:
            self.consecutive_hits[band] += 1
            # If a band is visited and hits continuously (> 12 times) without periodicity,
            # it is likely a continuous barrage decoy / jammer. Suppress weight.
            if self.consecutive_hits[band] > 12:
                tracker = self.periodicity_engine.trackers[band]
                # If no clear periodic pulse is present, attenuate
                if tracker.estimated_period is None or tracker.period_confidence < 0.4:
                    self.decoy_weights[band] = max(0.15, 1.0 - 0.05 * (self.consecutive_hits[band] - 12))
        else:
            self.consecutive_hits[band] = 0
            # Gradually restore weight if misses occur
            self.decoy_weights[band] = min(1.0, self.decoy_weights[band] + 0.1)

    def get_explainability_info(self, current_step: int) -> Dict[str, Any]:
        info = super().get_explainability_info(current_step)
        info["components"] = self.last_decision_components
        info["period_estimates"] = self.periodicity_engine.get_period_estimates()
        return info

    def reset(self):
        super().reset()
        self.beliefs = [self.stationary_prior] * self.num_bands
        self.steps_since_visit = [0] * self.num_bands
        self.consecutive_hits = [0] * self.num_bands
        self.decoy_weights = [1.0] * self.num_bands
        self.periodicity_engine.reset()
        self.last_decision_components = {}
