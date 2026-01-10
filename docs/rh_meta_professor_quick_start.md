# RH Meta-Professor: Quick Start Guide

## What Is This?

A **self-improving research organization** that:
1. Starts with 4 seed agents (specialized in quartic, Morse, exponential, spectral methods)
2. Automatically detects research gaps
3. **Synthesizes new specialized agents** as needed (via GPIA)
4. Cross-validates all proposals
5. Learns what works and evolves

**Key Innovation**: Agents are dynamically created for problems no human thought of.

## Quick Start (5 minutes)

```bash
# 1. Make sure OLLAMA is running
ollama serve  # In another terminal

# 2. Launch the system
### 2. Run Initial Session (30 mins)

```bash
python scripts/start_meta_professor.py --duration 30 --session rh_quick_test
```

This will:
1. Initialize the **Meta-Professor** agent.

# 3. Watch output - you'll see:
#    - Seed students initialize
#    - Proposals generated
#    - Cross-validation happening
#    - Gaps detected
#    - NEW students synthesized
#    - Cycle 1, 2, 3... complete
```

## What Happens in 30 Minutes?

### Cycle 1 (Minutes 1-7)
```
Initialization Phase:
  ✓ Create QuarticStudent (quartic potentials)
  ✓ Create MorseStudent (molecular potentials)
  ✓ Create ExponentialStudent (barrier potentials)
  ✓ Create SpectralStudent (spectral methods)

First Research Cycle:
  ✓ 4 students generate proposals
  ✓ Cross-validate 4 proposals
  ✓ Detect gaps
  ✓ Analyze convergence
```

### Cycle 2 (Minutes 8-15)
```
New Student Synthesis:
  ✓ Gap: "Topological properties unexplored"
  → HUNT: What kind of agent is needed?
  → DISSECT: Extract topological reasoning patterns
  → SYNTHESIZE: Generate TopologyStudent code
  ✓ TopologyStudent registered and active

Research with 5 Students:
  ✓ 5 students generate proposals
  ✓ Cross-validate against all peers
  ✓ Detect new gaps
```

### Cycle 3+ (Minutes 16-30)
```
Continuous Improvement:
  ✓ More students synthesized as gaps emerge
  ✓ Cross-validation consensus improving
  ✓ Parameter space coverage expanding
  ✓ Eigenvalue error potentially decreasing
  ✓ Emerging patterns detected
```

## Understanding the Output

```
[MetaProfessor] === INITIALIZATION PHASE ===
  → 4 seed students being created

[MetaProfessor] === RESEARCH CYCLE 1 ===

[MetaProfessor] Phase 1: Student Proposals
  ✓ Collected 4 proposals from 4 students
  - QuarticStudent: "Test V(x) = 0.1x² + 0.05x⁴..."
  - MorseStudent: "Apply Morse potential with dissociation..."
  - etc.

[MetaProfessor] Phase 2: Cross-Validation
  ✓ Validated 4 proposals
  Each proposal gets peer review from all students

[MetaProfessor] Phase 3: Gap Detection
  Gap Report:
    ⚠ Plateauing students: None yet
    ⚠ Blind spots: topology, symmetry
    ✓ Emerging patterns: Quartic convergence promising

[MetaProfessor] Phase 4: Student Synthesis
  ✓ Synthesized 1 new students
    - TopologyStudent (addressed topological gap)

[MetaProfessor] Phase 5: Learning & Feedback
  ✓ Feedback generated and saved
```

## Key Files Generated

### Session Root: `src/agents/rh_meta_research_v1/`

```
├─ meta_professor_final_report.json      Overall results
├─ gap_detection_report.json             Latest gap analysis
├─ cross_validation_report.json          Consensus findings
├─ cycle_1_summary.json                  Cycle 1 results
├─ cycle_2_summary.json                  Cycle 2 results
├─ feedback_cycle_1.txt                  Feedback for next cycle
├─ rh_proposals/                         All student proposals
├─ rh_results/                           Eigenvalue computation results
├─ rh_evaluations/                       Validation records
└─ synthesized_students/
    ├─ topology_student/
    │   ├── manifest.json               Student metadata
    │   └── agent.py                    Executable code
    └─ [other synthesized students...]
```

## Reading the Results

### 1. Final Report
```bash
cat src/agents/rh_meta_research_v1/meta_professor_final_report.json
```

Shows:
- How many cycles completed
- How many students synthesized
- History of synthesis (what gaps triggered what agents)

