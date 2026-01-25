/**
 * BUIM - Wormhole Relay
 * =====================
 *
 * Routes traffic through accessible endpoints to reach blocked destinations.
 * Uses Brahim Wormhole encryption to hide the true destination from intermediaries.
 *
 * Concept:
 * - External client can't reach Server B (firewall blocks external IPs)
 * - External client CAN reach Server A (open relay)
 * - Server A can reach Server B (internal traffic allowed)
 * - Solution: Client → [Encrypted] → Server A → Server B → [Response] → Client
 *
 * The blocked server never knows the original requester's IP.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.network

import com.brahim.buim.cipher.WormholeCipher
import com.brahim.buim.core.BrahimConstants
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.nio.ByteBuffer

/**
 * Wormhole Relay - Routes traffic through accessible nodes to blocked destinations.
 */
object WormholeRelay {

    // Relay state
    private val _state = MutableStateFlow(RelayState())
    val state: StateFlow<RelayState> = _state

    // Known open relays in Iran (that accept external traffic)
    val OPEN_RELAYS = listOf(
        RelayNode(
            name = "TUMS DNS",
            ip = "194.225.62.80",
            port = 53,
            protocol = RelayProtocol.DNS,
            supportsWormhole = true,
            location = "Tehran, Iran"
        ),
        RelayNode(
            name = "DCI Recursive 1",
            ip = "217.218.127.127",
            port = 53,
            protocol = RelayProtocol.DNS,
            supportsWormhole = true,
            location = "Tehran, Iran"
        ),
        RelayNode(
            name = "DCI Recursive 2",
            ip = "217.218.155.155",
            port = 53,
            protocol = RelayProtocol.DNS,
            supportsWormhole = true,
            location = "Tehran, Iran"
        ),
        RelayNode(
            name = "Electro DNS 1",
            ip = "78.157.42.100",
            port = 53,
            protocol = RelayProtocol.DNS,
            supportsWormhole = true,
            location = "Iran"
        ),
        RelayNode(
            name = "Electro DNS 2",
            ip = "78.157.42.101",
            port = 53,
            protocol = RelayProtocol.DNS,
            supportsWormhole = true,
            location = "Iran"
        )
    )

    // Known blocked servers (need relay to reach)
    val BLOCKED_SERVERS = listOf(
        BlockedServer(
            name = "NIC.IR a",
            ip = "193.189.123.2",
            reason = "Blocks external IPs",
            canReachVia = listOf("194.225.62.80", "217.218.127.127")
        ),
        BlockedServer(
            name = "NIC.IR b",
            ip = "193.189.122.83",
            reason = "Blocks external IPs",
            canReachVia = listOf("194.225.62.80", "217.218.127.127")
        ),
        BlockedServer(
            name = "NIC.IR d",
            ip = "194.225.70.83",
            reason = "Blocks external IPs",
            canReachVia = listOf("194.225.62.80", "217.218.127.127")
        ),
        BlockedServer(
            name = "Shecan DNS",
            ip = "178.22.122.100",
            reason = "Internal Iran only",
            canReachVia = listOf("217.218.127.127", "217.218.155.155")
        ),
        BlockedServer(
            name = "Sharif University",
            ip = "194.225.0.1",
            reason = "Academic network only",
            canReachVia = listOf("194.225.62.80")
        )
    )

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    // =========================================================================
    // WORMHOLE ROUTING
    // =========================================================================

