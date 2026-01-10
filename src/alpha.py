from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from skills.base import SkillContext
from skills.loader import SkillLoader
from skills.registry import get_registry


REPO_ROOT = Path(__file__).resolve().parent
SKILL_INDEXER = REPO_ROOT / "skills" / "system" / "skill-indexer" / "scripts" / "index_skills.py"
DEFAULT_INTERVAL_S = 300
DEFAULT_MAX_MEMORY = 20000


def _refresh_skill_index() -> None:
    if not SKILL_INDEXER.exists():
        return
    try:
        subprocess.run(
            [sys.executable, str(SKILL_INDEXER)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as exc:
        logging.debug("Alpha skill index refresh failed: %s", exc)


class AlphaAgent:
    """
    Diligent Student Alpha Agent runner.

    This is a standalone orchestration loop that:
    - Syncs skill index and registry
    - Uses perception -> decision -> action flow
    - Applies safety gates before actions
    - Stores progress in memory
    """

    def __init__(
        self,
        interval_s: Optional[int] = None,
        mode: str = "propose",
        max_memory: Optional[int] = None,
    ) -> None:
        self.interval_s = interval_s or int(os.getenv("ALPHA_INTERVAL", str(DEFAULT_INTERVAL_S)))
        self.mode = mode
        self.max_memory = max_memory or int(os.getenv("ALPHA_MAX_MEMORY", str(DEFAULT_MAX_MEMORY)))
        self._context = SkillContext(agent_role="alpha")
        self._cycle = 0
        self._messages: list[str] = []

        loader = SkillLoader()
        loader.scan_all(lazy=False)
        registry = get_registry()

        # Initialize Alpha's own memory database (separate from main system)
        self._init_alpha_memory()
        self.memory_skill = registry.get_skill("conscience/memory")
        self.retrieval_skill = registry.get_skill("foundational/fast-reflex-vector-mapper")
        self.judge_skill = registry.get_skill("foundational/meticulous-semantic-judge")
        self.scale_skill = registry.get_skill("foundational/retrieval-strategist")
        self.constrained_skill = registry.get_skill("foundational/hallucination-guard")

        # Load MindsetSkill for LLM-assisted reasoning
        try:
            self.mindset_skill = registry.get_skill("conscience/mindset")
            logging.info("Alpha will use MindsetSkill with LLM partners (DeepSeek-R1, Qwen3, CodeGemma)")
        except Exception:
            self.mindset_skill = None
            logging.warning("conscience/mindset not available")

        # Optional skills (may not be implemented yet)
        try:
            self.hybrid_skill = registry.get_skill("automation/hybrid-orchestrator")
        except Exception:
            self.hybrid_skill = None
            logging.warning("automation/hybrid-orchestrator not available")

        try:
            self.progressive_skill = registry.get_skill("automation/progressive-disclosure")
        except Exception:
            self.progressive_skill = None
            logging.warning("automation/progressive-disclosure not available")

        try:
            self.rehearsal_skill = registry.get_skill("enterprise/synthetic-rehearsal-tool")
        except Exception:
            self.rehearsal_skill = None
            logging.warning("enterprise/synthetic-rehearsal-tool not available")

        _refresh_skill_index()

    def _init_alpha_memory(self) -> None:
        """Initialize Alpha's own memory database (separate from main system)."""
        from skills.conscience.memory.skill import MemoryStore
        alpha_memory_path = REPO_ROOT / "skills" / "conscience" / "memory" / "store" / "alpha_memories.db"
        self.alpha_memory = MemoryStore(db_path=alpha_memory_path)
        logging.info(f"Alpha using separate memory database: {alpha_memory_path}")

    def status(self) -> Dict[str, Any]:
        return {
            "cycle": self._cycle,
            "mode": self.mode,
            "interval_s": self.interval_s,
            "max_memory": self.max_memory,
        }

    def update_config(
        self,
        mode: Optional[str] = None,
        interval_s: Optional[int] = None,
        max_memory: Optional[int] = None,
    ) -> None:
        if mode:
            self.mode = mode
        if interval_s:
            self.interval_s = interval_s
        if max_memory:
            self.max_memory = max_memory

    def handle_message(self, message: str) -> None:
        if not message:
            return
        self._messages.append(message)
        # Store in Alpha's own memory
        if self.alpha_memory:
            self.alpha_memory.store(
                content=f"Alpha message: {message}",
                memory_type="semantic",
                importance=0.6,
                context={"source": "alpha_message"},
            )

    def _boot_sequence(self) -> Dict[str, Any]:
        boot = {
            "timestamp": datetime.now().isoformat(),
            "index_refreshed": SKILL_INDEXER.exists(),
            "skills_loaded": True,
            "mode": self.mode,
        }

        if self.rehearsal_skill:
            result = self.rehearsal_skill.execute(
                {"capability": "generate", "corpus": "skills/index"},
                self._context,
            )
            boot["synthetic_rehearsal"] = result.output if result.success else {"error": result.error}

        # Store boot sequence in Alpha's own memory
        if self.alpha_memory:
            self.alpha_memory.store(
                content="Alpha boot sequence completed.",
                memory_type="procedural",
                importance=0.6,
                context=boot,
            )

        return boot

    def _pop_message(self) -> Optional[str]:
        if not self._messages:
            return None
        return self._messages.pop(0)

    def _load_skill_index(self) -> Dict[str, Any]:
        index_path = REPO_ROOT / "skills" / "INDEX.json"
        if not index_path.exists():
            return {"path": str(index_path), "count": 0, "skills": []}
        try:
            payload = json.loads(index_path.read_text(encoding="utf-8"))
            return {
                "path": str(index_path),
                "count": payload.get("count", 0),
                "skills": payload.get("skills", []),
            }
        except Exception:
            return {"path": str(index_path), "count": 0, "skills": []}

    def _perception(self) -> Dict[str, Any]:
        message = self._pop_message()
        query = message or "skills index"
        skill_index = self._load_skill_index()
        observations = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self._cycle,
            "index_path": skill_index["path"],
            "index_count": skill_index["count"],
            "allowed_ids": [entry.get("id") for entry in skill_index.get("skills", []) if entry.get("id")],
            "message": message,
            "query": query,
        }
        if self.alpha_memory:
            observations["memory_stats"] = self.alpha_memory.get_stats()
        if self.retrieval_skill:
            encode = self.retrieval_skill.execute({"capability": "encode", "query": query}, self._context)
            search = self.retrieval_skill.execute({"capability": "search", "query": query}, self._context)
            observations["vector_map"] = {
                "encode": encode.output if encode.success else {"error": encode.error},
                "search": search.output if search.success else {"error": search.error},
            }
        return observations

    def _decision(self, observations: Dict[str, Any]) -> Dict[str, Any]:
        query = observations.get("query", "skills index")
        decision = {
            "strategy": "retrieve_then_judge",
            "notes": "default decision flow",
        }

        # Use LLM partners for analysis if MindsetSkill is available
        if self.mindset_skill:
            problem = f"""Analyze this Alpha Agent cycle observation:
Cycle: {observations.get('cycle')}
Query: {query}
Skills available: {observations.get('index_count', 0)}
Memory stats: {observations.get('memory_stats', {})}
Message: {observations.get('message')}

What should Alpha focus on in this cycle?"""

            mindset_result = self.mindset_skill.execute(
                {
                    "capability": "analyze",
                    "problem": problem,
                    "pattern": "balanced",  # Uses DeepSeek -> Qwen -> DeepSeek chain
                },
                self._context,
            )
            if mindset_result.success:
                decision["llm_analysis"] = mindset_result.output
                logging.info(f"Alpha LLM reasoning: {mindset_result.output.get('summary', '')[:100]}")

        if self.scale_skill:
            scale = self.scale_skill.execute(
                {
                    "capability": "assess",
                    "corpus_size": observations.get("index_count", 0),
                },
                self._context,
            )
            decision["scale_check"] = scale.output if scale.success else {"error": scale.error}
        if self.progressive_skill:
            decision["progressive_disclosure"] = "enabled"
        if self.judge_skill:
            rerank = self.judge_skill.execute({"capability": "rerank", "query": query}, self._context)
            validate = self.judge_skill.execute({"capability": "validate", "query": query}, self._context)
            decision["semantic_judge"] = {
                "rerank": rerank.output if rerank.success else {"error": rerank.error},
                "validate": validate.output if validate.success else {"error": validate.error},
            }
        return decision

    def _safety_gates(self, observations: Dict[str, Any]) -> Dict[str, Any]:
        memory_total = 0
        if self.alpha_memory:
            stats = self.alpha_memory.get_stats()
            memory_total = stats.get("total_memories", 0)
        allowed_ids = observations.get("allowed_ids", [])
        decoding_ok = bool(self.constrained_skill)
        if self.constrained_skill and allowed_ids:
            verify = self.constrained_skill.execute(
                {"capability": "verify", "allowed": allowed_ids[:500]},
                self._context,
            )
            decoding_ok = verify.success
        gates = {
            "constrained_decoding": decoding_ok,
            "scale_awareness": bool(self.scale_skill),
            "resource_governor": memory_total <= self.max_memory,
        }
        gates["allowed"] = all(gates.values())
        return gates

    def _action(self, decision: Dict[str, Any], gates: Dict[str, Any]) -> Dict[str, Any]:
        action = {
            "mode": self.mode,
            "status": "no-op",
            "details": "actions disabled",
        }
        if not gates.get("allowed"):
            action["status"] = "blocked"
            action["details"] = "safety gate failure"
            return action

        if self.mode == "observe":
            action["details"] = "observe-only"
            return action

        if self.mode == "propose":
            action["status"] = "proposed"
            action["details"] = "no execution performed"
            return action

        if self.mode == "execute" and self.hybrid_skill:
            result = self.hybrid_skill.execute(
                {"capability": "run", "decision": decision},
                self._context,
            )
            action["status"] = "executed" if result.success else "failed"
            action["details"] = result.output or result.error
            return action

        return action

    def run_once(self) -> Dict[str, Any]:
        self._cycle += 1
        _refresh_skill_index()

        observations = self._perception()
        decision = self._decision(observations)
        gates = self._safety_gates(observations)
        action = self._action(decision, gates)

        # Store cycle experience in Alpha's own memory
        if self.alpha_memory:
            self.alpha_memory.store(
                content=f"Alpha cycle {self._cycle} completed.",
                memory_type="episodic",
                importance=0.5,
                context={
                    "observations": observations,
                    "decision": decision,
                    "gates": gates,
                    "action": action,
                },
            )

        return {
            "cycle": self._cycle,
            "observations": observations,
            "decision": decision,
            "gates": gates,
            "action": action,
        }

    def start(self, stop_event: Optional[threading.Event] = None) -> None:
        self._boot_sequence()
        while True:
            try:
                summary = self.run_once()
                logging.info("Alpha cycle %s: %s", summary["cycle"], summary["action"]["status"])
            except KeyboardInterrupt:
                logging.info("Alpha agent stopped by user.")
                break
            except Exception as exc:
                logging.exception("Alpha agent error: %s", exc)
            if stop_event and stop_event.is_set():
                logging.info("Alpha agent stop requested.")
                break
            time.sleep(self.interval_s)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Alpha Agent Runner")
    parser.add_argument("--once", action="store_true", help="Run single cycle then exit")
    parser.add_argument(
        "--mode",
        choices=["observe", "propose", "execute"],
        default=os.getenv("ALPHA_MODE", "propose"),
        help="Autonomy mode",
    )
    parser.add_argument("--interval", type=int, default=None, help="Loop interval in seconds")

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    agent = AlphaAgent(interval_s=args.interval, mode=args.mode)
    if args.once:
        print(json.dumps(agent.run_once(), indent=2))
        return
    agent.start()


if __name__ == "__main__":
    main()
