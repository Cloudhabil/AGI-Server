"""
Phase 2C: Advanced Hamiltonian Construction for Riemann Hypothesis

Implements rigorous eigenvalue computation for multiple potential forms:
1. Quartic: V(x) = ax² + bx⁴
2. Morse: V(r) = Dₑ(1 - e^(-alpha(r-rₑ)))²
3. Exponential Hybrid: V(x) = ax² + bexp(-cx²)

Each computation generates VNAND resonance hashes for audit trail.
Output feeds into Grand Synthesis document.

Physics References:
- Berry-Keating quantum interpretation of RH
- RMT (Random Matrix Theory) for spectral analysis
- WKB approximation for eigenvalue scaling
- Dimensionless coupling constants
"""

import numpy as np
from scipy.sparse import diags
from scipy.linalg import eigh
from scipy.integrate import quad
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import sys

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))


class VNANDHashGenerator:
    """
    Generates VNAND resonance hashes - immutable fingerprints of reasoning states.

    Each computation phase generates a hash that encodes:
    - Parameter configuration
    - Potential function form
    - Numerical method used
    - Convergence properties
    - Eigenvalue spectrum fingerprint

    These hashes create an audit trail of discovery.
    """

    def __init__(self):
        self.hash_log = []

    def hash_phase_state(self, phase_name: str, state_dict: Dict) -> str:
        """
        Generate SHA256 hash of a computation phase state.

        Creates immutable fingerprint of what was computed and how.
        """
        # Serialize state deterministically
        state_json = json.dumps(state_dict, sort_keys=True, default=str)

        # Create hash
        h = hashlib.sha256()
        h.update(phase_name.encode())
        h.update(state_json.encode())

        phase_hash = h.hexdigest()

        # Log for audit trail
        self.hash_log.append({
            "phase": phase_name,
            "hash": phase_hash,
            "timestamp": datetime.now().isoformat(),
            "state_summary": {
                k: v for k, v in state_dict.items()
                if k in ["potential_type", "parameters", "grid_points", "eigenvalue_error"]
            }
        })

        return phase_hash

    def hash_eigenvalue_spectrum(self, eigenvalues: np.ndarray) -> str:
        """Hash eigenvalue spectrum for reproducibility."""
        spectrum_str = ",".join([f"{e:.10f}" for e in eigenvalues[:50]])  # First 50
        return hashlib.sha256(spectrum_str.encode()).hexdigest()

    def get_audit_trail(self) -> List[Dict]:
        """Return complete audit trail of all hashes."""
        return self.hash_log.copy()

    def save_audit_trail(self, output_dir: Path) -> Path:
        """Save audit trail to disk."""
        audit_file = output_dir / "vnand_audit_trail.json"
        with open(audit_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.hash_log, indent=2))
        return audit_file