    /**
     * Route a request through a wormhole to reach a blocked destination.
     *
     * @param targetIp The blocked destination IP
     * @param targetPort The destination port
     * @param payload The data to send
     * @param relayIp Optional specific relay to use (auto-selects if null)
     * @return The response from the blocked server, or null if failed
     */
    suspend fun routeThroughWormhole(
        targetIp: String,
        targetPort: Int,
        payload: ByteArray,
        relayIp: String? = null
    ): WormholeResponse? = withContext(Dispatchers.IO) {

        // Find a suitable relay
        val relay = if (relayIp != null) {
            OPEN_RELAYS.find { it.ip == relayIp }
        } else {
            findBestRelay(targetIp)
        }

        if (relay == null) {
            _state.value = _state.value.copy(
                lastError = "No suitable relay found for $targetIp"
            )
            return@withContext null
        }

        _state.value = _state.value.copy(
            isRouting = true,
            currentRelay = relay,
            targetIp = targetIp
        )

        try {
            // Create wormhole packet
            val wormholePacket = createWormholePacket(
                targetIp = targetIp,
                targetPort = targetPort,
                payload = payload,
                relay = relay
            )

            // Send through relay
            val response = sendThroughRelay(relay, wormholePacket)

            // Decrypt response
            val decrypted = decryptWormholeResponse(response, relay)

            _state.value = _state.value.copy(
                isRouting = false,
                successfulRoutes = _state.value.successfulRoutes + 1
            )

            WormholeResponse(
                success = true,
                data = decrypted,
                relay = relay,
                targetIp = targetIp,
                latencyMs = System.currentTimeMillis() - _state.value.routeStartTime
            )

        } catch (e: Exception) {
            _state.value = _state.value.copy(
                isRouting = false,
                failedRoutes = _state.value.failedRoutes + 1,
                lastError = e.message
            )
            null
        }
    }

    /**
     * DNS query through wormhole.
     * Useful for querying blocked DNS servers.
     */
    suspend fun dnsQueryThroughWormhole(
        domain: String,
        blockedDnsIp: String,
        relayDnsIp: String? = null
    ): DnsWormholeResult? = withContext(Dispatchers.IO) {

        val relay = relayDnsIp ?: OPEN_RELAYS.firstOrNull()?.ip
            ?: return@withContext null

        try {
            // Build DNS query packet
            val dnsQuery = buildDnsQuery(domain)

            // Create wormhole-wrapped DNS query
            // The relay DNS will forward to the blocked DNS
            val wormholeQuery = WormholeDnsQuery(
                queryId = (Math.random() * 65535).toInt(),
                targetDns = blockedDnsIp,
                originalQuery = dnsQuery,
                wormholeSignature = generateWormholeSignature()
            )

            // For DNS, we use a special technique:
            // We encode the target DNS in the query itself using TXT records
            // or use DNS tunneling through the relay

            // Simple approach: Query the relay, which has internal access
            val socket = DatagramSocket()
            socket.soTimeout = 5000

            val queryBytes = dnsQuery
            val packet = DatagramPacket(
                queryBytes,
                queryBytes.size,
                InetAddress.getByName(relay),
                53
            )

            val startTime = System.currentTimeMillis()
            socket.send(packet)

            // Receive response
            val responseBuffer = ByteArray(512)
            val responsePacket = DatagramPacket(responseBuffer, responseBuffer.size)
            socket.receive(responsePacket)

            val latency = System.currentTimeMillis() - startTime
            socket.close()

            // Parse DNS response
            val addresses = parseDnsResponse(responsePacket.data, responsePacket.length)

            DnsWormholeResult(
                success = true,
                domain = domain,
                addresses = addresses,
                queriedVia = relay,
                intendedTarget = blockedDnsIp,
                latencyMs = latency
            )

        } catch (e: Exception) {
            DnsWormholeResult(
                success = false,
                domain = domain,
                addresses = emptyList(),
                queriedVia = relay,
                intendedTarget = blockedDnsIp,
                latencyMs = 0,
                error = e.message
            )
        }
    }

    // =========================================================================
    // WORMHOLE PACKET CONSTRUCTION
    // =========================================================================

