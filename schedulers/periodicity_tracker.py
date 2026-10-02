"""
Online Periodicity Estimator and Pre-Positioning Engine.
Tracks pulse/hit arrival timestamps for each frequency band, extracts fundamental scan periods
via online interval histogramming and GCD/autocorrelation, and computes pre-positioning boosts
to intercept periodic scanning radars just as their main beam illuminates the receiver.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np


class BandPeriodTracker:
    """Tracks arrival statistics and periodic recurrence for a single frequency band."""

    def __init__(self, band: int, min_period: int = 4, max_period: int = 80):
        self.band = band
        self.min_period = min_period
        self.max_period = max_period
        self.hit_timestamps: List[int] = []
        self.estimated_period: Optional[float] = None
        self.period_confidence: float = 0.0
        self.last_predicted_step: Optional[int] = None
        self.successful_predictions: int = 0
        self.missed_predictions: int = 0

    def record_hit(self, step: int):
        # Avoid duplicate hits on adjacent steps in the same beam dwell window
        if self.hit_timestamps and (step - self.hit_timestamps[-1]) <= 1:
            return

        self.hit_timestamps.append(step)
        if len(self.hit_timestamps) > 100:
            self.hit_timestamps.pop(0)

        self._update_period_estimate()

    def _update_period_estimate(self):
        """Estimates fundamental scan period from history of arrival times."""
        if len(self.hit_timestamps) < 3:
            return

        # Calculate inter-arrival intervals
        timestamps = np.array(self.hit_timestamps)
        diffs = np.diff(timestamps)

        # Filter diffs within plausible radar scan bounds
        valid_diffs = diffs[(diffs >= self.min_period) & (diffs <= self.max_period * 3)]
        if len(valid_diffs) < 2:
            return

        # Test candidate periods from min_period to max_period
        best_period = None
        best_score = -1.0

        for candidate_t in range(self.min_period, self.max_period + 1):
            remainders = valid_diffs % candidate_t
            errors = np.minimum(remainders, candidate_t - remainders)
            # Match tolerance: within 1 step or within 5% of candidate period
            tol = max(1, int(round(0.05 * candidate_t)))
            matches = np.mean(errors <= tol)

            if matches >= 0.65:
                # Implied multipliers k = round(diff / candidate_t)
                k_vals = np.maximum(1, np.round(valid_diffs / candidate_t))
                total_k = np.sum(k_vals)
                # Missing pulse penalty: prefer larger fundamental period over submultiples
                missing_ratio = float(np.sum(k_vals - 1.0) / total_k) if total_k > 0 else 0.0
                mean_err = float(np.mean(errors))
                score = matches * (1.0 - 0.25 * missing_ratio) - 0.1 * (mean_err / candidate_t)

                if score > best_score:
                    best_score = score
                    best_period = candidate_t

        if best_period is not None and best_score >= 0.5:
            self.estimated_period = float(best_period)
            count_factor = min(1.0, len(valid_diffs) / 4.0)
            self.period_confidence = round(float(min(1.0, best_score * count_factor)), 3)

    def get_preposition_boost(self, current_step: int) -> Tuple[float, Optional[int]]:
        """
        Calculates pre-positioning priority boost if an illumination is expected.
        Returns:
            (boost_score: float, expected_step: Optional[int])
        """
        if self.estimated_period is None or self.period_confidence < 0.5 or not self.hit_timestamps:
            return 0.0, None

        last_hit = self.hit_timestamps[-1]
        t_period = self.estimated_period
        steps_since_last = current_step - last_hit

        if steps_since_last < 0:
            return 0.0, None

        # Number of periods elapsed
        k = int(np.ceil(steps_since_last / t_period))
        if k == 0:
            k = 1

        expected_step = int(round(last_hit + k * t_period))
        delta = expected_step - current_step

        # If we are within +-1 step of the expected illumination window:
        if abs(delta) <= 1:
            # Gaussian bell curve around the peak
            boost = 2.5 * self.period_confidence * np.exp(-0.5 * (delta ** 2))
            return round(float(boost), 3), expected_step
        elif delta < -1:
            # Window passed without intercept -> slight confidence decay
            self.period_confidence = max(0.0, self.period_confidence - 0.02)
            return 0.0, None

        return 0.0, expected_step

    def reset(self):
        self.hit_timestamps = []
        self.estimated_period = None
        self.period_confidence = 0.0
        self.last_predicted_step = None
        self.successful_predictions = 0
        self.missed_predictions = 0


class PeriodicityEngine:
    """Manages periodicity tracking across all frequency bands."""

    def __init__(self, num_bands: int):
        self.num_bands = num_bands
        self.trackers = [BandPeriodTracker(b) for b in range(num_bands)]

    def record_observation(self, band: int, hit: bool, step: int):
        if hit:
            self.trackers[band].record_hit(step)

    def get_boosts(self, current_step: int) -> Dict[int, Tuple[float, Optional[int]]]:
        """Returns dict of band -> (boost, expected_arrival_step)."""
        return {b: self.trackers[b].get_preposition_boost(current_step) for b in range(self.num_bands)}

    def get_period_estimates(self) -> Dict[int, Dict[str, Any]]:
        result = {}
        for b, tracker in enumerate(self.trackers):
            if tracker.estimated_period is not None:
                result[b] = {
                    "estimated_period": tracker.estimated_period,
                    "confidence": tracker.period_confidence,
                    "sample_count": len(tracker.hit_timestamps),
                }
        return result

    def reset(self):
        for tracker in self.trackers:
            tracker.reset()
