/**
 * OpenAI Agent Bridge
 * ===================
 *
 * Connects Brahim tools to OpenAI function calling.
 * Each killer use case is exposed as an OpenAI tool.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.agent

import com.brahim.buim.usecase.BrahimGeoIDFactory
import com.brahim.buim.usecase.BrahimGeoID
import com.brahim.buim.blockchain.BrahimBlockchain
import com.brahim.buim.blockchain.BrahimMiningProtocol
import com.brahim.buim.gematria.BrahimGematria
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.*

/**
 * OpenAI Function Schema for tool registration.
 */
@Serializable
data class FunctionSchema(
    val name: String,
    val description: String,
    val parameters: JsonObject
)

/**
 * Tool call result.
 */
@Serializable
data class ToolResult(
    val success: Boolean,
    val tool: String,
    val result: JsonElement,
    val error: String? = null
)

/**
 * OpenAI Agent Bridge - Exposes Brahim tools as OpenAI functions.
 */
object OpenAIAgentBridge {

    /**
     * All available tools as OpenAI function schemas.
     */
    fun getToolSchemas(): List<FunctionSchema> = listOf(
        // Use Case 1: Geospatial Product IDs
        FunctionSchema(
            name = "create_geo_id",
            description = "Create a unique Brahim Geo ID from coordinates. Use for inventory slots, assets, or any location-based identifier.",
            parameters = buildJsonObject {
                put("type", JsonPrimitive("object"))
                putJsonObject("properties") {
                    putJsonObject("latitude") {
                        put("type", JsonPrimitive("number"))
                        put("description", JsonPrimitive("Latitude in degrees (-90 to 90)"))
                    }
                    putJsonObject("longitude") {
                        put("type", JsonPrimitive("number"))
                        put("description", JsonPrimitive("Longitude in degrees (-180 to 180)"))
                    }
                    putJsonObject("location_hint") {
                        put("type", JsonPrimitive("string"))
                        put("description", JsonPrimitive("Short location name (optional, max 4 chars)"))
                    }
                }
                putJsonArray("required") {
                    add(JsonPrimitive("latitude"))
                    add(JsonPrimitive("longitude"))
                }
            }
        ),

        // Use Case 2: Verify Geo ID
        FunctionSchema(
            name = "verify_geo_id",
            description = "Verify a Brahim Geo ID string. Checks if the check digit is valid.",
            parameters = buildJsonObject {
                put("type", JsonPrimitive("object"))
                putJsonObject("properties") {
                    putJsonObject("id") {
                        put("type", JsonPrimitive("string"))
                        put("description", JsonPrimitive("Brahim ID string (e.g., BN:949486203882100-7)"))
                    }
                }
                putJsonArray("required") {
                    add(JsonPrimitive("id"))
                }
            }
        ),

        // Use Case 3: Create Route
        FunctionSchema(
            name = "create_route",
            description = "Create a delivery route with Brahim Geo ID waypoints and tamper-proof checksum.",
            parameters = buildJsonObject {
                put("type", JsonPrimitive("object"))
                putJsonObject("properties") {
                    putJsonObject("route_id") {
                        put("type", JsonPrimitive("string"))
                        put("description", JsonPrimitive("Unique route identifier"))
                    }
                    putJsonObject("waypoints") {
                        put("type", JsonPrimitive("array"))
                        put("description", JsonPrimitive("Array of [lat, lon] coordinate pairs"))
                        putJsonObject("items") {
                            put("type", JsonPrimitive("array"))
                            putJsonObject("items") {
                                put("type", JsonPrimitive("number"))
                            }
                        }
                    }
                }
                putJsonArray("required") {
                    add(JsonPrimitive("route_id"))
                    add(JsonPrimitive("waypoints"))
                }
            }
        ),

        // Use Case 4: Dataset Fingerprint
        FunctionSchema(
            name = "fingerprint_dataset",
            description = "Create a unique fingerprint for a geospatial dataset. Detects any tampering.",
            parameters = buildJsonObject {
                put("type", JsonPrimitive("object"))
                putJsonObject("properties") {
                    putJsonObject("coordinates") {
                        put("type", JsonPrimitive("array"))
                        put("description", JsonPrimitive("Array of [lat, lon] coordinate pairs"))
                    }
                }
                putJsonArray("required") {
                    add(JsonPrimitive("coordinates"))
                }
            }
        ),

        // Use Case 5: Decode Brahim Number
        FunctionSchema(
            name = "decode_brahim_number",
            description = "Decode a Brahim Number back to original coordinates.",
            parameters = buildJsonObject {
                put("type", JsonPrimitive("object"))
                putJsonObject("properties") {
                    putJsonObject("brahim_number") {
                        put("type", JsonPrimitive("integer"))
                        put("description", JsonPrimitive("Brahim Number to decode"))
                    }
                }
                putJsonArray("required") {
                    add(JsonPrimitive("brahim_number"))
                }
            }
        ),

        // Use Case 6: Gematria Analysis
        FunctionSchema(
            name = "analyze_gematria",
            description = "Perform Hebrew gematria analysis on a number or coordinates.",
            parameters = buildJsonObject {
                put("type", JsonPrimitive("object"))
                putJsonObject("properties") {
                    putJsonObject("latitude") {
                        put("type", JsonPrimitive("number"))
                        put("description", JsonPrimitive("Latitude for coordinate analysis"))
                    }
                    putJsonObject("longitude") {
                        put("type", JsonPrimitive("number"))
                        put("description", JsonPrimitive("Longitude for coordinate analysis"))
                    }
                }
                putJsonArray("required") {
                    add(JsonPrimitive("latitude"))
                    add(JsonPrimitive("longitude"))
                }
            }
        ),

        // Use Case 7: Blockchain Verification
        FunctionSchema(
            name = "verify_block_candidate",
            description = "Check if coordinates qualify as a valid Brahim Blockchain block.",
            parameters = buildJsonObject {
                put("type", JsonPrimitive("object"))
                putJsonObject("properties") {
                    putJsonObject("latitude") {
                        put("type", JsonPrimitive("number"))
                        put("description", JsonPrimitive("Latitude"))
                    }
                    putJsonObject("longitude") {
                        put("type", JsonPrimitive("number"))
                        put("description", JsonPrimitive("Longitude"))
                    }
                    putJsonObject("cultural_description") {
                        put("type", JsonPrimitive("string"))
                        put("description", JsonPrimitive("Cultural/historical significance of location"))
                    }
                }
                putJsonArray("required") {
                    add(JsonPrimitive("latitude"))
                    add(JsonPrimitive("longitude"))
                }
            }
        )
    )

