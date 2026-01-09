#!/usr/bin/env python3
"""
Resource Analyzer - Auto-detect available resources and calculate deployment.

Solves: "What if we don't know the resources in Docker?"

Strategy:
1. Detect GPU VRAM (nvidia-smi, rocm, etc.)
2. Detect system RAM
3. Detect CPU cores
4. Calculate model sizes
5. Determine max concurrent students
6. Generate optimized docker-compose configuration
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re


class ResourceAnalyzer:
    """Analyze available system resources and determine deployment strategy."""

    # Model sizes (in GB) - based on actual quantized models
    MODEL_SIZES = {
        "nous-hermes:7b": 4.0,    # Q4_K_M quantization
        "llama2:7b": 3.8,          # Q4_0 quantization
        "mistral:latest": 4.1,     # Q4_K_M quantization
        "deepseek-r1:latest": 8.0, # Larger model
        "qwen:32b": 16.0,          # Very large
    }

    # Per-model overhead (OS buffer, context, etc)
    MODEL_OVERHEAD_GB = 0.5

    # Per-container overhead (Ollama process, etc)
    CONTAINER_OVERHEAD_GB = 0.3

    # Safety margin (never use 100% of available)
    VRAM_SAFETY_MARGIN = 0.15  # Keep 15% free

    def __init__(self):
        """Initialize resource analyzer."""
        self.gpu_vram_gb = 0.0
        self.system_ram_gb = 0.0
        self.cpu_cores = 0
        self.gpu_type = "unknown"
        self.available_vram_gb = 0.0

    def detect_gpu_vram(self) -> Tuple[float, str]:
        """Detect GPU VRAM using nvidia-smi or similar.

        Returns: (vram_in_gb, gpu_type)
        """
        # Try NVIDIA
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,nounits,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                vram_mb = int(result.stdout.strip().split('\n')[0])
                vram_gb = vram_mb / 1024
                return vram_gb, "NVIDIA"
        except Exception:
            pass

        # Try AMD ROCm
        try:
            result = subprocess.run(
                ["rocm-smi", "--showmeminfo"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse ROCm output
                for line in result.stdout.split('\n'):
                    if "VRAM Total" in line:
                        match = re.search(r'(\d+)\s*MB', line)
                        if match:
                            vram_mb = int(match.group(1))
                            return vram_mb / 1024, "AMD"
        except Exception:
            pass

        # Fallback: check environment variables
        if "CUDA_VISIBLE_DEVICES" in sys.argv:
            # Assume RTX 4070 Super (12GB) as default
            return 12.0, "Unknown (CUDA_VISIBLE_DEVICES set)"

        return 0.0, "No GPU detected"

    def detect_system_ram(self) -> float:
        """Detect total system RAM in GB."""
        try:
            import psutil
            return psutil.virtual_memory().total / (1024 ** 3)
        except ImportError:
            # Fallback: try /proc/meminfo
            try:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            kb = int(line.split()[1])
                            return kb / (1024 ** 2)
            except:
                pass
        return 0.0

    def detect_cpu_cores(self) -> int:
        """Detect number of CPU cores."""
        try:
            import os
            return os.cpu_count() or 4
        except:
            return 4

    def analyze(self) -> Dict:
        """Perform full resource analysis.

        Returns: {
            "gpu_vram_gb": float,
            "gpu_type": str,
            "available_vram_gb": float,
            "system_ram_gb": float,
            "cpu_cores": int,
            "max_concurrent_models": int,
            "deployment_strategy": str,
            "recommended_models": List[str],
            "reasoning": str
        }
        """
        # Detect resources
        self.gpu_vram_gb, self.gpu_type = self.detect_gpu_vram()
        self.system_ram_gb = self.detect_system_ram()
        self.cpu_cores = self.detect_cpu_cores()

        # Calculate available VRAM (apply safety margin)
        self.available_vram_gb = self.gpu_vram_gb * (1 - self.VRAM_SAFETY_MARGIN)

        # Determine deployment strategy
        max_concurrent = self._calculate_max_concurrent()
        strategy = self._determine_strategy(max_concurrent)
        recommended_models = self._select_models(max_concurrent)

        result = {
            "gpu_vram_gb": self.gpu_vram_gb,
            "gpu_type": self.gpu_type,
            "available_vram_gb": self.available_vram_gb,
            "system_ram_gb": self.system_ram_gb,
            "cpu_cores": self.cpu_cores,
            "max_concurrent_models": max_concurrent,
            "deployment_strategy": strategy,
            "recommended_models": recommended_models,
            "reasoning": self._generate_reasoning(max_concurrent, strategy)
        }

        return result

    def _calculate_max_concurrent(self) -> int:
        """Calculate maximum models that can run concurrently.

        Each model needs: model_size + overhead + container_overhead
        """
        if self.gpu_vram_gb == 0:
            return 0

        # Calculate VRAM needed per model (worst case: biggest model)
        max_model_size = max(self.MODEL_SIZES.values())
        per_model_vram = max_model_size + self.MODEL_OVERHEAD_GB + self.CONTAINER_OVERHEAD_GB

        # How many can fit?
        max_concurrent = int(self.available_vram_gb / per_model_vram)
        return max(1, max_concurrent)

    def _determine_strategy(self, max_concurrent: int) -> str:
        """Determine optimal deployment strategy based on resources."""
        if self.gpu_vram_gb == 0:
            return "CPU-ONLY (no GPU detected)"

        if max_concurrent >= 6:
            return "PARALLEL (6 concurrent containers - homogeneous flow)"
        elif max_concurrent >= 3:
            return "BATCHED (groups of 2-3, sequential batches)"
        elif max_concurrent >= 1:
            return "SEQUENTIAL (1 at a time, models load/unload)"
        else:
            return "INSUFFICIENT RESOURCES"

    def _select_models(self, max_concurrent: int) -> List[str]:
        """Select which models to use based on available resources."""
        if max_concurrent == 0:
            return []

        # Prefer smaller models when constrained
        sorted_models = sorted(
            self.MODEL_SIZES.items(),
            key=lambda x: x[1]  # Sort by size (smallest first)
        )

        selected = []
        total_vram = 0

        for model_name, size in sorted_models:
            per_model = size + self.MODEL_OVERHEAD_GB + self.CONTAINER_OVERHEAD_GB
            if total_vram + per_model <= self.available_vram_gb:
                selected.append(model_name)
                total_vram += per_model
                if len(selected) >= max_concurrent:
                    break

        return selected

    def _generate_reasoning(self, max_concurrent: int, strategy: str) -> str:
        """Generate human-readable reasoning for the deployment."""
        lines = [
            f"System Analysis:",
            f"  GPU: {self.gpu_type} with {self.gpu_vram_gb:.1f} GB VRAM",
            f"  Available (after {int(self.VRAM_SAFETY_MARGIN*100)}% safety margin): {self.available_vram_gb:.1f} GB",
            f"  System RAM: {self.system_ram_gb:.1f} GB",
            f"  CPU: {self.cpu_cores} cores",
            f"",
            f"Deployment Calculation:",
        ]

        if self.gpu_vram_gb > 0:
            max_model = max(self.MODEL_SIZES.values())
            per_model = max_model + self.MODEL_OVERHEAD_GB + self.CONTAINER_OVERHEAD_GB
            lines.append(f"  Largest model size: {max_model:.1f} GB")
            lines.append(f"  Per-model overhead: {self.MODEL_OVERHEAD_GB:.1f} GB")
            lines.append(f"  Per-container overhead: {self.CONTAINER_OVERHEAD_GB:.1f} GB")
            lines.append(f"  Total per model: {per_model:.1f} GB")
            lines.append(f"  Max concurrent: {max_concurrent} models")
        else:
            lines.append(f"  No GPU detected - CPU inference only")

        lines.append(f"")
        lines.append(f"Recommended Strategy: {strategy}")

        if strategy == "PARALLEL (6 concurrent containers - homogeneous flow)":
            lines.append(f"  [OPTIMAL] Run all 6 students in parallel")
            lines.append(f"  Result: Perfectly homogeneous flow (no spikes)")
        elif strategy.startswith("BATCHED"):
            lines.append(f"  Run students in groups, sequential batches")
            lines.append(f"  Result: Mostly homogeneous (minimal spike on batch start)")
        elif strategy.startswith("SEQUENTIAL"):
            lines.append(f"  Models load/unload each cycle")
            lines.append(f"  Result: Spikes on model transitions")
        else:
            lines.append(f"  WARNING: Insufficient resources for productive work")

        return "\n".join(lines)

    def print_analysis(self):
        """Print analysis in readable format."""
        result = self.analyze()

        print("\n" + "=" * 80)
        print("RESOURCE ANALYSIS - DOCKER DEPLOYMENT PLANNING")
        print("=" * 80)
        print(result["reasoning"])
        print("\n" + "=" * 80)
        print(f"Recommended deployment: {result['deployment_strategy']}")
        print("=" * 80 + "\n")

        return result

    def generate_docker_compose(self, result: Dict) -> str:
        """Generate docker-compose.yml based on available resources.

        Only creates containers for models that fit in available VRAM.
        """
        max_concurrent = result["max_concurrent_models"]
        strategy = result["deployment_strategy"]

        if "INSUFFICIENT" in strategy:
            return "# ERROR: Insufficient resources for deployment\n"

        # Student assignments (cycle through available models)
        student_models = {
            "alpha": "nous-hermes:7b",
            "beta": "llama2:7b",
            "gamma": "mistral:latest",
            "delta": "nous-hermes:7b",
            "epsilon": "llama2:7b",
            "zeta": "mistral:latest",
        }

        # Filter to only available models
        available_models = set(result["recommended_models"])

        compose = f"""version: '3.8'

