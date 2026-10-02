"""
RF Spectrum Environment Simulator.
Integrates emitters, propagation channel, and ES receiver into a cohesive discrete-time simulation.
"""
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from .config import SimConfig
from .emitter import Emitter
from .channel import RFChannel
from .receiver import ESReceiver, Observation, ReceiverTelemetry


class RFEnvironment:
    """
    Simulates the wideband RF spectral environment across discrete dwell timesteps.
    """

    def __init__(
        self,
        config: Optional[SimConfig] = None,
        emitters: Optional[List[Emitter]] = None,
        seed: Optional[int] = None,
    ):
        self.config = config or SimConfig()
        self.channel = RFChannel(
            noise_floor_dbm=self.config.noise_floor_dbm,
            snr_threshold_db=self.config.snr_threshold_db,
            default_p_fa=self.config.default_p_fa,
            seed=seed,
        )
        self.receiver = ESReceiver(self.config)
        self.emitters: List[Emitter] = emitters or []
        self.current_step: int = 0
        self.seed: Optional[int] = seed

    def add_emitter(self, emitter: Emitter):
        self.emitters.append(emitter)

    def get_ground_truth_active_emitters(self, step: int) -> Dict[int, List[Emitter]]:
        """Maps band_idx -> list of emitters actively radiating on that band."""
        active_map: Dict[int, List[Emitter]] = {b: [] for b in range(self.config.num_bands)}
        for emitter in self.emitters:
            band = emitter.get_current_band(step)
            if band is not None and 0 <= band < self.config.num_bands:
                active_map[band].append(emitter)
                emitter.total_emissions += 1
        return active_map

    def step(self, target_band: int) -> Tuple[Observation, ReceiverTelemetry, Dict[str, Any]]:
        """
        Advances the simulation by 1 dwell step on target_band.
        Returns:
            observation: Scheduler feedback (strictly realistic)
            telemetry: Detailed ground truth state for evaluation/UI
            info: Metadata about all active emitters across the spectrum
        """
        # 1. Determine active emissions across entire spectrum at this step
        active_map = self.get_ground_truth_active_emitters(self.current_step)
        active_in_target = active_map[target_band]

        # 2. Compute effective signal and SNR in chosen band
        is_signal_present = len(active_in_target) > 0
        if is_signal_present:
            # Aggregate SNR from active emitters in that band
            snr_vals = [e.base_snr_db for e in active_in_target]
            # Dominant emitter plus power sum approximation
            nominal_snr = float(max(snr_vals) + (1.5 if len(snr_vals) > 1 else 0.0))
        else:
            nominal_snr = None

        # 3. Simulate channel detection
        detection_result = self.channel.simulate_detection(nominal_snr, is_signal_present)

        # 4. Feed into ES receiver model
        observation, telemetry = self.receiver.dwell(
            target_band=target_band,
            step=self.current_step,
            detection_result=detection_result,
            active_emitters_in_band=active_in_target,
        )

        # 5. Format info dict for ground-truth inspection
        info = {
            "step": self.current_step,
            "spectrum_ground_truth": {
                b: [e.id for e in active_map[b]] for b in range(self.config.num_bands) if active_map[b]
            },
            "active_emitter_count": sum(len(el) for el in active_map.values()),
            "distinct_active_emitters": list({e.id for el in active_map.values() for e in el}),
            "done": self.current_step >= self.config.max_steps_per_episode - 1,
        }

        self.current_step += 1
        return observation, telemetry, info

    def reset(self, seed: Optional[int] = None) -> Observation:
        """Resets the environment for a new episode."""
        if seed is not None:
            self.seed = seed
        self.channel.reset(self.seed)
        self.receiver.reset()
        self.current_step = 0
        for emitter in self.emitters:
            emitter.reset()

        # Initial dummy observation before first action
        return Observation(
            band=0,
            hit=False,
            measured_snr_db=0.0,
            pulse_count=0,
            step=0,
            timestamp_ms=0.0,
            retune_cost_ms=0.0,
        )
