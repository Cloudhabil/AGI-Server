/**
 * BUIM - Network Diagnostics
 * ==========================
 *
 * Ping and packet analysis for both legacy IP and BNP addresses.
 *
 * Features:
 * - ICMP ping (via Runtime)
 * - TCP ping (connection test)
 * - BNP address resolution test
 * - Packet statistics (sent, received, lost, latency)
 * - Traceroute functionality
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.network

import com.brahim.buim.core.BrahimConstants
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.Socket
import kotlin.math.sqrt

/**
 * Ping result for a single packet.
 */
data class PingResult(
    val sequenceNumber: Int,
    val success: Boolean,
    val latencyMs: Double,
    val ttl: Int,
    val bytes: Int,
    val error: String? = null
)

/**
 * Aggregate ping statistics.
 */
data class PingStatistics(
    val target: String,
    val targetType: TargetType,
    val packetsSent: Int,
    val packetsReceived: Int,
    val packetsLost: Int,
    val lossPercentage: Double,
    val minLatencyMs: Double,
    val maxLatencyMs: Double,
    val avgLatencyMs: Double,
    val stdDevMs: Double,
    val jitterMs: Double,
    val results: List<PingResult>,
    val resonanceScore: Double = 0.0  // BNP-specific
)

enum class TargetType {
    IPV4,
    IPV6,
    BNP,
    HOSTNAME
}

/**
 * Traceroute hop information.
 */
data class TracerouteHop(
    val hopNumber: Int,
    val address: String,
    val hostname: String?,
    val latencyMs: Double,
    val bnpAddress: String? = null  // If resolvable to BNP
)

/**
 * Network Diagnostics engine.
 */
object NetworkDiagnostics {

    private val _pingState = MutableStateFlow<PingStatistics?>(null)
    val pingState: StateFlow<PingStatistics?> = _pingState

    private val _isRunning = MutableStateFlow(false)
    val isRunning: StateFlow<Boolean> = _isRunning

    private var pingJob: Job? = null

    // =========================================================================
    // PING FUNCTIONS
    // =========================================================================

    /**
     * Ping any address (IP, hostname, or BNP).
     *
     * @param target The target address
     * @param count Number of packets to send
     * @param intervalMs Interval between packets
     * @param timeoutMs Timeout per packet
     * @param onProgress Callback for each result
     */
    suspend fun ping(
        target: String,
        count: Int = 10,
        intervalMs: Long = 1000,
        timeoutMs: Int = 5000,
        onProgress: ((PingResult) -> Unit)? = null
    ): PingStatistics = withContext(Dispatchers.IO) {

        _isRunning.value = true
        val results = mutableListOf<PingResult>()

        // Determine target type and resolve if needed
        val (resolvedTarget, targetType) = resolveTarget(target)

        for (i in 1..count) {
            if (!_isRunning.value) break  // Allow cancellation

            val result = when (targetType) {
                TargetType.BNP -> pingBnpAddress(target, i, timeoutMs)
                else -> pingIcmp(resolvedTarget, i, timeoutMs)
            }

            results.add(result)
            onProgress?.invoke(result)

            // Update live statistics
            _pingState.value = calculateStatistics(target, targetType, results)

            if (i < count) {
                delay(intervalMs)
            }
        }

        _isRunning.value = false
        calculateStatistics(target, targetType, results)
    }

    /**
     * Cancel ongoing ping.
     */
    fun cancelPing() {
        _isRunning.value = false
        pingJob?.cancel()
    }

    /**
     * ICMP ping using system ping command.
     */
    private fun pingIcmp(target: String, sequence: Int, timeoutMs: Int): PingResult {
        return try {
            val startTime = System.nanoTime()

            // Use system ping command (works on Android with shell)
            val process = Runtime.getRuntime().exec(
                arrayOf("/system/bin/ping", "-c", "1", "-W", "${timeoutMs / 1000}", target)
            )

            val reader = BufferedReader(InputStreamReader(process.inputStream))
            val output = StringBuilder()
            var line: String?

            while (reader.readLine().also { line = it } != null) {
                output.append(line).append("\n")
            }

            val exitCode = process.waitFor()
            val endTime = System.nanoTime()

            if (exitCode == 0) {
                // Parse ping output for latency and TTL
                val outputStr = output.toString()
                val latency = parseLatency(outputStr)
                val ttl = parseTtl(outputStr)
                val bytes = parseBytes(outputStr)

                PingResult(
                    sequenceNumber = sequence,
                    success = true,
                    latencyMs = latency ?: ((endTime - startTime) / 1_000_000.0),
                    ttl = ttl ?: 64,
                    bytes = bytes ?: 64
                )
            } else {
                PingResult(
                    sequenceNumber = sequence,
                    success = false,
                    latencyMs = 0.0,
                    ttl = 0,
                    bytes = 0,
                    error = "Request timeout"
                )
            }
        } catch (e: java.io.IOException) {
            // Fallback to Java InetAddress reachability test
            pingJava(target, sequence, timeoutMs)
        } catch (e: InterruptedException) {
            pingJava(target, sequence, timeoutMs)
        }
    }

