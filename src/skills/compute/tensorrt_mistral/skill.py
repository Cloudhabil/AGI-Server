"""
TensorRT Mistral Skill
======================

Bridges the GPIA kernel to the high-speed Python 3.10 Sidecar running NVIDIA TensorRT-LLM.
"""

from typing import Dict, Any
from skills.base import Skill, SkillMetadata, SkillCategory, SkillResult, SkillContext
from integrations.trt_llm_client import TensorRTClient

class TensorRTMistralSkill(Skill):
    def __init__(self):
        super().__init__()
        self.client = TensorRTClient()

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="compute/tensorrt-mistral",
            name="tensorrt-mistral",
            description="High-speed INT4 inference via NVIDIA TensorRT-LLM.",
            category=SkillCategory.SYSTEM,
            tags=["compute", "speed", "nvidia"]
        )

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        prompt = input_data.get("prompt")
        if not prompt:
            return SkillResult(False, error="No prompt provided.")

        max_tokens = input_data.get("max_tokens", 512)
        temp = input_data.get("temperature", 0.1)

        result = self.client.query(prompt, max_tokens=max_tokens, temperature=temp)
        
        if "[Error]" in result:
            return SkillResult(False, error=result)

        return SkillResult(
            success=True,
            output={"text": result},
            skill_id=self.metadata().id
        )