    /**
     * Execute a tool call from OpenAI.
     */
    fun executeTool(name: String, arguments: JsonObject): ToolResult {
        return try {
            when (name) {
                "create_geo_id" -> executeCreateGeoId(arguments)
                "verify_geo_id" -> executeVerifyGeoId(arguments)
                "create_route" -> executeCreateRoute(arguments)
                "fingerprint_dataset" -> executeFingerprintDataset(arguments)
                "decode_brahim_number" -> executeDecodeBrahimNumber(arguments)
                "analyze_gematria" -> executeAnalyzeGematria(arguments)
                "verify_block_candidate" -> executeVerifyBlockCandidate(arguments)
                else -> ToolResult(
                    success = false,
                    tool = name,
                    result = JsonPrimitive("Unknown tool"),
                    error = "Tool '$name' not found"
                )
            }
        } catch (e: Exception) {
            ToolResult(
                success = false,
                tool = name,
                result = JsonPrimitive(e.message ?: "Error"),
                error = e.message
            )
        }
    }

    // =========================================================================
    // Tool Implementations
    // =========================================================================

    private fun executeCreateGeoId(args: JsonObject): ToolResult {
        val lat = args["latitude"]?.jsonPrimitive?.double ?: throw IllegalArgumentException("latitude required")
        val lon = args["longitude"]?.jsonPrimitive?.double ?: throw IllegalArgumentException("longitude required")
        val hint = args["location_hint"]?.jsonPrimitive?.contentOrNull ?: ""

        val geoId = BrahimGeoIDFactory.create(lat, lon, hint)

        return ToolResult(
            success = true,
            tool = "create_geo_id",
            result = buildJsonObject {
                put("full_id", JsonPrimitive(geoId.fullId))
                put("short_id", JsonPrimitive(geoId.shortId))
                put("human_id", JsonPrimitive(geoId.humanId))
                put("brahim_number", JsonPrimitive(geoId.brahimNumber))
                put("check_digit", JsonPrimitive(geoId.checkDigit.toString()))
                put("mod_214", JsonPrimitive(geoId.mod214))
            }
        )
    }

    private fun executeVerifyGeoId(args: JsonObject): ToolResult {
        val id = args["id"]?.jsonPrimitive?.content ?: throw IllegalArgumentException("id required")
        val isValid = BrahimGeoIDFactory.verify(id)

        return ToolResult(
            success = true,
            tool = "verify_geo_id",
            result = buildJsonObject {
                put("id", JsonPrimitive(id))
                put("valid", JsonPrimitive(isValid))
                put("message", JsonPrimitive(if (isValid) "ID is valid" else "Invalid check digit"))
            }
        )
    }