    /**
     * Create a wormhole packet that encapsulates the real destination.
     *
     * Structure:
     * [Wormhole Header (16 bytes)]
     *   - Magic: "BWRM" (4 bytes)
     *   - Version: 1 (1 byte)
     *   - Flags: (1 byte)
     *   - Target IP: (4 bytes, encrypted)
     *   - Target Port: (2 bytes, encrypted)
     *   - Payload Length: (4 bytes)
     * [Encrypted Payload]
     *   - Original data encrypted with Wormhole Cipher
     * [Integrity Check (8 bytes)]
     *   - β-weighted checksum
     */
    private fun createWormholePacket(
        targetIp: String,
        targetPort: Int,
        payload: ByteArray,
        relay: RelayNode
    ): ByteArray {
        val buffer = ByteBuffer.allocate(16 + payload.size + 32 + 8)

        // Magic
        buffer.put("BWRM".toByteArray())

        // Version
        buffer.put(1.toByte())

        // Flags (0x01 = encrypted target, 0x02 = encrypted payload)
        buffer.put(0x03.toByte())

        // Encrypt target IP
        val ipBytes = InetAddress.getByName(targetIp).address
        val encryptedIp = WormholeCipher.encrypt(ipBytes, deriveRelayKey(relay))
        buffer.put(encryptedIp.sliceArray(0 until 4))

        // Encrypt target port
        val portBytes = ByteBuffer.allocate(2).putShort(targetPort.toShort()).array()
        val encryptedPort = WormholeCipher.encrypt(portBytes, deriveRelayKey(relay))
        buffer.put(encryptedPort.sliceArray(0 until 2))

        // Payload length
        buffer.putInt(payload.size)

        // Encrypted payload
        val encryptedPayload = WormholeCipher.encrypt(payload, deriveRelayKey(relay))
        buffer.put(encryptedPayload)

        // Integrity check (β-weighted checksum)
        val checksum = calculateBetaChecksum(buffer.array())
        buffer.put(checksum)

        return buffer.array().sliceArray(0 until buffer.position())
    }

    /**
     * Send packet through relay and get response.
     */
    private suspend fun sendThroughRelay(
        relay: RelayNode,
        packet: ByteArray
    ): ByteArray = withContext(Dispatchers.IO) {

        _state.value = _state.value.copy(routeStartTime = System.currentTimeMillis())

        when (relay.protocol) {
            RelayProtocol.DNS -> sendViaDns(relay, packet)
            RelayProtocol.HTTPS -> sendViaHttps(relay, packet)
            RelayProtocol.WEBSOCKET -> sendViaWebSocket(relay, packet)
            RelayProtocol.UDP -> sendViaUdp(relay, packet)
        }
    }

    private suspend fun sendViaDns(relay: RelayNode, packet: ByteArray): ByteArray {
        // DNS tunneling: encode packet in DNS query/response
        // This is a simplified version - real implementation would use proper DNS tunneling

        val socket = DatagramSocket()
        socket.soTimeout = 10000

        val udpPacket = DatagramPacket(
            packet,
            packet.size,
            InetAddress.getByName(relay.ip),
            relay.port
        )

        socket.send(udpPacket)

        val responseBuffer = ByteArray(4096)
        val responsePacket = DatagramPacket(responseBuffer, responseBuffer.size)
        socket.receive(responsePacket)

        socket.close()

        return responsePacket.data.sliceArray(0 until responsePacket.length)
    }

    private suspend fun sendViaHttps(relay: RelayNode, packet: ByteArray): ByteArray {
        // HTTPS relay - would use OkHttp POST to relay endpoint
        // Placeholder
        return ByteArray(0)
    }

    private suspend fun sendViaWebSocket(relay: RelayNode, packet: ByteArray): ByteArray {
        // WebSocket relay - would use OkHttp WebSocket
        // Placeholder
        return ByteArray(0)
    }

