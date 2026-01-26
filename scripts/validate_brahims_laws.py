"""
Statistical Validation of Brahim's Laws
=======================================

This script performs rigorous statistical tests on the claimed scaling laws
using the Cremona/LMFDB elliptic curve database.

Tests performed:
1. Law 1: log(Sha) ~ α·log(Im(τ)) with claimed α = 2/3
2. Law 4: log(Sha) ~ γ·log(Rey) with claimed γ = 5/12
3. Law 3: Regime independence (χ² test)

Output: Academic-quality validation report with confidence intervals

Author: Elias Oulad Brahim
Date: 2026-01-26
Spec: BUIM_UNIFIED_ARCHITECTURE_SPEC.md
"""

import json
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import warnings

# Suppress warnings for clean output
warnings.filterwarnings('ignore')

try:
    from scipy import stats
    from scipy.stats import chi2_contingency
    import statsmodels.api as sm
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False
    print("Warning: scipy/statsmodels not available. Install with:")
    print("  pip install scipy statsmodels")


@dataclass
class CurveData:
    """Elliptic curve data point."""
    label: str
    conductor: int
    rank: int
    real_period: float
    tamagawa_product: int
    sha_analytic: Optional[float]
    regulator: float = 1.0

    @property
    def im_tau(self) -> float:
        """Approximate Im(τ) from period."""
        if self.real_period <= 0:
            return 1.0
        return 1.0 / (self.real_period ** 2)

    @property
    def reynolds(self) -> float:
        """Arithmetic Reynolds number."""
        denom = self.tamagawa_product * self.real_period
        if denom <= 0:
            return float('inf')
        return self.conductor / denom

    @property
    def log_sha(self) -> Optional[float]:
        """Log of Sha (None if Sha is None or <= 0)."""
        if self.sha_analytic is None or self.sha_analytic <= 0:
            return None
        return np.log(self.sha_analytic)

    @property
    def log_im_tau(self) -> float:
        return np.log(self.im_tau)

    @property
    def log_reynolds(self) -> float:
        if self.reynolds <= 0 or np.isinf(self.reynolds):
            return float('nan')
        return np.log(self.reynolds)


@dataclass
class ValidationResult:
    """Result of a statistical validation test."""
    test_name: str
    parameter_name: str
    n_samples: int
    fitted_value: float
    standard_error: float
    ci_lower: float
    ci_upper: float
    claimed_value: float
    t_statistic: float
    p_value_vs_claim: float
    r_squared: float
    claim_in_ci: bool
    conclusion: str


def load_cremona_data(data_dir: Path) -> List[CurveData]:
    """Load elliptic curve data from Cremona exports."""
    curves = []

    # Search for JSON/JSONL files
    for pattern in ["**/*.json", "**/*.jsonl"]:
        for filepath in data_dir.glob(pattern):
            try:
                curves.extend(load_file(filepath))
            except Exception as e:
                print(f"  Warning: Could not load {filepath.name}: {e}")

    return curves


def load_file(filepath: Path) -> List[CurveData]:
    """Load curves from a single file."""
    curves = []

    if filepath.suffix == ".jsonl":
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith('{'):
                    continue
                try:
                    data = json.loads(line)
                    curve = parse_curve(data)
                    if curve:
                        curves.append(curve)
                except json.JSONDecodeError:
                    continue
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different formats
        if isinstance(data, list):
            curve_list = data
        elif isinstance(data, dict):
            curve_list = data.get('curves', data.get('data', []))
        else:
            return []

        for item in curve_list:
            curve = parse_curve(item)
            if curve:
                curves.append(curve)

    return curves


