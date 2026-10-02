"""
Simulation configuration and spectral band definitions for Electronic Warfare (EW) Smart Scan.
"""
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class SimConfig:
    num_bands: int = 16
    freq_min_ghz: float = 0.5
    freq_max_ghz: float = 18.0
    dwell_time_ms: float = 2.0
    base_retune_time_ms: float = 0.1
    retune_time_per_hop_ms: float = 0.05
    noise_floor_dbm: float = -95.0
    default_p_fa: float = 0.02
    snr_threshold_db: float = 8.0
    max_steps_per_episode: int = 500

    def get_band_range_ghz(self, band_idx: int) -> Tuple[float, float]:
        """Returns the (low_ghz, high_ghz) frequency range for a sub-band."""
        if not (0 <= band_idx < self.num_bands):
            raise ValueError(f"band_idx {band_idx} out of range [0, {self.num_bands - 1}]")
        band_width = (self.freq_max_ghz - self.freq_min_ghz) / self.num_bands
        low = self.freq_min_ghz + band_idx * band_width
        high = low + band_width
        return round(low, 3), round(high, 3)

    def get_band_center_ghz(self, band_idx: int) -> float:
        low, high = self.get_band_range_ghz(band_idx)
        return round((low + high) / 2.0, 3)

    def calculate_retune_cost_ms(self, from_band: int, to_band: int) -> float:
        """Computes physical LO retuning latency based on band hopping distance."""
        if from_band is None or from_band == to_band:
            return 0.0
        hop_distance = abs(to_band - from_band)
        return round(self.base_retune_time_ms + hop_distance * self.retune_time_per_hop_ms, 3)