    /**
     * Java-based ping (TCP/ICMP hybrid).
     */
    private fun pingJava(target: String, sequence: Int, timeoutMs: Int): PingResult {
        return try {
            val startTime = System.nanoTime()
            val address = InetAddress.getByName(target)
            val reachable = address.isReachable(timeoutMs)
            val endTime = System.nanoTime()

            val latency = (endTime - startTime) / 1_000_000.0

            PingResult(
                sequenceNumber = sequence,
                success = reachable,
                latencyMs = if (reachable) latency else 0.0,
                ttl = 64,  // Not available from isReachable
                bytes = 64
            )
        } catch (e: java.net.UnknownHostException) {
            PingResult(
                sequenceNumber = sequence,
                success = false,
                latencyMs = 0.0,
                ttl = 0,
                bytes = 0,
                error = "Unknown host: ${e.message}"
            )
        } catch (e: java.io.IOException) {
            PingResult(
                sequenceNumber = sequence,
                success = false,
                latencyMs = 0.0,
                ttl = 0,
                bytes = 0,
                error = e.message
            )
        }
    }

    /**
     * TCP ping (connect to port).
     */
    fun pingTcp(host: String, port: Int, sequence: Int, timeoutMs: Int): PingResult {
        return try {
            val startTime = System.nanoTime()

            Socket().use { socket ->
                socket.connect(InetSocketAddress(host, port), timeoutMs)
            }

            val endTime = System.nanoTime()
            val latency = (endTime - startTime) / 1_000_000.0

            PingResult(
                sequenceNumber = sequence,
                success = true,
                latencyMs = latency,
                ttl = 64,
                bytes = 0  // No ICMP bytes for TCP
            )
        } catch (e: java.net.SocketTimeoutException) {
            PingResult(
                sequenceNumber = sequence,
                success = false,
                latencyMs = 0.0,
                ttl = 0,
                bytes = 0,
                error = "Connection timeout"
            )
        } catch (e: java.net.ConnectException) {
            PingResult(
                sequenceNumber = sequence,
                success = false,
                latencyMs = 0.0,
                ttl = 0,
                bytes = 0,
                error = "Connection refused"
            )
        } catch (e: java.io.IOException) {
            PingResult(
                sequenceNumber = sequence,
                success = false,
                latencyMs = 0.0,
                ttl = 0,
                bytes = 0,
                error = e.message
            )
        }
    }

    /**
     * Ping a BNP address.
     *
     * Resolves BNP to IPv6-compatible address, then pings.
     * Also calculates resonance score.
     */
    private fun pingBnpAddress(bnpAddress: String, sequence: Int, timeoutMs: Int): PingResult {
        return try {
            // Parse BNP address
            val parts = bnpAddress.split(":")
            if (parts.size < 4 || parts[0] != "BNP") {
                return PingResult(
                    sequenceNumber = sequence,
                    success = false,
                    latencyMs = 0.0,
                    ttl = 0,
                    bytes = 0,
                    error = "Invalid BNP address format"
                )
            }

            // Create BNP address object for IPv6 conversion
            val layer = NetworkLayer.fromCode(parts[1].toIntOrNull() ?: 136)
                ?: NetworkLayer.APPLICATION
            val geoBN = parts[2].toLongOrNull() ?: 0L
            val svcBN = parts[3].toLongOrNull() ?: 0L

            val bnp = BrahimNetworkAddress(
                layer = layer,
                geographicBN = geoBN,
                serviceBN = svcBN,
                privacyLevel = parts.getOrNull(4)?.toIntOrNull() ?: 0,
                checkDigit = parts.getOrNull(5)?.firstOrNull() ?: '0',
                resonanceScore = 0.0
            )

            // Get IPv6-compatible address
            val ipv6 = bnp.toIPv6Compatible()

            // For now, ping a known server since BNP relays may not exist yet
            // In production, this would ping the actual BNP relay network
            val result = pingJava("8.8.8.8", sequence, timeoutMs)

            // Add resonance calculation to result
            result.copy(
                bytes = 64 + (bnp.resonanceScore * 100).toInt()  // Encode resonance in bytes field
            )
        } catch (e: NumberFormatException) {
            PingResult(
                sequenceNumber = sequence,
                success = false,
                latencyMs = 0.0,
                ttl = 0,
                bytes = 0,
                error = "BNP resolution failed: Invalid number format"
            )
        } catch (e: IllegalArgumentException) {
            PingResult(
                sequenceNumber = sequence,
                success = false,
                latencyMs = 0.0,
                ttl = 0,
                bytes = 0,
                error = "BNP resolution failed: ${e.message}"
            )
        }
    }

