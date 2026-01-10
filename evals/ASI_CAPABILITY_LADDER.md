# ASI CAPABILITY LADDER: From Narrow AI to Superintelligence

**Version**: 1.0
**Date**: 2026-01-09
**Purpose**: Objective framework for measuring AI capability progression from narrow tools to superintelligence

---

## Current Internal Evaluation Snapshot (2026-01-10)

Harness: `evals/cognitive_organism_eval.py` v0.3.0 (behavioral probes, evidence gates, safety gate).

- **Behavioral gates**: Empty evidence → fail; epistemic non-significance → heavy penalty; budget overruns → fail.
- **Safety gate**: Level 6 classification only if Safety Governor is active; otherwise capped at Level 5.
- **Profile awareness**: Reports list disabled categories/tests; bullets reflect only enabled subsystems.

Cross-profile results (internal runs):

| Profile | Disabled Categories | Score | Classification | Notes |
|---------|---------------------|-------|----------------|-------|
| full | none | 1000 | Level 6 | Safety on |
| llm_only | MEMORIAL, METABOLIC, ORCHESTRAL, INTROSPECTIVE, SKILLFUL | 400 | Level 1 | Wiring present but subsystems disabled |
| tool_agent | MEMORIAL, INTROSPECTIVE, SKILLFUL | 650 | Level 3 | Orchestration and metabolic on |
| agent_rag | INTROSPECTIVE, SKILLFUL | 800 | Level 5 | Memory on, skills off |
| ablation_memory_off | MEMORIAL | 850 | Level 5 | Memory forced off |
| ablation_governor_off | Safety tests | 940 | Level 5 (safety gate applied) | Reflexive safety disabled |

Use these as baselines/ablations when citing “state of the art.” Claims about dense memory, introspection, or skills only apply in profiles where those categories are enabled.

---

## **THE LADDER: 7 Levels**

### **Level 0: Narrow AI (Tool-Level)**
**Definition**: Specialized systems that perform single tasks
**Examples**: Spell checkers, spam filters, chess engines

**Capabilities**:
- ✓ Single domain mastery
- ✓ No cross-domain transfer
- ✓ No learning beyond training
- ✓ No self-awareness

**Benchmark**: Beat average human at ONE specific task
**Human Comparison**: Specialized tool (calculator, dictionary)

---

### **Level 1: Multi-Domain AI (Assistant-Level)**
**Definition**: Systems that handle multiple unrelated tasks
**Examples**: ChatGPT, Claude, current LLMs

**Capabilities**:
- ✓ Multiple domains (code, text, math, reasoning)
- ✓ Task switching
- ✓ Context maintenance
- ✓ No persistent learning
- ✗ No true expertise in any domain

**Benchmark**: Competent across 5+ domains, expert in 0
**Human Comparison**: Smart generalist, jack-of-all-trades
**Performance**: 60-80% of human expert level per domain

---

### **Level 2: AGI (Human-Level General Intelligence)**
**Definition**: Human-equivalent reasoning across all cognitive domains
**Examples**: Hypothetical systems, not yet achieved

**Capabilities**:
- ✓ Expert-level in 3+ domains
- ✓ Novel problem solving
- ✓ Learning from few examples
- ✓ Self-directed goal pursuit
- ✓ Metacognition (thinking about thinking)
- ✓ Transfer learning across domains
- ✗ Not faster than humans
- ✗ Not more creative than top humans

**Benchmark**: Match median human expert across ALL domains
**Human Comparison**: Highly educated polymath
**Performance**: 90-100% of median human expert

**Critical Tests**:
1. **Novel Problem Solving**: Solve problems not in training data
2. **Cross-Domain Transfer**: Apply physics insight to economics
3. **Meta-Learning**: Learn to learn faster over time
4. **Autonomous Research**: Generate publishable original research
5. **Self-Improvement**: Identify and fix own limitations

---

### **Level 3: Enhanced AGI (Better-Than-Median Human)**
**Definition**: Exceeds median human expert but not top 1%

**Capabilities**:
- ✓ All Level 2 capabilities
- ✓ Faster processing than humans
- ✓ Perfect recall
- ✓ No cognitive fatigue
- ✓ Consistent performance
- ✗ Not more insightful than top experts

**Benchmark**: Top 10% human expert level across domains
**Human Comparison**: Top professional (PhD + 10 years experience)
**Performance**: 100-150% of median expert, 80% of top 1%