    private fun executeCreateRoute(args: JsonObject): ToolResult {
        val routeId = args["route_id"]?.jsonPrimitive?.content ?: throw IllegalArgumentException("route_id required")
        val waypointsJson = args["waypoints"]?.jsonArray ?: throw IllegalArgumentException("waypoints required")

        val waypoints = waypointsJson.map { wp ->
            val coords = wp.jsonArray
            coords[0].jsonPrimitive.double to coords[1].jsonPrimitive.double
        }

        val route = BrahimGeoIDFactory.createRoute(routeId, waypoints)

        return ToolResult(
            success = true,
            tool = "create_route",
            result = buildJsonObject {
                put("route_id", JsonPrimitive(route.routeId))
                put("waypoint_count", JsonPrimitive(route.waypoints.size))
                put("checksum", JsonPrimitive(route.checksum))
                putJsonArray("waypoint_ids") {
                    route.waypoints.forEach { wp ->
                        add(JsonPrimitive(wp.shortId))
                    }
                }
            }
        )
    }

    private fun executeFingerprintDataset(args: JsonObject): ToolResult {
        val coordsJson = args["coordinates"]?.jsonArray ?: throw IllegalArgumentException("coordinates required")

        val coordinates = coordsJson.map { coord ->
            val pair = coord.jsonArray
            pair[0].jsonPrimitive.double to pair[1].jsonPrimitive.double
        }

        val fingerprint = BrahimGeoIDFactory.fingerprintDataset(coordinates)

        return ToolResult(
            success = true,
            tool = "fingerprint_dataset",
            result = buildJsonObject {
                put("fingerprint_id", JsonPrimitive(fingerprint.fingerprintId))
                put("point_count", JsonPrimitive(fingerprint.count))
                put("xor_hash", JsonPrimitive(fingerprint.xorFingerprint))
                put("digital_root", JsonPrimitive(fingerprint.digitalRoot))
                put("check_digit", JsonPrimitive(fingerprint.checkDigit.toString()))
            }
        )
    }

    private fun executeDecodeBrahimNumber(args: JsonObject): ToolResult {
        val bn = args["brahim_number"]?.jsonPrimitive?.long ?: throw IllegalArgumentException("brahim_number required")

        val coords = BrahimGeoIDFactory.decode(bn)

        return if (coords != null) {
            ToolResult(
                success = true,
                tool = "decode_brahim_number",
                result = buildJsonObject {
                    put("brahim_number", JsonPrimitive(bn))
                    put("latitude", JsonPrimitive(coords.first))
                    put("longitude", JsonPrimitive(coords.second))
                }
            )
        } else {
            ToolResult(
                success = false,
                tool = "decode_brahim_number",
                result = JsonPrimitive("Could not decode"),
                error = "Invalid Brahim Number"
            )
        }
    }

    private fun executeAnalyzeGematria(args: JsonObject): ToolResult {
        val lat = args["latitude"]?.jsonPrimitive?.double ?: throw IllegalArgumentException("latitude required")
        val lon = args["longitude"]?.jsonPrimitive?.double ?: throw IllegalArgumentException("longitude required")

        val analysis = BrahimGematria.analyzeCoordinates(lat, lon)

        return ToolResult(
            success = true,
            tool = "analyze_gematria",
            result = buildJsonObject {
                put("brahim_number", JsonPrimitive(analysis.brahimNumber))
                put("digit_sum", JsonPrimitive(analysis.digitSum))
                put("digital_root", JsonPrimitive(analysis.digitalRoot))
                put("mod_26_letter", JsonPrimitive(analysis.mod26Letter.toString()))
                putJsonArray("hebrew_letters") {
                    analysis.hebrewLetters.forEach { letter ->
                        addJsonObject {
                            put("letter", JsonPrimitive(letter.letter.toString()))
                            put("name", JsonPrimitive(letter.name))
                            put("value", JsonPrimitive(letter.value))
                            put("meaning", JsonPrimitive(letter.meaning))
                        }
                    }
                }
            }
        )
    }

    private fun executeVerifyBlockCandidate(args: JsonObject): ToolResult {
        val lat = args["latitude"]?.jsonPrimitive?.double ?: throw IllegalArgumentException("latitude required")
        val lon = args["longitude"]?.jsonPrimitive?.double ?: throw IllegalArgumentException("longitude required")
        val cultural = args["cultural_description"]?.jsonPrimitive?.contentOrNull ?: ""

        val receipt = BrahimMiningProtocol.verifyBlock(
            latitude = kotlin.math.abs(lat),
            longitude = kotlin.math.abs(lon),
            culturalDescription = cultural,
            difficulty = com.brahim.buim.blockchain.MiningDifficulty.FOUNDER
        )

        return ToolResult(
            success = true,
            tool = "verify_block_candidate",
            result = buildJsonObject {
                put("is_valid", JsonPrimitive(receipt.isValid))
                put("score", JsonPrimitive(receipt.score))
                put("max_score", JsonPrimitive(receipt.maxScore))
                put("brahim_number", JsonPrimitive(receipt.brahimNumber))
                put("digit_sum", JsonPrimitive(receipt.digitSum))
                put("digital_root", JsonPrimitive(receipt.digitalRoot))
                putJsonObject("criteria") {
                    receipt.criteriaResults.forEach { (key, value) ->
                        put(key, JsonPrimitive(value))
                    }
                }
            }
        )
    }
}
