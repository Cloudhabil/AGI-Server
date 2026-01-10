#!/usr/bin/env python3
"""
BSD Dual-Model Gap Closure Orchestrator
========================================

Parallel execution of R1 (Euler Systems) and R2 (Control Theorem) gaps
using two specialized LLMs with cross-validation.

Architecture:
- Model A (qwen2-math:7b): R1 - Euler Systems Construction
- Model B (gpia-deepseek-r1): R2 - Control Theorem Machinery
- Cross-validation phase: Each verifies other's work
- Shared vnand state for dependency tracking

Run:
    python bsd_dual_model_gap_closure.py --parallel
    python bsd_dual_model_gap_closure.py --sequential  # fallback
    python bsd_dual_model_gap_closure.py --validate-only
"""

import json
import sys
import time
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))

# =============================================================================
# CONFIGURATION
# =============================================================================

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "data" / "bsd_gap_closure_dual"
VNAND_DIR = ROOT / "data" / "vnand"

# Dual model configuration
MODELS = {
    "math": {
        "id": "qwen2-math:7b",
        "target": "R1",
        "focus": "Euler Systems Construction",
        "strengths": ["algebraic manipulation", "proof steps", "explicit formulas"]
    },
    "reasoning": {
        "id": "gpia-deepseek-r1:latest",
        "target": "R2",
        "focus": "Control Theorem Machinery",
        "strengths": ["logical chains", "generalization", "bound derivation"]
    }
}

# Gap specifications
GAPS = {
    "R1": {
        "name": "Euler Systems Existence",
        "severity": "CRITICAL",
        "subgoals": [
            "R1.1: Prove wedge product norm-compatibility",
            "R1.2: Define Arithmetic Horizon thickening rigorously",
            "R1.3: Construct base case r=2 explicitly",
            "R1.4: Prove inductive step r → r+1",
            "R1.5: Verify non-triviality condition"
        ],
        "dependencies": [],
        "outputs": ["euler_existence_proof.tex", "norm_compatibility_lemma.tex"]
    },
    "R2": {
        "name": "Control Theorem Machinery",
        "severity": "CRITICAL",
        "subgoals": [
            "R2.1: State generalized Kolyvagin axioms for rank r",
            "R2.2: Prove r independent cohomology classes exist",
            "R2.3: Derive descent exact sequence",
            "R2.4: Compute explicit Selmer bound",
            "R2.5: Handle error terms and Tamagawa factors"
        ],
        "dependencies": ["R1.1", "R1.3"],  # Needs Euler system structure
        "outputs": ["control_theorem_proof.tex", "selmer_bound_formula.tex"]
    }
}


class GapStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    NEEDS_VALIDATION = "needs_validation"
    VALIDATED = "validated"
    COMPLETE = "complete"


@dataclass
class SubgoalResult:
    """Result of working on a subgoal."""
    subgoal_id: str
    model_used: str
    status: GapStatus
    content: str
    rigor_score: float
    proof_steps: List[str]
    dependencies_satisfied: bool
    validation_notes: str = ""
    cycle_num: int = 0


@dataclass
class GapState:
    """Tracks state of a gap."""
    gap_id: str
    status: GapStatus = GapStatus.PENDING
    subgoal_results: Dict[str, SubgoalResult] = field(default_factory=dict)
    progress: float = 0.0
    validation_passed: bool = False
    cross_validator: str = ""


@dataclass
class DualModelState:
    """Global state for dual-model execution."""
    session_id: str
    r1_state: GapState = field(default_factory=lambda: GapState("R1"))
    r2_state: GapState = field(default_factory=lambda: GapState("R2"))
    total_cycles: int = 0
    math_cycles: int = 0
    reasoning_cycles: int = 0
    cross_validations: int = 0
    started_at: str = ""
    last_updated: str = ""


# =============================================================================
# LLM INTERFACE (Ollama)
# =============================================================================