def parse_curve(data: Dict[str, Any]) -> Optional[CurveData]:
    """Parse a curve dictionary to CurveData."""
    try:
        label = data.get('label', data.get('lmfdb_label', ''))
        conductor = int(data.get('conductor', 0))
        rank = int(data.get('rank', 0))
        real_period = float(data.get('real_period', data.get('omega', 1.0)))
        tamagawa = int(data.get('tamagawa_product', data.get('tamagawa', 1)))
        sha = data.get('sha_an', data.get('sha', None))
        regulator = float(data.get('regulator', 1.0))

        if conductor <= 0 or real_period <= 0:
            return None

        return CurveData(
            label=label,
            conductor=conductor,
            rank=rank,
            real_period=real_period,
            tamagawa_product=tamagawa,
            sha_analytic=float(sha) if sha is not None else None,
            regulator=regulator
        )
    except (ValueError, TypeError):
        return None


def test_law1(curves: List[CurveData]) -> ValidationResult:
    """
    Test Law 1: Sha ~ Im(τ)^α

    H0: α = 0 (no relationship)
    H1: α ≠ 0

    Secondary: Test if α = 2/3 (claimed value)
    """
    # Filter to curves with non-trivial Sha
    valid = [c for c in curves if c.sha_analytic is not None and c.sha_analytic > 1]

    if len(valid) < 30:
        return ValidationResult(
            test_name="Law 1: Sha ~ Im(τ)^α",
            parameter_name="α",
            n_samples=len(valid),
            fitted_value=float('nan'),
            standard_error=float('nan'),
            ci_lower=float('nan'),
            ci_upper=float('nan'),
            claimed_value=2/3,
            t_statistic=float('nan'),
            p_value_vs_claim=float('nan'),
            r_squared=float('nan'),
            claim_in_ci=False,
            conclusion=f"INSUFFICIENT DATA: Only {len(valid)} curves with Sha > 1"
        )

    y = np.array([c.log_sha for c in valid])
    X = np.array([c.log_im_tau for c in valid])
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    alpha_fitted = model.params[1]
    alpha_se = model.bse[1]
    ci = model.conf_int(0.05)[1]
    ci_lower, ci_upper = ci[0], ci[1]

    # Test vs claimed value
    alpha_claimed = 2/3
    t_stat = (alpha_fitted - alpha_claimed) / alpha_se
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=model.df_resid))

    claim_in_ci = ci_lower <= alpha_claimed <= ci_upper

    if claim_in_ci:
        conclusion = f"SUPPORTED: Claimed α = {alpha_claimed:.4f} is within 95% CI"
    else:
        conclusion = f"NOT SUPPORTED: Claimed α = {alpha_claimed:.4f} is outside 95% CI"

    return ValidationResult(
        test_name="Law 1: Sha ~ Im(τ)^α",
        parameter_name="α",
        n_samples=len(valid),
        fitted_value=alpha_fitted,
        standard_error=alpha_se,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        claimed_value=alpha_claimed,
        t_statistic=t_stat,
        p_value_vs_claim=p_value,
        r_squared=model.rsquared,
        claim_in_ci=claim_in_ci,
        conclusion=conclusion
    )


