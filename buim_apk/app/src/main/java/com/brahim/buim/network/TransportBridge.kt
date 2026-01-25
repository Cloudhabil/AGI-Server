/**
 * BUIM - Transport Bridge
 * =======================
 *
 * Bridges Brahim Network Protocol to existing infrastructure:
 * - WebSocket over HTTPS (primary)
 * - TCP/UDP sockets
 * - Tor hidden services
 * - Signal Protocol servers (compatible)
 *
 * Ensures backwards compatibility while maintaining Brahim security.
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
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

/**
 * Transport modes for different network environments.
 */
enum class TransportMode {
    WEBSOCKET_HTTPS,    // Primary: WebSocket over TLS (works everywhere)
    DIRECT_TCP,         // Direct TCP for mesh networks
    TOR_HIDDEN,         // Tor hidden service (.onion / .brahimion)
    SIGNAL_BRIDGE,      // Signal protocol compatible servers
    MATRIX_BRIDGE,      // Matrix federation compatible
    WEBRTC_P2P          // Direct peer-to-peer via WebRTC
}

/**
 * Connection state.
 */
data class ConnectionState(
    val isConnected: Boolean = false,
    val mode: TransportMode = TransportMode.WEBSOCKET_HTTPS,
    val serverUrl: String = "",
    val latencyMs: Long = 0,
    val messagesSent: Long = 0,
    val messagesReceived: Long = 0,
    val lastError: String? = null
)

/**
 * Transport Bridge - Connects BNP to existing networks.
 */
class TransportBridge {

    private val _state = MutableStateFlow(ConnectionState())
    val state: StateFlow<ConnectionState> = _state

    private var webSocket: WebSocket? = null
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .pingInterval(30, TimeUnit.SECONDS)
        .build()

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    // Message listeners
    private val messageListeners = mutableListOf<(BridgedMessage) -> Unit>()

    companion object {
        // Default relay servers (can be self-hosted)
        val DEFAULT_RELAYS = listOf(
            "wss://relay.brahim.network/v1/ws",
            "wss://relay-eu.brahim.network/v1/ws",
            "wss://relay-us.brahim.network/v1/ws"
        )

        // Signal-compatible bridge (for interop)
        const val SIGNAL_BRIDGE_URL = "https://bridge.brahim.network/signal/v1"

        // Matrix bridge (for federation)
        const val MATRIX_BRIDGE_URL = "https://matrix.brahim.network/_matrix/client/v3"

        // Protocol version
        const val PROTOCOL_VERSION = "BNP/1.0"
    }

    // =========================================================================
    // CONNECTION MANAGEMENT
    // =========================================================================