### 2. Gap Detection Report
```bash
cat src/agents/rh_meta_research_v1/gap_detection_report.json
```

Shows:
- Convergence status per student (improving? plateauing?)
- Parameter coverage (unexplored regions)
- Blind spots (missing mathematical domains)
- Recommendations for new students

### 3. Cross-Validation Report
```bash
cat src/agents/rh_meta_research_v1/cross_validation_report.json
```

Shows:
- How many proposals got HIGH consensus (all agreed)
- How many got MODERATE or LOW consensus
- Where reviewers disagreed (divergent opinions)

### 4. Cycle Summaries
```bash
cat src/agents/rh_meta_research_v1/cycle_2_summary.json
```

Example output:
```json
{
  "cycle": 2,
  "timestamp": "2026-01-03T15:30:00",
  "proposals_generated": 5,
  "validations_completed": 5,
  "students_synthesized": 1,
  "gaps_detected": 3
}
```

## Success Indicators

### ✓ Good Signs
- Students are being synthesized (✓ if >0 in cycle 2+)
- Cross-validation showing consensus on some proposals
- Gap detection finding meaningful opportunities
- New students addressing different problems

### ⚠ Warning Signs
- No student synthesis after 5+ cycles (gap detection not working)
- All students agreeing on everything (no diversity)
- Eigenvalue error not improving (all approaches failing)
- Synthesis creating students with duplicate specializations

## Customization

### Change Duration
```bash
# Run for 2 hours instead of 30 minutes
python start_meta_professor.py --duration 120
```

### Change Session Name
```bash
# Use custom session directory name
python start_meta_professor.py --session rh_long_form_breakthrough
```

### Full Options
```bash
python start_meta_professor.py --help
```

## Common Questions

**Q: What are "synthesized students"?**
A: New agents created dynamically by the system. Unlike the 4 seed students (predefined), synthesized students are generated based on gaps discovered during research.

**Q: How does cross-validation work?**
A: Each student reviews every proposal from their specialty perspective. If 4 students agree proposal X is good, confidence is high. If they disagree, that tension reveals something important.

**Q: What makes a "gap" worth synthesizing a student for?**
A: High priority gaps are:
- Students plateauing (not improving)
- Mathematical domains unexplored (e.g., topology)
- Parameter spaces uncovered
- Reasoning patterns missing

**Q: Can I add my own seed students?**
A: Yes. Modify `MetaProfessor.initialization_phase()` to add more. But synthesis is more powerful—let the system create what it needs.

**Q: Does this actually solve RH?**
A: It's a framework for exploring RH, not a proof engine. Success = finding promising mathematical directions, reducing eigenvalue error, discovering patterns humans missed.

## Integration with Boot

To integrate with your CLI boot system:

```python
# In boot.py or main orchestrator:
elif args.mode == "rh-meta-professor":
    from rh_meta_professor import MetaProfessor

    duration = getattr(args, 'duration', 30)
    meta_prof = MetaProfessor(session_name="rh_integrated")
    meta_prof.run_research_session(duration_minutes=duration)
```

Then run:
```bash
python manage.py server --mode rh-meta-professor --duration 60
```

## Architecture Philosophy

**Agents are fuel. Skills are fire. GPIA is the furnace.**

This system treats student agents as **living researchers** that:
1. Have specialized knowledge (skill)
2. Generate proposals (fuel)
3. Learn from each other (fire)
4. Create new specialists as needed (furnace producing new agents)

## Next Steps

1. **Run the quick start** (30 minutes)
2. **Examine the output files** (understand what's happening)
3. **Read `RH_META_PROFESSOR_INTEGRATION.md`** (full technical details)
4. **Customize for your needs** (add domain-specific logic)
5. **Long-form run** (hours/days for serious research)

## Support

- **Logs**: Check console output (real-time)
- **Reports**: Check JSON files in session directory
- **Code**: `rh_meta_professor.py` (main orchestrator)
- **Synthesis**: `rh_student_synthesizer.py` (agent generation)
- **Gap Detection**: `rh_pattern_gap_detector.py` (analysis)
- **Validation**: `rh_cross_validation_hub.py` (consensus)

---

**Ready?**

```bash
python start_meta_professor.py --duration 30
```

Watch as the system:
1. Initializes seed students
2. Detects research gaps
3. **Synthesizes new specialized agents**
4. Validates proposals across all students
5. Learns and improves each cycle

🚀