class OllamaInterface:
    """Interface to Ollama for model queries."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.base_url = "http://localhost:11434"

    def query(self, prompt: str, system: str = "", max_tokens: int = 2000) -> str:
        """Query the model."""
        import requests

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_id,
                    "messages": messages,
                    "stream": False,
                    "options": {"num_predict": max_tokens}
                },
                timeout=120
            )

            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                return f"[ERROR] Model returned status {response.status_code}"

        except Exception as e:
            return f"[ERROR] {str(e)}"

    def is_available(self) -> bool:
        """Check if model is available."""
        import requests
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                return any(self.model_id in m for m in models)
        except:
            pass
        return False


# =============================================================================
# GAP WORKERS
# =============================================================================

class GapWorker:
    """Worker for a specific gap using assigned model."""

    def __init__(self, gap_id: str, model_config: Dict, state: GapState):
        self.gap_id = gap_id
        self.gap_spec = GAPS[gap_id]
        self.model_config = model_config
        self.state = state
        self.llm = OllamaInterface(model_config["id"])
        self.output_dir = OUTPUT_DIR / gap_id.lower()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_subgoal(self, subgoal_id: str, context: Dict) -> SubgoalResult:
        """Execute a single subgoal."""
        subgoal_text = next(
            (s for s in self.gap_spec["subgoals"] if s.startswith(subgoal_id)),
            subgoal_id
        )

        system_prompt = f"""You are a mathematical proof assistant specializing in {self.model_config['focus']}.
Your strengths: {', '.join(self.model_config['strengths'])}.

You are working on the BSD Conjecture, specifically Gap {self.gap_id}: {self.gap_spec['name']}.

Output Format:
1. State the claim precisely
2. List proof steps with justification
3. Cite any external theorems used
4. Rate your confidence (0-1)
5. Note any gaps or assumptions

Be rigorous. If uncertain, say so explicitly."""

        prompt = f"""SUBGOAL: {subgoal_text}

CONTEXT:
{json.dumps(context, indent=2)}

PRIOR RESULTS IN THIS GAP:
{json.dumps({k: v.content[:500] for k, v in self.state.subgoal_results.items()}, indent=2)}

Provide a complete mathematical treatment of this subgoal."""

        response = self.llm.query(prompt, system=system_prompt, max_tokens=3000)

        # Parse response for rigor indicators
        rigor_score = self._assess_rigor(response)
        proof_steps = self._extract_proof_steps(response)

        result = SubgoalResult(
            subgoal_id=subgoal_id,
            model_used=self.model_config["id"],
            status=GapStatus.NEEDS_VALIDATION if rigor_score > 0.6 else GapStatus.IN_PROGRESS,
            content=response,
            rigor_score=rigor_score,
            proof_steps=proof_steps,
            dependencies_satisfied=self._check_dependencies(subgoal_id, context)
        )

        # Save output
        output_file = self.output_dir / f"{subgoal_id.replace('.', '_')}.md"
        output_file.write_text(f"# {subgoal_text}\n\n{response}", encoding='utf-8')

        return result

    def _assess_rigor(self, response: str) -> float:
        """Assess mathematical rigor of response."""
        score = 0.5  # Base score

        # Positive indicators
        if "\\begin{proof}" in response or "Proof:" in response:
            score += 0.1
        if "\\begin{lemma}" in response or "Lemma" in response:
            score += 0.05
        if any(word in response.lower() for word in ["therefore", "hence", "thus", "qed"]):
            score += 0.05
        if "by Theorem" in response or "by Lemma" in response:
            score += 0.05
        if "\\[" in response or "$$" in response:  # Has equations
            score += 0.1

        # Negative indicators
        if "I think" in response or "probably" in response.lower():
            score -= 0.1
        if "unclear" in response.lower() or "not sure" in response.lower():
            score -= 0.1
        if "[ERROR]" in response:
            score -= 0.3

        return max(0.0, min(1.0, score))

    def _extract_proof_steps(self, response: str) -> List[str]:
        """Extract proof steps from response."""
        steps = []
        lines = response.split('\n')

        for line in lines:
            line = line.strip()
            # Look for numbered steps or bullet points
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                if len(line) > 10:  # Meaningful content
                    steps.append(line[:200])

        return steps[:10]  # Limit to 10 steps

    def _check_dependencies(self, subgoal_id: str, context: Dict) -> bool:
        """Check if dependencies for this subgoal are satisfied."""
        # Simple check - in full impl, would verify specific lemmas exist
        deps = self.gap_spec.get("dependencies", [])
        if not deps:
            return True

        # Check if prior subgoals in dependency chain are complete
        for dep in deps:
            if dep.startswith(self.gap_id):
                # Internal dependency
                dep_num = dep.split('.')[-1]
                current_num = subgoal_id.split('.')[-1]
                if int(dep_num) < int(current_num):
                    if dep not in self.state.subgoal_results:
                        return False

        return True

    def run_cycle(self, cycle_num: int, context: Dict) -> List[SubgoalResult]:
        """Run one cycle, working on pending subgoals."""
        results = []

        for subgoal in self.gap_spec["subgoals"]:
            subgoal_id = subgoal.split(':')[0]

            # Skip if already complete
            if subgoal_id in self.state.subgoal_results:
                if self.state.subgoal_results[subgoal_id].status == GapStatus.COMPLETE:
                    continue

            # Check dependencies
            if not self._check_dependencies(subgoal_id, context):
                continue

            print(f"    [{self.gap_id}] Working on {subgoal_id}...")
            result = self.run_subgoal(subgoal_id, context)
            result.cycle_num = cycle_num
            results.append(result)

            self.state.subgoal_results[subgoal_id] = result

            # Update gap progress
            complete = sum(1 for r in self.state.subgoal_results.values()
                          if r.status in [GapStatus.VALIDATED, GapStatus.COMPLETE])
            self.state.progress = complete / len(self.gap_spec["subgoals"])

            # One subgoal per cycle for balanced progress
            break

        return results


# =============================================================================
# CROSS-VALIDATOR
# =============================================================================

class CrossValidator:
    """Validates work from one model using the other."""

    def __init__(self, validator_model: Dict):
        self.model_config = validator_model
        self.llm = OllamaInterface(validator_model["id"])

    def validate(self, result: SubgoalResult, gap_spec: Dict) -> Tuple[bool, str, float]:
        """Validate a subgoal result."""

        system_prompt = f"""You are a mathematical proof validator. Your task is to critically examine