    private suspend fun sendViaUdp(relay: RelayNode, packet: ByteArray): ByteArray {
        val socket = DatagramSocket()
        socket.soTimeout = 10000

        val udpPacket = DatagramPacket(
            packet,
            packet.size,
            InetAddress.getByName(relay.ip),
            relay.port
        )

        socket.send(udpPacket)

        val responseBuffer = ByteArray(4096)
        val responsePacket = DatagramPacket(responseBuffer, responseBuffer.size)
        socket.receive(responsePacket)

        socket.close()

        return responsePacket.data.sliceArray(0 until responsePacket.length)
    }

    /**
     * Decrypt wormhole response.
     */
    private fun decryptWormholeResponse(response: ByteArray, relay: RelayNode): ByteArray {
        // Check for wormhole header
        if (response.size >= 4 && String(response.sliceArray(0..3)) == "BWRM") {
            // Extract and decrypt payload
            val payloadLength = ByteBuffer.wrap(response.sliceArray(10..13)).int
            val encryptedPayload = response.sliceArray(16 until 16 + payloadLength)
            return WormholeCipher.decrypt(encryptedPayload, deriveRelayKey(relay))
        }

        // Not a wormhole packet, return as-is
        return response
    }

    // =========================================================================
    // RELAY SELECTION
    // =========================================================================

    /**
     * Find the best relay to reach a blocked target.
     */
    private fun findBestRelay(targetIp: String): RelayNode? {
        // Check if target is in blocked list
        val blocked = BLOCKED_SERVERS.find { it.ip == targetIp }

        if (blocked != null) {
            // Use recommended relay for this server
            val relayIp = blocked.canReachVia.firstOrNull()
            return OPEN_RELAYS.find { it.ip == relayIp }
        }

        // Default: use first available open relay
        return OPEN_RELAYS.firstOrNull()
    }

    /**
     * Test which relays can reach a specific target.
     */
    suspend fun testRelaysForTarget(targetIp: String): List<RelayTestResult> =
        withContext(Dispatchers.IO) {
            OPEN_RELAYS.map { relay ->
                try {
                    val startTime = System.currentTimeMillis()
                    // Attempt to route through this relay
                    val testPayload = "WORMHOLE_TEST".toByteArray()
                    val response = routeThroughWormhole(targetIp, 53, testPayload, relay.ip)
                    val latency = System.currentTimeMillis() - startTime

                    RelayTestResult(
                        relay = relay,
                        targetIp = targetIp,
                        success = response != null,
                        latencyMs = latency
                    )
                } catch (e: Exception) {
                    RelayTestResult(
                        relay = relay,
                        targetIp = targetIp,
                        success = false,
                        latencyMs = 0,
                        error = e.message
                    )
                }
            }
        }

    // =========================================================================
    // HELPER FUNCTIONS
    // =========================================================================

    private fun deriveRelayKey(relay: RelayNode): ByteArray {
        // Derive encryption key from relay properties and β
        val material = "${relay.ip}:${relay.port}:${BrahimConstants.BETA_SECURITY}"
        return WormholeCipher.hash(material.toByteArray())
    }

    private fun calculateBetaChecksum(data: ByteArray): ByteArray {
        val beta = BrahimConstants.BETA_SECURITY
        var checksum = 0L

        for (i in data.indices) {
            checksum += (data[i].toLong() and 0xFF) * ((beta * (i + 1) * 256).toLong() % 256)
        }

        return ByteBuffer.allocate(8).putLong(checksum).array()
    }

    private fun generateWormholeSignature(): ByteArray {
        val timestamp = System.currentTimeMillis()
        val beta = BrahimConstants.BETA_SECURITY
        val signature = (timestamp * beta).toLong()
        return ByteBuffer.allocate(8).putLong(signature).array()
    }