def test_law4(curves: List[CurveData]) -> ValidationResult:
    """
    Test Law 4: Sha ~ Rey^γ

    H0: γ = 0
    H1: γ = 5/12 (claimed)
    """
    # Filter valid curves
    valid = [c for c in curves
             if c.sha_analytic is not None
             and c.sha_analytic > 1
             and not np.isnan(c.log_reynolds)
             and not np.isinf(c.log_reynolds)]

    if len(valid) < 30:
        return ValidationResult(
            test_name="Law 4: Sha ~ Rey^γ",
            parameter_name="γ",
            n_samples=len(valid),
            fitted_value=float('nan'),
            standard_error=float('nan'),
            ci_lower=float('nan'),
            ci_upper=float('nan'),
            claimed_value=5/12,
            t_statistic=float('nan'),
            p_value_vs_claim=float('nan'),
            r_squared=float('nan'),
            claim_in_ci=False,
            conclusion=f"INSUFFICIENT DATA: Only {len(valid)} valid curves"
        )

    y = np.array([c.log_sha for c in valid])
    X = np.array([c.log_reynolds for c in valid])
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    gamma_fitted = model.params[1]
    gamma_se = model.bse[1]
    ci = model.conf_int(0.05)[1]
    ci_lower, ci_upper = ci[0], ci[1]

    gamma_claimed = 5/12
    t_stat = (gamma_fitted - gamma_claimed) / gamma_se
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=model.df_resid))

    claim_in_ci = ci_lower <= gamma_claimed <= ci_upper

    if claim_in_ci:
        conclusion = f"SUPPORTED: Claimed γ = {gamma_claimed:.4f} is within 95% CI"
    else:
        conclusion = f"NOT SUPPORTED: Claimed γ = {gamma_claimed:.4f} is outside 95% CI"

    return ValidationResult(
        test_name="Law 4: Sha ~ Rey^γ",
        parameter_name="γ",
        n_samples=len(valid),
        fitted_value=gamma_fitted,
        standard_error=gamma_se,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        claimed_value=gamma_claimed,
        t_statistic=t_stat,
        p_value_vs_claim=p_value,
        r_squared=model.rsquared,
        claim_in_ci=claim_in_ci,
        conclusion=conclusion
    )


def test_law3(curves: List[CurveData]) -> Dict[str, Any]:
    """
    Test Law 3: Regime independence

    H0: P(Sha > 1 | Rey < 10) = P(Sha > 1 | Rey > 30)
    H1: Probabilities differ
    """
    # Filter curves with known Sha
    valid = [c for c in curves if c.sha_analytic is not None]

    low_rey = [c for c in valid if c.reynolds < 10]
    high_rey = [c for c in valid if c.reynolds > 30]

    if len(low_rey) < 20 or len(high_rey) < 20:
        return {
            "test_name": "Law 3: Regime Independence",
            "status": "INSUFFICIENT DATA",
            "n_low_rey": len(low_rey),
            "n_high_rey": len(high_rey),
            "conclusion": f"Need at least 20 curves in each regime"
        }

    # Count non-trivial Sha in each regime
    low_trivial = sum(1 for c in low_rey if c.sha_analytic == 1)
    low_nontrivial = sum(1 for c in low_rey if c.sha_analytic > 1)
    high_trivial = sum(1 for c in high_rey if c.sha_analytic == 1)
    high_nontrivial = sum(1 for c in high_rey if c.sha_analytic > 1)

    # Contingency table
    table = [
        [low_trivial, low_nontrivial],
        [high_trivial, high_nontrivial]
    ]

    chi2, p_value, dof, expected = chi2_contingency(table)

    p_nontrivial_low = low_nontrivial / len(low_rey) if len(low_rey) > 0 else 0
    p_nontrivial_high = high_nontrivial / len(high_rey) if len(high_rey) > 0 else 0

    regimes_differ = p_value < 0.05

    if regimes_differ:
        conclusion = f"SUPPORTED: Regimes differ significantly (p = {p_value:.4f})"
    else:
        conclusion = f"NOT SUPPORTED: No significant regime difference (p = {p_value:.4f})"

    return {
        "test_name": "Law 3: Regime Independence",
        "status": "COMPLETE",
        "n_low_rey": len(low_rey),
        "n_high_rey": len(high_rey),
        "p_nontrivial_low": p_nontrivial_low,
        "p_nontrivial_high": p_nontrivial_high,
        "chi2": chi2,
        "p_value": p_value,
        "regimes_differ": regimes_differ,
        "conclusion": conclusion
    }


def format_result(result: ValidationResult) -> str:
    """Format a validation result for output."""
    return f"""
{result.test_name}
{'=' * len(result.test_name)}
Sample size: N = {result.n_samples}

Model: log(Sha) = {result.parameter_name}·log(X) + β + ε

Fitted parameters:
  {result.parameter_name} = {result.fitted_value:.4f} ± {result.standard_error:.4f}
  95% CI: [{result.ci_lower:.4f}, {result.ci_upper:.4f}]

Hypothesis test (H0: {result.parameter_name} = {result.claimed_value:.4f}):
  t = {result.t_statistic:.3f}
  p = {result.p_value_vs_claim:.4f}

R² = {result.r_squared:.4f}

CONCLUSION: {result.conclusion}
"""


