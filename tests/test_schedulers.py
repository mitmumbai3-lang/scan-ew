"""
Unit tests for Schedulers: Sequential, Random, Priority Round-Robin, SmartScan-BayesianRMAB, and RL.
"""
import pytest
from sim.receiver import Observation
from schedulers import (
    SequentialScheduler,
    RandomSweepScheduler,
    RoundRobinPriorityScheduler,
    SmartScanScheduler,
    RLScheduler,
    get_scheduler,
    list_schedulers,
)


def test_scheduler_registry():
    schedulers = list_schedulers()
    assert len(schedulers) == 5
    sched_ids = [s["id"] for s in schedulers]
    assert "smart_scan" in sched_ids
    assert "sequential" in sched_ids
    assert "random" in sched_ids


def test_sequential_scheduler():
    scheduler = SequentialScheduler(num_bands=4)
    actions = [scheduler.select_band(i) for i in range(10)]
    assert actions == [0, 1, 2, 3, 0, 1, 2, 3, 0, 1]


def test_random_scheduler():
    scheduler = RandomSweepScheduler(num_bands=8, seed=42)
    actions = [scheduler.select_band(i) for i in range(20)]
    assert all(0 <= a < 8 for a in actions)
    # Uniform randomness should select multiple distinct bands
    assert len(set(actions)) > 3


def test_smart_scan_bayesian_updates():
    scheduler = SmartScanScheduler(num_bands=8, seed=42)
    init_beliefs = scheduler.get_belief_state()
    # Initial beliefs should be equal across all bands
    assert len(set(init_beliefs)) == 1

    # Dwell on band 2 with a HIT
    obs_hit = Observation(
        band=2, hit=True, measured_snr_db=20.0, pulse_count=5, step=0, timestamp_ms=2.0, retune_cost_ms=0.0
    )
    scheduler.observe(obs_hit)

    updated_beliefs = scheduler.get_belief_state()
    # Visited band 2 belief should increase significantly
    assert updated_beliefs[2] > init_beliefs[2]

    # Dwell on band 2 with a MISS
    obs_miss = Observation(
        band=2, hit=False, measured_snr_db=0.0, pulse_count=0, step=1, timestamp_ms=4.0, retune_cost_ms=0.0
    )
    scheduler.observe(obs_miss)
    assert scheduler.get_belief_state()[2] < updated_beliefs[2]


def test_smart_scan_decoy_suppression():
    scheduler = SmartScanScheduler(num_bands=8, seed=42)
    # Hit continuous decoy 20 times in a row
    for step in range(20):
        obs = Observation(
            band=1, hit=True, measured_snr_db=22.0, pulse_count=6, step=step, timestamp_ms=step * 2.0, retune_cost_ms=0.0
        )
        scheduler.observe(obs)

    # Decoy weight should have dropped below 1.0
    assert scheduler.decoy_weights[1] < 1.0


def test_smart_scan_explainability():
    scheduler = SmartScanScheduler(num_bands=8, seed=42)
    band = scheduler.select_band(0)
    info = scheduler.get_explainability_info(0)
    assert "components" in info
    assert band in info["components"]
    comp = info["components"][band]
    assert "total_score" in comp
    assert "exploitation" in comp
    assert "exploration" in comp
    assert "periodicity_boost" in comp
    assert "retune_penalty" in comp


def test_rl_scheduler():
    rl_sched = RLScheduler(num_bands=8, hidden_dim=32, seed=42)
    action = rl_sched.select_band(0)
    assert 0 <= action < 8

    obs = Observation(
        band=action, hit=True, measured_snr_db=18.0, pulse_count=4, step=0, timestamp_ms=2.0, retune_cost_ms=0.0
    )
    rl_sched.observe(obs)
    next_action = rl_sched.select_band(1)
    assert 0 <= next_action < 8
