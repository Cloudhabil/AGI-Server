/**
 * BUIM - Wormhole Exit Node
 * =========================
 *
 * Deployed on accessible servers to bridge traffic to blocked infrastructure.
 * The blocked servers see traffic coming from the Exit Node (internal IP),
 * not from the external client.
 *
 * Deployment:
 * - Install on server with external access (e.g., 194.225.62.80 TUMS)
 * - Exit Node accepts encrypted requests from anywhere
 * - Forwards to blocked internal servers
 * - Returns encrypted responses
 *
 * The blocked servers never see external IPs - only the Exit Node's IP.
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
import java.net.*
import java.nio.ByteBuffer
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

/**
 * Wormhole Exit Node - Bridge external traffic to blocked internal servers.
 *
 * This would be deployed on a server inside the restricted network that
 * has both external access AND internal access to blocked services.
 */
class WormholeExitNode(
    private val config: ExitNodeConfig
) {
    // State
    private val _state = MutableStateFlow(ExitNodeState())
    val state: StateFlow<ExitNodeState> = _state

    // Statistics
    private val requestsReceived = AtomicLong(0)
    private val requestsForwarded = AtomicLong(0)
    private val bytesIn = AtomicLong(0)
    private val bytesOut = AtomicLong(0)

    // Active connections
    private val activeConnections = ConcurrentHashMap<String, ConnectionInfo>()

    // Allowed destination whitelist (blocked servers we can reach)
    private val allowedDestinations = mutableSetOf<String>()

    // Coroutine scope
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    // Servers
    private var udpServer: DatagramSocket? = null
    private var tcpServer: ServerSocket? = null

    // =========================================================================
    // EXIT NODE LIFECYCLE
    // =========================================================================

    /**
     * Start the Exit Node.
     * Begins listening for incoming wormhole requests.
     */
    fun start() {
        if (_state.value.isRunning) return

        _state.value = _state.value.copy(
            isRunning = true,
            startTime = System.currentTimeMillis()
        )

        // Add default allowed destinations (blocked servers we can reach internally)
        allowedDestinations.addAll(config.allowedDestinations)

        // Start UDP listener (for DNS-style requests)
        scope.launch { startUdpListener() }

        // Start TCP listener (for HTTPS/WebSocket requests)
        scope.launch { startTcpListener() }

        // Start statistics reporter
        scope.launch { reportStatistics() }

        println("""
            ╔═══════════════════════════════════════════════════════════════╗
            ║           WORMHOLE EXIT NODE STARTED                          ║
            ╠═══════════════════════════════════════════════════════════════╣
            ║  Node ID:     ${config.nodeId.take(16)}...
            ║  Listen IP:   ${config.listenIp}
            ║  UDP Port:    ${config.udpPort}
            ║  TCP Port:    ${config.tcpPort}
            ║  Allowed:     ${allowedDestinations.size} destinations
            ╚═══════════════════════════════════════════════════════════════╝
        """.trimIndent())
    }

    /**
     * Stop the Exit Node.
     */
    fun stop() {
        _state.value = _state.value.copy(isRunning = false)

        udpServer?.close()
        tcpServer?.close()
        scope.cancel()

        println("Wormhole Exit Node stopped.")
    }

    // =========================================================================
    // UDP LISTENER (DNS-style)
    // =========================================================================

    private suspend fun startUdpListener() = withContext(Dispatchers.IO) {
        try {
            udpServer = DatagramSocket(config.udpPort, InetAddress.getByName(config.listenIp))

            println("[UDP] Listening on ${config.listenIp}:${config.udpPort}")

            val buffer = ByteArray(4096)

            while (_state.value.isRunning) {
                val packet = DatagramPacket(buffer, buffer.size)

                try {
                    udpServer?.receive(packet)

                    requestsReceived.incrementAndGet()
                    bytesIn.addAndGet(packet.length.toLong())

                    // Process in separate coroutine
                    scope.launch {
                        handleUdpRequest(packet)
                    }
                } catch (e: SocketTimeoutException) {
                    // Normal timeout, continue
                } catch (e: Exception) {
                    if (_state.value.isRunning) {
                        println("[UDP] Error: ${e.message}")
                    }
                }
            }
        } catch (e: Exception) {
            println("[UDP] Failed to start: ${e.message}")
            _state.value = _state.value.copy(lastError = e.message)
        }
    }

    private suspend fun handleUdpRequest(packet: DatagramPacket) {
        val clientAddress = packet.address
        val clientPort = packet.port
        val data = packet.data.sliceArray(0 until packet.length)

        // Check if it's a wormhole packet
        if (isWormholePacket(data)) {
            handleWormholeRequest(data, clientAddress, clientPort, TransportType.UDP)
        } else {
            // Regular DNS query - check if we should forward
            handleRegularDnsQuery(data, clientAddress, clientPort)
        }
    }

    // =========================================================================
    // TCP LISTENER (HTTPS/WebSocket)
    // =========================================================================

    private suspend fun startTcpListener() = withContext(Dispatchers.IO) {
        try {
            tcpServer = ServerSocket(config.tcpPort, 50, InetAddress.getByName(config.listenIp))

            println("[TCP] Listening on ${config.listenIp}:${config.tcpPort}")

            while (_state.value.isRunning) {
                try {
                    val clientSocket = tcpServer?.accept() ?: break

                    requestsReceived.incrementAndGet()

                    // Handle in separate coroutine
                    scope.launch {
                        handleTcpConnection(clientSocket)
                    }
                } catch (e: Exception) {
                    if (_state.value.isRunning) {
                        println("[TCP] Error: ${e.message}")
                    }
                }
            }
        } catch (e: Exception) {
            println("[TCP] Failed to start: ${e.message}")
            _state.value = _state.value.copy(lastError = e.message)
        }
    }

    private suspend fun handleTcpConnection(clientSocket: Socket) = withContext(Dispatchers.IO) {
        try {
            val inputStream = clientSocket.getInputStream()
            val outputStream = clientSocket.getOutputStream()

            // Read request
            val buffer = ByteArray(8192)
            val bytesRead = inputStream.read(buffer)

            if (bytesRead > 0) {
                bytesIn.addAndGet(bytesRead.toLong())
                val data = buffer.sliceArray(0 until bytesRead)

                if (isWormholePacket(data)) {
                    val response = processWormholeRequest(data)
                    outputStream.write(response)
                    bytesOut.addAndGet(response.size.toLong())
                }
            }

            clientSocket.close()
        } catch (e: Exception) {
            println("[TCP] Connection error: ${e.message}")
        }
    }

    // =========================================================================
    // WORMHOLE REQUEST PROCESSING
    // =========================================================================

    private fun isWormholePacket(data: ByteArray): Boolean {
        return data.size >= 4 && String(data.sliceArray(0..3)) == "BWRM"
    }

    private suspend fun handleWormholeRequest(
        data: ByteArray,
        clientAddress: InetAddress,
        clientPort: Int,
        transport: TransportType
    ) {
        val response = processWormholeRequest(data)

        when (transport) {
            TransportType.UDP -> {
                val responsePacket = DatagramPacket(
                    response,
                    response.size,
                    clientAddress,
                    clientPort
                )
                udpServer?.send(responsePacket)
                bytesOut.addAndGet(response.size.toLong())
            }
            TransportType.TCP -> {
                // Handled in TCP connection handler
            }
        }

        requestsForwarded.incrementAndGet()
    }

    /**
     * Process a wormhole request:
     * 1. Decrypt to get real destination
     * 2. Forward to blocked server (appears as internal traffic)
     * 3. Encrypt response
     * 4. Return to client
     */
    private suspend fun processWormholeRequest(data: ByteArray): ByteArray = withContext(Dispatchers.IO) {
        try {
            // Parse wormhole header
            // [BWRM][Version][Flags][Encrypted Target IP][Encrypted Port][Payload Length][Encrypted Payload]

            val version = data[4].toInt()
            val flags = data[5].toInt()

            // Decrypt target IP
            val encryptedIp = data.sliceArray(6..9)
            val targetIpBytes = WormholeCipher.decrypt(encryptedIp, config.nodeKey)
            val targetIp = InetAddress.getByAddress(targetIpBytes).hostAddress

            // Decrypt target port
            val encryptedPort = data.sliceArray(10..11)
            val targetPortBytes = WormholeCipher.decrypt(encryptedPort, config.nodeKey)
            val targetPort = ByteBuffer.wrap(targetPortBytes).short.toInt() and 0xFFFF

            // Check if destination is allowed
            if (!isDestinationAllowed(targetIp)) {
                println("[BLOCKED] Request to non-whitelisted destination: $targetIp")
                return@withContext createErrorResponse("Destination not allowed")
            }

            // Get payload length and decrypt payload
            val payloadLength = ByteBuffer.wrap(data.sliceArray(12..15)).int
            val encryptedPayload = data.sliceArray(16 until 16 + payloadLength)
            val payload = WormholeCipher.decrypt(encryptedPayload, config.nodeKey)

            println("[FORWARD] ${data.size} bytes → $targetIp:$targetPort")

            // Forward to blocked server
            val response = forwardToBlockedServer(targetIp, targetPort, payload)

            // Encrypt response
            val encryptedResponse = WormholeCipher.encrypt(response, config.nodeKey)

            // Build wormhole response
            createWormholeResponse(encryptedResponse)

        } catch (e: Exception) {
            println("[ERROR] Processing wormhole request: ${e.message}")
            createErrorResponse(e.message ?: "Unknown error")
        }
    }

    /**
     * Forward request to blocked server.
     * The blocked server sees this Exit Node's IP, not the external client.
     */
    private suspend fun forwardToBlockedServer(
        targetIp: String,
        targetPort: Int,
        payload: ByteArray
    ): ByteArray = withContext(Dispatchers.IO) {

        // Use UDP for DNS (port 53)
        if (targetPort == 53) {
            return@withContext forwardDns(targetIp, payload)
        }

        // Use TCP for other ports
        return@withContext forwardTcp(targetIp, targetPort, payload)
    }

    private fun forwardDns(targetIp: String, query: ByteArray): ByteArray {
        val socket = DatagramSocket()
        socket.soTimeout = 5000

        val packet = DatagramPacket(
            query,
            query.size,
            InetAddress.getByName(targetIp),
            53
        )

        socket.send(packet)

        val responseBuffer = ByteArray(512)
        val responsePacket = DatagramPacket(responseBuffer, responseBuffer.size)
        socket.receive(responsePacket)

        socket.close()

        return responsePacket.data.sliceArray(0 until responsePacket.length)
    }

    private fun forwardTcp(targetIp: String, targetPort: Int, payload: ByteArray): ByteArray {
        val socket = Socket()
        socket.connect(InetSocketAddress(targetIp, targetPort), 5000)
        socket.soTimeout = 10000

        socket.getOutputStream().write(payload)

        val response = socket.getInputStream().readBytes()
        socket.close()

        return response
    }

    // =========================================================================
    // REGULAR DNS FORWARDING
    // =========================================================================

    private suspend fun handleRegularDnsQuery(
        data: ByteArray,
        clientAddress: InetAddress,
        clientPort: Int
    ) {
        // Forward to configured upstream DNS
        val response = forwardDns(config.upstreamDns, data)

        val responsePacket = DatagramPacket(
            response,
            response.size,
            clientAddress,
            clientPort
        )

        udpServer?.send(responsePacket)
        bytesOut.addAndGet(response.size.toLong())
        requestsForwarded.incrementAndGet()
    }

    // =========================================================================
    // HELPERS
    // =========================================================================

    private fun isDestinationAllowed(ip: String): Boolean {
        // Allow if in whitelist
        if (allowedDestinations.contains(ip)) return true

        // Allow if in same /24 subnet as any whitelisted IP
        val targetPrefix = ip.substringBeforeLast(".")
        return allowedDestinations.any { it.substringBeforeLast(".") == targetPrefix }
    }

    private fun createWormholeResponse(encryptedPayload: ByteArray): ByteArray {
        val buffer = ByteBuffer.allocate(16 + encryptedPayload.size)

        // Magic
        buffer.put("BWRM".toByteArray())

        // Version
        buffer.put(1.toByte())

        // Flags (response)
        buffer.put(0x80.toByte())

        // Reserved
        buffer.put(ByteArray(6))

        // Payload length
        buffer.putInt(encryptedPayload.size)

        // Encrypted payload
        buffer.put(encryptedPayload)

        return buffer.array()
    }

    private fun createErrorResponse(message: String): ByteArray {
        val errorPayload = "ERROR:$message".toByteArray()
        val encrypted = WormholeCipher.encrypt(errorPayload, config.nodeKey)
        return createWormholeResponse(encrypted)
    }

    /**
     * Add a destination to the whitelist.
     */
    fun addAllowedDestination(ip: String) {
        allowedDestinations.add(ip)
        println("[CONFIG] Added allowed destination: $ip")
    }

    /**
     * Remove a destination from the whitelist.
     */
    fun removeAllowedDestination(ip: String) {
        allowedDestinations.remove(ip)
        println("[CONFIG] Removed allowed destination: $ip")
    }

    // =========================================================================
    // STATISTICS
    // =========================================================================

    private suspend fun reportStatistics() {
        while (_state.value.isRunning) {
            delay(60000)  // Every minute

            val stats = ExitNodeStats(
                uptime = System.currentTimeMillis() - _state.value.startTime,
                requestsReceived = requestsReceived.get(),
                requestsForwarded = requestsForwarded.get(),
                bytesIn = bytesIn.get(),
                bytesOut = bytesOut.get(),
                activeConnections = activeConnections.size,
                allowedDestinations = allowedDestinations.size
            )

            _state.value = _state.value.copy(stats = stats)

            println("""
                [STATS] Uptime: ${stats.uptime / 1000}s |
                Requests: ${stats.requestsReceived} in, ${stats.requestsForwarded} fwd |
                Traffic: ${stats.bytesIn / 1024}KB in, ${stats.bytesOut / 1024}KB out
            """.trimIndent().replace("\n", ""))
        }
    }

    fun getStats(): ExitNodeStats {
        return ExitNodeStats(
            uptime = System.currentTimeMillis() - _state.value.startTime,
            requestsReceived = requestsReceived.get(),
            requestsForwarded = requestsForwarded.get(),
            bytesIn = bytesIn.get(),
            bytesOut = bytesOut.get(),
            activeConnections = activeConnections.size,
            allowedDestinations = allowedDestinations.size
        )
    }
}

