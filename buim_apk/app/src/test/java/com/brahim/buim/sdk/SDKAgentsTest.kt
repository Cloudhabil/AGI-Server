/**
 * SDK Agents Unit Tests
 * =====================
 *
 * Verifies the BOA SDK agent functionality.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.sdk

import org.junit.Test
import org.junit.Assert.*
import kotlinx.coroutines.runBlocking

class SDKAgentsTest {

    // Egyptian Fractions Agent Tests

    @Test
    fun `egyptian fractions agent has correct name`() {
        val agent = EgyptianFractionsAgent()
        assertEquals("Egyptian Fractions Solver", agent.name)
    }

    @Test
    fun `egyptian fractions agent domain is mathematics`() {
        val agent = EgyptianFractionsAgent()
        assertEquals("mathematics", agent.domain)
    }

    @Test
    fun `egyptian fractions can handle relevant queries`() {
        val agent = EgyptianFractionsAgent()

        assertTrue(agent.canHandle("egyptian fraction"))
        assertTrue(agent.canHandle("4/n decomposition"))
        assertTrue(agent.canHandle("unit fraction"))
        assertTrue(agent.canHandle("fair division problem"))
    }

    @Test
    fun `egyptian fractions cannot handle irrelevant queries`() {
        val agent = EgyptianFractionsAgent()

        assertFalse(agent.canHandle("weather today"))
        assertFalse(agent.canHandle("hello world"))
    }

    @Test
    fun `egyptian fractions solve returns valid solution`() {
        val agent = EgyptianFractionsAgent()
        val solution = agent.solve(5)

        assertTrue(solution.isValid)
        assertTrue(solution.a > 0)
        assertTrue(solution.b > 0)
        assertTrue(solution.c > 0)
    }

    @Test
    fun `egyptian fractions verify returns true for valid solution`() {
        val agent = EgyptianFractionsAgent()
        val solution = agent.solve(5)

        assertTrue(agent.verify(solution))
    }

    @Test
    fun `egyptian fractions hard case detection works`() {
        val agent = EgyptianFractionsAgent()

        // Primes p ≡ 1 mod 4 are hard cases
        assertTrue(agent.isHardCase(5))   // 5 ≡ 1 mod 4
        assertTrue(agent.isHardCase(13))  // 13 ≡ 1 mod 4
        assertTrue(agent.isHardCase(17))  // 17 ≡ 1 mod 4
    }

    @Test
    fun `egyptian fractions process returns successful response`() = runBlocking {
        val agent = EgyptianFractionsAgent()
        val response = agent.process("Solve 4/7")

        assertTrue(response.success)
        assertNotNull(response.result)
        assertNull(response.error)
    }

    @Test
    fun `egyptian fractions has openai schema`() {
        val agent = EgyptianFractionsAgent()
        val schema = agent.getOpenAISchema()

        assertTrue(schema.isNotEmpty())
        assertEquals("solve_egyptian_fraction", schema[0].name)
    }

    // SAT Solver Agent Tests

    @Test
    fun `sat solver agent has correct name`() {
        val agent = SATSolverAgent()
        assertEquals("SAT Solver", agent.name)
    }

    @Test
    fun `sat solver agent domain is logic`() {
        val agent = SATSolverAgent()
        assertEquals("logic", agent.domain)
    }

    @Test
    fun `sat solver can handle relevant queries`() {
        val agent = SATSolverAgent()

        assertTrue(agent.canHandle("SAT problem"))
        assertTrue(agent.canHandle("CNF formula"))
        assertTrue(agent.canHandle("boolean satisfiability"))
        assertTrue(agent.canHandle("p cnf 3 2"))
    }

    @Test
    fun `sat solver cannot handle irrelevant queries`() {
        val agent = SATSolverAgent()

        assertFalse(agent.canHandle("weather forecast"))
        assertFalse(agent.canHandle("hello"))
    }

    @Test
    fun `sat solver parses DIMACS format`() {
        val dimacs = """
            p cnf 3 2
            1 2 0
            -1 3 0
        """.trimIndent()

        val formula = CNFFormula.fromDIMACS(dimacs)

        assertEquals(3, formula.numVars)
        assertEquals(2, formula.clauses.size)
    }

    @Test
    fun `sat solver finds satisfying assignment for simple formula`() {
        val agent = SATSolverAgent()

        // (x1 OR x2) AND (-x1 OR x2) -> x2 = true satisfies
        val formula = CNFFormula(
            numVars = 2,
            clauses = listOf(
                Clause(listOf(1, 2)),
                Clause(listOf(-1, 2))
            )
        )

        val solution = agent.solve(formula)

        assertEquals(SATResult.SAT, solution.result)
        assertNotNull(solution.assignment)
        // x2 should be true
        assertEquals(true, solution.assignment?.get(2))
    }

    @Test
    fun `sat solver detects unsatisfiable formula`() {
        val agent = SATSolverAgent()

        // (x1) AND (-x1) -> UNSAT
        val formula = CNFFormula(
            numVars = 1,
            clauses = listOf(
                Clause(listOf(1)),
                Clause(listOf(-1))
            )
        )

        val solution = agent.solve(formula)

        assertEquals(SATResult.UNSAT, solution.result)
        assertNull(solution.assignment)
    }

    @Test
    fun `sat solver estimates hardness correctly`() {
        val agent = SATSolverAgent()

        // Low ratio = easy (underconstrained)
        val easyFormula = CNFFormula(numVars = 10, clauses = listOf(Clause(listOf(1))))
        assertTrue(agent.estimateHardness(easyFormula).contains("EASY"))

        // High ratio near phase transition = hard
        val hardFormula = CNFFormula(
            numVars = 10,
            clauses = (1..45).map { Clause(listOf(1, 2, 3)) }
        )
        assertTrue(agent.estimateHardness(hardFormula).contains("HARD"))
    }

    @Test
    fun `sat solver has openai schema`() {
        val agent = SATSolverAgent()
        val schema = agent.getOpenAISchema()

        assertTrue(schema.isNotEmpty())
        assertEquals("solve_sat", schema[0].name)
    }

    // Agent Registry Tests

    @Test
    fun `agent registry registers agents correctly`() {
        val agent = EgyptianFractionsAgent()
        AgentRegistry.register(agent)

        val retrieved = AgentRegistry.get("Egyptian Fractions Solver")
        assertNotNull(retrieved)
        assertEquals(agent.name, retrieved?.name)
    }

    @Test
    fun `agent registry finds by domain`() {
        AgentRegistry.register(EgyptianFractionsAgent())
        AgentRegistry.register(SATSolverAgent())

        val mathAgents = AgentRegistry.getByDomain("mathematics")
        val logicAgents = AgentRegistry.getByDomain("logic")

        assertTrue(mathAgents.any { it.name == "Egyptian Fractions Solver" })
        assertTrue(logicAgents.any { it.name == "SAT Solver" })
    }

    @Test
    fun `agent registry finds for query`() {
        AgentRegistry.register(EgyptianFractionsAgent())
        AgentRegistry.register(SATSolverAgent())

        val egyptianAgent = AgentRegistry.findForQuery("egyptian fraction for 4/7")
        val satAgent = AgentRegistry.findForQuery("solve this SAT problem")

        assertNotNull(egyptianAgent)
        assertNotNull(satAgent)
    }
}