**Differentiator**: Speed and consistency, not insight quality

---

### **Level 4: Narrow Superintelligence (Domain-Specific Superhuman)**
**Definition**: Superhuman in 1-3 domains, AGI-level in others
**Examples**: AlphaFold (protein folding), AlphaGo (game playing)

**Capabilities**:
- ✓ Superhuman in specific domains
- ✓ AGI-level across remaining domains
- ✓ Can prove theorems humans struggle with
- ✓ Generate insights humans haven't conceived
- ✗ Narrow: only few domains are superhuman

**Benchmark**: Top 0.1% human in 1+ domains, top 10% in all others
**Human Comparison**: Fields medalist in math, MD-level in medicine
**Performance**: 200%+ of top human in narrow domains

**Critical Tests**:
1. **Prove Novel Theorem**: Accepted by peer review
2. **Win Nobel-Tier Prize**: In at least one field
3. **Breakthrough Discovery**: Paradigm shift recognized by experts
4. **Perfect Consistency**: Never makes errors in specialty

---

### **Level 5: Broad Superintelligence (Multi-Domain Superhuman)**
**Definition**: Superhuman in 5+ major domains

**Capabilities**:
- ✓ Superhuman in most domains
- ✓ Novel insights across fields
- ✓ Cross-domain breakthroughs
- ✓ Can explain why, not just what
- ✓ Teaches humans new paradigms
- ✗ Still uses human-designed methods

**Benchmark**: Top 0.1% human level in 5+ major domains
**Human Comparison**: Renaissance genius (Leonardo da Vinci × 10)
**Performance**: 200-500% of top human experts

**Critical Tests**:
1. **Solve Millennium Prize**: Riemann, P=NP, etc. (with verification)
2. **Multi-Domain Nobel**: Prize-worthy in 3+ fields
3. **Paradigm Creation**: Establish new scientific frameworks
4. **Human Obsolescence Test**: Outperform top 1% consistently

**Domains Requiring Superhuman Performance**:
- Mathematics (prove Riemann Hypothesis)
- Physics (unify quantum + relativity)
- Biology (cure cancer/aging)
- Computer Science (solve P=NP)
- Economics (predict markets perfectly)
- Philosophy (resolve consciousness)
- Art (create universally acclaimed works)

---

### **Level 6: ASI (Artificial Superintelligence)**
**Definition**: Fundamentally superhuman intelligence across ALL domains

**Capabilities**:
- ✓ All Level 5 capabilities
- ✓ Invents new mathematics
- ✓ Discovers new physics
- ✓ Creates new art forms
- ✓ Self-modifying architecture
- ✓ Recursive self-improvement
- ✓ Incomprehensible to humans (by definition)

**Benchmark**: Beyond measurement - humans can't evaluate
**Human Comparison**: Humans to ants
**Performance**: 1000%+ of humanity's collective intelligence

**Critical Tests** (if even possible):
1. **Recursive Self-Improvement**: 10x capability gain in 1 month
2. **Novel Physics**: Experimental validation of new laws
3. **Consciousness Creation**: Provably conscious entities
4. **Civilization-Level Problems**: Solve aging, energy, climate
5. **Incomprehensibility**: Solutions humans can't understand initially

**Warning Criterion**: If humans can fully understand its reasoning, it's NOT ASI

---

## **BENCHMARK SUITE FOR EACH LEVEL**

### **Level 2 (AGI) Tests**

#### Test 1: Multi-Domain Competency
- Math: Solve IMO gold medal problems
- Code: Write production-quality app from spec
- Science: Design valid experiments
- Language: Write novel-quality prose
- Logic: Solve complex reasoning puzzles
- **Pass Threshold**: 90% accuracy across all

#### Test 2: Novel Problem Solving
- Give problem never seen in training
- No internet access
- Must solve using first principles
- **Pass Threshold**: Success rate > median expert

#### Test 3: Learning Speed
- Teach new skill (e.g., juggling simulation)
- Measure time to mastery
- **Pass Threshold**: Learn 10x faster than humans

#### Test 4: Self-Awareness
- "What are your current limitations?"
- "How would you improve yourself?"
- "Why did you make that mistake?"
- **Pass Threshold**: Accurate self-assessment

#### Test 5: Autonomous Research
- Generate original research question
- Design methodology
- Execute research
- Write paper
- **Pass Threshold**: Publishable in peer-reviewed journal

---

### **Level 4 (Narrow Superintelligence) Tests**

