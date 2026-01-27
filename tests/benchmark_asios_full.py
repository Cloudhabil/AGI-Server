#!/usr/bin/env python3
"""
ASIOS 2.0 Full Benchmark Suite
==============================

Tests the complete Lucas Architecture + Phi-Pi Gap + 18 Agents integration.

Run with: python tests/benchmark_asios_full.py
"""

import sys
import os
import time
import math
import random

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def run_benchmark():
    """Run the complete ASIOS benchmark suite."""

    print('=' * 75)
    print('ASIOS 2.0 FULL BENCHMARK SUITE')
    print('Lucas Architecture + Phi-Pi Gap + 18 Agents')
    print('=' * 75)
    print()

    results = {}
    start_time = time.time()

    # =========================================================================
    # BENCHMARK 1: Constants Verification
    # =========================================================================
    print('[1/8] CONSTANTS VERIFICATION')
    print('-' * 40)

    try:
        from src.core.constants import (
            PHI, PI, BETA_SECURITY, PHI_12, PHI_PI_GAP,
            LUCAS, LUCAS_TOTAL, GAMMA_TESSERACT,
            lucas_capacity, lucas_state, lucas_state_with_gap,
            transponder, transponder_dimension, transponder_phase,
            is_converged, creative_adjustment, verify_constants
        )

        v = verify_constants()

        tests = [
            ('phi^2 = phi + 1', abs(PHI**2 - (PHI + 1)) < 1e-14),
            ('alpha + beta = 1/phi', v['alpha_plus_beta_equals_1_over_phi']),
            ('beta^4 = gamma^3', v['grand_unification_beta4_equals_gamma3']),
            ('phi_12 = 0.31%', v['phi_12_is_0_31_percent']),
            ('gap = 1.16%', v['phi_pi_gap_is_1_16_percent']),
            ('Lucas total = 840', LUCAS_TOTAL == 840),
        ]

        passed = sum(1 for _, t in tests if t)
        for name, result in tests:
            status = 'PASS' if result else 'FAIL'
            print(f'  [{status}] {name}')

        results['constants'] = f'{passed}/{len(tests)}'
        print(f'  Result: {passed}/{len(tests)} passed')
    except Exception as e:
        results['constants'] = f'ERROR: {e}'
        print(f'  ERROR: {e}')
    print()

    # =========================================================================
    # BENCHMARK 2: Lucas Recurrence
    # =========================================================================
    print('[2/8] LUCAS NUMBER VERIFICATION')
    print('-' * 40)

    try:
        tests = []
        # Verify L(n) = L(n-1) + L(n-2)
        for n in range(3, 13):
            valid = LUCAS[n] == LUCAS[n-1] + LUCAS[n-2]
            tests.append((f'L({n}) = L({n-1}) + L({n-2})', valid))

        # Verify L(n) approx phi^n
        for n in [6, 9, 12]:
            diff = abs(LUCAS[n] - PHI**n)
            valid = diff < 0.1
            tests.append((f'L({n}) approx phi^{n} (diff={diff:.4f})', valid))

        passed = sum(1 for _, t in tests if t)
        for name, result in tests[:5]:
            status = 'PASS' if result else 'FAIL'
            print(f'  [{status}] {name}')
        print(f'  ... and {len(tests)-5} more')

        results['lucas'] = f'{passed}/{len(tests)}'
        print(f'  Result: {passed}/{len(tests)} passed')
    except Exception as e:
        results['lucas'] = f'ERROR: {e}'
        print(f'  ERROR: {e}')
    print()

    # =========================================================================
    # BENCHMARK 3: Transponder Accuracy
    # =========================================================================
    print('[3/8] TRANSPONDER ACCURACY')
    print('-' * 40)

    try:
        tests = []
        # Test dimensional thresholds
        thresholds = [(n, 1/PHI**n) for n in range(1, 13)]

        for n, threshold in thresholds:
            t = transponder(threshold * 0.99)
            valid = t['dimension_int'] == n
            tests.append((f'D{n} threshold', valid))

        # Test phase calculation
        for x in [0.25, 0.5, 0.75]:
            t = transponder(x)
            expected_phase = 2 * PI * x
            valid = abs(t['phase'] - expected_phase) < 1e-10
            tests.append((f'Phase at x={x}', valid))

        passed = sum(1 for _, t in tests if t)
        for name, result in tests[:6]:
            status = 'PASS' if result else 'FAIL'
            print(f'  [{status}] {name}')
        print(f'  ... and {len(tests)-6} more')

        results['transponder'] = f'{passed}/{len(tests)}'
        print(f'  Result: {passed}/{len(tests)} passed')
    except Exception as e:
        results['transponder'] = f'ERROR: {e}'
        print(f'  ERROR: {e}')
    print()

    # =========================================================================
    # BENCHMARK 4: Lucas State Mapping
    # =========================================================================
    print('[4/8] LUCAS STATE MAPPING')
    print('-' * 40)

    try:
        tests = []

        # Test state bounds
        for n in range(1, 13):
            for _ in range(10):
                x = random.uniform(0.001, 0.999)
                state = lucas_state(x, n)
                valid = 0 <= state < LUCAS[n]
                tests.append((f'D{n} state in bounds', valid))

        passed = sum(1 for _, t in tests if t)
        print(f'  Tested {len(tests)} random state mappings')
        print(f'  All states within [0, L(n)) bounds: {passed == len(tests)}')

        results['state_mapping'] = f'{passed}/{len(tests)}'
        print(f'  Result: {passed}/{len(tests)} passed')
    except Exception as e:
        results['state_mapping'] = f'ERROR: {e}'
        print(f'  ERROR: {e}')
    print()

    # =========================================================================
    # BENCHMARK 5: Creativity Gap Behavior
    # =========================================================================
    print('[5/8] CREATIVITY GAP BEHAVIOR')
    print('-' * 40)

    try:
        x = 0.1
        dim = 5

        states_normal = set()
        states_exploring = set()

        for _ in range(100):
            r1 = lucas_state_with_gap(x, dim, exploring=False)
            r2 = lucas_state_with_gap(x, dim, exploring=True)
            states_normal.add(r1['state'])
            states_exploring.add(r2['state'])

        tests = [
            ('Normal mode is deterministic', len(states_normal) == 1),
            ('Exploring mode varies', len(states_exploring) > 1),
            ('Variation within gap band', len(states_exploring) <= 3),
        ]

        passed = sum(1 for _, t in tests if t)
        for name, result in tests:
            status = 'PASS' if result else 'FAIL'
            print(f'  [{status}] {name}')

        print(f'  Normal states: {states_normal}')
        print(f'  Exploring states: {states_exploring}')

        results['creativity_gap'] = f'{passed}/{len(tests)}'
        print(f'  Result: {passed}/{len(tests)} passed')
    except Exception as e:
        results['creativity_gap'] = f'ERROR: {e}'
        print(f'  ERROR: {e}')
    print()

    # =========================================================================
    # BENCHMARK 6: Agent Suite Integration
    # =========================================================================
    print('[6/8] AGENT SUITE INTEGRATION')
    print('-' * 40)

    try:
        from src.core.biophilic_agent_suite import BiophilicAgentSuite

        suite = BiophilicAgentSuite()
        agents = suite.list_agents()

        dim_agents = len(agents['dimensional'])
        bio_agents = len(agents['biophilic'])

        tests = [
            ('12 dimensional agents', dim_agents == 12),
            ('6 biophilic agents', bio_agents == 6),
            ('Total 18 agents', dim_agents + bio_agents == 18),
        ]

        # Test agent activation
        for n in range(1, 13):
            x = 1 / PHI**n * 0.9
            t = transponder(x)
            valid = t['dimension_int'] == n
            tests.append((f'D{n} activation', valid))

        passed = sum(1 for _, t in tests if t)
        for name, result in tests[:6]:
            status = 'PASS' if result else 'FAIL'
            print(f'  [{status}] {name}')
        print(f'  ... and {len(tests)-6} more')

        results['agent_suite'] = f'{passed}/{len(tests)}'
        print(f'  Result: {passed}/{len(tests)} passed')
    except Exception as e:
        results['agent_suite'] = f'ERROR: {e}'
        print(f'  ERROR: {e}')
    print()

    # =========================================================================
    # BENCHMARK 7: Wormhole Engine Integration
    # =========================================================================
    print('[7/8] WORMHOLE ENGINE INTEGRATION')
    print('-' * 40)

    try:
        from src.core.brahim_wormhole_engine import BrahimWormholeEngine

        engine = BrahimWormholeEngine()
        validation = engine.validate()

        tests = [
            ('Geometry valid', validation.get('geometry_valid', False)),
            ('Traversable', validation.get('traversable', False)),
            ('Stable', validation.get('stable', False)),
            ('Sequence valid', validation.get('sequence_valid', False)),
            ('All valid', validation.get('all_valid', False)),
        ]

        passed = sum(1 for _, t in tests if t)
        for name, result in tests:
            status = 'PASS' if result else 'FAIL'
            print(f'  [{status}] {name}')

        results['wormhole'] = f'{passed}/{len(tests)}'
        print(f'  Result: {passed}/{len(tests)} passed')
    except Exception as e:
        results['wormhole'] = f'ERROR: {e}'
        print(f'  ERROR: {e}')
    print()

    # =========================================================================
    # BENCHMARK 8: Full Deployment Test
    # =========================================================================
    print('[8/8] FULL DEPLOYMENT TEST')
    print('-' * 40)

    try:
        import asios_deploy
        from asios_deploy import get_deployment

        # Reset and deploy
        asios_deploy._deployment = None

        deployment = get_deployment()
        result = deployment.initialize()

        tests = [
            ('Initialized', result['initialized']),
            ('7 subsystems', result['subsystems_total'] == 7),
            ('All subsystems OK', result['subsystems_ok'] == 7),
            ('100+ components', result['components'] >= 100),
        ]

        passed = sum(1 for _, t in tests if t)
        for name, res in tests:
            status = 'PASS' if res else 'FAIL'
            print(f'  [{status}] {name}')

        print(f'  Components: {result["components"]}')

        results['deployment'] = f'{passed}/{len(tests)}'
        print(f'  Result: {passed}/{len(tests)} passed')
    except Exception as e:
        results['deployment'] = f'ERROR: {e}'
        print(f'  ERROR: {e}')
    print()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    elapsed = time.time() - start_time

    print('=' * 75)
    print('BENCHMARK SUMMARY')
    print('=' * 75)
    print()

    total_passed = 0
    total_tests = 0

    for name, result in results.items():
        if '/' in str(result):
            p, t = result.split('/')
            total_passed += int(p)
            total_tests += int(t)
        print(f'  {name:20}: {result}')

    print()
    print(f'  TOTAL: {total_passed}/{total_tests} tests passed')
    print(f'  TIME:  {elapsed:.2f} seconds')
    print()

    if total_passed == total_tests:
        print('  STATUS: ALL BENCHMARKS PASSED!')
        status_code = 0
    else:
        print(f'  STATUS: {total_tests - total_passed} FAILURES')
        status_code = 1

    print()
    print('=' * 75)

    return status_code


if __name__ == '__main__':
    sys.exit(run_benchmark())