// =========================================================================
// CONFIGURATION & DATA CLASSES
// =========================================================================

/**
 * Exit Node configuration.
 */
data class ExitNodeConfig(
    val nodeId: String,                          // Unique node identifier
    val nodeKey: ByteArray,                      // Wormhole encryption key
    val listenIp: String = "0.0.0.0",           // IP to listen on
    val udpPort: Int = 5353,                     // UDP port (DNS-style)
    val tcpPort: Int = 8443,                     // TCP port (HTTPS-style)
    val upstreamDns: String = "8.8.8.8",        // Fallback DNS
    val allowedDestinations: Set<String> = setOf(  // Blocked servers we can reach
        "193.189.123.2",    // a.nic.ir
        "193.189.122.83",   // b.nic.ir
        "194.225.70.83",    // d.nic.ir
        "178.22.122.100",   // Shecan
        "185.51.200.2",     // Shecan 2
        "194.225.0.1",      // Sharif
        "185.55.226.26"     // Begzar
    )
)

data class ExitNodeState(
    val isRunning: Boolean = false,
    val startTime: Long = 0,
    val lastError: String? = null,
    val stats: ExitNodeStats? = null
)

data class ExitNodeStats(
    val uptime: Long,
    val requestsReceived: Long,
    val requestsForwarded: Long,
    val bytesIn: Long,
    val bytesOut: Long,
    val activeConnections: Int,
    val allowedDestinations: Int
)

