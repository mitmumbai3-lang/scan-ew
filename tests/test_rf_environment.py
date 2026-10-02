"""
Unit tests for RF Environment, Emitters, and Channel physics.
"""
import pytest
from sim.config import SimConfig
from sim.emitter import FixedEmitter, PeriodicRadarEmitter, FrequencyAgileEmitter, DecoyEmitter
from sim.channel import RFChannel
from sim.rf_environment import RFEnvironment
from sim.presets import get_scenario_preset, list_available_presets
from sim.dataset_adapter import DatasetAdapter


def test_sim_config():
    config = SimConfig(num_bands=16, freq_min_ghz=0.5, freq_max_ghz=18.0)
    low, high = config.get_band_range_ghz(0)
    assert low == 0.5
    assert high > 0.5
    center = config.get_band_center_ghz(0)
    assert low < center < high

    # Retune cost check
    cost_0_to_0 = config.calculate_retune_cost_ms(0, 0)
    assert cost_0_to_0 == 0.0
    cost_0_to_5 = config.calculate_retune_cost_ms(0, 5)
    cost_0_to_10 = config.calculate_retune_cost_ms(0, 10)
    assert cost_0_to_10 > cost_0_to_5 > 0.0


def test_fixed_emitter():
    emitter = FixedEmitter(id="TEST_F1", name="Fixed 1", band=3, duty_cycle=1.0, seed=42)
    assert emitter.get_current_band(0) == 3
    assert emitter.is_emitting(0) is True


def test_periodic_emitter():
    # Scan period 10, beam width 2, phase offset 0
    emitter = PeriodicRadarEmitter(
        id="TEST_P1", name="Periodic 1", band=4, scan_period=10, beam_width=2, phase_offset=0
    )
    # Steps 0, 1 -> main beam
    assert emitter.get_current_band(0) == 4
    assert emitter.get_current_band(1) == 4
    # Step 2..9 -> silent / outside main beam
    assert emitter.get_current_band(2) is None
    assert emitter.get_current_band(9) is None
    # Step 10 -> back in main beam
    assert emitter.get_current_band(10) == 4


def test_frequency_agile_emitter():
    hop_bands = [1, 5, 8]
    emitter = FrequencyAgileEmitter(
        id="TEST_A1", name="Agile 1", hop_bands=hop_bands, dwell_per_hop=2, hop_mode="cyclic", seed=42
    )
    assert emitter.get_current_band(0) == 1
    assert emitter.get_current_band(1) == 1
    assert emitter.get_current_band(2) == 5
    assert emitter.get_current_band(3) == 5
    assert emitter.get_current_band(4) == 8


def test_decoy_emitter():
    emitter = DecoyEmitter(id="TEST_D1", name="Decoy 1", band=2, duty_cycle=1.0)
    assert emitter.priority == 3
    assert emitter.emitter_type == "decoy"
    assert emitter.get_current_band(0) == 2


def test_channel_detection():
    channel = RFChannel(snr_threshold_db=8.0, default_p_fa=0.0, seed=42)
    # High SNR -> Pd near 1
    pd_high = channel.calculate_pd(25.0)
    assert pd_high > 0.95
    # Low SNR -> Pd near 0
    pd_low = channel.calculate_pd(-5.0)
    assert pd_low < 0.05

    # Simulated hit with high SNR
    hit, snr, is_fa = channel.simulate_detection(25.0, is_signal_present=True)
    assert hit is True
    assert snr > 15.0
    assert is_fa is False


def test_rf_environment_step():
    env = get_scenario_preset("periodic_emitters", num_bands=16, seed=42)
    obs = env.reset(seed=42)
    assert obs.step == 0

    # Step on band 3 (where Air Defense Radar operates)
    obs, telem, info = env.step(target_band=3)
    assert obs.band == 3
    assert telem.dwell_band == 3
    assert "spectrum_ground_truth" in info
    assert env.current_step == 1


def test_dataset_adapter():
    presets = list_available_presets()
    assert len(presets) == 5

    env = get_scenario_preset("cold_start")
    json_data = DatasetAdapter.export_to_json(env)
    assert "emitters" in json_data
    assert len(json_data["emitters"]) == 4

    # Reimport
    reloaded_env = DatasetAdapter.load_from_json(json_data)
    assert len(reloaded_env.emitters) == 4
