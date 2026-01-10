"""
Forward to actual evaluation service in evals/benchmarks
"""
import sys
from pathlib import Path

# Add evals/benchmarks to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "evals" / "benchmarks"))

from evaluation_service import EvaluationService

__all__ = ['EvaluationService']
