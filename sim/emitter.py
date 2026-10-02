"""
Emitter definitions for synthetic Electronic Warfare (EW) spectrum simulation.
Models Fixed-Frequency, Periodic/Scanning Radar, Frequency-Agile (Hopping), and Decoy emitters.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np


class Emitter(ABC):
    """Abstract base class for all simulated RF emitters."""

    def __init__(
        self,
        id: str,
        name: str,
        emitter_type: str,
        priority: int = 1,
        base_snr_db: float = 18.0,
        start_step: int = 0,
        stop_step: Optional[int] = None,
    ):
        self.id = id
        self.name = name
        self.emitter_type = emitter_type
        self.priority = priority  # 1 = Critical/Threat, 2 = Medium, 3 = Decoy/Low
        self.base_snr_db = base_snr_db
        self.start_step = start_step
        self.stop_step = stop_step
        self.total_emissions = 0
        self.intercept_count = 0

    @abstractmethod
    def get_current_band(self, current_step: int) -> Optional[int]:
        """Returns active band index at current step, or None if inactive/silent."""
        pass

    def is_emitting(self, current_step: int) -> bool:
        if current_step < self.start_step:
            return False
        if self.stop_step is not None and current_step >= self.stop_step:
            return False
        return self.get_current_band(current_step) is not None

    def get_pulse_count(self, current_step: int) -> int:
        """Simulates number of pulses received within the dwell."""
        if not self.is_emitting(current_step):
            return 0
        return int(np.random.randint(3, 12))

    def reset(self):
        self.total_emissions = 0
        self.intercept_count = 0


class FixedEmitter(Emitter):
    """Fixed-frequency continuous or high-duty pulsed emitter."""

    def __init__(
        self,
        id: str,
        name: str,
        band: int,
        duty_cycle: float = 0.9,
        base_snr_db: float = 16.0,
        priority: int = 1,
        start_step: int = 0,
        stop_step: Optional[int] = None,
        seed: Optional[int] = None,
    ):
        super().__init__(id, name, "fixed", priority, base_snr_db, start_step, stop_step)
        self.band = band
        self.duty_cycle = min(max(duty_cycle, 0.05), 1.0)
        self.rng = np.random.default_rng(seed)

    def get_current_band(self, current_step: int) -> Optional[int]:
        if current_step < self.start_step or (self.stop_step and current_step >= self.stop_step):
            return None
        # Duty cycle check
        if self.rng.uniform(0.0, 1.0) <= self.duty_cycle:
            return self.band
        return None

    def reset(self):
        super().reset()


class PeriodicRadarEmitter(Emitter):
    """
    Periodic scanning radar emitter.
    Simulates a rotating search/acquisition radar whose main beam illuminates
    the surveillance receiver periodically every scan_period steps for beam_width steps.
    """

    def __init__(
        self,
        id: str,
        name: str,
        band: int,
        scan_period: int = 25,
        beam_width: int = 2,
        phase_offset: int = 0,
        base_snr_db: float = 22.0,
        sidelobe_snr_db: float = 2.0,
        priority: int = 1,
        start_step: int = 0,
        stop_step: Optional[int] = None,
    ):
        super().__init__(id, name, "periodic", priority, base_snr_db, start_step, stop_step)
        self.band = band
        self.scan_period = max(3, scan_period)
        self.beam_width = max(1, min(beam_width, self.scan_period - 1))
        self.phase_offset = phase_offset % self.scan_period
        self.sidelobe_snr_db = sidelobe_snr_db
        self.illumination_count = 0

    def is_in_main_beam(self, current_step: int) -> bool:
        if current_step < self.start_step or (self.stop_step and current_step >= self.stop_step):
            return False
        effective_step = (current_step + self.phase_offset) % self.scan_period
        return effective_step < self.beam_width

    def get_current_band(self, current_step: int) -> Optional[int]:
        if self.is_in_main_beam(current_step):
            return self.band
        return None

    def get_effective_snr(self, current_step: int) -> float:
        if self.is_in_main_beam(current_step):
            return self.base_snr_db
        return self.sidelobe_snr_db

    def reset(self):
        super().reset()
        self.illumination_count = 0


class FrequencyAgileEmitter(Emitter):
    """
    Frequency agile (hopping) emitter.
    Hops across a set of carrier bands in pseudorandom or cyclic patterns.
    """

    def __init__(
        self,
        id: str,
        name: str,
        hop_bands: List[int],
        dwell_per_hop: int = 1,
        hop_mode: str = "pseudorandom",  # "pseudorandom", "cyclic", or "markov"
        base_snr_db: float = 17.0,
        priority: int = 1,
        start_step: int = 0,
        stop_step: Optional[int] = None,
        seed: Optional[int] = None,
    ):
        super().__init__(id, name, "agile", priority, base_snr_db, start_step, stop_step)
        if not hop_bands:
            raise ValueError("hop_bands must contain at least one band")
        self.hop_bands = list(hop_bands)
        self.dwell_per_hop = max(1, dwell_per_hop)
        self.hop_mode = hop_mode
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._current_hop_idx = 0
        self._hop_schedule = self._generate_schedule(5000)

    def _generate_schedule(self, length: int) -> List[int]:
        schedule = []
        num_hops = int(np.ceil(length / self.dwell_per_hop))
        if self.hop_mode == "cyclic":
            for i in range(num_hops):
                band = self.hop_bands[i % len(self.hop_bands)]
                schedule.extend([band] * self.dwell_per_hop)
        else:  # pseudorandom
            for _ in range(num_hops):
                band = int(self.rng.choice(self.hop_bands))
                schedule.extend([band] * self.dwell_per_hop)
        return schedule[:length]

    def get_current_band(self, current_step: int) -> Optional[int]:
        if current_step < self.start_step or (self.stop_step and current_step >= self.stop_step):
            return None
        offset_step = current_step - self.start_step
        if offset_step >= len(self._hop_schedule):
            self._hop_schedule = self._generate_schedule(offset_step + 5000)
        return self._hop_schedule[offset_step]

    def reset(self):
        super().reset()
        self.rng = np.random.default_rng(self.seed)
        self._hop_schedule = self._generate_schedule(5000)


class DecoyEmitter(FixedEmitter):
    """
    Decoy emitter. Continuous, high-power or high-duty transmission designed to distract
    and saturate a naive scheduler's dwell time. Lowest operational priority (3).
    """

    def __init__(
        self,
        id: str,
        name: str,
        band: int,
        duty_cycle: float = 0.98,
        base_snr_db: float = 24.0,
        start_step: int = 0,
        stop_step: Optional[int] = None,
        seed: Optional[int] = None,
    ):
        super().__init__(
            id=id,
            name=name,
            band=band,
            duty_cycle=duty_cycle,
            base_snr_db=base_snr_db,
            priority=3,  # Decoy priority
            start_step=start_step,
            stop_step=stop_step,
            seed=seed,
        )
        self.emitter_type = "decoy"