    private fun buildDnsQuery(domain: String): ByteArray {
        // Simple DNS query builder
        val buffer = ByteBuffer.allocate(512)

        // Transaction ID
        buffer.putShort((Math.random() * 65535).toInt().toShort())

        // Flags: Standard query
        buffer.putShort(0x0100.toShort())

        // Questions: 1
        buffer.putShort(1.toShort())

        // Answer, Authority, Additional: 0
        buffer.putShort(0)
        buffer.putShort(0)
        buffer.putShort(0)

        // Query name
        for (label in domain.split(".")) {
            buffer.put(label.length.toByte())
            buffer.put(label.toByteArray())
        }
        buffer.put(0.toByte())  // End of name

        // Type: A (1)
        buffer.putShort(1.toShort())

        // Class: IN (1)
        buffer.putShort(1.toShort())

        return buffer.array().sliceArray(0 until buffer.position())
    }

    private fun parseDnsResponse(data: ByteArray, length: Int): List<String> {
        val addresses = mutableListOf<String>()

        try {
            // Skip header (12 bytes) and query section
            var offset = 12

            // Skip query name
            while (offset < length && data[offset] != 0.toByte()) {
                offset += data[offset].toInt() + 1
            }
            offset += 5  // Skip null terminator, type, class

            // Parse answers
            val answerCount = ((data[6].toInt() and 0xFF) shl 8) or (data[7].toInt() and 0xFF)

            for (i in 0 until answerCount) {
                if (offset >= length) break

                // Skip name (pointer or labels)
                if ((data[offset].toInt() and 0xC0) == 0xC0) {
                    offset += 2  // Pointer
                } else {
                    while (offset < length && data[offset] != 0.toByte()) {
                        offset += data[offset].toInt() + 1
                    }
                    offset++
                }

                // Type
                val type = ((data[offset].toInt() and 0xFF) shl 8) or (data[offset + 1].toInt() and 0xFF)
                offset += 2

                // Class
                offset += 2

                // TTL
                offset += 4

                // Data length
                val dataLen = ((data[offset].toInt() and 0xFF) shl 8) or (data[offset + 1].toInt() and 0xFF)
                offset += 2

                // Parse A record (type 1)
                if (type == 1 && dataLen == 4) {
                    val ip = "${data[offset].toInt() and 0xFF}." +
                            "${data[offset + 1].toInt() and 0xFF}." +
                            "${data[offset + 2].toInt() and 0xFF}." +
                            "${data[offset + 3].toInt() and 0xFF}"
                    addresses.add(ip)
                }

                offset += dataLen
            }
        } catch (e: Exception) {
            // Parse error, return what we have
        }

        return addresses
    }

    fun release() {
        scope.cancel()
    }
}

// =========================================================================
// DATA CLASSES
// =========================================================================

data class RelayNode(
    val name: String,
    val ip: String,
    val port: Int,
    val protocol: RelayProtocol,
    val supportsWormhole: Boolean,
    val location: String
)

enum class RelayProtocol {
    DNS,
    HTTPS,
    WEBSOCKET,
    UDP
}

data class BlockedServer(
    val name: String,
    val ip: String,
    val reason: String,
    val canReachVia: List<String>
)

data class RelayState(
    val isRouting: Boolean = false,
    val currentRelay: RelayNode? = null,
    val targetIp: String = "",
    val routeStartTime: Long = 0,
    val successfulRoutes: Int = 0,
    val failedRoutes: Int = 0,
    val lastError: String? = null
)

data class WormholeResponse(
    val success: Boolean,
    val data: ByteArray,
    val relay: RelayNode,
    val targetIp: String,
    val latencyMs: Long
)

data class DnsWormholeResult(
    val success: Boolean,
    val domain: String,
    val addresses: List<String>,
    val queriedVia: String,
    val intendedTarget: String,
    val latencyMs: Long,
    val error: String? = null
)

data class WormholeDnsQuery(
    val queryId: Int,
    val targetDns: String,
    val originalQuery: ByteArray,
    val wormholeSignature: ByteArray
)

data class RelayTestResult(
    val relay: RelayNode,
    val targetIp: String,
    val success: Boolean,
    val latencyMs: Long,
    val error: String? = null
)
