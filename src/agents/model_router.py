"""
Model Router - Unified interface for all local LLMs

Routes tasks to the appropriate model based on task type.
Supports all 5 Ollama models plus GPIA Core:
- codegemma:latest (133 tok/s) - fast parsing
- qwen3:latest (87 tok/s) - creative/dialogue
- deepseek-r1:latest (74 tok/s) - reasoning
- llava:latest - vision
- gpt-oss:20b - complex synthesis
- gpia-core - action protocol brain
"""

import os
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from core.dynamic_budget_orchestrator import apply_dynamic_budget, compute_budget
from integrations.trt_llm_client import TensorRTClient

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
ROUTER_MODEL_ID = os.getenv("ROUTER_MODEL_ID", "gpia-router:latest")
USE_NEURONIC_ROUTER = os.getenv("USE_NEURONIC_ROUTER", "").strip().lower() in ("1", "true", "yes", "on")

# SUBSTRATE EQUILIBRIUM: TensorRT Sidecar Client
_trt_client = None

def get_trt_client():
    global _trt_client
    if _trt_client is None:
        _trt_client = TensorRTClient()
    return _trt_client

# Metabolic throttling thresholds (env configurable)
EXPANSION_MAX_PROMPT_TOKENS = int(os.getenv("METABOLIC_EXPANSION_MAX_PROMPT_TOKENS", "3000"))
EXPANSION_MIN_VRAM_MB = int(os.getenv("METABOLIC_EXPANSION_MIN_VRAM_MB", "2048"))
CRYSTALLIZATION_MIN_VRAM_MB = int(os.getenv("METABOLIC_CRYSTALLIZATION_MIN_VRAM_MB", "4096"))
OLLAMA_HEALTH_TIMEOUT = int(os.getenv("OLLAMA_HEALTH_TIMEOUT_SECONDS", "5"))

# Map external model IDs to internal registry keys where they differ
MODEL_ID_TO_NAME = {
    "gpia-codegemma:latest": "codegemma",
    "codegemma:latest": "codegemma",
    "gpia-qwen3:latest": "qwen3",
    "gpia-deepseek-r1:latest": "deepseek_r1",
    "gpia-gpt-oss:20b": "gpt_oss_20b",
    "gpia-gpt-oss:latest": "gpt_oss_20b",
    "gpia-llama3:8b": "gpt_oss_20b",  # fallback
    "gpia-master:latest": "gpia_core",
    "gpia-llava:latest": "llava",
    "qwen2-math:7b": "qwen3",  # not in MODELS; fall back to qwen3 unless added
}

# Optional Hugging Face models (set via env to keep flexible)
HF_FAST_MODEL_ID = os.getenv("HF_FAST_MODEL_ID")  # e.g., "models/mamba-130m-hf" or "tiiuae/falcon-7b-instruct"
HF_HEAVY_MODEL_ID = os.getenv("HF_HEAVY_MODEL_ID")  # e.g., "meta-llama/Llama-2-13b-chat-hf"

class ModelRole(Enum):
    FAST = "fast"
    CREATIVE = "creative"
    REASONING = "reasoning"
    VISION = "vision"
    SYNTHESIS = "synthesis"


@dataclass
class Model:
    name: str
    ollama_id: str
    role: ModelRole
    speed: str
    size: str
    strengths: List[str]
    backend: str = "ollama"   # "ollama" or "hf"
    hf_id: Optional[str] = None


