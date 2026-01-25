/**
 * SAT Solver Agent - Boolean Satisfiability Solver
 * =================================================
 *
 * Implements DPLL-based SAT solving with Brahim security layer.
 *
 * Applications:
 * - Circuit verification
 * - Planning problems
 * - Constraint satisfaction
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.sdk

import com.brahim.buim.core.BrahimConstants
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * SAT result enum.
 */
enum class SATResult {
    SAT, UNSAT, UNKNOWN, TIMEOUT
}

/**
 * CNF clause representation.
 */
data class Clause(val literals: List<Int>)

/**
 * CNF formula representation.
 */
data class CNFFormula(
    val numVars: Int,
    val clauses: List<Clause>
) {
    val clauseVarRatio: Double get() = clauses.size.toDouble() / numVars

    /**
     * Parse from DIMACS format string.
     */
    companion object {
        fun fromDIMACS(dimacs: String): CNFFormula {
            val lines = dimacs.lines().filter { !it.startsWith("c") && it.isNotBlank() }
            var numVars = 0
            val clauses = mutableListOf<Clause>()

            for (line in lines) {
                if (line.startsWith("p cnf")) {
                    val parts = line.split(" ")
                    numVars = parts[2].toInt()
                } else {
                    val literals = line.split(" ")
                        .filter { it.isNotBlank() }
                        .map { it.toInt() }
                        .filter { it != 0 }
                    if (literals.isNotEmpty()) {
                        clauses.add(Clause(literals))
                    }
                }
            }

            return CNFFormula(numVars, clauses)
        }
    }
}

/**
 * SAT solution with statistics.
 */
data class SATSolution(
    val result: SATResult,
    val assignment: Map<Int, Boolean>?,
    val conflicts: Int,
    val decisions: Int,
    val propagations: Int
)

/**
 * SAT Solver Agent using DPLL algorithm.
 */
class SATSolverAgent : BaseBOAAgent() {

    override val name = "SAT Solver"
    override val domain = "logic"
    override val description = "Solves Boolean satisfiability problems using DPLL"
    override val capabilities = listOf(
        "CNF formula solving",
        "DIMACS format parsing",
        "Phase transition detection",
        "Hardness estimation"
    )

    // Statistics
    private var conflicts = 0
    private var decisions = 0
    private var propagations = 0

    // Phase transition threshold for 3-SAT
    private val phaseTransitionRatio = 4.26

    override suspend fun process(query: String): AgentSolverResponse {
        return withContext(Dispatchers.Default) {
            val startTime = System.currentTimeMillis()

            try {
                // Parse formula from query
                val formula = parseFormula(query) ?: return@withContext AgentSolverResponse(
                    success = false,
                    result = null,
                    error = "Could not parse CNF formula from query",
                    executionTime = System.currentTimeMillis() - startTime
                )

                val solution = solve(formula)

                AgentSolverResponse(
                    success = true,
                    result = mapOf(
                        "result" to solution.result.name,
                        "satisfiable" to (solution.result == SATResult.SAT),
                        "assignment" to solution.assignment,
                        "statistics" to mapOf(
                            "conflicts" to solution.conflicts,
                            "decisions" to solution.decisions,
                            "propagations" to solution.propagations
                        ),
                        "formula_info" to mapOf(
                            "variables" to formula.numVars,
                            "clauses" to formula.clauses.size,
                            "ratio" to formula.clauseVarRatio,
                            "near_phase_transition" to (formula.clauseVarRatio in 3.5..5.0)
                        )
                    ),
                    error = null,
                    executionTime = System.currentTimeMillis() - startTime
                )
            } catch (e: Exception) {
                AgentSolverResponse(
                    success = false,
                    result = null,
                    error = e.message,
                    executionTime = System.currentTimeMillis() - startTime
                )
            }
        }
    }

    /**
     * Solve a CNF formula using DPLL.
     */
    fun solve(formula: CNFFormula, timeout: Long = 5000): SATSolution {
        conflicts = 0
        decisions = 0
        propagations = 0

        val startTime = System.currentTimeMillis()
        val assignment = mutableMapOf<Int, Boolean>()

        val result = dpll(formula.clauses.toMutableList(), assignment, startTime, timeout)

        return SATSolution(
            result = result,
            assignment = if (result == SATResult.SAT) assignment else null,
            conflicts = conflicts,
            decisions = decisions,
            propagations = propagations
        )
    }

