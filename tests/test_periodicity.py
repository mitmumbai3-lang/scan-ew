"""
Unit tests for Periodicity Tracker and Pre-Positioning Engine.
"""
import pytest
from schedulers.periodicity_tracker import BandPeriodTracker, PeriodicityEngine


def test_period_tracker_estimation():
    tracker = BandPeriodTracker(band=3, min_period=5, max_period=50)

    # Simulate periodic radar with period = 18 steps
    # Detections occur at steps: 12, 30, 48, 66, 84
    true_period = 18
    start_step = 12
    for i in range(6):
        tracker.record_hit(start_step + i * true_period)

    assert tracker.estimated_period is not None
    assert abs(tracker.estimated_period - true_period) <= 1
    assert tracker.period_confidence >= 0.6


def test_preposition_boost_window():
    tracker = BandPeriodTracker(band=2, min_period=5, max_period=50)
    true_period = 20

    for i in range(5):
        tracker.record_hit(10 + i * true_period)  # 10, 30, 50, 70, 90

    # Next expected hit should be around 110
    # At step 100, delta = 10 -> boost is 0
    boost_100, exp_step = tracker.get_preposition_boost(100)
    assert boost_100 == 0.0
    assert exp_step == 110

    # At step 109 (1 step before 110) -> in pre-positioning window!
    boost_109, exp_step_109 = tracker.get_preposition_boost(109)
    assert boost_109 > 0.5
    assert exp_step_109 == 110


def test_periodicity_engine_multi_band():
    engine = PeriodicityEngine(num_bands=8)
    # Band 1 has period 15
    for i in range(5):
        engine.record_observation(band=1, hit=True, step=15 * i)

    estimates = engine.get_period_estimates()
    assert 1 in estimates
    assert abs(estimates[1]["estimated_period"] - 15) <= 1
