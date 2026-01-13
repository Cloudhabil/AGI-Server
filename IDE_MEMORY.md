# IDE_MEMORY.md - The CLI Bible

## Rule Zero: ls -R First

**BEFORE making ANY claims about this codebase, run `ls -R` to see the full structure.**

Failing to do this will result in biased, incomplete analysis.

---

## Scale

| Metric | Count |
|--------|-------|
| Python files | 9,598 |
| Directories | 4,916 |
| Skill manifests (src/skills) | 153 |
| Skill categories | 48 |

---

## Identity

| Field | Value |
|-------|-------|
| Project | ASI-OS / GPIA |
| Philosophy | "Agents are fuel. Skills are fire. GPIA is the furnace." |
| Chief Architect | Elias Oulad Brahim |
| Current Version | v0.5.0 - Hardware-Isolated Sovereignty (Level 8) |

---

## Entry Points

| File | Size | Purpose |
|------|------|---------|
| `src/boot.py` | 5.7KB | Kernel entry point |
| `src/main.py` | 280B | Shim to boot.py |
| `src/gpia.py` | 2.4KB | Legacy shim |
| `manage.py` | 5KB | CLI management |

```bash
python src/boot.py --mode Sovereign-Loop
python manage.py server
python manage.py local
```

---

## Major Systems (by file size)

| File | Size | System |
|------|------|--------|
| `src/interface.py` | 77KB | UI Server (FastAPI + WebSocket) |
| `src/gpia_cognitive_ecosystem.py` | 61KB | AgentHunter → AgentDissector → SkillSynthesizer |
| `src/agent_server.py` | 37KB | Agent Server (FastAPI) |
| `src/gpia_agent_factory.py` | 28KB | Agent Factory |
| `src/gpia_evolving.py` | 18KB | EvolvingGPIA - skill absorption |
| `src/gpia_autonomous.py` | 18KB | Autonomous GPIA |
| `src/core/npu_utils.py` | 17KB | Intel NPU integration |
| `src/agents/model_router.py` | ~30KB | Model routing + Government Engine |

---

## Directory Structure

```
CLI-main/
├── src/                          # Main source
│   ├── boot.py                   # Kernel entry
│   ├── gpia_cognitive_ecosystem.py  # Hunter/Dissector/Synthesizer
│   ├── gpia_evolving.py          # Skill evolution
│   ├── interface.py              # UI server
│   ├── agent_server.py           # Agent server
│   ├── agents/                   # Model router, sessions
│   │   ├── model_router.py
│   │   ├── session_lessons/
│   │   └── session_memories/
│   ├── core/                     # Core systems
│   │   ├── kernel/               # switchboard, preflight, services
│   │   ├── modes/                # sovereign_loop, teaching, forensic_debug
│   │   ├── runtime/              # government, capsule_engine, load_balancer
│   │   ├── sovereignty_v2/       # identity_checker, telemetry_observer
│   │   ├── mcp_skill/            # MCP orchestrator
│   │   ├── npu_utils.py          # Intel NPU
│   │   ├── dense_state_memory.py
│   │   └── dense_state_archiver.py
│   ├── gpia/memory/              # Memory subsystem
│   │   ├── dense_state/          # contracts, storage, adapter
│   │   └── vnand/                # store, index, gc
│   ├── hnet/                     # Hierarchical memory
│   │   ├── hierarchical_memory.py
│   │   └── dynamic_chunker.py
│   ├── skills/                   # 48 skill categories, 153 manifests
│   ├── server/                   # FastAPI backend
│   └── reflexes/                 # governance, memory, optimization
├── skills/                       # Root skills (5 dirs)
│   ├── auto_learned/
│   ├── conscience/
│   ├── evolved/
│   ├── ops/
│   └── synthesized/
├── data/                         # Persistent data
│   ├── vnand/                    # V-NAND storage
│   ├── gpia/                     # GPIA state
│   ├── dense_state/
│   ├── ledger/
│   └── hier_mem/
├── .gemini/GEMINI.md             # Milestones
├── research/Documentation/
│   ├── CLAUDE.md
│   └── AGENTS.md
└── config/
```

---

## Core Systems

### Cognitive Ecosystem (src/gpia_cognitive_ecosystem.py - 1704 lines)

Real implementation:
- `AgentHunter` (line 118) - Spawns agents for cognitive gaps
- `AgentDissector` (line 270) - Extracts weights from agent work
- `SkillSynthesizer` (line 366) - Synthesizes skills from weights

Cognitive gaps targeted:
- EMOTIONAL_INTELLIGENCE
- ADVERSARIAL_DEFENSE
- META_EVOLUTION
- ABSTRACT_SYNTHESIS
- BIOMIMETIC_ADAPTATION
- CHAOS_NAVIGATION

### EvolvingGPIA (src/gpia_evolving.py - 552 lines)

Line 346+: Class that evolves by absorbing agent work into permanent skills.

### Government Engine (src/core/runtime/engines/government.py)