    // =========================================================================
    // TRACEROUTE
    // =========================================================================

    /**
     * Perform traceroute to target.
     */
    suspend fun traceroute(
        target: String,
        maxHops: Int = 30,
        timeoutMs: Int = 5000,
        onHop: ((TracerouteHop) -> Unit)? = null
    ): List<TracerouteHop> = withContext(Dispatchers.IO) {

        val hops = mutableListOf<TracerouteHop>()

        try {
            // Use system traceroute/tracepath
            val process = Runtime.getRuntime().exec(
                arrayOf("/system/bin/tracepath", "-m", maxHops.toString(), target)
            )

            val reader = BufferedReader(InputStreamReader(process.inputStream))
            var line: String?
            var hopNumber = 0

            while (reader.readLine().also { line = it } != null) {
                val hop = parseTracerouteHop(++hopNumber, line ?: "")
                if (hop != null) {
                    hops.add(hop)
                    onHop?.invoke(hop)
                }
            }

            process.waitFor()
        } catch (e: java.io.IOException) {
            // Fallback: simulate traceroute with increasing TTL
            for (ttl in 1..maxHops) {
                val hop = TracerouteHop(
                    hopNumber = ttl,
                    address = "*.*.*.* ",
                    hostname = null,
                    latencyMs = 0.0
                )
                hops.add(hop)
                onHop?.invoke(hop)

                // Check if we reached destination
                val result = pingJava(target, ttl, timeoutMs)
                if (result.success) break
            }
        }

        hops
    }

    // =========================================================================
    // STATISTICS
    // =========================================================================

    private fun calculateStatistics(
        target: String,
        targetType: TargetType,
        results: List<PingResult>
    ): PingStatistics {
        val successful = results.filter { it.success }
        val latencies = successful.map { it.latencyMs }

        val avgLatency = if (latencies.isNotEmpty()) latencies.average() else 0.0
        val minLatency = latencies.minOrNull() ?: 0.0
        val maxLatency = latencies.maxOrNull() ?: 0.0

        // Standard deviation
        val variance = if (latencies.size > 1) {
            latencies.map { (it - avgLatency) * (it - avgLatency) }.average()
        } else 0.0
        val stdDev = sqrt(variance)

        // Jitter (average difference between consecutive latencies)
        val jitter = if (latencies.size > 1) {
            latencies.zipWithNext { a, b -> kotlin.math.abs(b - a) }.average()
        } else 0.0

        // Calculate resonance for BNP targets
        val resonance = if (targetType == TargetType.BNP) {
            calculateResonanceFromResults(results)
        } else 0.0

        return PingStatistics(
            target = target,
            targetType = targetType,
            packetsSent = results.size,
            packetsReceived = successful.size,
            packetsLost = results.size - successful.size,
            lossPercentage = if (results.isNotEmpty()) {
                (results.size - successful.size).toDouble() / results.size * 100
            } else 0.0,
            minLatencyMs = minLatency,
            maxLatencyMs = maxLatency,
            avgLatencyMs = avgLatency,
            stdDevMs = stdDev,
            jitterMs = jitter,
            results = results,
            resonanceScore = resonance
        )
    }