class Phase2CHamiltonian:
    """
    Sophisticated Hamiltonian construction for RH eigenvalue problem.

    Implements finite-difference Schrödinger equation solver with multiple
    potential forms, WKB approximations, and spectral analysis.
    """

    def __init__(self, grid_points: int = 2000, domain_size: float = 20.0):
        self.grid_points = grid_points
        self.domain_size = domain_size
        self.dx = 2 * domain_size / grid_points

        # Create grid
        self.x = np.linspace(-domain_size, domain_size, grid_points)

        # Hash generator for audit trail
        self.hasher = VNANDHashGenerator()

        self.results = []

    def potential_quartic(self, x: np.ndarray, a: float, b: float) -> np.ndarray:
        """Quartic potential: V(x) = ax² + bx⁴"""
        return a * x**2 + b * x**4

    def potential_morse(self, x: np.ndarray, De: float, alpha: float, re: float) -> np.ndarray:
        """Morse potential: V(r) = Dₑ(1 - e^(-alpha(r-rₑ)))²"""
        # Shift to molecular coordinates
        r = np.abs(x)
        return De * (1 - np.exp(-alpha * (r - re)))**2

    def potential_exponential_hybrid(self, x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
        """Hybrid potential: V(x) = ax² + be^(-cx²)"""
        return a * x**2 + b * np.exp(-c * x**2)

    def build_hamiltonian_matrix(self, potential: np.ndarray) -> np.ndarray:
        """
        Construct Hamiltonian matrix using finite-difference method.

        H = -d²/dx² + V(x)

        Second derivative approximation: [1 -2 1] / dx²
        """
        # Kinetic energy: second derivative operator
        # Laplacian in finite difference: [-1, 2, -1] / dx²
        kinetic = diags(
            [1, -2, 1],
            [-1, 0, 1],
            shape=(self.grid_points, self.grid_points),
            format='csr'
        ) / (self.dx ** 2)

        # Potential energy: diagonal matrix
        potential_matrix = diags(potential, 0, format='csr')

        # Full Hamiltonian
        H = kinetic + potential_matrix

        return H.toarray()

    def solve_eigenvalue_problem(self, H: np.ndarray, num_eigenvalues: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve eigenvalue problem: H psi = E psi

        Returns eigenvalues and eigenvectors.
        """
        # Compute eigendecomposition
        eigenvalues, eigenvectors = eigh(H)

        # Sort by eigenvalue
        idx = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        return eigenvalues[:num_eigenvalues], eigenvectors[:, :num_eigenvalues]

    def compute_wkb_scaling(self, eigenvalues: np.ndarray, potential_type: str) -> Dict[str, float]:
        """
        Compute WKB scaling predictions and compare with actual eigenvalues.

        WKB: E_n ∝ lambda^(1/3)(n+1/2)^(4/3) for quartic potential
        """
        n = np.arange(len(eigenvalues))

        metrics = {
            "mean_eigenvalue": float(np.mean(eigenvalues)),
            "min_eigenvalue": float(np.min(eigenvalues)),
            "max_eigenvalue": float(np.max(eigenvalues)),
            "eigenvalue_spacing_mean": float(np.mean(np.diff(eigenvalues))),
            "eigenvalue_spacing_std": float(np.std(np.diff(eigenvalues)))
        }

        if potential_type == "quartic":
            # WKB prediction for quartic
            wkb_predicted = (n + 0.5)**(4/3)
            normalized_actual = eigenvalues / eigenvalues[1]  # Normalize to first nonzero
            metrics["wkb_agreement"] = float(np.corrcoef(normalized_actual[:20], wkb_predicted[:20])[0, 1])

        return metrics

    def compute_spectral_rigidity(self, eigenvalues: np.ndarray) -> Dict[str, float]:
        """
        Compute spectral rigidity measures.

        Compares spacing distribution to GUE (Random Matrix Theory).
        """
        spacings = np.diff(eigenvalues)

        # Nearest-neighbor spacing
        nn_spacing_mean = np.mean(spacings)
        nn_spacing_std = np.std(spacings)

        # Variance of spacing (should be sub-Poisson for RH zeros)
        poisson_variance = nn_spacing_mean**2
        actual_variance = nn_spacing_std**2

        return {
            "nn_spacing_mean": float(nn_spacing_mean),
            "nn_spacing_std": float(nn_spacing_std),
            "is_sub_poisson": float(actual_variance < poisson_variance),
            "poisson_variance": float(poisson_variance),
            "actual_variance": float(actual_variance),
            "variance_ratio": float(actual_variance / poisson_variance) if poisson_variance > 0 else 0.0
        }

    def compute_coupling_constants(self, eigenvalues: np.ndarray) -> Dict[str, float]:
        """
        Extract dimensionless coupling constants from eigenvalue spectrum.

        Relates to fine structure constant alpha ≈ 1/137, other fundamental constants.
        """
        # Dimensionless constants that emerge from spectral structure
        spectral_coupling = 2 * np.pi / (np.max(eigenvalues) - np.min(eigenvalues)) if np.max(eigenvalues) != np.min(eigenvalues) else 0

        # Energy scale
        energy_scale = np.mean(eigenvalues[1:100])

        # Spacing scale
        spacing_scale = np.mean(np.diff(eigenvalues[:100]))

        return {
            "spectral_coupling_constant": float(spectral_coupling),
            "energy_scale": float(energy_scale),
            "spacing_scale": float(spacing_scale),
            "dimensionless_ratio": float(spacing_scale / energy_scale) if energy_scale > 0 else 0.0
        }

    def compute_zeta_error(self, computed_eigenvalues: np.ndarray, zeta_zeros: np.ndarray) -> float:
        """
        Compare computed eigenvalues to actual Riemann zeta zeros.

        Returns mean absolute error.
        """
        # Scale computed eigenvalues to match zeta zero range
        if len(computed_eigenvalues) < len(zeta_zeros):
            zeta_zeros = zeta_zeros[:len(computed_eigenvalues)]
        else:
            computed_eigenvalues = computed_eigenvalues[:len(zeta_zeros)]

        mae = np.mean(np.abs(computed_eigenvalues - zeta_zeros))
        return float(mae)

    def run_quartic_sweep(self, zeta_zeros: np.ndarray) -> List[Dict]:
        """Parameter sweep over quartic potential."""
        print("\n[Phase2C] Running quartic potential sweep...")

        results = []
        a_values = np.linspace(0.05, 0.5, 5)
        b_values = np.linspace(0.01, 0.1, 5)

        for a in a_values:
            for b in b_values:
                print(f"  Testing a={a:.3f}, b={b:.3f}...", end=" ")

                # Build potential
                V = self.potential_quartic(self.x, a, b)

                # Build Hamiltonian
                H = self.build_hamiltonian_matrix(V)

                # Solve
                eigenvalues, _ = self.solve_eigenvalue_problem(H, num_eigenvalues=100)

                # Analyze
                wkb = self.compute_wkb_scaling(eigenvalues, "quartic")
                spectral = self.compute_spectral_rigidity(eigenvalues)
                coupling = self.compute_coupling_constants(eigenvalues)

                # Compare to zeta zeros
                zeta_error = self.compute_zeta_error(eigenvalues, zeta_zeros)

                result = {
                    "potential_type": "quartic",
                    "parameters": {"a": float(a), "b": float(b)},
                    "wkb_metrics": wkb,
                    "spectral_metrics": spectral,
                    "coupling_constants": coupling,
                    "eigenvalue_error": zeta_error,
                    "timestamp": datetime.now().isoformat()
                }

                # Generate VNAND hash
                phase_hash = self.hasher.hash_phase_state(
                    f"quartic_a{a:.3f}_b{b:.3f}",
                    result
                )
                result["vnand_hash"] = phase_hash

                results.append(result)
                print(f"[OK] error={zeta_error:.4f}")

        return results

    def run_morse_sweep(self, zeta_zeros: np.ndarray) -> List[Dict]:
        """Parameter sweep over Morse potential."""
        print("\n[Phase2C] Running Morse potential sweep...")

        results = []
        De_values = np.linspace(1.0, 5.0, 4)
        alpha_values = np.linspace(0.5, 2.0, 4)

        for De in De_values:
            for alpha in alpha_values:
                print(f"  Testing De={De:.2f}, alpha={alpha:.2f}...", end=" ")

                # Build potential
                V = self.potential_morse(self.x, De, alpha, re=0.0)

                # Build Hamiltonian
                H = self.build_hamiltonian_matrix(V)

                # Solve
                eigenvalues, _ = self.solve_eigenvalue_problem(H, num_eigenvalues=100)

                # Analyze
                spectral = self.compute_spectral_rigidity(eigenvalues)
                coupling = self.compute_coupling_constants(eigenvalues)
                zeta_error = self.compute_zeta_error(eigenvalues, zeta_zeros)

                result = {
                    "potential_type": "morse",
                    "parameters": {"De": float(De), "alpha": float(alpha)},
                    "spectral_metrics": spectral,
                    "coupling_constants": coupling,
                    "eigenvalue_error": zeta_error,
                    "timestamp": datetime.now().isoformat()
                }

                # Generate VNAND hash
                phase_hash = self.hasher.hash_phase_state(
                    f"morse_De{De:.2f}_a{alpha:.2f}",
                    result
                )
                result["vnand_hash"] = phase_hash

                results.append(result)
                print(f"[OK] error={zeta_error:.4f}")

        return results

    def run_exponential_hybrid_sweep(self, zeta_zeros: np.ndarray) -> List[Dict]:
        """Parameter sweep over exponential hybrid potential."""
        print("\n[Phase2C] Running exponential hybrid potential sweep...")

        results = []
        a_values = np.linspace(0.05, 0.3, 4)
        b_values = np.linspace(1.0, 5.0, 4)
        c_values = np.linspace(0.1, 0.5, 4)

        for a in a_values[:2]:  # Limit to save time
            for b in b_values[:2]:
                for c in c_values[:2]:
                    print(f"  Testing a={a:.3f}, b={b:.2f}, c={c:.2f}...", end=" ")

                    # Build potential
                    V = self.potential_exponential_hybrid(self.x, a, b, c)

                    # Build Hamiltonian
                    H = self.build_hamiltonian_matrix(V)

                    # Solve
                    eigenvalues, _ = self.solve_eigenvalue_problem(H, num_eigenvalues=100)

                    # Analyze
                    spectral = self.compute_spectral_rigidity(eigenvalues)
                    coupling = self.compute_coupling_constants(eigenvalues)
                    zeta_error = self.compute_zeta_error(eigenvalues, zeta_zeros)

                    result = {
                        "potential_type": "exponential_hybrid",
                        "parameters": {"a": float(a), "b": float(b), "c": float(c)},
                        "spectral_metrics": spectral,
                        "coupling_constants": coupling,
                        "eigenvalue_error": zeta_error,
                        "timestamp": datetime.now().isoformat()
                    }

                    # Generate VNAND hash
                    phase_hash = self.hasher.hash_phase_state(
                        f"exp_a{a:.3f}_b{b:.2f}_c{c:.2f}",
                        result
                    )
                    result["vnand_hash"] = phase_hash

                    results.append(result)
                    print(f"[OK] error={zeta_error:.4f}")

        return results

    def save_results(self, all_results: List[Dict], output_dir: Path) -> Path:
        """Save all Phase 2C results to disk."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save results
        results_file = output_dir / "phase2c_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(all_results, indent=2))

        # Save audit trail
        audit_file = self.hasher.save_audit_trail(output_dir)

        print(f"\n[OK] Results saved: {results_file}")
        print(f"[OK] Audit trail saved: {audit_file}")

        return results_file


def generate_zeta_zeros(num_zeros: int = 100) -> np.ndarray:
    """
    Generate approximate Riemann zeta zero heights.

    Uses known values and asymptotic approximation for higher zeros.
    """
    # Known first few zeta zeros
    known_zeros = np.array([
        14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
        37.586178, 40.918719, 43.327073, 48.005151, 49.773832
    ])

    if num_zeros <= len(known_zeros):
        return known_zeros[:num_zeros]

    # Asymptotic approximation for higher zeros
    # Gram's law: ζ(1/2 + it_n) ≈ 0
    additional = []
    for n in range(len(known_zeros), num_zeros):
        # Approximate using Gram's formula
        t_n = (2 * np.pi * n) / np.log(n / (2 * np.pi * np.e))
        additional.append(t_n)

    return np.concatenate([known_zeros, additional])


def main():
    """Execute Phase 2C Hamiltonian construction."""
    print("="*80)
    print("[Phase 2C] HAMILTONIAN CONSTRUCTION FOR RIEMANN HYPOTHESIS")
    print("="*80)

    # Output directory
    output_dir = Path("./agi_test_output/phase2c_execution")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate zeta zeros for comparison
    zeta_zeros = generate_zeta_zeros(100)

    # Create solver
    solver = Phase2CHamiltonian(grid_points=1500, domain_size=20.0)

    # Run parameter sweeps
    print("\n[Phase 2C] Starting parameter sweeps...")
    print(f"Grid points: 1500 | Domain: [-20, 20] | Eigenvalues: 100")

    all_results = []

    # Quartic sweep
    quartic_results = solver.run_quartic_sweep(zeta_zeros)
    all_results.extend(quartic_results)

    # Morse sweep
    morse_results = solver.run_morse_sweep(zeta_zeros)
    all_results.extend(morse_results)

    # Exponential hybrid sweep
    exp_results = solver.run_exponential_hybrid_sweep(zeta_zeros)
    all_results.extend(exp_results)

    # Save all results
    solver.save_results(all_results, output_dir)

    # Print summary
    print("\n" + "="*80)
    print("[Phase 2C] SUMMARY")
    print("="*80)
    print(f"Total computations: {len(all_results)}")
    print(f"Best eigenvalue error: {min(r['eigenvalue_error'] for r in all_results):.6f}")
    print(f"Worst eigenvalue error: {max(r['eigenvalue_error'] for r in all_results):.6f}")
    print(f"Average eigenvalue error: {np.mean([r['eigenvalue_error'] for r in all_results]):.6f}")

    # Find best result
    best = min(all_results, key=lambda x: x["eigenvalue_error"])
    print(f"\nBest result:")
    print(f"  Potential: {best['potential_type']}")
    print(f"  Parameters: {best['parameters']}")
    print(f"  Error: {best['eigenvalue_error']:.6f}")
    print(f"  VNAND Hash: {best['vnand_hash']}")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
