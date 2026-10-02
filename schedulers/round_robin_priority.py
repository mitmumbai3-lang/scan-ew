"""
Baseline Scheduler: Weighted Priority Round-Robin.
Interleaves exploratory sweeping with priority revisits to bands where hits were recently observed.
"""
from typing import Dict, Any, List, Optional
import numpy as np
from .base import BaseScheduler
from sim.receiver import Observation


class RoundRobinPriorityScheduler(BaseScheduler):
    """
    Priority Round-Robin Baseline.
    Allocates 60% of dwells to active bands (recent hits) and 40% to sweeping unexplored bands.
    """

    def __init__(self, num_bands: int = 16, explore_rate: float = 0.35, seed: Optional[int] = None):
        super().__init__(num_bands=num_bands, name="Priority Round-Robin")
        self.explore_rate = explore_rate
        self.last_hit_step: List[int] = [-1000] * num_bands
        self.sweep_pointer: int = 0
        self.rng = np.random.default_rng(seed)
        self.seed = seed

    def select_band(self, current_step: int) -> int:
        active_bands = [
            b for b in range(self.num_bands)
            if (current_step - self.last_hit_step[b]) <= 25
        ]

        # Exploration vs exploitation coin flip
        if not active_bands or self.rng.uniform(0.0, 1.0) < self.explore_rate:
            band = self.sweep_pointer
            self.sweep_pointer = (self.sweep_pointer + 1) % self.num_bands
            return band
        else:
            # Round-robin among active bands
            idx = int(self.rng.integers(0, len(active_bands)))
            return active_bands[idx]

    def observe(self, observation: Observation):
        super().observe(observation)
        if observation.hit:
            self.last_hit_step[observation.band] = observation.step

    def get_explainability_info(self, current_step: int) -> Dict[str, Any]:
        info = super().get_explainability_info(current_step)
        for b in range(self.num_bands):
            is_active = (current_step - self.last_hit_step[b]) <= 25
            info["components"][b] = {
                "total_score": 1.0 if is_active else 0.35,
                "exploitation": 1.0 if is_active else 0.0,
                "exploration": 0.35,
                "periodicity_boost": 0.0,
                "retune_penalty": 0.0,
                "decoy_discount": 0.0,
                "reason": "Active target" if is_active else "Exploration pool",
            }
        return info

    def reset(self):
        super().reset()
        self.last_hit_step = [-1000] * self.num_bands
        self.sweep_pointer = 0
        self.rng = np.random.default_rng(self.seed)