# Auto-generated from resource analysis
# Strategy: {strategy}
# Available VRAM: {result['available_vram_gb']:.1f} GB
# Max concurrent: {max_concurrent} models

services:
  orchestrator:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rh-orchestrator
    environment:
      PYTHONUNBUFFERED: "1"
      MAX_CONCURRENT_STUDENTS: "{max_concurrent}"
      DEPLOYMENT_STRATEGY: "{strategy}"
    volumes:
      - ./agents/sessions:/app/agents/sessions
    networks:
      - rh-network
    depends_on:
"""

        # Create student containers only if model is available
        port = 11435
        for student, default_model in student_models.items():
            # Pick a model that's available (or default if available)
            if default_model in available_models:
                model = default_model
            elif available_models:
                model = list(available_models)[0]
            else:
                continue  # Skip this student

            compose += f"      - {student}\n"

        compose += f"""
"""

        # Add container definitions
        port = 11435
        for student, default_model in student_models.items():
            # Pick a model that's available
            if default_model in available_models:
                model = default_model
            elif available_models:
                model = list(available_models)[0]
            else:
                continue

            compose += f"""
  {student}:
    image: ollama/ollama:latest
    container_name: rh-student-{student}
    environment:
      OLLAMA_HOST: "0.0.0.0:11434"
    ports:
      - "{port}:11434"
    volumes:
      - ollama-{student}:/root/.ollama
    command: >
      sh -c "ollama serve &
      sleep 3 &&
      ollama pull {model} &&
      wait"
    networks:
      - rh-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 5s
      timeout: 3s
      retries: 5

"""
            port += 1

        compose += f"""
volumes:
"""
        port = 11435
        for student in student_models.keys():
            compose += f"  ollama-{student}:\n"

        compose += f"""
networks:
  rh-network:
    driver: bridge
"""

        return compose


def main():
    """Main entry point."""
    analyzer = ResourceAnalyzer()
    result = analyzer.print_analysis()

    # Generate docker-compose
    compose_yml = analyzer.generate_docker_compose(result)

    # Save to file
    output_path = Path("docker-compose.rh-auto.yml")
    output_path.write_text(compose_yml)

    print(f"[OK] Generated auto-configured docker-compose file: {output_path}")
    print(f"\nTo deploy:")
    print(f"  docker-compose -f {output_path} up -d")
    print(f"  python orchestrator_multi_student.py --duration 10 --session rh_auto\n")


if __name__ == "__main__":
    main()