a proof step and identify any gaps, errors, or unjustified claims.

Be strict but fair. A valid proof must:
1. Have clear logical flow
2. Justify each step
3. Not skip non-trivial claims
4. Use correct notation
5. Cite external results properly

Output format:
VALID: [yes/no]
ISSUES: [list any problems]
SUGGESTIONS: [how to fix]
CONFIDENCE: [0-1]"""

        prompt = f"""VALIDATE THIS PROOF STEP:

Subgoal: {result.subgoal_id}
Gap: {gap_spec['name']}

Content to validate:
{result.content[:3000]}

Extracted proof steps:
{json.dumps(result.proof_steps, indent=2)}

Original rigor score: {result.rigor_score}

Provide your validation."""

        response = self.llm.query(prompt, system=system_prompt, max_tokens=1500)

        # Parse validation result
        is_valid = "VALID: yes" in response.lower() or "valid: yes" in response.lower()
        confidence = self._extract_confidence(response)

        return is_valid, response, confidence

    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from response."""
        import re
        match = re.search(r'CONFIDENCE:\s*([0-9.]+)', response, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
        return 0.5


# =============================================================================
# DUAL MODEL ORCHESTRATOR
# =============================================================================

class DualModelOrchestrator:
    """Orchestrates parallel gap closure with two models."""

    def __init__(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        self.state = DualModelState(
            session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            started_at=datetime.now().isoformat()
        )

        # Initialize workers
        self.r1_worker = GapWorker("R1", MODELS["math"], self.state.r1_state)
        self.r2_worker = GapWorker("R2", MODELS["reasoning"], self.state.r2_state)

        # Cross-validators (each validates the other's work)
        self.r1_validator = CrossValidator(MODELS["reasoning"])  # Reasoning validates Math's work
        self.r2_validator = CrossValidator(MODELS["math"])       # Math validates Reasoning's work

        self._load_state()

    def _load_state(self):
        """Load previous state if exists."""
        state_file = OUTPUT_DIR / "dual_model_state.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text(encoding='utf-8'))
                self.state.total_cycles = data.get("total_cycles", 0)
                self.state.math_cycles = data.get("math_cycles", 0)
                self.state.reasoning_cycles = data.get("reasoning_cycles", 0)
                print(f"[ORCH] Loaded state: {self.state.total_cycles} cycles completed")
            except:
                pass

    def _save_state(self):
        """Save current state."""
        state_file = OUTPUT_DIR / "dual_model_state.json"
        self.state.last_updated = datetime.now().isoformat()

        data = {
            "session_id": self.state.session_id,
            "total_cycles": self.state.total_cycles,
            "math_cycles": self.state.math_cycles,
            "reasoning_cycles": self.state.reasoning_cycles,
            "cross_validations": self.state.cross_validations,
            "r1_progress": self.state.r1_state.progress,
            "r2_progress": self.state.r2_state.progress,
            "started_at": self.state.started_at,
            "last_updated": self.state.last_updated
        }

        state_file.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def check_models(self) -> Tuple[bool, bool]:
        """Check if both models are available."""
        math_ok = self.r1_worker.llm.is_available()
        reasoning_ok = self.r2_worker.llm.is_available()
        return math_ok, reasoning_ok

    def run_parallel_cycle(self, cycle_num: int) -> Dict[str, Any]:
        """Run one cycle with both models in parallel."""
        print(f"\n{'='*70}")
        print(f"CYCLE {cycle_num} | Parallel Execution")
        print(f"{'='*70}")

        context = {
            "cycle": cycle_num,
            "r1_progress": self.state.r1_state.progress,
            "r2_progress": self.state.r2_state.progress
        }

        results = {"r1": [], "r2": []}

        # Run both workers in parallel using threads
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.r1_worker.run_cycle, cycle_num, context): "r1",
                executor.submit(self.r2_worker.run_cycle, cycle_num, context): "r2"
            }

            for future in as_completed(futures):
                gap_id = futures[future]
                try:
                    result = future.result()
                    results[gap_id] = result
                except Exception as e:
                    print(f"  [ERROR] {gap_id}: {e}")

        # Update cycle counts
        self.state.total_cycles += 1
        if results["r1"]:
            self.state.math_cycles += 1
        if results["r2"]:
            self.state.reasoning_cycles += 1

        # Print progress
        print(f"\n  [R1] Progress: {self.state.r1_state.progress:.1%}")
        print(f"  [R2] Progress: {self.state.r2_state.progress:.1%}")

        self._save_state()

        return results

    def run_cross_validation(self) -> Dict[str, Any]:
        """Cross-validate completed subgoals."""
        print(f"\n{'='*70}")
        print("CROSS-VALIDATION PHASE")
        print(f"{'='*70}")

        validation_results = {"r1": {}, "r2": {}}

        # Validate R1 results with R2's model
        for subgoal_id, result in self.state.r1_state.subgoal_results.items():
            if result.status == GapStatus.NEEDS_VALIDATION:
                print(f"  Validating R1/{subgoal_id} with reasoning model...")
                is_valid, notes, confidence = self.r1_validator.validate(result, GAPS["R1"])

                validation_results["r1"][subgoal_id] = {
                    "valid": is_valid,
                    "confidence": confidence,
                    "notes": notes[:500]
                }

                if is_valid and confidence > 0.6:
                    result.status = GapStatus.VALIDATED
                    result.validation_notes = notes

                self.state.cross_validations += 1

        # Validate R2 results with R1's model
        for subgoal_id, result in self.state.r2_state.subgoal_results.items():
            if result.status == GapStatus.NEEDS_VALIDATION:
                print(f"  Validating R2/{subgoal_id} with math model...")
                is_valid, notes, confidence = self.r2_validator.validate(result, GAPS["R2"])

                validation_results["r2"][subgoal_id] = {
                    "valid": is_valid,
                    "confidence": confidence,
                    "notes": notes[:500]
                }

                if is_valid and confidence > 0.6:
                    result.status = GapStatus.VALIDATED
                    result.validation_notes = notes

                self.state.cross_validations += 1

        self._save_state()

        return validation_results

    def run_full_closure(self, max_cycles: int = 30, validate_every: int = 5):
        """Run full gap closure with periodic validation."""
        print("\n" + "="*80)
        print("BSD DUAL-MODEL GAP CLOSURE")
        print(f"Models: {MODELS['math']['id']} (R1) + {MODELS['reasoning']['id']} (R2)")
        print(f"Max cycles: {max_cycles}, Validate every: {validate_every}")
        print("="*80)

        # Check model availability
        math_ok, reasoning_ok = self.check_models()
        print(f"\nModel Status:")
        print(f"  Math ({MODELS['math']['id']}): {'OK' if math_ok else 'NOT AVAILABLE'}")
        print(f"  Reasoning ({MODELS['reasoning']['id']}): {'OK' if reasoning_ok else 'NOT AVAILABLE'}")

        if not (math_ok and reasoning_ok):
            print("\n[ERROR] Both models must be available for parallel execution")
            print("Falling back to sequential mode with available model...")
            return self.run_sequential_fallback(max_cycles)

        for cycle in range(1, max_cycles + 1):
            # Run parallel cycle
            self.run_parallel_cycle(cycle)

            # Periodic cross-validation
            if cycle % validate_every == 0:
                self.run_cross_validation()

            # Check completion
            if self.state.r1_state.progress >= 1.0 and self.state.r2_state.progress >= 1.0:
                print("\n[COMPLETE] Both gaps fully addressed!")
                break

        # Final validation
        self.run_cross_validation()

        # Generate synthesis
        self.generate_synthesis()

        return self.get_summary()

    def run_sequential_fallback(self, max_cycles: int):
        """Fallback to sequential execution if one model unavailable."""
        math_ok, reasoning_ok = self.check_models()

        worker = self.r1_worker if math_ok else self.r2_worker
        gap_id = "R1" if math_ok else "R2"

        print(f"\n[FALLBACK] Running sequential with {worker.model_config['id']} on {gap_id}")

        for cycle in range(1, max_cycles + 1):
            print(f"\nCycle {cycle}...")
            context = {"cycle": cycle, "mode": "sequential"}
            worker.run_cycle(cycle, context)
            self.state.total_cycles += 1
            self._save_state()

        return self.get_summary()

    def generate_synthesis(self):
        """Generate combined proof document from both gaps."""
        synthesis_path = OUTPUT_DIR / "gap_closure_synthesis.tex"

        r1_content = self._collect_gap_content("R1", self.state.r1_state)
        r2_content = self._collect_gap_content("R2", self.state.r2_state)

        synthesis = f"""% BSD Gap Closure Synthesis
% Generated by Dual-Model Orchestrator
% Date: {datetime.now().isoformat()}

\\documentclass{{article}}
\\usepackage{{amsmath, amssymb, amsthm}}

\\title{{BSD Conjecture: Gap R1 and R2 Closure}}
\\author{{GPIA Dual-Model Framework}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

\\section{{Gap R1: Euler Systems Existence}}
Progress: {self.state.r1_state.progress:.1%}
Model: {MODELS['math']['id']}

{r1_content}

\\section{{Gap R2: Control Theorem Machinery}}
Progress: {self.state.r2_state.progress:.1%}
Model: {MODELS['reasoning']['id']}

{r2_content}

\\section{{Cross-Validation Summary}}
Total validations: {self.state.cross_validations}

\\end{{document}}
"""

        synthesis_path.write_text(synthesis, encoding='utf-8')
        print(f"\n[SYNTHESIS] Generated: {synthesis_path}")

    def _collect_gap_content(self, gap_id: str, state: GapState) -> str:
        """Collect all content for a gap."""
        content = []
        for subgoal_id, result in sorted(state.subgoal_results.items()):
            status_marker = "✓" if result.status in [GapStatus.VALIDATED, GapStatus.COMPLETE] else "○"
            content.append(f"\\subsection{{{status_marker} {subgoal_id}}}")
            content.append(f"Rigor: {result.rigor_score:.2f}")
            content.append("")
            # Include first 1000 chars of content
            content.append(result.content[:1000])
            content.append("")
        return "\n".join(content)

    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        return {
            "session_id": self.state.session_id,
            "total_cycles": self.state.total_cycles,
            "math_cycles": self.state.math_cycles,
            "reasoning_cycles": self.state.reasoning_cycles,
            "cross_validations": self.state.cross_validations,
            "r1_progress": self.state.r1_state.progress,
            "r2_progress": self.state.r2_state.progress,
            "r1_subgoals_complete": sum(1 for r in self.state.r1_state.subgoal_results.values()
                                        if r.status in [GapStatus.VALIDATED, GapStatus.COMPLETE]),
            "r2_subgoals_complete": sum(1 for r in self.state.r2_state.subgoal_results.values()
                                        if r.status in [GapStatus.VALIDATED, GapStatus.COMPLETE]),
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="BSD Dual-Model Gap Closure")
    parser.add_argument("--parallel", action="store_true", help="Run models in parallel")
    parser.add_argument("--sequential", action="store_true", help="Run sequentially (fallback)")
    parser.add_argument("--validate-only", action="store_true", help="Only run cross-validation")
    parser.add_argument("--cycles", type=int, default=30, help="Max cycles")
    parser.add_argument("--validate-every", type=int, default=5, help="Validate every N cycles")

    args = parser.parse_args()

    orchestrator = DualModelOrchestrator()

    if args.validate_only:
        results = orchestrator.run_cross_validation()
        print(json.dumps(results, indent=2))
    else:
        summary = orchestrator.run_full_closure(
            max_cycles=args.cycles,
            validate_every=args.validate_every
        )

        print("\n" + "="*70)
        print("EXECUTION SUMMARY")
        print("="*70)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
