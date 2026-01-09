# PHASE 2 INFRASTRUCTURE - TASK BRIEFING FOR GPIA

**Status**: Ready for autonomous execution
**Beat Range**: 150-300 (25 baseline + 5 refinement)
**Goal**: Build legitimate proof verification & expert review infrastructure

---

## PHASE 2 BASELINE: BEATS 150-275 (25 Cycles)

### Cycles 1-5 (Beats 150-175): Design 3-Tier Verification System

**Cycle 1 (Beats 150-155)**: Define Verification Tiers
- [ ] Tier 1: Logical Consistency Check (automated, no human required)
  - All cited theorems exist in literature
  - All hypotheses explicitly stated
  - No circular logic
  - All functions well-defined on domains
- [ ] Tier 2: Expert Mathematician Review (manual, required)
  - Peer review by 2-3 specialists
  - Assessment: new theorem? known result? partial? exploratory?
  - Identification of gaps
  - Rigorous feedback
- [ ] Tier 3: Publication Gate (policy-based)
  - arXiv preprint (low barrier)
  - Peer-reviewed journals (medium barrier)
  - Clay Mathematics Institute (high barrier—only for real advances)

**Cycle 2 (Beats 155-160)**: Create Verification Checklist
- [ ] Automated checks (Python script: `tools/verify_proof.py`)
  - Citation validator: compare against theorem database
  - Notation consistency: no variable redefinitions
  - Hypothesis extractor: identify all assumptions
  - Domain validator: functions defined correctly
- [ ] Output format: structured report (human-readable + JSON)

**Cycle 3 (Beats 160-165)**: Design Dynamic Rigor Assessment
- [ ] Replace: hardcoded `rigor_progression: [0.65, 0.67, ...]`
- [ ] New model: rigor_score only populated AFTER expert review
- [ ] Track: hypotheses_stated, theorems_cited, gaps_identified, unproven_claims
- [ ] Output: JSON structure with "expert_review": "pending|passed|failed"

**Cycle 4 (Beats 165-170)**: Create Expert Reviewer Framework
- [ ] Role: independent mathematicians in domain
- [ ] Review template with sections:
  - Does proof cite all needed theorems?
  - Are hypotheses stated?
  - What gaps remain?
  - Is result new, known, or partial?
  - Ready for publication? (yes/conditional/no)
- [ ] File: `templates/expert_review_template.md`

**Cycle 5 (Beats 170-175)**: Design Publication Decision Tree
- [ ] New theorem → arXiv + top journals (Annals, Inventiones, etc.)
- [ ] Partial result → arXiv + specialized journals (J. Number Theory)
- [ ] Methodology → arXiv + methodology venues
- [ ] Exploratory → arXiv only (initially)
- [ ] File: `PUBLICATION_STRATEGY.md`

### Cycles 6-10 (Beats 175-200): Refactor Research Orchestrators

**Cycle 6 (Beats 175-180)**: Refactor BSD Orchestrator
- [ ] Remove: hardcoded `rigor_progression`
- [ ] Add: gap_tracking dict per cycle
- [ ] Add: unproven_claims list
- [ ] Add: expert_review_pending field
- [ ] New output: honest cycle report (gaps, not fake rigor)

**Cycle 7 (Beats 180-185)**: Refactor Riemann Orchestrator
- [ ] Same refactoring
- [ ] Ensure: proof "outlines" labeled as such
- [ ] Ensure: each outline lists missing steps

**Cycle 8 (Beats 185-190)**: Refactor Hodge Orchestrator
- [ ] Same refactoring
- [ ] Identify: which subproblems are tractable
- [ ] Mark: open subproblems explicitly

**Cycle 9 (Beats 190-195)**: Add Dynamic Rigor to All Orchestrators
- [ ] After each cycle, output includes:
  - hypotheses_stated: Y/N
  - theorems_verified: count
  - gaps_identified: [list]
  - unproven_steps: count
  - expert_review_status: "pending"
- [ ] NO fake rigor_score until expert review

**Cycle 10 (Beats 195-200)**: Test Refactored Orchestrators
- [ ] Run: BSD phase 1, cycles 1-3 (test run)
- [ ] Verify: output is honest about gaps, NOT fake rigor
- [ ] Verify: JSON structure matches new schema

### Cycles 11-15 (Beats 200-225): Build Proof Verification Tools

**Cycle 11 (Beats 200-205)**: Citation Validator
- [ ] Create: `tools/citation_validator.py`
- [ ] Database: list of real theorems (Kolyvagin, Gross-Zagier, Wiles, etc.)
- [ ] Check: every cited theorem exists
- [ ] Output: report of valid/invalid citations

**Cycle 12 (Beats 205-210)**: Notation Checker
- [ ] Create: `tools/notation_checker.py`
- [ ] Scan: all mathematical notation
- [ ] Check: no variable redefinition, consistent symbols
- [ ] Output: issues found

**Cycle 13 (Beats 210-215)**: Hypothesis Extractor
- [ ] Create: `tools/hypothesis_extractor.py`
- [ ] Scan: proof text for "assume", "let", "suppose"
- [ ] Extract: all explicit and implicit hypotheses
- [ ] Output: list of assumptions

**Cycle 14 (Beats 215-220)**: Integration Test
- [ ] Run all three tools on BSD manuscript
- [ ] Run all three tools on Riemann manuscript
- [ ] Verify: tools catch real problems
- [ ] Refine: false positive/negative rates

**Cycle 15 (Beats 220-225)**: Create Verification Runner
- [ ] Script: `tools/verify_proof.py <manuscript>`
- [ ] Runs: all checks in sequence
- [ ] Output: unified report (human + JSON)
- [ ] Include: timestamp, version, review status