def format_law3_result(result: Dict[str, Any]) -> str:
    """Format Law 3 result for output."""
    if result["status"] != "COMPLETE":
        return f"""
{result['test_name']}
{'=' * len(result['test_name'])}
Status: {result['status']}
{result['conclusion']}
"""

    return f"""
{result['test_name']}
{'=' * len(result['test_name'])}
Low Reynolds (Rey < 10): N = {result['n_low_rey']}
  P(Sha > 1) = {result['p_nontrivial_low']:.4f}

High Reynolds (Rey > 30): N = {result['n_high_rey']}
  P(Sha > 1) = {result['p_nontrivial_high']:.4f}

Chi-squared test:
  χ² = {result['chi2']:.3f}
  p = {result['p_value']:.4f}

CONCLUSION: {result['conclusion']}
"""


def main():
    """Run full validation suite."""
    print("=" * 70)
    print("STATISTICAL VALIDATION OF BRAHIM'S LAWS")
    print("=" * 70)
    print()

    if not STATS_AVAILABLE:
        print("ERROR: scipy/statsmodels required for statistical tests")
        return

    # Find data directory
    data_dir = Path("data/cremona")
    if not data_dir.exists():
        # Try relative to script
        script_dir = Path(__file__).parent
        data_dir = script_dir.parent / "data" / "cremona"

    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        print("Please ensure Cremona data is in data/cremona/")
        return

    print(f"Loading data from: {data_dir}")
    curves = load_cremona_data(data_dir)
    print(f"Loaded {len(curves)} curves total")

    # Count curves with Sha data
    with_sha = [c for c in curves if c.sha_analytic is not None]
    with_sha_gt1 = [c for c in curves if c.sha_analytic is not None and c.sha_analytic > 1]
    print(f"  - With Sha data: {len(with_sha)}")
    print(f"  - With Sha > 1: {len(with_sha_gt1)}")
    print()

    # Run tests
    print("-" * 70)
    result1 = test_law1(curves)
    print(format_result(result1))

    print("-" * 70)
    result4 = test_law4(curves)
    print(format_result(result4))

    print("-" * 70)
    result3 = test_law3(curves)
    print(format_law3_result(result3))

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    if result1.n_samples >= 30:
        status1 = "✓ SUPPORTED" if result1.claim_in_ci else "✗ NOT SUPPORTED"
        print(f"Law 1 (α = 2/3): {status1}")
        print(f"  Fitted: α = {result1.fitted_value:.4f} [{result1.ci_lower:.4f}, {result1.ci_upper:.4f}]")
    else:
        print(f"Law 1: INSUFFICIENT DATA ({result1.n_samples} samples)")

    print()

    if result4.n_samples >= 30:
        status4 = "✓ SUPPORTED" if result4.claim_in_ci else "✗ NOT SUPPORTED"
        print(f"Law 4 (γ = 5/12): {status4}")
        print(f"  Fitted: γ = {result4.fitted_value:.4f} [{result4.ci_lower:.4f}, {result4.ci_upper:.4f}]")
    else:
        print(f"Law 4: INSUFFICIENT DATA ({result4.n_samples} samples)")

    print()

    if result3["status"] == "COMPLETE":
        status3 = "✓ SUPPORTED" if result3["regimes_differ"] else "✗ NOT SUPPORTED"
        print(f"Law 3 (Regime Difference): {status3}")
        print(f"  χ² = {result3['chi2']:.3f}, p = {result3['p_value']:.4f}")
    else:
        print(f"Law 3: {result3['status']}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
