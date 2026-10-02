"""
RF Simulation package for Electronic Support (ES) Smart Scan.
"""
from .config import SimConfig
from .emitter import Emitter, FixedEmitter, PeriodicRadarEmitter, FrequencyAgileEmitter, DecoyEmitter
from .channel import RFChannel
from .rf_environment import RFEnvironment
from .receiver import ESReceiver, Observation
from .presets import get_scenario_preset, list_available_presets

__all__ = [
    "SimConfig",
    "Emitter",
    "FixedEmitter",
    "PeriodicRadarEmitter",
    "FrequencyAgileEmitter",
    "DecoyEmitter",
    "RFChannel",
    "RFEnvironment",
    "ESReceiver",
    "Observation",
    "get_scenario_preset",
    "list_available_presets",
]