    /**
     * Connect to relay server using best available transport.
     */
    suspend fun connect(
        serverUrl: String? = null,
        mode: TransportMode = TransportMode.WEBSOCKET_HTTPS,
        bnpAddress: BrahimNetworkAddress? = null
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            val url = serverUrl ?: selectBestRelay()

            when (mode) {
                TransportMode.WEBSOCKET_HTTPS -> connectWebSocket(url, bnpAddress)
                TransportMode.SIGNAL_BRIDGE -> connectSignalBridge(url, bnpAddress)
                TransportMode.MATRIX_BRIDGE -> connectMatrixBridge(url, bnpAddress)
                TransportMode.TOR_HIDDEN -> connectTorHidden(url, bnpAddress)
                TransportMode.DIRECT_TCP -> connectDirectTcp(url, bnpAddress)
                TransportMode.WEBRTC_P2P -> connectWebRTC(url, bnpAddress)
            }

            _state.value = _state.value.copy(
                isConnected = true,
                mode = mode,
                serverUrl = url
            )

            true
        } catch (e: IOException)  // TODO: catch specific type {
            _state.value = _state.value.copy(
                isConnected = false,
                lastError = e.message
            )
            false
        }
    }

    /**
     * Disconnect from current transport.
     */
    fun disconnect() {
        webSocket?.close(1000, "User disconnect")
        webSocket = null
        _state.value = ConnectionState()
    }

    // =========================================================================
    // WEBSOCKET TRANSPORT (PRIMARY)
    // =========================================================================

    private suspend fun connectWebSocket(url: String, bnpAddress: BrahimNetworkAddress?) {
        val request = Request.Builder()
            .url(url)
            .addHeader("X-BNP-Version", PROTOCOL_VERSION)
            .addHeader("X-BNP-Address", bnpAddress?.fullAddress ?: "")
            .build()

        val listener = object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                // Send registration message
                val registration = buildRegistrationMessage(bnpAddress)
                webSocket.send(registration)
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                handleIncomingMessage(text)
            }

            override fun onMessage(webSocket: WebSocket, bytes: okio.ByteString) {
                handleIncomingBinaryMessage(bytes.toByteArray())
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                _state.value = _state.value.copy(isConnected = false)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _state.value = _state.value.copy(
                    isConnected = false,
                    lastError = t.message
                )
            }
        }

        webSocket = client.newWebSocket(request, listener)
    }

    /**
     * Send message via WebSocket.
     */
    fun sendMessage(message: BridgedMessage): Boolean {
        val ws = webSocket ?: return false

        // Wrap in BNP envelope
        val envelope = wrapInBNPEnvelope(message)

        // Send
        val success = ws.send(envelope)

        if (success) {
            _state.value = _state.value.copy(
                messagesSent = _state.value.messagesSent + 1
            )
        }

        return success
    }

    /**
     * Send binary message (for voice/media).
     */
    fun sendBinaryMessage(data: ByteArray, recipientBnp: String): Boolean {
        val ws = webSocket ?: return false

        // Add BNP header
        val header = "BNP:$recipientBnp:".toByteArray()
        val payload = header + data

        return ws.send(okio.ByteString.of(*payload))
    }

    // =========================================================================
    // SIGNAL PROTOCOL BRIDGE
    // =========================================================================

    /**
     * Connect to Signal-compatible server for interoperability.
     *
     * This allows BUIM users to communicate with Signal users
     * through a bridge server that translates between protocols.
     */
    private suspend fun connectSignalBridge(url: String, bnpAddress: BrahimNetworkAddress?) {
        // Signal uses HTTP for message delivery, WebSocket for realtime
        // We register our BNP address and get a Signal-compatible identifier

        val registrationUrl = "$url/register"

        val body = """
            {
                "protocol": "BNP/1.0",
                "bnp_address": "${bnpAddress?.fullAddress}",
                "ipv6_compat": "${bnpAddress?.toIPv6Compatible()}",
                "capabilities": ["text", "voice", "groups"]
            }
        """.trimIndent()

        val request = Request.Builder()
            .url(registrationUrl)
            .post(body.toRequestBody("application/json".toMediaType()))
            .build()

        client.newCall(request).execute().use { response ->
            if (response.isSuccessful) {
                // Parse Signal-compatible ID
                val responseBody = response.body?.string() ?: "{}"
                // Store signal bridge ID for cross-protocol messaging
            }
        }

        // Connect WebSocket for realtime
        connectWebSocket("$url/ws", bnpAddress)
    }

    // =========================================================================
    // MATRIX FEDERATION BRIDGE
    // =========================================================================

    /**
     * Connect to Matrix federation for decentralized messaging.
     *
     * Matrix provides:
     * - Decentralized servers
     * - End-to-end encryption (Megolm)
     * - Cross-platform bridging
     */
    private suspend fun connectMatrixBridge(url: String, bnpAddress: BrahimNetworkAddress?) {
        // Matrix uses standard REST API + sync endpoint

        // Register BNP-derived Matrix ID
        // Format: @bnp_<address>:<server>
        val matrixId = "@bnp_${bnpAddress?.shortAddress?.replace(":", "_")}:brahim.network"

        // Initial sync
        val syncUrl = "$url/sync?timeout=30000"

        // WebSocket for realtime (if supported)
        connectWebSocket(url.replace("http", "ws") + "/sync", bnpAddress)
    }

    // =========================================================================
    // TOR HIDDEN SERVICE
    // =========================================================================

    /**
     * Connect via Tor hidden service for maximum privacy.
     */
    private suspend fun connectTorHidden(url: String, bnpAddress: BrahimNetworkAddress?) {
        // Convert BNP to .brahimion address
        val onionAddress = bnpAddress?.toOnionAddress() ?: return

        // Would require Tor proxy configuration
        // For now, fall back to WebSocket with onion-style routing
        connectWebSocket(url, bnpAddress)
    }

    // =========================================================================
    // DIRECT TCP (MESH NETWORKS)
    // =========================================================================

    /**
     * Direct TCP connection for mesh/local networks.
     */
    private suspend fun connectDirectTcp(url: String, bnpAddress: BrahimNetworkAddress?) {
        // Extract host:port from URL
        // Establish raw TCP socket
        // Use Wormhole Cipher for encryption

        // For Android, fall back to WebSocket for simplicity
        connectWebSocket(url, bnpAddress)
    }

    // =========================================================================
    // WEBRTC P2P
    // =========================================================================

    /**
     * WebRTC for direct peer-to-peer connections.
     *
     * Uses STUN/TURN servers for NAT traversal.
     */
    private suspend fun connectWebRTC(url: String, bnpAddress: BrahimNetworkAddress?) {
        // WebRTC signaling via WebSocket
        // Then upgrade to direct P2P

        // Signaling server
        connectWebSocket(url, bnpAddress)

        // WebRTC setup would happen after signaling
    }

    // =========================================================================
    // MESSAGE HANDLING
    // =========================================================================

    private fun handleIncomingMessage(text: String) {
        // Parse BNP envelope
        val message = parseBNPEnvelope(text)

        if (message != null) {
            _state.value = _state.value.copy(
                messagesReceived = _state.value.messagesReceived + 1
            )

            // Notify listeners
            messageListeners.forEach { it(message) }
        }
    }

    private fun handleIncomingBinaryMessage(data: ByteArray) {
        // Parse BNP header from binary
        val headerEnd = data.indexOf(':'.code.toByte(), data.indexOf(':'.code.toByte()) + 1)

        if (headerEnd > 0) {
            val header = String(data.sliceArray(0 until headerEnd))
            val payload = data.sliceArray(headerEnd + 1 until data.size)

            val parts = header.split(":")
            if (parts.size >= 2 && parts[0] == "BNP") {
                val message = BridgedMessage(
                    senderBnp = parts[1],
                    recipientBnp = "",  // Would be in header
                    payload = payload,
                    isBinary = true,
                    timestamp = System.currentTimeMillis()
                )

                messageListeners.forEach { it(message) }
            }
        }
    }

    fun addMessageListener(listener: (BridgedMessage) -> Unit) {
        messageListeners.add(listener)
    }

    fun removeMessageListener(listener: (BridgedMessage) -> Unit) {
        messageListeners.remove(listener)
    }

    // =========================================================================
    // PROTOCOL HELPERS
    // =========================================================================

    private fun buildRegistrationMessage(bnpAddress: BrahimNetworkAddress?): String {
        return """
            {
                "type": "register",
                "protocol": "$PROTOCOL_VERSION",
                "bnp_address": "${bnpAddress?.fullAddress}",
                "ipv6": "${bnpAddress?.toIPv6Compatible()}",
                "timestamp": ${System.currentTimeMillis()},
                "capabilities": {
                    "text": true,
                    "voice": true,
                    "video": false,
                    "groups": true,
                    "walkie_talkie": true
                }
            }
        """.trimIndent()
    }

    private fun wrapInBNPEnvelope(message: BridgedMessage): String {
        val payloadBase64 = if (message.isBinary) {
            android.util.Base64.encodeToString(message.payload, android.util.Base64.NO_WRAP)
        } else {
            String(message.payload)
        }

        return """
            {
                "protocol": "$PROTOCOL_VERSION",
                "type": "message",
                "sender": "${message.senderBnp}",
                "recipient": "${message.recipientBnp}",
                "payload": "$payloadBase64",
                "binary": ${message.isBinary},
                "timestamp": ${message.timestamp}
            }
        """.trimIndent()
    }

    private fun parseBNPEnvelope(json: String): BridgedMessage? {
        // Simple JSON parsing (use Gson/Moshi in production)
        try {
            val senderMatch = """"sender"\s*:\s*"([^"]+)"""".toRegex().find(json)
            val recipientMatch = """"recipient"\s*:\s*"([^"]+)"""".toRegex().find(json)
            val payloadMatch = """"payload"\s*:\s*"([^"]+)"""".toRegex().find(json)
            val binaryMatch = """"binary"\s*:\s*(true|false)""".toRegex().find(json)
            val timestampMatch = """"timestamp"\s*:\s*(\d+)""".toRegex().find(json)

            if (senderMatch != null && payloadMatch != null) {
                val isBinary = binaryMatch?.groupValues?.get(1) == "true"
                val payload = if (isBinary) {
                    android.util.Base64.decode(payloadMatch.groupValues[1], android.util.Base64.NO_WRAP)
                } else {
                    payloadMatch.groupValues[1].toByteArray()
                }

                return BridgedMessage(
                    senderBnp = senderMatch.groupValues[1],
                    recipientBnp = recipientMatch?.groupValues?.get(1) ?: "",
                    payload = payload,
                    isBinary = isBinary,
                    timestamp = timestampMatch?.groupValues?.get(1)?.toLongOrNull()
                        ?: System.currentTimeMillis()
                )
            }
        } catch (e: IOException)  // TODO: catch specific type {
            // Parse error
        }

        return null
    }

    private suspend fun selectBestRelay(): String {
        // Test latency to each relay and pick the best
        var bestRelay = DEFAULT_RELAYS[0]
        var bestLatency = Long.MAX_VALUE

        for (relay in DEFAULT_RELAYS) {
            try {
                val httpUrl = relay.replace("wss://", "https://").replace("/ws", "/health")
                val request = Request.Builder().url(httpUrl).build()

                val start = System.currentTimeMillis()
                client.newCall(request).execute().use { response ->
                    val latency = System.currentTimeMillis() - start
                    if (response.isSuccessful && latency < bestLatency) {
                        bestLatency = latency
                        bestRelay = relay
                    }
                }
            } catch (e: IOException)  // TODO: catch specific type {
                // Skip this relay
            }
        }

        _state.value = _state.value.copy(latencyMs = bestLatency)
        return bestRelay
    }

    fun release() {
        disconnect()
        scope.cancel()
    }
}

