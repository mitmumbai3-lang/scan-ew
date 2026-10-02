"""
Base class and interface for Electronic Support (ES) spectrum schedulers.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from sim.receiver import Observation


class BaseScheduler(ABC):
    """
    Abstract Base Class for all spectrum schedulers.
    Defines the pluggable closed-loop interface: observe(feedback) -> select_band(step).
    """

    def __init__(self, num_bands: int, name: str):
        self.num_bands = num_bands
        self.name = name
        self.current_band: Optional[int] = None
        self.step_count: int = 0
        self.visit_counts: List[int] = [0] * num_bands
        self.hit_counts: List[int] = [0] * num_bands

    @abstractmethod
    def select_band(self, current_step: int) -> int:
        """Selects the next frequency band to dwell on (0 to num_bands - 1)."""
        pass

    @abstractmethod
    def observe(self, observation: Observation):
        """Processes observation feedback from the physical receiver."""
        self.current_band = observation.band
        self.visit_counts[observation.band] += 1
        if observation.hit:
            self.hit_counts[observation.band] += 1
        self.step_count += 1

    def get_belief_state(self) -> List[float]:
        """Returns per-band occupancy belief probabilities [0.0, 1.0]."""
        # Default placeholder: empirical hit frequency
        beliefs = []
        for v, h in zip(self.visit_counts, self.hit_counts):
            beliefs.append(h / v if v > 0 else 0.5)
        return beliefs

    def get_explainability_info(self, current_step: int) -> Dict[str, Any]:
        """Returns decision attribution breakdown for the current step."""
        return {
            "chosen_band": self.current_band if self.current_band is not None else 0,
            "step": current_step,
            "algorithm": self.name,
            "components": {
                b: {
                    "total_score": 0.0,
                    "exploitation": 0.0,
                    "exploration": 0.0,
                    "periodicity_boost": 0.0,
                    "retune_penalty": 0.0,
                    "decoy_discount": 0.0,
                }
                for b in range(self.num_bands)
            },
        }

    def reset(self):
        """Resets all internal scheduler state."""
        self.current_band = None
        self.step_count = 0
        self.visit_counts = [0] * self.num_bands
        self.hit_counts = [0] * self.num_bands
