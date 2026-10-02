"""
Electronic Support (ES) Receiver Model.
Enforces hardware physical constraints:
- Instantaneous Bandwidth (IBW) limited to 1 sub-band per dwell.
- Local Oscillator (LO) synthesizer retune delay when switching bands.
- Strict information hiding: Schedulers only receive binary hit/miss and measured SNR.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .config import SimConfig


@dataclass
class Observation:
    """Feedback returned to the scheduler after dwelling on a band."""
    band: int
    hit: bool
    measured_snr_db: float
    pulse_count: int
    step: int
    timestamp_ms: float
    retune_cost_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "band": self.band,
            "hit": self.hit,
            "measured_snr_db": self.measured_snr_db,
            "pulse_count": self.pulse_count,
            "step": self.step,
            "timestamp_ms": round(self.timestamp_ms, 2),
            "retune_cost_ms": round(self.retune_cost_ms, 2),
        }


@dataclass
class ReceiverTelemetry:
    """Internal ground-truth telemetry used ONLY for evaluation and visualization."""
    step: int
    dwell_band: int
    hit: bool
    measured_snr_db: float
    pulse_count: int
    retune_cost_ms: float
    cumulative_time_ms: float
    intercepted_emitter_ids: list = field(default_factory=list)
    is_false_alarm: bool = False
    is_decoy: bool = False


class ESReceiver:
    """
    Physical ES Receiver with LO retune dynamics and dwell control.
    """

    def __init__(self, config: SimConfig):
        self.config = config
        self.current_band: Optional[int] = None
        self.cumulative_time_ms: float = 0.0
        self.total_dwells: int = 0
        self.total_retune_cost_ms: float = 0.0

    def dwell(
        self,
        target_band: int,
        step: int,
        detection_result: tuple,  # (hit, snr, is_fa)
        active_emitters_in_band: list,
    ) -> tuple[Observation, ReceiverTelemetry]:
        """
        Executes a single dwell on the specified target_band.
        Enforces retuning delay and formats realistic observation.
        """
        if not (0 <= target_band < self.config.num_bands):
            raise ValueError(f"Target band {target_band} invalid for {self.config.num_bands} bands.")

        retune_cost_ms = self.config.calculate_retune_cost_ms(self.current_band, target_band)
        dwell_time_ms = self.config.dwell_time_ms

        self.cumulative_time_ms += retune_cost_ms + dwell_time_ms
        self.total_retune_cost_ms += retune_cost_ms
        self.total_dwells += 1
        self.current_band = target_band

        hit, measured_snr, is_fa = detection_result

        # Calculate observed pulse count
        pulse_count = 0
        intercepted_ids = []
        is_decoy = False

        if hit and not is_fa:
            for emitter in active_emitters_in_band:
                intercepted_ids.append(emitter.id)
                pulse_count += emitter.get_pulse_count(step)
                emitter.intercept_count += 1
                if emitter.emitter_type == "decoy":
                    is_decoy = True
        elif hit and is_fa:
            pulse_count = 1  # False alarm artifact

        # Scheduler-facing observation (strictly no ground-truth IDs or emitter types)
        observation = Observation(
            band=target_band,
            hit=hit,
            measured_snr_db=measured_snr,
            pulse_count=pulse_count,
            step=step,
            timestamp_ms=self.cumulative_time_ms,
            retune_cost_ms=retune_cost_ms,
        )

        # Ground-truth telemetry (for metrics and supervisor/UI)
        telemetry = ReceiverTelemetry(
            step=step,
            dwell_band=target_band,
            hit=hit,
            measured_snr_db=measured_snr,
            pulse_count=pulse_count,
            retune_cost_ms=retune_cost_ms,
            cumulative_time_ms=self.cumulative_time_ms,
            intercepted_emitter_ids=intercepted_ids,
            is_false_alarm=is_fa,
            is_decoy=is_decoy,
        )

        return observation, telemetry

    def reset(self):
        self.current_band = None
        self.cumulative_time_ms = 0.0
        self.total_dwells = 0
        self.total_retune_cost_ms = 0.0