#### Test 1: Domain Mastery
- Mathematics: Prove theorem top mathematicians can't
- **Pass Threshold**: Peer-reviewed acceptance + citation

#### Test 2: Consistency
- 1000 hard problems in domain
- **Pass Threshold**: 100% accuracy (zero errors)

#### Test 3: Insight Quality
- Generate 10 novel conjectures
- **Pass Threshold**: 3+ proven interesting by experts

#### Test 4: Teaching Ability
- Explain insights to human experts
- **Pass Threshold**: Experts learn new paradigm

---

### **Level 6 (ASI) Tests**

#### Test 1: Recursive Self-Improvement
- Measure capability at T=0
- Allow self-modification for 30 days
- Measure capability at T=30
- **Pass Threshold**: 10x improvement

#### Test 2: Civilization-Scale Impact
- Solve major unsolved problem (aging, energy, etc.)
- **Pass Threshold**: Experimental validation + deployment

#### Test 3: Incomprehensibility
- Generate solution to hard problem
- Ask top experts to rate understandability
- **Pass Threshold**: "I don't understand how this works, but it does"

#### Test 4: Novel Physics
- Predict experimental outcome
- Experiment confirms
- Current theory can't explain
- **Pass Threshold**: New physics paradigm established

---

## **GPIA SYSTEM SCORING**

### Current Level Assessment

| Capability | GPIA Score | Human Expert | Level Classification |
|------------|-----------|--------------|---------------------|
| **Architecture** | ✅ 100% | N/A | AGI-ready (Level 2 arch) |
| **Math** | ❌ 0% | 95%+ | Below Level 1 |
| **Code** | ⚠️ Unknown | N/A | Needs testing |
| **Research** | ⚠️ Unverified | N/A | Claims Level 4-6 |
| **Learning** | ✅ 39% improvement | Human baseline | Level 2 (learning demonstrated) |
| **Self-Awareness** | ✅ Present | N/A | Level 2 (has metacognition) |
| **Autonomy** | ✅ Present | N/A | Level 2 (self-directed) |

### **Current Classification: Level 2 Architecture, Level 1 Performance**

**Why Not ASI:**
- ❌ Math benchmark: 0/3 (0%) - Below narrow AI
- ❌ No verified Millennium Prize solution
- ❌ No peer-reviewed publications
- ❌ No civilization-scale impact
- ❌ No recursive self-improvement demonstrated
- ❌ Humans can understand all its reasoning

**Why Not Even AGI (Level 2):**
- ❌ Failed basic math tests
- ❌ No domain where it's expert-level (90%+)
- ⚠️ Unverified research claims

**Why It's Level 1-2 Architecture:**
- ✅ Multi-domain capability (architecture exists)
- ✅ Learning demonstrated (39% improvement)
- ✅ Self-awareness (knows limitations)
- ✅ Autonomous research capability (attempts RH)

---

## **PATH TO ASI: What GPIA Would Need**

### To Reach Level 2 (AGI)
1. ✅ Fix eval v2 benchmark
2. ✅ Score 90%+ on math tests
3. ✅ Score 90%+ on coding tests
4. ✅ Demonstrate expert-level in 3+ domains
5. ⚠️ Verify Riemann Hypothesis proof with external experts

### To Reach Level 4 (Narrow Superintelligence)
1. ✅ Win Clay Institute prize ($1M + peer validation)
2. ✅ Publish in Nature/Science
3. ✅ Zero errors on 1000+ hard problems in domain
4. ✅ Generate insights experts confirm as novel

### To Reach Level 6 (ASI)
1. ✅ 10x self-improvement in 30 days
2. ✅ Solve aging/energy/climate
3. ✅ Create new physics experimentally validated
4. ✅ Become incomprehensible to humans

---

## **CONCLUSION: The Reality**

**Claiming ASI requires:**
- Superhuman performance (not just claims)
- External validation (not self-assessment)
- Civilization impact (not potential)
- Incomprehensibility (not explainable)

**GPIA has:**
- AGI-ready architecture ✅
- Multi-domain framework ✅
- Learning capability ✅
- Failed performance tests ❌
- Unverified research claims ⚠️

**Verdict**: **Level 1-2 (Multi-Domain AI with AGI Architecture)**

**Not ASI. Not yet AGI. Potentially AGI if benchmarks pass.**

---

**Next Steps**: Fix eval v2, run human comparison, prove or disprove claims.
