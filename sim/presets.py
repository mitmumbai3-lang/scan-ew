"""
Pre-configured evaluation scenarios for EW Smart Scan.
Provides benchmark presets:
1. Cold Start: New emitters appear without warning; tests rapid discovery.
2. Periodic Emitters: Rotating radars with distinctive scan periods; tests pre-positioning.
3. Frequency Agile: Fast-hopping emitters across band subsets; tests agile tracking.
4. Decoy-Heavy: Saturated continuous distractors; tests dwell starvation avoidance.
5. Multi-Emitter Congested: Realistic dense battlefield with mixed emitter classes.
"""
from typing import Dict, List, Tuple
from .config import SimConfig
from .emitter import Emitter, FixedEmitter, PeriodicRadarEmitter, FrequencyAgileEmitter, DecoyEmitter
from .rf_environment import RFEnvironment


def create_cold_start_scenario(num_bands: int = 16, seed: int = 42) -> Tuple[SimConfig, List[Emitter]]:
    config = SimConfig(num_bands=num_bands, max_steps_per_episode=300)
    emitters = [
        FixedEmitter(id="EM_FIXED_1", name="Long-Range Comm", band=2, duty_cycle=0.85, base_snr_db=16.0, start_step=0),
        PeriodicRadarEmitter(id="RADAR_SURV_1", name="Surveillance Radar S1", band=6, scan_period=20, beam_width=2, phase_offset=3, base_snr_db=22.0, start_step=15),
        FixedEmitter(id="EM_FIXED_2", name="Telemetry Link", band=9, duty_cycle=0.75, base_snr_db=15.0, start_step=40),
        PeriodicRadarEmitter(id="RADAR_FIRE_1", name="Fire Control Radar FC1", band=13, scan_period=14, beam_width=2, phase_offset=7, base_snr_db=24.0, start_step=60),
    ]
    return config, emitters


def create_periodic_emitters_scenario(num_bands: int = 16, seed: int = 42) -> Tuple[SimConfig, List[Emitter]]:
    config = SimConfig(num_bands=num_bands, max_steps_per_episode=350)
    emitters = [
        PeriodicRadarEmitter(id="RADAR_AIR_1", name="Air Defense Radar A1", band=3, scan_period=16, beam_width=2, phase_offset=0, base_snr_db=22.0),
        PeriodicRadarEmitter(id="RADAR_COASTAL_2", name="Coastal Early Warning C2", band=7, scan_period=28, beam_width=2, phase_offset=5, base_snr_db=20.0),
        PeriodicRadarEmitter(id="RADAR_TRACK_3", name="Target Tracking Radar T3", band=11, scan_period=21, beam_width=2, phase_offset=11, base_snr_db=25.0),
        PeriodicRadarEmitter(id="RADAR_SEARCH_4", name="Search Radar S4", band=14, scan_period=35, beam_width=3, phase_offset=18, base_snr_db=19.0),
    ]
    return config, emitters


def create_frequency_agile_scenario(num_bands: int = 16, seed: int = 42) -> Tuple[SimConfig, List[Emitter]]:
    config = SimConfig(num_bands=num_bands, max_steps_per_episode=350)
    emitters = [
        FrequencyAgileEmitter(
            id="AGILE_HOPPER_1",
            name="Agile Hopper Tactical-A",
            hop_bands=[1, 4, 8, 12],
            dwell_per_hop=2,
            hop_mode="pseudorandom",
            base_snr_db=18.0,
            seed=seed,
        ),
        FrequencyAgileEmitter(
            id="AGILE_HOPPER_2",
            name="Agile Hopper Tactical-B",
            hop_bands=[2, 6, 10, 14],
            dwell_per_hop=1,
            hop_mode="cyclic",
            base_snr_db=19.0,
            seed=seed + 1,
        ),
        FixedEmitter(id="EM_ANCHOR", name="Stationary Data Link", band=5, duty_cycle=0.8, base_snr_db=15.0),
    ]
    return config, emitters


