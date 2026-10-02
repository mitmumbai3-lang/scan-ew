"""
RF Channel and Detection physics model.
Calculates SNR with log-normal fading, detection probability (Pd),
and noise-induced false alarms (Pfa).
"""
import numpy as np
from typing import Tuple, Optional


class RFChannel:
    """
    Simulates RF propagation, receiver noise floor, and detection statistics.
    """

    def __init__(
        self,
        noise_floor_dbm: float = -95.0,
        snr_threshold_db: float = 8.0,
        default_p_fa: float = 0.02,
        fading_std_db: float = 1.5,
        seed: Optional[int] = None,
    ):
        self.noise_floor_dbm = noise_floor_dbm
        self.snr_threshold_db = snr_threshold_db
        self.default_p_fa = default_p_fa
        self.fading_std_db = fading_std_db
        self.rng = np.random.default_rng(seed)

    def calculate_pd(self, snr_db: float) -> float:
        """
        Sigmoidal detection probability curve modeling an energy/envelope detector.
        At SNR = snr_threshold_db, Pd is ~0.5. At SNR >= threshold + 6 dB, Pd > 0.98.
        """
        k = 0.75  # Slope factor
        logit = k * (snr_db - self.snr_threshold_db)
        # Numerical stability clip
        logit = np.clip(logit, -20.0, 20.0)
        pd = 1.0 / (1.0 + np.exp(-logit))
        return float(pd)

    def simulate_detection(
        self,
        nominal_snr_db: Optional[float],
        is_signal_present: bool,
    ) -> Tuple[bool, float, bool]:
        """
        Simulates single dwell detection test.
        Returns:
            (hit: bool, measured_snr_db: float, is_false_alarm: bool)
        """
        if is_signal_present and nominal_snr_db is not None:
            # Add fading noise
            fading = self.rng.normal(0.0, self.fading_std_db)
            actual_snr_db = max(0.0, nominal_snr_db + fading)
            pd = self.calculate_pd(actual_snr_db)

            # Did detector trigger on signal?
            detected = bool(self.rng.uniform(0.0, 1.0) <= pd)
            if detected:
                # Add slight measurement estimation error to reported SNR
                meas_noise = self.rng.normal(0.0, 0.5)
                measured_snr = round(max(1.0, actual_snr_db + meas_noise), 2)
                return True, measured_snr, False
            else:
                # Signal was present but missed (missed detection)
                # However, noise might still trigger a false alarm
                if self.rng.uniform(0.0, 1.0) <= self.default_p_fa:
                    fa_snr = round(float(self.rng.uniform(1.0, 4.0)), 2)
                    return True, fa_snr, True
                return False, 0.0, False
        else:
            # Noise only -> check for false alarm
            is_fa = bool(self.rng.uniform(0.0, 1.0) <= self.default_p_fa)
            if is_fa:
                fa_snr = round(float(self.rng.uniform(1.0, 4.5)), 2)
                return True, fa_snr, True
            return False, 0.0, False

    def reset(self, seed: Optional[int] = None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
