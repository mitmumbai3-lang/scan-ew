"""
Schedulers package for Electronic Support Smart Scan.
"""
from .base import BaseScheduler
from .sequential import SequentialScheduler
from .random_sweep import RandomSweepScheduler
from .round_robin_priority import RoundRobinPriorityScheduler
from .periodicity_tracker import PeriodicityEngine, BandPeriodTracker
from .belief_rmab import SmartScanScheduler
from .rl_scheduler import RLScheduler

SCHEDULER_REGISTRY = {
    "smart_scan": SmartScanScheduler,
    "sequential": SequentialScheduler,
    "random": RandomSweepScheduler,
    "priority_rr": RoundRobinPriorityScheduler,
    "rl_dqn": RLScheduler,
}

SCHEDULER_METADATA = {
    "smart_scan": {
        "name": "SmartScan-BayesianRMAB (Proposed)",
        "type": "proposed",
        "description": "Bayesian Restless Bandit with online periodicity tracking, pre-positioning, decoy suppression, and retune optimization.",
        "badge": "DRDO Flagship",
    },
    "sequential": {
        "name": "Sequential Sweep",
        "type": "baseline",
        "description": "Open-loop round-robin scan across all sub-bands. Standard legacy EW receiver baseline.",
        "badge": "Baseline",
    },
    "random": {
        "name": "Random Sweep",
        "type": "baseline",
        "description": "Uniform random band hopping. Unbiased but erratic retuning and no learning.",
        "badge": "Baseline",
    },
    "priority_rr": {
        "name": "Priority Round-Robin",
        "type": "baseline",
        "description": "Weighted round-robin favoring bands with recent activity with exploratory sweep.",
        "badge": "Baseline",
    },
    "rl_dqn": {
        "name": "RL (DQN-GRU)",
        "type": "ml",
        "description": "Recurrent Deep Q-Network learning sequential EW band-selection policies.",
        "badge": "Neural",
    },
}


import inspect

def get_scheduler(scheduler_id: str, num_bands: int = 16, **kwargs) -> BaseScheduler:
    if scheduler_id not in SCHEDULER_REGISTRY:
        raise ValueError(f"Unknown scheduler_id '{scheduler_id}'. Available: {list(SCHEDULER_REGISTRY.keys())}")
    cls = SCHEDULER_REGISTRY[scheduler_id]
    sig = inspect.signature(cls.__init__)
    valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return cls(num_bands=num_bands, **valid_kwargs)


def list_schedulers():
    return [{"id": k, **SCHEDULER_METADATA[k]} for k in SCHEDULER_REGISTRY.keys()]


__all__ = [
    "BaseScheduler",
    "SequentialScheduler",
    "RandomSweepScheduler",
    "RoundRobinPriorityScheduler",
    "PeriodicityEngine",
    "BandPeriodTracker",
    "SmartScanScheduler",
    "RLScheduler",
    "get_scheduler",
    "list_schedulers",
    "SCHEDULER_REGISTRY",
    "SCHEDULER_METADATA",
]