data class ConnectionInfo(
    val clientIp: String,
    val connectedAt: Long,
    val bytesTransferred: Long
)

enum class TransportType {
    UDP,
    TCP
}

// =========================================================================
// FACTORY / BUILDER
// =========================================================================

/**
 * Create an Exit Node for Iranian infrastructure.
 */
fun createIranExitNode(
    nodeKey: ByteArray,
    listenPort: Int = 5353
): WormholeExitNode {
    val config = ExitNodeConfig(
        nodeId = "IR-EXIT-${System.currentTimeMillis()}",
        nodeKey = nodeKey,
        udpPort = listenPort,
        tcpPort = listenPort + 1,
        allowedDestinations = setOf(
            // NIC.IR (Domain Registry)
            "193.189.123.2",    // a.nic.ir
            "193.189.122.83",   // b.nic.ir
            "45.93.171.206",    // c.nic.ir
            "194.225.70.83",    // d.nic.ir

            // Anti-sanction DNS
            "178.22.122.100",   // Shecan 1
            "185.51.200.2",     // Shecan 2

            // Universities
            "194.225.0.1",      // Sharif
            "194.225.24.1",     // Tehran University
            "194.225.62.80",    // TUMS

            // ISP DNS
            "85.15.1.14",       // Afranet
            "5.200.200.200"     // Pishgaman
        )
    )

    return WormholeExitNode(config)
}
