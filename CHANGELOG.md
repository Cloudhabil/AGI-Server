# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-01-09
### Added
- **Unified Kernel Substrate**: Formalized integration of all 19 major cognitive and safety systems into a single persistent substrate.
- **Neuronic Router Integration**: Advanced model routing and PASS protocol now power the web interface (`interface.py`).
- **Reflex Mood**: Implemented high-speed deterministic safety responses triggered by hardware stress (VRAM/Thermal).
- **Evaluation Service**: Autonomous cognitive health checking suite (`evals/run_system_v2.py`) integrated into the kernel.
- **Human-vs-AI Protocol**: Formal benchmark suite based on the ASI Capability Ladder.
- **Alpha Agent**: Dedicated student agent module (`alpha/agent.py`) for autonomous learning.

### Changed
- **Substrate Connectivity**: Replaced kernel stubs with production-ready services (Ledger, Perception, Telemetry).
- **Livelink API**: Refactored generated endpoints to `APIRouter` for stable frontend-backend integration.
- **Sovereign Alignment**: Enforced "Survival of the Substrate" as the primary ethical law in the `PhilosophicalGovernor`.

### Fixed
- **V-Nand Resonance**: Restored the 8x8x8 voxel resonance gate logic (0.95 threshold) in the Dense State Learner.
- **Circular Dependencies**: Resolved critical import loops preventing server startup.

## [0.1.0] - 2025-12-30
### Initial Release
- Multi-agent orchestration and Task Bus.
- Integrated KB and basic cognitive skills.
- Initial support for local LLMs via Ollama.