# All available models (UPDATED with gpia- prefix)
MODELS = {
    "codegemma": Model(
        name="codegemma",
        ollama_id="gpia-codegemma:latest",
        role=ModelRole.FAST,
        speed="133 tok/s",
        size="5.0 GB",
        strengths=["intent parsing", "entity extraction", "quick checks", "agreement summary"]
    ),
    "qwen3": Model(
        name="qwen3",
        ollama_id="gpia-qwen3:latest",
        role=ModelRole.CREATIVE,
        speed="87 tok/s",
        size="5.2 GB",
        strengths=["dialogue", "lesson creation", "creative writing", "Alpha responses"]
    ),
    "deepseek_r1": Model(
        name="deepseek_r1",
        ollama_id="gpia-deepseek-r1:latest",
        role=ModelRole.REASONING,
        speed="74 tok/s",
        size="5.2 GB",
        strengths=["analysis", "grading", "critique", "chain-of-thought", "Professor tasks"]
    ),
    "llava": Model(
        name="llava",
        ollama_id="gpia-llava:latest",
        role=ModelRole.VISION,
        speed="N/A",
        size="4.7 GB",
        strengths=["image analysis", "visual reasoning", "screenshot review"]
    ),
    "gpt_oss_20b": Model(
        name="gpt_oss_20b",
        ollama_id="gpia-gpt-oss:latest",
        role=ModelRole.SYNTHESIS,
        speed="~40 tok/s",
        size="13 GB",
        strengths=["complex synthesis", "dispute resolution", "final judgment", "long-form"]
    ),
    "gpia_core": Model(
        name="gpia_core",
        ollama_id="gpia-master:latest",
        role=ModelRole.REASONING,
        speed="custom",
        size="custom",
        strengths=["action schema", "json protocol", "system-2 reasoning"]      
    ),
}

# Dynamically register optional Hugging Face models if provided
if HF_FAST_MODEL_ID:
    MODELS["hf_fast"] = Model(
        name="hf_fast",
        ollama_id=HF_FAST_MODEL_ID,  # reuse field for budget tagging
        role=ModelRole.FAST,
        speed="hf-local",
        size="local",
        strengths=["local HF fast model"],
        backend="hf",
        hf_id=HF_FAST_MODEL_ID,
    )

if HF_HEAVY_MODEL_ID:
    MODELS["hf_heavy"] = Model(
        name="hf_heavy",
        ollama_id=HF_HEAVY_MODEL_ID,  # reuse field for budget tagging
        role=ModelRole.SYNTHESIS,
        speed="hf-local",
        size="local-heavy",
        strengths=["local HF heavy model"],
        backend="hf",
        hf_id=HF_HEAVY_MODEL_ID,
    )

# Task to model mapping
TASK_ROUTING = {
    # Fast tasks (codegemma)
    "intent_parsing": "codegemma",
    "entity_extraction": "codegemma",
    "agreement_summary": "codegemma",
    "quick_check": "codegemma",

    # Creative tasks (qwen3)
    "alpha_response": "qwen3",
    "alpha_challenge": "qwen3",
    "lesson_creation": "qwen3",
    "dialogue": "qwen3",
    "creative": "qwen3",

    # Reasoning tasks (deepseek_r1)
    "professor_analysis": "deepseek_r1",
    "professor_grading": "deepseek_r1",
    "critique": "deepseek_r1",
    "reasoning": "deepseek_r1",
    "debug": "deepseek_r1",

    # Vision tasks (llava)
    "image_analysis": "llava",
    "screenshot_review": "llava",
    "visual": "llava",

    # Synthesis tasks (gpt_oss_20b)
    "final_synthesis": "gpt_oss_20b",
    "dispute_resolution": "gpt_oss_20b",
    "complex": "gpt_oss_20b",
    "arbiter": "gpt_oss_20b",
}


def _env_bool(name: str, default: str = "1") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}

# Global Enforcement Toggle
USE_GOVERNMENT_ENGINE = _env_bool("GPIA_ENFORCE_GOVERNMENT", "1")
USE_TENSORRT_ROUTING = _env_bool("GPIA_USE_TENSORRT", "1")
TRT_ELIGIBLE_ROLES = {ModelRole.REASONING, ModelRole.SYNTHESIS}
TRT_HEAVY_TASKS = {
    "reasoning",
    "professor_analysis",
    "professor_grading",
    "debug",
    "final_synthesis",
    "dispute_resolution",
    "complex",
    "arbiter",
}

