/**
 * BOA Agent Interface - Domain-Specific Solver Base
 * ==================================================
 *
 * Base interface for all BOA SDK agents.
 * Each agent implements domain-specific problem solving.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.sdk

import com.brahim.buim.core.BrahimConstants

/**
 * Agent response wrapper.
 */
data class AgentSolverResponse(
    val success: Boolean,
    val result: Any?,
    val error: String?,
    val executionTime: Long,
    val metadata: Map<String, Any> = emptyMap()
)

/**
 * OpenAI-compatible function schema.
 */
data class FunctionSchema(
    val name: String,
    val description: String,
    val parameters: Map<String, Any>
)

/**
 * Base interface for BOA SDK agents.
 */
interface BOAAgent {
    val name: String
    val domain: String
    val description: String
    val capabilities: List<String>

    /**
     * Process a query and return result.
     */
    suspend fun process(query: String): AgentSolverResponse

    /**
     * Get OpenAI function calling schema.
     */
    fun getOpenAISchema(): List<FunctionSchema>

    /**
     * Check if agent can handle the query.
     */
    fun canHandle(query: String): Boolean

    /**
     * Get agent info.
     */
    fun getInfo(): Map<String, Any>
}

/**
 * Abstract base class with common functionality.
 */
abstract class BaseBOAAgent : BOAAgent {

    // Brahim security layer
    protected val beta = BrahimConstants.BETA_SECURITY
    protected val phi = BrahimConstants.PHI

    override fun getInfo(): Map<String, Any> {
        return mapOf(
            "name" to name,
            "domain" to domain,
            "description" to description,
            "capabilities" to capabilities,
            "beta" to beta,
            "phi" to phi
        )
    }

    /**
     * Apply Brahim security encoding.
     */
    protected fun securityEncode(value: Double): Double {
        return (value * phi + beta) / (1 + beta)
    }

    /**
     * Apply Brahim security decoding.
     */
    protected fun securityDecode(encoded: Double): Double {
        return (encoded * (1 + beta) - beta) / phi
    }
}

/**
 * Agent registry for discovery.
 */
object AgentRegistry {
    private val agents = mutableMapOf<String, BOAAgent>()

    fun register(agent: BOAAgent) {
        agents[agent.name] = agent
    }

    fun get(name: String): BOAAgent? = agents[name]

    fun getByDomain(domain: String): List<BOAAgent> {
        return agents.values.filter { it.domain == domain }
    }

    fun getAll(): List<BOAAgent> = agents.values.toList()

    fun findForQuery(query: String): BOAAgent? {
        return agents.values.find { it.canHandle(query) }
    }
}
