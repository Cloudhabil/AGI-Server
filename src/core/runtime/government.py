import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def _get_embedding_vector(text: str) -> np.ndarray:
    """Helper to get normalized embedding vector from OpenVINO or fallback hash."""
    try:
        from integrations.openvino_embedder import get_embeddings
        vec = np.array(get_embeddings(text), dtype="float32")
    except Exception:
        # Fallback hash-based embedder (consistent but less semantic)
        import hashlib
        dim = 384
        embedding = []
        for seed in range(dim // 32):
            hash_input = f"{text}:{seed}".encode('utf-8')
            hash_digest = hashlib.md5(hash_input).hexdigest()
            for i in range(0, 32, 2):
                byte_val = int(hash_digest[i:i+2], 16)
                embedding.append((byte_val / 127.5) - 1.0)
        vec = np.array(embedding[:dim], dtype="float32")
    
    # Normalize for cosine similarity
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

@dataclass
class Minister:
    """
    A Minister is a role with a portfolio. Backend IDs stay internal.
    """
    title: str
    model_id: str
    role_description: str
    capabilities: List[str]
    metabolic_cost: str  # "micro", "low", "medium", "high", "extreme"
    embedding: np.ndarray = field(default_factory=lambda: np.zeros(384))

@dataclass
class Government:
    """
    Role-first cabinet. Only the President stores backend IDs; others are ephemeral.
    """
    president: Minister
    cabinet: Dict[str, Minister] = field(default_factory=dict)
    confidence_threshold: float = 0.6  # Falling back to President if similarity is low

    @classmethod
    def form_cabinet(cls) -> "Government":
        """
        Build an ephemeral cabinet with pre-calculated semantic signatures.
        """
        president = Minister(
            title="President",
            model_id="gpia-master:latest",
            role_description="Sovereign intent, policy, and final veto.",
            capabilities=["sovereign", "arbiter", "intent", "veto"],
            metabolic_cost="low",
        )
        president.embedding = _get_embedding_vector(f"{president.title} {president.role_description} {' '.join(president.capabilities)}")
        
        gov = cls(president=president)

        # Cabinet Portfolios
        ministers = [
            Minister(
                title="Prime Minister (Reason)",
                model_id="gpia-codegemma:latest",
                role_description="Low-memory logic, routine planning, and context expansion.",
                capabilities=["planning", "logic", "expansion", "routine"],
                metabolic_cost="micro",
            ),
            Minister(
                title="Chief Strategist",
                model_id="gpia-deepseek-r1:latest",
                role_description="High-rigor reasoning, deep decomposition, and complex strategy.",
                capabilities=["cot", "strategy", "complex_logic", "rigor"],
                metabolic_cost="medium",
            ),
            Minister(
                title="Minister of Constitution",
                model_id="gpia-gpt-oss:20b",
                role_description="Deep synthesis, long-context reasoning, final legal check.",
                capabilities=["dense_synthesis", "longform", "constitution"],
                metabolic_cost="extreme",
            ),
            Minister(
                title="Minister of Mathematics",
                model_id="qwen2-math:7b",
                role_description="High-rigor algebra, formal proofs, and numerical verification.",
                capabilities=["mathematics", "algebra", "proof", "derivation"],
                metabolic_cost="medium",
            ),
            Minister(
                title="Minister of Foreign Affairs",
                model_id="neural-chat:latest",
                role_description="External comms, negotiation, diplomacy, politeness.",
                capabilities=["comms", "email", "diplomacy", "politeness"],
                metabolic_cost="low",
            ),
            Minister(
                title="Minister of Intelligence",
                model_id="nous-hermes:7b",
                role_description="Simulation, red-team, creative scenarios, imagine.",
                capabilities=["simulation", "red_team", "creative"],
                metabolic_cost="low",
            ),
            Minister(
                title="Minister of Truth",
                model_id="gpia-llama3:8b",
                role_description="Fact-check, grounding, and verification.",
                capabilities=["fact_check", "grounding", "baseline"],
                metabolic_cost="medium",
            ),
            Minister(
                title="Minister of Engineering",
                model_id="gpia-codegemma:latest",
                role_description="Code generation, validation, python scripts.",
                capabilities=["code", "python", "json_schema"],
                metabolic_cost="medium",
            ),
            Minister(
                title="Minister of Perception",
                model_id="gpia-llava:latest",
                role_description="Vision, image analysis, visual look see.",
                capabilities=["vision", "ocr", "image"],
                metabolic_cost="low",
            ),
            Minister(
                title="The Archivist",
                model_id="gpia-minilm-l6-v2:latest",
                role_description="Embeddings, vector memory, and context recall.",
                capabilities=["embedding", "vector", "memory"],
                metabolic_cost="micro",
            ),
        ]

        for m in ministers:
            m.embedding = _get_embedding_vector(f"{m.title} {m.role_description} {' '.join(m.capabilities)}")
            gov.appoint(m)

        return gov

    def appoint(self, minister: Minister) -> None:
        self.cabinet[minister.title] = minister

    def convene(self, issue: str) -> Tuple[Minister, float]:
        """
        Select a minister based on embedding similarity + confidence score.
        Returns: (Minister, confidence_score)
        """
        if not issue:
            return self.president, 1.0

        issue_vec = _get_embedding_vector(issue)
        
        best_minister = self.president
        max_similarity = -1.0
        
        # Calculate cosine similarity for each minister in cabinet
        for title, minister in self.cabinet.items():
            similarity = np.dot(issue_vec, minister.embedding)
            if similarity > max_similarity:
                max_similarity = similarity
                best_minister = minister

        return best_minister, max_similarity