class ModelRouter:
    """Routes tasks to appropriate models and handles LLM queries."""

    def __init__(self, ollama_url: str = OLLAMA_URL):
        self.ollama_url = ollama_url
        self.models = MODELS
        self.routing = TASK_ROUTING
        self._hf_clients: Dict[str, Any] = {}
        self._gov_engine: Optional[Any] = None
        
        # MULTICELLULAR DISCOVERY: Detect dedicated student nodes
        self.student_nodes = {
            "gpia-master": "http://localhost:11435/api/generate",
            "gpia-deepseek-r1": "http://localhost:11436/api/generate",
            "gpia-qwen3": "http://localhost:11437/api/generate"
        }

    def _get_target_url(self, model_id: str) -> str:
        """Find the optimal node for the requested model."""
        base_id = model_id.split(":")[0]
        if base_id in self.student_nodes:
            # Check if student node is alive
            try:
                node_url = self.student_nodes[base_id]
                resp = requests.get(node_url.replace("/generate", "/tags"), timeout=1)
                if resp.status_code == 200:
                    return node_url
            except:
                pass
        return self.ollama_url

    def get_model_for_task(self, task: str) -> Model:
        """Get the appropriate model for a task."""
        model_name = self.routing.get(task, "qwen3")  # Default to qwen3
        return self.models.get(model_name, self.models["qwen3"])

    def get_model_by_role(self, role: ModelRole) -> Model:
        """Get a model by its role."""
        for model in self.models.values():
            if model.role == role:
                return model
        return self.models["qwen3"]

    def query_governed(self, prompt: str, task: str = None, **kwargs) -> str:
        """Execute query via Government Engine for full audit/safety gating."""
        engine = self._get_gov_engine()
        if not engine:
            return self.query(prompt, task=task, **kwargs)  # Fallback
            
        from core.runtime.capsule_types import Capsule
        from core.agents.base import AgentContext
        
        capsule = Capsule(
            id=f"gov-q-{abs(hash(prompt)) % 1000000}",
            kind="task" if task in ["reasoning", "complex", "debug"] else "skill",
            goal=prompt,
            trace={"arbiter": True}
        )
        
        # Build minimal context for engine
        class FakeCtx:
            def __init__(self):
                self.telemetry = type('T', (), {'emit': lambda *a, **k: None})()
                self.ledger = type('L', (), {'append': lambda *a, **k: None})()
                self.perception = type('P', (), {'write': lambda *a, **k: None})()
                
        res = engine.execute(capsule, FakeCtx())
        
        # Handle PASS resolution if engine returned blocked
        if res.blocked and res.pass_request and hasattr(engine, "pass_broker"):
            res = engine.pass_broker.resolve(capsule, res)
            
        return res.output.get("text", res.error or "Execution failed")

    def query(
        self,
        prompt: str,
        task: str = None,
        model: str = None,
        mode_hint: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.1,  # Standardized for deterministic output
        timeout: int = 120,
        bypass_gov: bool = False
    ) -> str:
        """Query an LLM with automatic model selection."""
        
        # Global Enforcement: Route through Government Engine unless explicitly bypassed
        if USE_GOVERNMENT_ENGINE and not bypass_gov:
            # Avoid recursion if called by Government Engine itself
            import inspect
            stack = inspect.stack()
            if not any("engines/government.py" in s.filename for s in stack[1:5]):
                return self.query_governed(prompt, task=task, max_tokens=max_tokens, temperature=temperature)

        # Determine which model to use (load + hint aware)

    def get_model_by_role(self, role: ModelRole) -> Model:
        """Get a model by its role."""
        for model in self.models.values():
            if model.role == role:
                return model
        return self.models["qwen3"]

    def _ensure_ollama_ready(self) -> bool:
        """
        Lightweight Ollama health check so we don't silently degrade routing.
        """
        try:
            resp = requests.get(self.ollama_url.replace("/generate", "/tags"), timeout=OLLAMA_HEALTH_TIMEOUT)
            return resp.status_code == 200
        except Exception:
            return False

    def _ensure_hf_ready(self, hf_id: str) -> bool:
        """
        Lightweight Hugging Face availability check (local path or HF id).
        """
        try:
            # Lazy import to avoid hard dependency when unused
            from transformers import AutoTokenizer  # type: ignore
            # If hf_id is a local path, confirm it exists; if remote, trust cache
            if os.path.isdir(hf_id):
                return True
            return True  # assume cached/available; failures handled in load
        except Exception:
            return False

    def _get_hf_client(self, hf_id: str):
        """
        Lazy-load and cache a text-generation pipeline for HF models.
        """
        if hf_id in self._hf_clients:
            return self._hf_clients[hf_id]
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline  # type: ignore
            import torch  # type: ignore
        except Exception as e:
            raise RuntimeError(f"[Router] transformers not available for HF model '{hf_id}': {e}")

        tokenizer = AutoTokenizer.from_pretrained(hf_id)
        model = AutoModelForCausalLM.from_pretrained(hf_id, device_map="auto")
        gen_pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, torch_dtype=torch.float16 if torch.cuda.is_available() else None)
        self._hf_clients[hf_id] = gen_pipe
        return gen_pipe

    def _compute_load(self, prompt: str, requested_tokens: int, model_id: str | None) -> Dict[str, Any]:
        """
        Estimate metabolic load using prompt size and resource snapshot from the dynamic budgeter.
        """
        try:
            _, details = compute_budget(prompt, requested_tokens, model_id=model_id)
            snapshot = details.get("resource_snapshot", {}) or {}
            return {
                "prompt_tokens": details.get("prompt_tokens", 0),
                "vram_free_mb": snapshot.get("vram_free_mb"),
                "ram_free_mb": snapshot.get("ram_free_mb"),
            }
        except Exception:
            # Fallback to rough estimates
            return {
                "prompt_tokens": max(1, len(prompt) // 4),
                "vram_free_mb": None,
                "ram_free_mb": None,
            }

    def _should_route_tensorrt(self, model_obj: Optional[Model], task: Optional[str]) -> bool:
        """Determine whether to offload to the TensorRT sidecar."""
        if not USE_TENSORRT_ROUTING or not model_obj:
            return False
        if model_obj.role in TRT_ELIGIBLE_ROLES:
            return True
        return (task or "") in TRT_HEAVY_TASKS

    def _query_tensorrt(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Query the TensorRT sidecar; return None if unavailable or failed."""
        try:
            client = get_trt_client()
            result = client.query(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
            if result and not str(result).startswith("[Error]"):
                return result
            if result:
                print(f"[Router] TensorRT returned error, falling back: {result}")
        except Exception as e:
            print(f"[Router] TensorRT query failed: {e}")
        return None

    def _select_model(
        self,
        prompt: str,
        requested_tokens: int,
        model: Optional[str],
        task: Optional[str],
        mode_hint: Optional[str],
    ) -> Model:
        """
        Choose model based on hint + load; defaults to existing task routing when unspecified.
        """
        # GLOBAL LOCAL OVERRIDE (For local-only operation)
        local_override = os.getenv("GPIA_LOCAL_OVERRIDE")
        if local_override:
            # Route all tasks to the user-specified local model
            return Model(
                name="local_master",
                ollama_id=local_override,
                role=ModelRole.REASONING,
                speed="local",
                size="custom",
                strengths=["local intelligence override"],
                backend="ollama"
            )

        # Explicit override wins
        if model and model in self.models:
            return self.models[model]

        # Task-driven fallback
        model_obj = self.get_model_for_task(task) if task else None

        # Metabolic/load-aware selection
        load = self._compute_load(prompt, requested_tokens, model_obj.ollama_id if model_obj else None)
        prompt_tokens = load.get("prompt_tokens") or 0
        vram_free = load.get("vram_free_mb")

        hint = (mode_hint or "").lower().strip()
        if hint == "expansion":
            if (vram_free is None or vram_free >= EXPANSION_MIN_VRAM_MB) and prompt_tokens <= EXPANSION_MAX_PROMPT_TOKENS:
                if "hf_fast" in self.models:
                    return self.models["hf_fast"]
                return self.models["codegemma"]
            # If expansion blocked by load, fall through to synthesis for stability
            if "hf_heavy" in self.models:
                return self.models["hf_heavy"]
            return self.models["gpt_oss_20b"]

        if hint == "crystallization":
            # Prefer heavy model if VRAM is acceptable; otherwise fallback to reasoning
            if vram_free is None or vram_free >= CRYSTALLIZATION_MIN_VRAM_MB:
                if "hf_heavy" in self.models:
                    return self.models["hf_heavy"]
                return self.models["gpt_oss_20b"]
            return self.models.get("deepseek_r1", self.models["qwen3"])

        # Auto mode: small prompts -> codegemma; large or low VRAM -> gpt_oss_20b
        if prompt_tokens <= EXPANSION_MAX_PROMPT_TOKENS and (vram_free is None or vram_free >= EXPANSION_MIN_VRAM_MB):
            if "hf_fast" in self.models:
                return self.models["hf_fast"]
            return self.models.get("codegemma", self.models["qwen3"])
        if "hf_heavy" in self.models:
            return self.models["hf_heavy"]
        return self.models.get("gpt_oss_20b", self.models["qwen3"])

    def query(
        self,
        prompt: str,
        task: str = None,
        model: str = None,
        mode_hint: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.1,  # Standardized for deterministic output
        timeout: int = 120,
        bypass_gov: bool = False
    ) -> str:
        """Query an LLM with automatic model selection."""
        
        # Global Enforcement: Route through Government Engine unless explicitly bypassed
        if USE_GOVERNMENT_ENGINE and not bypass_gov:
            # Avoid recursion if called by Government Engine itself
            import inspect
            stack = inspect.stack()
            if not any("engines/government.py" in s.filename for s in stack[1:5]):
                return self.query_governed(prompt, task=task, max_tokens=max_tokens, temperature=temperature)

        # Determine which model to use (load + hint aware)
        model_obj = self._select_model(prompt, max_tokens, model, task, mode_hint)

        # If selection failed, let router pick
        if model_obj is None:
            routed_id = self._route_via_router_model(prompt)
            model_obj = self._model_from_id(routed_id) or self.models["qwen3"]

        effective_max = self._adjust_max_tokens(prompt, max_tokens, model_obj.ollama_id)

        # Prefer TensorRT sidecar for heavy reasoning/synthesis when available
        if self._should_route_tensorrt(model_obj, task):
            trt_response = self._query_tensorrt(prompt, effective_max, temperature)
            if trt_response:
                return trt_response

        # Health guard per backend
        if model_obj.backend == "ollama":
            if not self._ensure_ollama_ready():
                return "[Router] Ollama unavailable (health check failed). Run 'ollama serve' in the main folder and verify models with 'ollama list'."
        else:  # hf
            if not self._ensure_hf_ready(model_obj.hf_id or model_obj.name):
                return f"[Router] HF model '{model_obj.hf_id or model_obj.name}' unavailable. Ensure transformers is installed and the model exists locally."

        if model_obj.backend == "hf":
            return self._query_hf(
                model_obj.hf_id or model_obj.name,
                prompt,
                effective_max,
                temperature,
            )

        return self._query_ollama(
            model_obj.ollama_id,
            prompt,
            effective_max,
            temperature,
            timeout
        )

    def query_with_continuation(
        self,
        prompt: str,
        task: str = None,
        model: str = None,
        max_tokens: int = 800,
        temperature: float = 0.1,  # Standardized
        max_continuations: int = 2
    ) -> str:
        """Query with automatic continuation for truncated responses."""

        if model:
            model_obj = self.models.get(model, self.models["qwen3"])
        elif task:
            model_obj = self.get_model_for_task(task)
        else:
            model_obj = self.models["qwen3"]

        full_response = ""
        continuation_prompt = prompt

        for attempt in range(max_continuations + 1):
            effective_max = self._adjust_max_tokens(
                continuation_prompt,
                max_tokens,
                model_obj.ollama_id,
            )
            chunk = self._query_ollama(
                model_obj.ollama_id,
                continuation_prompt,
                effective_max,
                temperature,
                120
            )

            if full_response and chunk:
                full_response += "\n"
            full_response += chunk

            # Check if complete
            if chunk and (chunk[-1] in '.!?"' or len(chunk) < effective_max * 0.75):
                break

            # Check for truncation
            truncation_indicators = ["...", "-", "I'm", "I'll", "Could", "How", "What"]
            near_limit = len(chunk) >= int(effective_max * 0.9)
            needs_continuation = near_limit or any(
                chunk.rstrip().endswith(ind) for ind in truncation_indicators
            )

            if needs_continuation and attempt < max_continuations:
                continuation_prompt = (
                    f"Continue your previous response. You were saying:\n\n"
                    f"{chunk[-300:]}\n\nContinue from where you left off:"
                )
            else:
                break

        return full_response

    def query_council(
        self,
        prompt: str,
        models: List[str] = None,
        max_tokens: int = 600
    ) -> Dict[str, str]:
        """Query multiple models and return all responses."""
        if models is None:
            models = ["codegemma", "qwen3", "deepseek_r1", "gpt_oss_20b"]

        responses = {}
        for model_name in models:
            model_obj = self.models.get(model_name)
            if model_obj:
                effective_max = self._adjust_max_tokens(prompt, max_tokens, model_obj.ollama_id)
                response = self._query_ollama(
                    model_obj.ollama_id,
                    prompt,
                    effective_max,
                    0.7,
                    120
                )
                responses[model_name] = response

        return responses

    def synthesize_council(
        self,
        prompt: str,
        council_models: List[str] = None,
        synthesis_model: str = "gpt_oss_20b",
        max_tokens: int = 600
    ) -> Dict[str, Any]:
        """Query council and synthesize responses."""
        # Get council responses
        council_responses = self.query_council(prompt, council_models, max_tokens)

        # Format for synthesis
        formatted_responses = "\n\n".join([
            f"[{model}]: {response}"
            for model, response in council_responses.items()
        ])

        synthesis_prompt = f"""Synthesize these perspectives into a unified response:

{formatted_responses}

Provide a balanced synthesis that:
1. Identifies common ground
2. Notes key disagreements
3. Proposes a resolution

Keep response under 300 words."""

        synthesis = self.query(
            synthesis_prompt,
            model=synthesis_model,
            max_tokens=500
        )

        return {
            "council_responses": council_responses,
            "synthesis": synthesis
        }

    def _query_ollama(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
        timeout: int
    ) -> str:
        """Internal method to query Ollama API."""
        target_url = self._get_target_url(model_id)
        try:
            payload = {
                "model": model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.1,          # Standardized for deterministic logic
                    "top_k": 10,           # Limit vocabulary noise
                    "repeat_penalty": 1.1  # Prevent logical loops
                },
            }
            response = requests.post(target_url, json=payload, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                result = (data.get("response") or "").strip()

                # Clean DeepSeek thinking tags
                if "<think>" in result:
                    import re
                    result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()

                if not result and data.get("thinking"):
                    retry_payload = {
                        "model": model_id,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                        },
                    }
                    retry = requests.post(target_url, json=retry_payload, timeout=timeout)
                    if retry.status_code == 200:
                        result = (retry.json().get("response") or "").strip()

                return result
        except Exception as e:
            print(f"LLM Error ({model_id} on {target_url}): {e}")

        return ""

    def _query_hf(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Internal method to query Hugging Face local models."""
        if not self._ensure_hf_ready(model_id):
            return f"[Router] HF model '{model_id}' unavailable. Install transformers and ensure the model path/id is valid."
        try:
            pipe = self._get_hf_client(model_id)
            outputs = pipe(prompt, max_new_tokens=max_tokens, temperature=temperature, do_sample=temperature > 0)
            if outputs and isinstance(outputs, list):
                text = outputs[0].get("generated_text", "").strip()
                return text
        except Exception as e:
            return f"[Router] HF query failed for '{model_id}': {e}"
        return ""

    def _model_from_id(self, model_id: str) -> Optional[Model]:
        # Direct match on ollama_id
        for m in self.models.values():
            if m.ollama_id == model_id:
                return m
        # Map external id to internal name
        mapped = MODEL_ID_TO_NAME.get(model_id)
        if mapped and mapped in self.models:
            return self.models[mapped]
        # Fallback by name
        return self.models.get(model_id)

    def _route_via_router_model(self, prompt: str) -> str:
        """Call the gpia-router model to get a route."""
        try:
            payload = {
                "model": ROUTER_MODEL_ID,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "num_predict": 100,
                },
            }
            resp = requests.post(OLLAMA_URL, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                raw = (data.get("response") or "").strip()
                # Expect JSON: {"route": "<id>", "reason": "..."}
                import json
                try:
                    obj = json.loads(raw)
                    routed = obj.get("route")
                    if routed:
                        return routed
                except Exception:
                    pass
        except Exception as e:
            print(f"Router Error ({ROUTER_MODEL_ID}): {e}")
        # Fallback
        return "gpia-qwen3:latest"

    def _adjust_max_tokens(self, prompt: str, max_tokens: int, model_id: str) -> int:
        try:
            return apply_dynamic_budget(prompt, max_tokens, model_id=model_id)
        except Exception:
            return max_tokens

    def list_models(self) -> None:
        """Print available models."""
        print("\nAvailable Models:")
        print("-" * 60)
        for name, model in self.models.items():
            print(f"  {name:<15} | {model.speed:<12} | {model.size:<8} | {model.role.value}")
        print()


# Convenience functions
_router = None


def get_router() -> ModelRouter:
    """Get singleton router instance."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


def query(prompt: str, task: str = None, model: str = None, **kwargs) -> str:   
    """Convenience function to query LLM."""
    return get_router().query(prompt, task, model, **kwargs)


def query_fast(prompt: str, **kwargs) -> str:
    """Quick query using codegemma."""
    return get_router().query(prompt, model="codegemma", **kwargs)


def query_creative(prompt: str, **kwargs) -> str:
    """Creative query using qwen3."""
    return get_router().query(prompt, model="qwen3", **kwargs)


def query_reasoning(prompt: str, **kwargs) -> str:
    """Reasoning query using deepseek_r1."""
    return get_router().query(prompt, model="deepseek_r1", **kwargs)


def query_synthesis(prompt: str, **kwargs) -> str:
    """Complex synthesis using gpt_oss_20b."""
    return get_router().query(prompt, model="gpt_oss_20b", **kwargs)


def query_expansion(prompt: str, **kwargs) -> str:
    """Expansion (25-beat) mode: prefer codegemma when load allows."""
    return get_router().query(prompt, mode_hint="expansion", **kwargs)


def query_crystallization(prompt: str, **kwargs) -> str:
    """Crystallization (5-beat) mode: prefer gpt_oss_20b when VRAM allows."""
    return get_router().query(prompt, mode_hint="crystallization", **kwargs)


def query_gpia_core(prompt: str, **kwargs) -> str:
    """Action-protocol brain for structured outputs."""
    return get_router().query(prompt, model="gpia_core", **kwargs)


def query_council(prompt: str, **kwargs) -> Dict[str, str]:
    """Query all models."""
    return get_router().query_council(prompt, **kwargs)


# Active router selector (Neuronic -> base)
_active_router = None


def get_active_router():
    """Return neuronic router if enabled, else base router."""
    global _active_router
    if _active_router is None:
        if USE_NEURONIC_ROUTER:
            try:
                from agents.neuronic_router import get_neuronic_router
                _active_router = get_neuronic_router()
            except Exception as e:
                print(f"[Router] Failed to init NeuronicRouter, falling back: {e}")
                _active_router = get_router()
        else:
            _active_router = get_router()
    return _active_router


def query_active(prompt: str, task: str = None, model: str = None, **kwargs) -> str:
    """Query via neuronic router when enabled, else base router."""
    router = get_active_router()
    if hasattr(router, "query"):
        return router.query(prompt=prompt, task=task, model=model, **kwargs)
    return get_router().query(prompt, task, model, **kwargs)


if __name__ == "__main__":
    # Test the router
    router = ModelRouter()
    router.list_models()

    print("\nTesting model routing...")
    test_tasks = [
        "intent_parsing",
        "alpha_response",
        "professor_analysis",
        "final_synthesis"
    ]

    for task in test_tasks:
        model = router.get_model_for_task(task)
        print(f"  {task:<20} -> {model.name} ({model.ollama_id})")
