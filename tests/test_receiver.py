"""
Unit tests for ES Receiver model and information hiding guarantees.
"""
import pytest
from sim.config import SimConfig
from sim.receiver import ESReceiver, Observation, ReceiverTelemetry


def test_receiver_retune_and_dwell():
    config = SimConfig(num_bands=16, dwell_time_ms=2.0)
    receiver = ESReceiver(config)

    # First dwell on band 2
    obs1, telem1 = receiver.dwell(
        target_band=2,
        step=0,
        detection_result=(True, 20.5, False),
        active_emitters_in_band=[],
    )
    assert obs1.band == 2
    assert obs1.hit is True
    assert obs1.measured_snr_db == 20.5
    # Since from_band was None, initial retune is 0
    assert obs1.retune_cost_ms == 0.0
    assert receiver.cumulative_time_ms == 2.0

    # Second dwell hop to band 10 (hop distance = 8)
    obs2, telem2 = receiver.dwell(
        target_band=10,
        step=1,
        detection_result=(False, 0.0, False),
        active_emitters_in_band=[],
    )
    assert obs2.band == 10
    assert obs2.hit is False
    assert obs2.retune_cost_ms > 0.0
    # Strict information hiding check: observation dict must not leak internal ground-truth
    obs_dict = obs2.to_dict()
    assert "intercepted_emitter_ids" not in obs_dict
    assert "is_decoy" not in obs_dict
    assert "is_false_alarm" not in obs_dict


def test_receiver_invalid_band():
    config = SimConfig(num_bands=16)
    receiver = ESReceiver(config)
    with pytest.raises(ValueError):
        receiver.dwell(target_band=99, step=0, detection_result=(False, 0.0, False), active_emitters_in_band=[])