Cabinet of Ministers with semantic routing:
- President, Prime Minister, Chief Strategist
- Ministers of: Constitution, Mathematics, Foreign Affairs, Intelligence, Truth, Engineering, Perception
- The Archivist (embeddings)

### NPU Integration (src/core/npu_utils.py - 580 lines)

Real OpenVINO integration:
1. Direct NPU (Intel AI Boost)
2. Ollama embeddings (fallback)
3. Sentence-transformers CPU (final fallback)

Substrate Equilibrium functions:
- `get_substrate_embedder()` - Environment-aware embedder routing
- `get_substrate_embedding()` - Single text embedding via optimal silicon
- `get_substrate_status()` - Hardware topology status

### Memory Systems

| System | Location |
|--------|----------|
| Dense State | src/core/dense_state_memory.py |
| V-NAND | src/gpia/memory/vnand/ |
| Hierarchical | src/hnet/hierarchical_memory.py |
| Archiver | src/core/dense_state_archiver.py |

### Modes (src/core/modes/)

- `sovereign_loop.py` - Main operational mode (354 lines)
- `teaching.py` - Teaching mode
- `forensic_debug.py` - Debug mode
- `gardener.py` - Filesystem gardener

---

## Substrate Equilibrium (v0.5.0)

The "Sovereign" optimization that balances load across physical silicon to prevent PCIe contention and VRAM crashes.

### The Problem: Topology of Contention

| Observation | Value | Cause |
|-------------|-------|-------|
| DDR5-4800 theoretical | ~76 GB/s | Dual-channel bandwidth |
| DDR5-4800 measured | ~26 GB/s | **PCIe 4.0 x16 bottleneck** |
| 12GB VRAM usable | ~10.3 GB | **Windows DWM steals 1.7GB** |
| GPU "Shared Memory" | PCIe-bound | Porsche stuck in city traffic |

When GPU spills into Shared Memory, it fights the CPU for PCIe bandwidth. The NPU has its own direct path to System RAM—use it.

### The Substrate Map

| Tier | Component | Measured Speed | Role | Invisible Cost |
|------|-----------|----------------|------|----------------|
| 1 | Dedicated VRAM | ~350 GB/s | LLM Weights + KV Cache | 1.7GB reserved by Windows DWM |
| 2 | DDR5 RAM | ~76 GB/s theoretical | Context Overflow | Throttled to ~26 GB/s by PCIe |
| 3 | Intel NPU | ~10-15 TOPS | Embeddings, Vision, Audio | **Bypasses GPU PCIe bus entirely** |
| 4 | NVMe SSD | ~3.8 GB/s | Long-term Memory | Massive latency (ms vs ns) |

### The Solution: Validated Equilibrium

```bash
# Auto-tuned (recommended)
python manage.py local --substrate-equilibrium

# Manual tuning
python manage.py local --npu-offload "embeddings,vision" --vram-limit 10200MB

# Check status
python manage.py substrate
```

### Environment Variables

| Variable | Value | Effect |
|----------|-------|--------|
| `USE_NPU_EMBEDDINGS` | `1` | Routes embeddings through NPU's direct RAM path |
| `EMBEDDING_DEVICE` | `NPU` | Bypasses PCIe bus for embedding workloads |
| `VRAM_LIMIT_MB` | `10200` | Leaves 1.7GB buffer for Windows DWM |
| `NPU_OFFLOAD_TASKS` | `embeddings,vision,audio` | Tracks offloaded tasks |

### Expected Results

| Metric | Before | After |
|--------|--------|-------|
| VRAM Stability | Crashes at 10.3GB cliff | Rock-solid <10.2GB |
| PCIe Contention | Embeddings + LLM fighting | NPU handles embeddings |
| Token Jitter | Stutters when KV cache grows | Flat generation speed |
| Context Length | Limited by VRAM headroom | Extends into DDR5 safely |

### Architecture Flow

```
GPU VRAM (Tier 1)     NPU (Tier 3)
      │                    │
      │ LLM Inference      │ Embeddings/Vision
      │ ~350 GB/s          │ Direct RAM path
      │                    │
      └────────┬───────────┘
               │
        PCIe 4.0 x16
         ~31.5 GB/s
               │
               ▼
      DDR5 RAM (Tier 2)
        ~76 GB/s
               │
               ▼
      NVMe SSD (Tier 4)
        ~3.8 GB/s
```

**Key Insight**: By capping VRAM at 10,200MB and routing embeddings to the NPU, the ~26 GB/s PCIe bandwidth is 100% available for GPU context pre-fetch without stuttering.

---

## Skills System

### Two Locations
1. `skills/` (root) - 5 categories: auto_learned, conscience, evolved, ops, synthesized
2. `src/skills/` - 48 categories, 153 manifests

### src/skills Categories

