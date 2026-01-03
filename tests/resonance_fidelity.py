from __future__ import annotations

import numpy as np

from core.resonant_kernel.interface import TemporalFormalismContract
from core.dense_logic.decoder import verify_intent_integrity


def test_resonance_compass_stable():
    contract = TemporalFormalismContract(state_dim=32, resonance_threshold=0.95)
    tokens = list(range(12))
    env = contract.observe_telemetry(10.0, 10.0)

    contract.evolve_state(tokens, env)
    result = contract.evolve_state(tokens, env)

    assert result["resonance_score"] >= 0.95
    assert result["is_stable"] is True


def test_intent_integrity_drift_small():
    contract = TemporalFormalismContract(state_dim=16)
    tokens = list(range(16))
    state = contract._tokens_to_state(tokens)
    drift = verify_intent_integrity(tokens, state, phase_mod=contract.phase_mod)

    assert drift < 1e-6


def test_environment_capture_guard():
    contract = TemporalFormalismContract(state_dim=16)
    tokens = list(range(16))
    env_bias = contract.observe_telemetry(100.0, 100.0)
    logic_state = contract._tokens_to_state(tokens)

    mixed = (logic_state * 0.7) + (env_bias * 0.3)
    drift_mixed = verify_intent_integrity(tokens, mixed, phase_mod=contract.phase_mod)
    drift_env = verify_intent_integrity(tokens, env_bias, phase_mod=contract.phase_mod)

    assert drift_mixed <= drift_env