def create_decoy_heavy_scenario(num_bands: int = 16, seed: int = 42) -> Tuple[SimConfig, List[Emitter]]:
    config = SimConfig(num_bands=num_bands, max_steps_per_episode=350)
    emitters = [
        DecoyEmitter(id="DECOY_JAMMER_1", name="High-Duty Decoy J1", band=3, duty_cycle=0.98, base_snr_db=25.0, seed=seed),
        DecoyEmitter(id="DECOY_JAMMER_2", name="High-Duty Decoy J2", band=9, duty_cycle=0.95, base_snr_db=23.0, seed=seed + 1),
        PeriodicRadarEmitter(id="HIGH_THREAT_RADAR", name="Priority Threat Radar R1", band=5, scan_period=20, beam_width=2, phase_offset=4, base_snr_db=22.0, priority=1),
        PeriodicRadarEmitter(id="HIGH_THREAT_MISSILE", name="Missile Guidance Radar R2", band=12, scan_period=15, beam_width=2, phase_offset=8, base_snr_db=24.0, priority=1),
        FixedEmitter(id="DISPERSED_COMM", name="Covert Tactical Comm", band=15, duty_cycle=0.6, base_snr_db=14.0, priority=2),
    ]
    return config, emitters


def create_congested_scenario(num_bands: int = 16, seed: int = 42) -> Tuple[SimConfig, List[Emitter]]:
    config = SimConfig(num_bands=num_bands, max_steps_per_episode=400)
    emitters = [
        FixedEmitter(id="EM_FIXED_COMM", name="C2 Tactical Radio", band=1, duty_cycle=0.8, base_snr_db=16.0),
        PeriodicRadarEmitter(id="RADAR_EARLY_WARN", name="Early Warning 3D Radar", band=4, scan_period=18, beam_width=2, phase_offset=2, base_snr_db=23.0),
        FrequencyAgileEmitter(id="AGILE_RADAR", name="Frequency-Agile Interceptor", hop_bands=[6, 7, 8, 10], dwell_per_hop=2, base_snr_db=18.0, seed=seed),
        DecoyEmitter(id="NOISE_DECOY", name="Broadband Barrage Decoy", band=11, duty_cycle=0.95, base_snr_db=22.0, seed=seed + 2),
        PeriodicRadarEmitter(id="RADAR_FIRE_CTRL", name="Multi-Function Tracking Radar", band=13, scan_period=26, beam_width=2, phase_offset=12, base_snr_db=25.0),
        FixedEmitter(id="EM_UAV_LINK", name="UAV Video Downlink", band=15, duty_cycle=0.9, base_snr_db=17.0),
    ]
    return config, emitters


PRESET_FACTORIES = {
    "cold_start": create_cold_start_scenario,
    "periodic_emitters": create_periodic_emitters_scenario,
    "frequency_agile": create_frequency_agile_scenario,
    "decoy_heavy": create_decoy_heavy_scenario,
    "congested": create_congested_scenario,
}

PRESET_METADATA = {
    "cold_start": {
        "name": "Cold Start Discovery",
        "description": "Uninformed surveillance where multiple unknown threats appear over time. Tests initial discovery speed.",
        "difficulty": "Medium",
    },
    "periodic_emitters": {
        "name": "Periodic Scanning Radars",
        "description": "Multiple rotating search and acquisition radars with narrow beam illumination windows. Tests scan period tracking and pre-positioning.",
        "difficulty": "Hard",
    },
    "frequency_agile": {
        "name": "Frequency Agile Hoppers",
        "description": "Hopping transmitters jumping across frequency sub-bands. Tests multi-band agility and non-stationarity handling.",
        "difficulty": "Hard",
    },
    "decoy_heavy": {
        "name": "Decoy-Heavy Electronic Attack",
        "description": "High-duty continuous noise distractors designed to trap naive schedulers. Tests decoy suppression and exploration floor.",
        "difficulty": "Very Hard",
    },
    "congested": {
        "name": "Congested Multi-Emitter Battlefield",
        "description": "Complex realistic operational environment combining fixed, periodic, agile, and decoy emitters simultaneously.",
        "difficulty": "Extreme",
    },
}


def list_available_presets() -> List[Dict]:
    return [
        {"id": key, **PRESET_METADATA[key]} for key in PRESET_FACTORIES.keys()
    ]


def get_scenario_preset(scenario_id: str, num_bands: int = 16, seed: int = 42) -> RFEnvironment:
    if scenario_id not in PRESET_FACTORIES:
        raise ValueError(f"Unknown scenario_id '{scenario_id}'. Available: {list(PRESET_FACTORIES.keys())}")
    config, emitters = PRESET_FACTORIES[scenario_id](num_bands=num_bands, seed=seed)
    return RFEnvironment(config=config, emitters=emitters, seed=seed)