/**
 * Bridged message structure.
 */
data class BridgedMessage(
    val senderBnp: String,
    val recipientBnp: String,
    val payload: ByteArray,
    val isBinary: Boolean = false,
    val timestamp: Long = System.currentTimeMillis()
)

/**
 * IPv4/IPv6 to BNP Converter utilities.
 */
object LegacyNetworkConverter {

    /**
     * Convert any IP address to BNP address.
     */
    fun ipToBnp(ip: String): BrahimNetworkAddress? {
        return if (ip.contains(":")) {
            BrahimNetworkProtocol.fromIPv6(ip)
        } else {
            BrahimNetworkProtocol.fromIPv4(ip)
        }
    }

    /**
     * Convert BNP to best legacy format.
     */
    fun bnpToLegacy(bnp: BrahimNetworkAddress, preferIPv6: Boolean = true): String {
        return if (preferIPv6) {
            bnp.toIPv6Compatible()
        } else {
            // Extract IPv4-like representation
            val coords = bnp.geographicBN % 0xFFFFFFFF
            val o1 = (coords shr 24 and 0xFF).toInt()
            val o2 = (coords shr 16 and 0xFF).toInt()
            val o3 = (coords shr 8 and 0xFF).toInt()
            val o4 = (coords and 0xFF).toInt()
            "$o1.$o2.$o3.$o4"
        }
    }

    /**
     * Create DNS-compatible hostname from BNP.
     */
    fun bnpToHostname(bnp: BrahimNetworkAddress): String {
        // Format: <short_address>.bnp.brahim.network
        val safe = bnp.shortAddress
            .replace(":", "-")
            .lowercase()
        return "$safe.bnp.brahim.network"
    }

    /**
     * Resolve DNS hostname to BNP (if registered).
     */
    suspend fun hostnameTobnp(hostname: String): BrahimNetworkAddress? = withContext(Dispatchers.IO) {
        // Would perform DNS TXT record lookup for _bnp.<hostname>
        // For now, parse from hostname if it's a .bnp.brahim.network address
        if (hostname.endsWith(".bnp.brahim.network")) {
            val parts = hostname.removeSuffix(".bnp.brahim.network").split("-")
            // Reconstruct BNP address
            // ...
        }
        null
    }
}