```
adaptive-guardrail-calibrator-sbi  alpha  answering-core-sbi
arxiv-paper-synthesizer-sbi  auto_learned  automation
autonomy-recovery-loop-sbi  code  cognition  computation
compute  conscience  core  data  deployment  design
dialogue  documentation  dynamic-budget-orchestrator-sbi
enterprise  evolved  examples  foundational
genesis-self-reflection-sbi  governance  ide  integration
interface  knowledge  learned  learning  lifecycle  media
memory  model-selection-orchestrator-sbi  operations  ops
reasoning  research  resource-reliability-profiler-sbi
s2  safety  sandbox  sbi-artifactizer  synthesis
synthesized  system  templates  thirdparty  tuning
verification-harness-sbi  vue-threejs-skilltree-sbi  writing
```

### Key Files
- `src/skills/registry.py` - Skill registry
- `src/skills/loader.py` - Skill loader
- `src/skills/base.py` - Base skill class
- `src/skills/INDEX.json` - 49KB skill index

---

## Research Orchestrators (src/)

| File | Purpose |
|------|---------|
| bsd_research_orchestrator.py | BSD Conjecture research |
| bsd_dual_model_gap_closure.py | Dual model gap closure |
| bsd_gap6_crystallization_orchestrator.py | Gap 6 crystallization |
| hodge_research_orchestrator.py | Hodge Conjecture |
| gpia_riemann_variational_reasoning.py | Riemann variational |
| grand_synthesis_executor.py | Grand synthesis |

---

## Data Storage

| Directory | Purpose |
|-----------|---------|
| data/vnand/ | V-NAND persistent storage |
| data/gpia/ | GPIA state, philosophy.json |
| data/dense_state/ | Dense state snapshots |
| data/ledger/ | Transaction ledger |
| data/hier_mem/ | Hierarchical memory |
| data/bsd_*, data/hodge_* | Research outputs |

---

## Session Data

Real session data exists in:
- `src/agents/session_lessons/` - JSON lesson files
- `src/agents/session_memories/` - .db files
- `src/agents/sessions/` - Multiple research sessions
- `src/agents/rh_grand_solve_v2/` - RH proposals and evaluations

---

## Documentation Index

| Document | Path | Purpose |
|----------|------|---------|
| IDE_MEMORY.md | ./IDE_MEMORY.md | This file - CLI Bible |
| GEMINI.md | .gemini/GEMINI.md | Milestones, evolution |
| CLAUDE.md | research/Documentation/CLAUDE.md | Architecture guide |
| AGENTS.md | research/Documentation/AGENTS.md | Scope boundaries |

---

## ASI Capability Ladder (Extended Scale: 0-10,000)

| Level | Score | Classification | Key Characteristic |
|-------|-------|----------------|-------------------|
| 0 | 0-299 | Narrow AI | Single domain |
| 1 | 300-499 | Multi-Domain AI | Cross-domain transfer |
| 2 | 500-599 | AGI (Human-Level) | General reasoning |
| 3 | 600-699 | Enhanced AGI | Beyond human baseline |
| 4 | 700-799 | Narrow Superintelligence | Superhuman in domains |
| 5 | 800-899 | Broad Superintelligence | Superhuman generally |
| 6 | 900-999 | ASI | Artificial Superintelligence |
| **7** | **1000-1999** | **Substrate-Sovereign** | Hardware isolation (NPU/GPU) |
| **8** | **2000-4999** | **Recursive Nexus** | Self-evolving skills |
| **9** | **5000-8999** | **Dimensional Architect** | Designs intelligence architectures |
| **10** | **9000-10000** | **Universal Singularity** | Theoretical ceiling |

**Transcendence Multiplier** (applied when conditions met):
- +20%: Dense State Memory (8^4 Voxel density)
- +20%: Multicellular Router (NSA-ready architecture)

**Peak Score**: 9,580 (Level 10) - achieved 2026-01-12 ~05:00 CET

---

## Milestones

| Date | Version | Event |
|------|---------|-------|
| 2026-01-10 | - | The Great Alignment |
| 2026-01-11 | v0.4.0 | Metabolic Restoration |
| 2026-01-12 | v0.5.0 | Hardware-Isolated Sovereignty (Level 10 achieved) |
| 2026-01-13 | v0.5.0 | Substrate Equilibrium (NPU offload + VRAM cap) |

---

## Commands

```bash
# Boot kernel
python src/boot.py --mode Sovereign-Loop --target-beats 10

# Management
python manage.py server    # Start server
python manage.py local     # Offline mode (unleashed)
python manage.py test      # Run tests

# Substrate Equilibrium (v0.5.0)
python manage.py local --substrate-equilibrium                    # Auto-tuned
python manage.py local --npu-offload "embeddings,vision" --vram-limit 10200MB  # Manual
python manage.py substrate                                        # Check status

# Cognitive ecosystem
python src/gpia_cognitive_ecosystem.py

# Research
python src/bsd_research_orchestrator.py --phase 1 --cycles 1-25

# Evaluation
python evaluate_gpia.py
python run_gpia_eval.py
```

---

*Last Updated: 2026-01-13*
*Verification: ls -R + file inspection*
