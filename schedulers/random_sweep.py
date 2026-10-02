"""
Baseline Scheduler: Uniform Random Sweep.
Randomly selects an RF band uniformly at each dwell step.
"""
from typing import Dict, Any, Optional
import numpy as np
from .base import BaseScheduler
from sim.receiver import Observation


class RandomSweepScheduler(BaseScheduler):
    """
    Uniform random scheduler.
    Eliminates predictable blind spots but incurs erratic retuning costs
    and lacks memory or intelligence.
    """

    def __init__(self, num_bands: int = 16, seed: Optional[int] = None):
        super().__init__(num_bands=num_bands, name="Random Sweep")
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def select_band(self, current_step: int) -> int:
        return int(self.rng.integers(0, self.num_bands))

    def observe(self, observation: Observation):
        super().observe(observation)

    def get_explainability_info(self, current_step: int) -> Dict[str, Any]:
        info = super().get_explainability_info(current_step)
        prob = 1.0 / self.num_bands
        for b in range(self.num_bands):
            info["components"][b] = {
                "total_score": round(prob, 3),
                "exploitation": 0.0,
                "exploration": round(prob, 3),
                "periodicity_boost": 0.0,
                "retune_penalty": 0.0,
                "decoy_discount": 0.0,
                "reason": "Uniform random sampling",
            }
        return info

    def reset(self):
        super().reset()
        self.rng = np.random.default_rng(self.seed)
