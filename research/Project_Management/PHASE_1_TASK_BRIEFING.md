# PHASE 1 CREDIBILITY FIXES - TASK BRIEFING FOR GPIA

**Status**: Ready for autonomous execution
**Beat Range**: 0-150 (25 baseline + 5 refinement)
**Target**: Transform manuscripts from "proof claims" to "research framework"

## IMMEDIATE ACTIONS (Beats 0-25, Cycles 1-5)

### CYCLE 1 (Beats 0-5): BSD Manuscript Title & Abstract

**File**: `BSD_PROOF_MANUSCRIPT.tex`

**Action 1: Change Title**
- Current: `The Birch and Swinnerton-Dyer Conjecture: Proof of the Weak Form and Strong Form for Rank $\leq 1$`
- New: `The Birch and Swinnerton-Dyer Conjecture: Research Framework and Partial Results for Rank $\leq 1$`
- Reason: Honest framing—this is research, not a proof

**Action 2: Update Header**
- Current \lhead: `Rank $\leq 1$ Complete Proof`
- New \lhead: `Synthesis of Known Results and Research Methodology`
- Reason: Reflect actual scope

**Action 3: Rewrite Abstract**
- Current starts: "We present a rigorous proof of the Birch and Swinnerton-Dyer (BSD) conjecture..."
- New starts: "We survey known results and present a structured research approach to the Birch and Swinnerton-Dyer (BSD) conjecture..."
- Replace "rigorous proof" with "literature synthesis"
- Add: "Note: This is a research framework, not a proof of the general conjecture"
- Add: "Rank ≥ 2 remains open"

**Output**: Save modified file, generate report

---

### CYCLE 2 (Beats 5-10): Riemann Manuscript Title & Abstract

**File**: `RIEMANN_PROOF_FINAL_MANUSCRIPT.tex`

**Action 1: Change Title**
- Current: `Proof of the Riemann Hypothesis via Berry-Keating Hamiltonian...`
- New: `Hamiltonian Variational Approach to the Riemann Hypothesis: A Research Exploration`
- Reason: This is exploratory, not a complete proof

**Action 2: Rewrite Abstract**
- Remove: "We provide a complete proof"
- Add: "We explore a variational formulation using the Berry-Keating Hamiltonian"
- Add: "This is NOT a complete proof but a framework for future research"
- Add: "Key gaps remain in establishing uniqueness of the critical line"

**Output**: Save modified file, generate report

---

### CYCLE 3 (Beats 10-15): Add Scope & Claims (BSD)

**File**: `BSD_PROOF_MANUSCRIPT.tex`

**Action**: Insert new section after Abstract

```latex
\section*{Scope and Claims}

\textbf{What this manuscript does:}
\begin{itemize}
\item Surveys known results: Kolyvagin (rank 0), Gross-Zagier (rank 1 with CM), Wiles (modularity)
\item Presents structured research approach to BSD rank $\leq 1$
\item Documents existing methodology and identifies remaining gaps
\end{itemize}

\textbf{What this manuscript does NOT do:}
\begin{itemize}
\item Does NOT claim new proofs of the general BSD conjecture
\item Does NOT address rank $\geq 2$ cases
\item Does NOT resolve open problems in the strong form for generic curves
\end{itemize}

\textbf{Mathematical Definitions:}
\begin{itemize}
\item Algebraic rank: dimension of the free part of $E(\mathbb{Q})$
\item Analytic rank: order of vanishing of $L(E,s)$ at $s=1$
\item This manuscript addresses cases where these are equal, as conjectured
\end{itemize}
```

**Output**: Generate report

---

### CYCLE 4 (Beats 15-20): Add Scope & Claims (Riemann)

**File**: `RIEMANN_PROOF_FINAL_MANUSCRIPT.tex`

**Action**: Insert similar Scope and Claims section explaining:
- What the variational approach explores
- Why it's not a complete proof
- What would be needed to finish it
- Which steps are speculative

**Output**: Generate report

---

### CYCLE 5 (Beats 20-25): Rewrite Validation Report

**File**: `BSD_VALIDATION_REPORT.md`

**Actions**:
1. Remove all "100% proven" language
2. Replace with: "Rank 0 case aligns with Kolyvagin (1990s); Rank 1 with CM aligns with Gross-Zagier (1986)"
3. Add section: "What 'Validation' Means Here"
   - "Validation = literature consistency check"
   - "NOT = independent proof verification"
4. For rank ≥ 2: explicitly mark as "NOT VALIDATED — remains open"
5. Add caveats: "These results build on foundational work. Independent verification required."

**Output**: Generate report

---

## NEXT PHASES (Beats 25-150)

Once Cycles 1-5 complete, continue with:
- **Cycles 6-10 (Beats 25-50)**: Add hypotheses to all theorem statements
- **Cycles 11-15 (Beats 50-75)**: Add LICENSE, CITATION.cff, reproducibility docs
- **Cycles 16-20 (Beats 75-100)**: Remove hardcoded rigor metrics from orchestrators
- **Cycles 21-25 (Beats 100-125)**: Update CLAUDE.md and root docs
- **Refinement (Beats 125-150)**: Deep consistency checks and final polish

---

## SUCCESS CRITERIA FOR PHASE 1

✅ All manuscripts titled as "research framework", not "proofs"
✅ Scope & Claims sections explicitly state what is/isn't addressed
✅ All hypotheses documented
✅ All gaps identified
✅ No over-claims
✅ Publication metadata added (LICENSE, CITATION.cff)
✅ Reproducibility documented
✅ Code updated (hardcoded rigor removed)
✅ A mathematician would read this and trust the integrity

---

## GPIA INSTRUCTIONS

1. Read this briefing
2. Process each cycle sequentially (don't parallelize)
3. For each cycle:
   - Read current file state
   - Make specified edits
   - Generate change summary
   - Report completion
4. After Beat 25 (5 cycles done), wait for next briefing
5. Continue through Beat 150

**Do not proceed beyond Beat 150 without explicit approval.**

---

**Beat 0 Status**: Ready to execute
