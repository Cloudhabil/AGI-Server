/**
 * Egyptian Fractions Agent - Fair Division Solver
 * ================================================
 *
 * Solves Egyptian fraction problems: express 4/n as sum of unit fractions.
 * 4/n = 1/a + 1/b + 1/c (Erdős-Straus conjecture)
 *
 * Applications:
 * - Fair division problems
 * - Resource allocation
 * - Scheduling optimization
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.sdk

import com.brahim.buim.core.BrahimConstants
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Egyptian fraction solution.
 */
data class EgyptianSolution(
    val n: Int,
    val a: Long,
    val b: Long,
    val c: Long,
    val isValid: Boolean,
    val isHardCase: Boolean
)

/**
 * Egyptian Fractions Agent.
 */
class EgyptianFractionsAgent : BaseBOAAgent() {

    override val name = "Egyptian Fractions Solver"
    override val domain = "mathematics"
    override val description = "Solves Egyptian fraction problems (4/n = 1/a + 1/b + 1/c)"
    override val capabilities = listOf(
        "Erdős-Straus conjecture solutions",
        "Fair division calculations",
        "Unit fraction decomposition",
        "Hard case detection"
    )

    // Hard residue set (mod 840)
    private val hardResidues = setOf(1, 121, 169, 289, 361, 529)
    private val modulus = 840

    // Solution cache
    private val cache = mutableMapOf<Int, EgyptianSolution>()

    override suspend fun process(query: String): AgentSolverResponse {
        return withContext(Dispatchers.Default) {
            val startTime = System.currentTimeMillis()

            try {
                // Extract n from query
                val n = extractNumber(query) ?: return@withContext AgentSolverResponse(
                    success = false,
                    result = null,
                    error = "Could not extract a positive integer from query",
                    executionTime = System.currentTimeMillis() - startTime
                )

                val solution = solve(n)

                AgentSolverResponse(
                    success = solution.isValid,
                    result = mapOf(
                        "n" to solution.n,
                        "expression" to "4/${solution.n} = 1/${solution.a} + 1/${solution.b} + 1/${solution.c}",
                        "denominators" to listOf(solution.a, solution.b, solution.c),
                        "is_hard_case" to solution.isHardCase,
                        "verified" to verify(solution)
                    ),
                    error = null,
                    executionTime = System.currentTimeMillis() - startTime,
                    metadata = mapOf(
                        "algorithm" to "Brahim-enhanced greedy search",
                        "cached" to (n in cache)
                    )
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
     * Solve 4/n = 1/a + 1/b + 1/c
     */
    fun solve(n: Int): EgyptianSolution {
        require(n > 0) { "n must be positive" }

        // Check cache
        cache[n]?.let { return it }

        val isHard = isHardCase(n)

        // Try greedy algorithm
        val solution = greedySolve(n) ?: fallbackSolve(n)

        val result = solution?.let {
            EgyptianSolution(n, it.first, it.second, it.third, true, isHard)
        } ?: EgyptianSolution(n, 0, 0, 0, false, isHard)

        cache[n] = result
        return result
    }

    /**
     * Greedy algorithm for Egyptian fractions.
     */
    private fun greedySolve(n: Int): Triple<Long, Long, Long>? {
        // 4/n = 1/a + remaining
        // Start with a = ceil(n/4) + 1

        val maxA = n * 2L

        for (a in (n / 4 + 1)..maxA) {
            // Remaining: 4/n - 1/a = (4a - n) / (na)
            val numerator = 4 * a - n
            val denominator = n.toLong() * a

            if (numerator <= 0) continue

            // Now solve: numerator/denominator = 1/b + 1/c
            val result = solveTwoFractions(numerator, denominator)
            if (result != null) {
                return Triple(a, result.first, result.second)
            }
        }

        return null
    }

    /**
     * Solve p/q = 1/b + 1/c
     */
    private fun solveTwoFractions(p: Long, q: Long): Pair<Long, Long>? {
        // 1/b + 1/c = p/q
        // c = qb / (pb - q)

        val maxB = q * 2 / p + 1

        for (b in (q / p + 1)..maxB) {
            val numerator = q * b
            val denominator = p * b - q

            if (denominator > 0 && numerator % denominator == 0L) {
                val c = numerator / denominator
                if (c >= b) {
                    return b to c
                }
            }
        }

        return null
    }

    /**
     * Fallback solver for difficult cases.
     */
    private fun fallbackSolve(n: Int): Triple<Long, Long, Long>? {
        // Use identity: 4/n = 1/n + 1/n + 2/n
        // And 2/n = 1/((n+1)/2) + 1/(n(n+1)/2) when n is odd

        if (n % 2 == 1) {
            val a = n.toLong()
            val b = (n + 1L) / 2 * n
            val c = (n + 1L) / 2 * n

            // Verify
            if (4.0 / n == 1.0 / a + 1.0 / b + 1.0 / c) {
                return Triple(a, b, c)
            }
        }

        // General fallback: 4/n = 1/(n+1)/4 * ... (complex identity)
        val a = (n + 1L) / 4 + 1
        val remaining = 4.0 / n - 1.0 / a
        // This is a simplified fallback

        return null
    }

    /**
     * Check if n is a "hard case" (prime p ≡ 1 mod 4).
     */
    fun isHardCase(n: Int): Boolean {
        val residue = n % modulus
        return residue in hardResidues || (isPrime(n) && n % 4 == 1)
    }

    /**
     * Simple primality check.
     */
    private fun isPrime(n: Int): Boolean {
        if (n < 2) return false
        if (n == 2) return true
        if (n % 2 == 0) return false
        var i = 3
        while (i * i <= n) {
            if (n % i == 0) return false
            i += 2
        }
        return true
    }

    /**
     * Verify a solution.
     */
    fun verify(solution: EgyptianSolution): Boolean {
        if (!solution.isValid) return false

        val sum = 1.0 / solution.a + 1.0 / solution.b + 1.0 / solution.c
        val target = 4.0 / solution.n

        return kotlin.math.abs(sum - target) < 1e-10
    }

    /**
     * Extract number from query text.
     */
    private fun extractNumber(query: String): Int? {
        val pattern = Regex("""\d+""")
        return pattern.find(query)?.value?.toIntOrNull()
    }

    override fun canHandle(query: String): Boolean {
        val lower = query.lowercase()
        return "egyptian" in lower || "4/n" in lower || "unit fraction" in lower ||
               "fair division" in lower || ("fraction" in lower && extractNumber(query) != null)
    }

    override fun getOpenAISchema(): List<FunctionSchema> {
        return listOf(
            FunctionSchema(
                name = "solve_egyptian_fraction",
                description = "Solve 4/n = 1/a + 1/b + 1/c for positive integer n",
                parameters = mapOf(
                    "type" to "object",
                    "properties" to mapOf(
                        "n" to mapOf(
                            "type" to "integer",
                            "description" to "The denominator n in 4/n"
                        )
                    ),
                    "required" to listOf("n")
                )
            )
        )
    }
}