    /**
     * DPLL algorithm implementation.
     */
    private fun dpll(
        clauses: MutableList<Clause>,
        assignment: MutableMap<Int, Boolean>,
        startTime: Long,
        timeout: Long
    ): SATResult {
        // Check timeout
        if (System.currentTimeMillis() - startTime > timeout) {
            return SATResult.TIMEOUT
        }

        // Unit propagation
        var changed = true
        while (changed) {
            changed = false
            val unitClauses = clauses.filter { it.literals.size == 1 }

            for (unit in unitClauses) {
                val lit = unit.literals[0]
                val variable = kotlin.math.abs(lit)
                val value = lit > 0

                if (variable in assignment && assignment[variable] != value) {
                    conflicts++
                    return SATResult.UNSAT
                }

                assignment[variable] = value
                propagations++

                // Remove satisfied clauses and false literals
                clauses.removeAll { clause ->
                    clause.literals.any { l ->
                        val v = kotlin.math.abs(l)
                        v in assignment && (assignment[v] == (l > 0))
                    }
                }

                for (clause in clauses) {
                    val toRemove = clause.literals.filter { l ->
                        val v = kotlin.math.abs(l)
                        v in assignment && assignment[v] != (l > 0)
                    }
                    (clause.literals as MutableList).removeAll(toRemove)
                }

                changed = true
            }
        }

        // Check for empty clause (conflict)
        if (clauses.any { it.literals.isEmpty() }) {
            conflicts++
            return SATResult.UNSAT
        }

        // Check if all clauses satisfied
        if (clauses.isEmpty()) {
            return SATResult.SAT
        }

        // Choose a variable to branch on
        val variable = chooseVariable(clauses, assignment)
        if (variable == null) {
            return SATResult.SAT
        }

        decisions++

        // Try true
        val trueAssignment = assignment.toMutableMap()
        trueAssignment[variable] = true
        val trueClauses = clauses.map { Clause(it.literals.toMutableList()) }.toMutableList()

        val trueResult = dpll(trueClauses, trueAssignment, startTime, timeout)
        if (trueResult == SATResult.SAT) {
            assignment.clear()
            assignment.putAll(trueAssignment)
            return SATResult.SAT
        }

        // Try false
        val falseAssignment = assignment.toMutableMap()
        falseAssignment[variable] = false
        val falseClauses = clauses.map { Clause(it.literals.toMutableList()) }.toMutableList()

        val falseResult = dpll(falseClauses, falseAssignment, startTime, timeout)
        if (falseResult == SATResult.SAT) {
            assignment.clear()
            assignment.putAll(falseAssignment)
            return SATResult.SAT
        }

        return SATResult.UNSAT
    }

    /**
     * Choose variable using simple heuristic.
     */
    private fun chooseVariable(
        clauses: List<Clause>,
        assignment: Map<Int, Boolean>
    ): Int? {
        val unassigned = clauses.flatMap { it.literals }
            .map { kotlin.math.abs(it) }
            .filter { it !in assignment }
            .distinct()

        return unassigned.maxByOrNull { variable ->
            clauses.count { clause ->
                clause.literals.any { kotlin.math.abs(it) == variable }
            }
        }
    }

    /**
     * Parse formula from query.
     */
    private fun parseFormula(query: String): CNFFormula? {
        // Try DIMACS format
        if (query.contains("p cnf")) {
            return CNFFormula.fromDIMACS(query)
        }

        // Try simple format: (1 2 -3) (-1 2) (3)
        val clausePattern = Regex("""\(([^)]+)\)""")
        val matches = clausePattern.findAll(query)

        val clauses = mutableListOf<Clause>()
        var maxVar = 0

        for (match in matches) {
            val literals = match.groupValues[1].trim()
                .split(Regex("""\s+"""))
                .mapNotNull { it.toIntOrNull() }
                .filter { it != 0 }

            if (literals.isNotEmpty()) {
                clauses.add(Clause(literals))
                maxVar = maxOf(maxVar, literals.maxOf { kotlin.math.abs(it) })
            }
        }

        return if (clauses.isNotEmpty()) {
            CNFFormula(maxVar, clauses)
        } else null
    }

    /**
     * Estimate hardness of a formula.
     */
    fun estimateHardness(formula: CNFFormula): String {
        val ratio = formula.clauseVarRatio

        return when {
            ratio < 2.0 -> "EASY (underconstrained)"
            ratio < 3.5 -> "MODERATE (satisfiable region)"
            ratio < 5.0 -> "HARD (near phase transition)"
            else -> "MODERATE (unsatisfiable region)"
        }
    }

    override fun canHandle(query: String): Boolean {
        val lower = query.lowercase()
        return "sat" in lower || "cnf" in lower || "boolean" in lower ||
               "satisf" in lower || query.contains("p cnf") ||
               Regex("""\([^)]*\d+[^)]*\)""").containsMatchIn(query)
    }

    override fun getOpenAISchema(): List<FunctionSchema> {
        return listOf(
            FunctionSchema(
                name = "solve_sat",
                description = "Solve a Boolean satisfiability problem in CNF format",
                parameters = mapOf(
                    "type" to "object",
                    "properties" to mapOf(
                        "formula" to mapOf(
                            "type" to "string",
                            "description" to "CNF formula in DIMACS or (literal) format"
                        )
                    ),
                    "required" to listOf("formula")
                )
            )
        )
    }
}