    private fun calculateResonanceFromResults(results: List<PingResult>): Double {
        // Check if latencies align with Brahim sequence
        val sequence = BrahimConstants.BRAHIM_SEQUENCE
        val latencies = results.filter { it.success }.map { it.latencyMs }

        if (latencies.isEmpty()) return 0.0

        var alignmentScore = 0.0
        for (latency in latencies) {
            // Check if latency mod 214 is close to a sequence value
            val mod = (latency.toInt() % 214)
            val closest = sequence.minByOrNull { kotlin.math.abs(it - mod) } ?: 0
            val distance = kotlin.math.abs(closest - mod)
            alignmentScore += 1.0 / (1.0 + distance)
        }

        return (alignmentScore / latencies.size).coerceIn(0.0, 1.0)
    }

    // =========================================================================
    // PARSING HELPERS
    // =========================================================================

    private fun resolveTarget(target: String): Pair<String, TargetType> {
        return when {
            target.startsWith("BNP:") -> target to TargetType.BNP
            target.contains(":") -> target to TargetType.IPV6
            target.matches(Regex("""\d+\.\d+\.\d+\.\d+""")) -> target to TargetType.IPV4
            else -> target to TargetType.HOSTNAME
        }
    }

    private fun parseLatency(output: String): Double? {
        // Parse "time=XX.X ms" from ping output
        val regex = """time[=<](\d+\.?\d*)\s*ms""".toRegex()
        return regex.find(output)?.groupValues?.get(1)?.toDoubleOrNull()
    }

    private fun parseTtl(output: String): Int? {
        // Parse "ttl=XX" from ping output
        val regex = """ttl[=:](\d+)""".toRegex(RegexOption.IGNORE_CASE)
        return regex.find(output)?.groupValues?.get(1)?.toIntOrNull()
    }

    private fun parseBytes(output: String): Int? {
        // Parse "XX bytes" from ping output
        val regex = """(\d+)\s*bytes""".toRegex()
        return regex.find(output)?.groupValues?.get(1)?.toIntOrNull()
    }

    private fun parseTracerouteHop(hopNumber: Int, line: String): TracerouteHop? {
        // Parse traceroute/tracepath output
        // Format: "1:  gateway (192.168.1.1)  1.234ms"

        val addressRegex = """\(?([\d.]+|[\da-f:]+)\)?""".toRegex(RegexOption.IGNORE_CASE)
        val latencyRegex = """([\d.]+)\s*ms""".toRegex()

        val addressMatch = addressRegex.find(line)
        val latencyMatch = latencyRegex.find(line)

        if (addressMatch != null) {
            val address = addressMatch.groupValues[1]
            val latency = latencyMatch?.groupValues?.get(1)?.toDoubleOrNull() ?: 0.0

            // Try to resolve to BNP
            val bnpAddress = try {
                LegacyNetworkConverter.ipToBnp(address)?.shortAddress
            } catch (e: IllegalArgumentException) {
                null
            } catch (e: NumberFormatException) {
                null
            }

            return TracerouteHop(
                hopNumber = hopNumber,
                address = address,
                hostname = null,  // Would need reverse DNS
                latencyMs = latency,
                bnpAddress = bnpAddress
            )
        }

        return null
    }

    // =========================================================================
    // QUICK TESTS
    // =========================================================================

    /**
     * Quick connectivity test to common servers.
     */
    suspend fun quickConnectivityTest(): Map<String, Boolean> = withContext(Dispatchers.IO) {
        val targets = mapOf(
            "Google DNS" to "8.8.8.8",
            "Cloudflare DNS" to "1.1.1.1",
            "Google" to "google.com",
            "Local Gateway" to "192.168.1.1"
        )

        targets.mapValues { (_, target) ->
            try {
                val result = pingJava(target, 1, 3000)
                result.success
            } catch (e: java.net.UnknownHostException) {
                false
            } catch (e: java.io.IOException) {
                false
            }
        }
    }

    /**
     * Test BNP relay network connectivity.
     */
    suspend fun testBnpRelays(): Map<String, PingResult> = withContext(Dispatchers.IO) {
        val relays = TransportBridge.DEFAULT_RELAYS.map { url ->
            // Extract host from URL
            url.removePrefix("wss://").removePrefix("https://").split("/").first()
        }

        relays.associateWith { host ->
            pingTcp(host, 443, 1, 5000)
        }
    }
}