### Cycles 16-20 (Beats 225-250): Establish Expert Review System

**Cycle 16 (Beats 225-230)**: Create Reviewer Recruitment
- [ ] Document: what experts needed per problem
- [ ] Template: outreach communication
- [ ] Agreement: confidentiality, timeline, deliverables
- [ ] File: `EXPERT_REVIEWERS.md` (metadata only, no contact in repo)

**Cycle 17 (Beats 230-235)**: Design Feedback Loop
- [ ] Workflow:
  1. GPIA generates proof
  2. Run verification tool
  3. Submit to expert
  4. Expert returns report
  5. Identify gaps/revisions
  6. Iterate (if needed)
- [ ] Create: `reviews/` directory

**Cycle 18 (Beats 235-240)**: Create Review Tracking System
- [ ] Format: `reviews/bsd_rank1_review_001.md`
- [ ] Contents: reviewer name (anonymized), date, findings, recommendation
- [ ] Status: "pending" → "in_progress" → "complete"
- [ ] File: `reviews/index.md` (master index)

**Cycle 19 (Beats 240-245)**: Design Revision Workflow
- [ ] After review feedback:
  - Identify: claims needing revision
  - Identify: fixable gaps vs fundamental obstacles
  - Plan: next research cycle targeting gaps
  - Document: all decisions
- [ ] Create: `revisions/` directory

**Cycle 20 (Beats 245-250)**: Plan Formalization (Optional)
- [ ] Decide: Lean 4 or Coq for key lemmas?
- [ ] If yes:
  - Create: `formalization/` directory
  - Set up: Lean project structure
  - Define: which lemmas to formalize
- [ ] If no: note that proof is informal but peer-reviewed

### Cycles 21-25 (Beats 250-275): Plan Publication Pipeline

**Cycle 21 (Beats 250-255)**: Define Publication Tiers
- [ ] Tier 1 (Strong): New theorems → top journals
- [ ] Tier 2 (Partial): Subproblems → specialized journals
- [ ] Tier 3 (Exploratory): Methodology → arXiv
- [ ] Millennium: Special handling for Clay prizes
- [ ] File: `PUBLICATION_STRATEGY.md`

**Cycle 22 (Beats 255-260)**: Create arXiv Submission Template
- [ ] Metadata format: title, authors, abstract, keywords
- [ ] Note: "Proof search orchestrated via GPIA system"
- [ ] Track: submissions log with versions, feedback, status
- [ ] File: `submissions/arxiv_template.md`

**Cycle 23 (Beats 260-265)**: Design Attribution Model
- [ ] Option A: "X, Y, Z with GPIA-orchestrated proof search"
- [ ] Option B: "GPIA (led by X)"
- [ ] Option C: "X et al., with computational assistance"
- [ ] Document: `ATTRIBUTION.md` (chosen policy)

**Cycle 24 (Beats 265-270)**: Create Journal Selection Criteria
- [ ] Per problem: which venues accept this?
- [ ] Research: editorial scope, review timeline, open access
- [ ] Create: `JOURNAL_TARGETS.md`
- [ ] Include: pros/cons per venue

**Cycle 25 (Beats 270-275)**: Create Publication Checklist
- [ ] Pre-submission: verification passed, expert review passed, disclaimers present
- [ ] Submission: formatting per journal, cover letter, author info
- [ ] Post-submission: track reviews, manage revisions
- [ ] File: `PUBLICATION_CHECKLIST.md`

---

## PHASE 2 REFINEMENT: BEATS 275-300 (5 Cycles)

**Cycle 26 (Beats 275-280)**: Test Full Verification Pipeline
- [ ] Create mock proof with intentional errors
- [ ] Run verification suite
- [ ] Verify: all errors caught
- [ ] Test: reviewer template clarity

**Cycle 27 (Beats 280-285)**: Test Expert Review Workflow
- [ ] Simulate: full review cycle on BSD rank-1 proof
- [ ] Collect: feedback on workflow
- [ ] Revise: templates, process, timing
- [ ] Document: lessons learned

**Cycle 28 (Beats 285-290)**: Integration Test
- [ ] Run: complete orchestrator → verification → review simulation
- [ ] Verify: no broken links, missing files
- [ ] Test: all Python scripts execute correctly
- [ ] Output: integration test report

**Cycle 29 (Beats 290-295)**: Documentation Review
- [ ] Read: all Phase 2 docs end-to-end
- [ ] Check: consistency, completeness, clarity
- [ ] Ensure: new developers can follow process
- [ ] Revise: unclear sections

**Cycle 30 (Beats 295-300)**: Final Commit & Tag
- [ ] Git commit all Phase 2 infrastructure
- [ ] Tag: `phase2-infrastructure-complete-beat300`
- [ ] Create: "Phase 2 Infrastructure Report"

---

## SUCCESS CRITERIA

✅ 3-tier verification system designed and documented
✅ Research orchestrators refactored (no fake rigor metrics)
✅ Automated verification tools created and tested
✅ Expert review framework established
✅ Publication strategy documented
✅ Full pipeline tested end-to-end
✅ All artifacts logged and reproducible

---

## NEXT PHASE (AFTER BEAT 300)

**Phase 2 Execution: Beats 300-525**
- Run first legitimate BSD research cycle (rank ≤ 1)
- Use verification infrastructure
- Get expert review
- Prepare for publication

---

## GPIA INSTRUCTIONS

1. Read this briefing
2. Process each cycle sequentially (no parallelize)
3. For each cycle:
   - Create specified files/tools/docs
   - Test where applicable
   - Generate summary report
4. After Beat 300: infrastructure ready for research
5. Phase 2 Execution briefing will be provided

**Ready to begin?**
