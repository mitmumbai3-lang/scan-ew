"""
Baseline Scheduler: Sequential Sweep.
Classic open-loop round-robin scan across all frequency channels.
"""
from typing import Dict, Any
from .base import BaseScheduler
from sim.receiver import Observation


class SequentialScheduler(BaseScheduler):
    """
    Standard open-loop sequential sweep: 0 -> 1 -> ... -> N-1 -> 0.
    Wastes dwell time on empty bands and suffers high latency on periodic threats.
    """

    def __init__(self, num_bands: int = 16):
        super().__init__(num_bands=num_bands, name="Sequential Sweep")
        self.next_band_idx: int = 0

    def select_band(self, current_step: int) -> int:
        band = self.next_band_idx
        self.next_band_idx = (self.next_band_idx + 1) % self.num_bands
        return band

    def observe(self, observation: Observation):
        super().observe(observation)

    def get_explainability_info(self, current_step: int) -> Dict[str, Any]:
        info = super().get_explainability_info(current_step)
        for b in range(self.num_bands):
            is_chosen = (b == self.current_band)
            info["components"][b] = {
                "total_score": 1.0 if is_chosen else 0.0,
                "exploitation": 0.0,
                "exploration": 1.0 if is_chosen else 0.0,
                "periodicity_boost": 0.0,
                "retune_penalty": 0.0,
                "decoy_discount": 0.0,
                "reason": "Sequential order" if is_chosen else "Waiting in queue",
            }
        return info

    def reset(self):
        super().reset()
        self.next_band_idx = 0
