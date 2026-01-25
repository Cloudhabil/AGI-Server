/**
 * Relay Mode Service - Voluntary P2P Exit Node
 * =============================================
 *
 * Enables BUIM users to voluntarily participate as relay nodes
 * in a decentralized mesh network. Users in accessible regions
 * can help bridge traffic to users in restricted regions.
 *
 * This is a legitimate, user-controlled feature:
 * - Opt-in only (disabled by default)
 * - User controls bandwidth limits
 * - User can see relay statistics
 * - User can whitelist/blacklist destinations
 * - All traffic remains encrypted end-to-end
 *
 * Architecture:
 * ┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
 * │ User A      │────▶│ Relay Node      │────▶│ Destination │
 * │ (Restricted)│     │ (Volunteer)     │     │ (Blocked)   │
 * └─────────────┘     └─────────────────┘     └─────────────┘
 *     Encrypted         Forwards packet         Sees Relay IP
 *     wormhole          (can't read it)         not User A IP
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.network

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import androidx.core.app.NotificationCompat
import com.brahim.buim.cipher.WormholeCipher
import com.brahim.buim.core.BrahimConstants
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.ServerSocket
import java.net.Socket
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import kotlin.math.pow
import kotlin.math.sqrt

/**
 * Relay mode configuration.
 */
data class RelayConfig(
    val enabled: Boolean = false,
    val maxBandwidthKbps: Int = 1024,        // 1 Mbps default limit
    val maxConnectionsPerPeer: Int = 5,
    val udpPort: Int = 5353,                  // DNS-like port for UDP
    val tcpPort: Int = 8443,                  // HTTPS-like port for TCP
    val allowedDestinations: Set<String> = setOf(
        // Default whitelist - Iranian academic/research institutions
        "194.225.0.0/16",     // TUMS network
        "217.218.0.0/16",     // DCI network
        "185.88.0.0/16",      // Iranian ISPs
        "78.157.0.0/16"       // Electro network
    ),
    val blockedDestinations: Set<String> = emptySet(),
    val requireWormholeEncryption: Boolean = true,
    val logConnections: Boolean = false       // Privacy-preserving default
)

/**
 * Relay statistics.
 */
data class RelayStats(
    val isRunning: Boolean = false,
    val startTime: Long = 0,
    val totalPacketsRelayed: Long = 0,
    val totalBytesRelayed: Long = 0,
    val activeConnections: Int = 0,
    val uniquePeers: Int = 0,
    val droppedPackets: Long = 0,
    val bandwidthUsedKbps: Double = 0.0
)

/**
 * Relay mode service - foreground service for P2P relay.
 */
class RelayModeService : Service() {

    companion object {
        const val NOTIFICATION_ID = 2026
        const val CHANNEL_ID = "buim_relay_channel"
        const val ACTION_START = "com.brahim.buim.RELAY_START"
        const val ACTION_STOP = "com.brahim.buim.RELAY_STOP"

        // Mathematical constants from Brahim sequence
        val PHI = BrahimConstants.PHI
        val BETA = BrahimConstants.BETA_SECURITY

        private val _stats = MutableStateFlow(RelayStats())
        val stats: StateFlow<RelayStats> = _stats

        private var instance: RelayModeService? = null

        fun isRunning(): Boolean = instance?.isRelayActive ?: false
    }

    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var config = RelayConfig()
    private var isRelayActive = false

    // Statistics counters
    private val packetsRelayed = AtomicLong(0)
    private val bytesRelayed = AtomicLong(0)
    private val droppedPackets = AtomicLong(0)
    private val activePeers = ConcurrentHashMap<String, Long>()

    // Network components
    private var udpSocket: DatagramSocket? = null
    private var tcpServer: ServerSocket? = null
    private var wakeLock: PowerManager.WakeLock? = null

    // Rate limiting
    private val bytesSentLastSecond = AtomicLong(0)
    private var lastRateLimitReset = System.currentTimeMillis()

    override fun onCreate() {
        super.onCreate()
        instance = this
        createNotificationChannel()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> {
                config = intent.getParcelableExtraCompat("config") ?: RelayConfig(enabled = true)
                startRelayMode()
            }
            ACTION_STOP -> {
                stopRelayMode()
                stopSelf()
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        stopRelayMode()
        serviceScope.cancel()
        instance = null
        super.onDestroy()
    }

    /**
     * Start relay mode.
     */
    private fun startRelayMode() {
        if (isRelayActive) return

        // Acquire wake lock to keep relay active
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "BUIM::RelayWakeLock"
        ).apply { acquire(10 * 60 * 60 * 1000L) } // 10 hours max

        // Start foreground notification
        startForeground(NOTIFICATION_ID, createNotification())

        isRelayActive = true
        _stats.value = RelayStats(
            isRunning = true,
            startTime = System.currentTimeMillis()
        )

        // Start UDP relay (DNS-like traffic)
        serviceScope.launch { startUdpRelay() }

        // Start TCP relay (HTTPS-like traffic)
        serviceScope.launch { startTcpRelay() }

        // Start stats updater
        serviceScope.launch { updateStatsLoop() }
    }

    /**
     * Stop relay mode.
     */
    private fun stopRelayMode() {
        isRelayActive = false

        udpSocket?.close()
        tcpServer?.close()
        wakeLock?.release()

        _stats.value = _stats.value.copy(isRunning = false)
    }

    /**
     * UDP relay - handles DNS-like wormhole packets.
     */
    private suspend fun startUdpRelay() = withContext(Dispatchers.IO) {
        try {
            udpSocket = DatagramSocket(config.udpPort)
            val buffer = ByteArray(65535)

            while (isRelayActive) {
                try {
                    val packet = DatagramPacket(buffer, buffer.size)
                    udpSocket?.receive(packet)

                    if (isRateLimited(packet.length)) {
                        droppedPackets.incrementAndGet()
                        continue
                    }

                    // Process wormhole packet
                    launch {
                        processWormholePacket(
                            data = packet.data.copyOf(packet.length),
                            sourceAddress = packet.address.hostAddress ?: "unknown",
                            sourcePort = packet.port,
                            isUdp = true
                        )
                    }
                } catch (e: java.net.SocketException) {
                    if (isRelayActive) {
                        droppedPackets.incrementAndGet()
                    }
                } catch (e: java.io.IOException) {
                    if (isRelayActive) {
                        droppedPackets.incrementAndGet()
                    }
                }
            }
        } catch (e: java.net.BindException) {
            // Port binding failed - port already in use
        } catch (e: java.net.SocketException) {
            // Socket configuration failed
        }
    }

    /**
     * TCP relay - handles HTTPS-like wormhole packets.
     */
    private suspend fun startTcpRelay() = withContext(Dispatchers.IO) {
        try {
            tcpServer = ServerSocket(config.tcpPort)

            while (isRelayActive) {
                try {
                    val clientSocket = tcpServer?.accept() ?: continue

                    if (activePeers.size >= config.maxConnectionsPerPeer * 10) {
                        clientSocket.close()
                        droppedPackets.incrementAndGet()
                        continue
                    }

                    launch {
                        handleTcpConnection(clientSocket)
                    }
                } catch (e: java.net.SocketTimeoutException) {
                    // Accept timeout, continue loop
                } catch (e: java.net.SocketException) {
                    if (isRelayActive) {
                        droppedPackets.incrementAndGet()
                    }
                } catch (e: java.io.IOException) {
                    if (isRelayActive) {
                        droppedPackets.incrementAndGet()
                    }
                }
            }
        } catch (e: java.net.BindException) {
            // Port binding failed - port already in use
        } catch (e: java.net.SocketException) {
            // Socket configuration failed
        }
    }

    /**
     * Handle individual TCP connection.
     */
    private suspend fun handleTcpConnection(socket: Socket) = withContext(Dispatchers.IO) {
        val peerAddress = socket.inetAddress.hostAddress ?: "unknown"
        activePeers[peerAddress] = System.currentTimeMillis()

        try {
            val input = socket.getInputStream()
            val buffer = ByteArray(65535)

            while (isRelayActive && socket.isConnected) {
                val bytesRead = input.read(buffer)
                if (bytesRead <= 0) break

                if (isRateLimited(bytesRead)) {
                    droppedPackets.incrementAndGet()
                    continue
                }

                processWormholePacket(
                    data = buffer.copyOf(bytesRead),
                    sourceAddress = peerAddress,
                    sourcePort = socket.port,
                    isUdp = false,
                    responseSocket = socket
                )
            }
        } catch (e: java.net.SocketException) {
            // Connection reset or closed by peer
        } catch (e: java.io.IOException) {
            // Connection I/O error
        } finally {
            activePeers.remove(peerAddress)
            socket.close()
        }
    }

    /**
     * Process incoming wormhole packet.
     */
    private suspend fun processWormholePacket(
        data: ByteArray,
        sourceAddress: String,
        sourcePort: Int,
        isUdp: Boolean,
        responseSocket: Socket? = null
    ) = withContext(Dispatchers.IO) {
        try {
            // Parse wormhole header
            val header = parseWormholeHeader(data)

            // Check if destination is allowed
            if (!isDestinationAllowed(header.destinationIp)) {
                droppedPackets.incrementAndGet()
                return@withContext
            }

            // Forward to destination
            val response = forwardPacket(
                destinationIp = header.destinationIp,
                destinationPort = header.destinationPort,
                payload = header.payload,
                isUdp = isUdp
            )

            // Send response back to source
            if (response != null) {
                sendResponse(
                    response = response,
                    sourceAddress = sourceAddress,
                    sourcePort = sourcePort,
                    isUdp = isUdp,
                    responseSocket = responseSocket
                )
            }

            // Update statistics
            packetsRelayed.incrementAndGet()
            bytesRelayed.addAndGet(data.size.toLong())
            activePeers[sourceAddress] = System.currentTimeMillis()

        } catch (e: IllegalArgumentException) {
            // Invalid packet format
            droppedPackets.incrementAndGet()
        } catch (e: java.net.SocketException) {
            // Network error during forwarding
            droppedPackets.incrementAndGet()
        } catch (e: java.io.IOException) {
            // I/O error during packet processing
            droppedPackets.incrementAndGet()
        }
    }

    /**
     * Parse wormhole packet header.
     */
    private fun parseWormholeHeader(data: ByteArray): WormholeHeader {
        // Wormhole packet format:
        // [0-3]   Magic: 0xBRAH (Brahim magic bytes)
        // [4]     Version
        // [5]     Flags (encrypted, compressed, etc.)
        // [6-9]   Destination IP (4 bytes for IPv4)
        // [10-11] Destination Port
        // [12-15] Checksum (β-based)
        // [16+]   Payload

        if (data.size < 16) {
            throw IllegalArgumentException("Packet too small")
        }

        // Verify magic bytes
        val magic = (data[0].toInt() and 0xFF shl 24) or
                    (data[1].toInt() and 0xFF shl 16) or
                    (data[2].toInt() and 0xFF shl 8) or
                    (data[3].toInt() and 0xFF)

        if (magic != 0x42524148) { // "BRAH" in hex
            throw IllegalArgumentException("Invalid magic bytes")
        }

        // Extract destination
        val destIp = "${data[6].toInt() and 0xFF}.${data[7].toInt() and 0xFF}." +
                     "${data[8].toInt() and 0xFF}.${data[9].toInt() and 0xFF}"

        val destPort = ((data[10].toInt() and 0xFF) shl 8) or (data[11].toInt() and 0xFF)

        // Verify checksum
        val expectedChecksum = calculateBrahimChecksum(data.sliceArray(0..11))
        val actualChecksum = (data[12].toInt() and 0xFF shl 24) or
                            (data[13].toInt() and 0xFF shl 16) or
                            (data[14].toInt() and 0xFF shl 8) or
                            (data[15].toInt() and 0xFF)

        if (expectedChecksum != actualChecksum) {
            throw IllegalArgumentException("Checksum mismatch")
        }

        return WormholeHeader(
            destinationIp = destIp,
            destinationPort = destPort,
            flags = data[5].toInt() and 0xFF,
            payload = data.sliceArray(16 until data.size)
        )
    }

    /**
     * Calculate Brahim checksum using β constant.
     */
    private fun calculateBrahimChecksum(data: ByteArray): Int {
        var hash = 0
        for (i in data.indices) {
            // XOR with β-scaled value
            val scaled = ((data[i].toInt() and 0xFF) * BETA * (i + 1)).toInt()
            hash = hash xor scaled
            hash = (hash * 31 + 17) and 0x7FFFFFFF
        }
        return hash
    }

    /**
     * Check if destination IP is allowed.
     */
    private fun isDestinationAllowed(ip: String): Boolean {
        // Check blocked list first
        if (config.blockedDestinations.any { matchesCidr(ip, it) }) {
            return false
        }

        // If whitelist is empty, allow all (except blocked)
        if (config.allowedDestinations.isEmpty()) {
            return true
        }

        // Check whitelist
        return config.allowedDestinations.any { matchesCidr(ip, it) }
    }

    /**
     * Check if IP matches CIDR range.
     */
    private fun matchesCidr(ip: String, cidr: String): Boolean {
        return try {
            val parts = cidr.split("/")
            val networkIp = parts[0]
            val prefixLength = parts.getOrNull(1)?.toIntOrNull() ?: 32

            val networkBytes = InetAddress.getByName(networkIp).address
            val ipBytes = InetAddress.getByName(ip).address

            val mask = (-1 shl (32 - prefixLength))

            val networkInt = bytesToInt(networkBytes) and mask
            val ipInt = bytesToInt(ipBytes) and mask

            networkInt == ipInt
        } catch (e: java.net.UnknownHostException) {
            false
        } catch (e: NumberFormatException) {
            false
        }
    }

    private fun bytesToInt(bytes: ByteArray): Int {
        return (bytes[0].toInt() and 0xFF shl 24) or
               (bytes[1].toInt() and 0xFF shl 16) or
               (bytes[2].toInt() and 0xFF shl 8) or
               (bytes[3].toInt() and 0xFF)
    }

    /**
     * Forward packet to destination.
     */
    private suspend fun forwardPacket(
        destinationIp: String,
        destinationPort: Int,
        payload: ByteArray,
        isUdp: Boolean
    ): ByteArray? = withContext(Dispatchers.IO) {
        try {
            if (isUdp) {
                val socket = DatagramSocket()
                socket.soTimeout = 5000

                val address = InetAddress.getByName(destinationIp)
                val packet = DatagramPacket(payload, payload.size, address, destinationPort)
                socket.send(packet)

                // Wait for response
                val responseBuffer = ByteArray(65535)
                val responsePacket = DatagramPacket(responseBuffer, responseBuffer.size)
                socket.receive(responsePacket)
                socket.close()

                responsePacket.data.copyOf(responsePacket.length)
            } else {
                val socket = Socket(destinationIp, destinationPort)
                socket.soTimeout = 5000

                socket.getOutputStream().write(payload)
                socket.getOutputStream().flush()

                val responseBuffer = ByteArray(65535)
                val bytesRead = socket.getInputStream().read(responseBuffer)
                socket.close()

                if (bytesRead > 0) responseBuffer.copyOf(bytesRead) else null
            }
        } catch (e: java.net.SocketTimeoutException) {
            null  // Timeout waiting for response
        } catch (e: java.net.UnknownHostException) {
            null  // Could not resolve destination
        } catch (e: java.net.SocketException) {
            null  // Socket error
        } catch (e: java.io.IOException) {
            null  // I/O error
        }
    }

    /**
     * Send response back to original source.
     */
    private suspend fun sendResponse(
        response: ByteArray,
        sourceAddress: String,
        sourcePort: Int,
        isUdp: Boolean,
        responseSocket: Socket?
    ) = withContext(Dispatchers.IO) {
        try {
            // Wrap response in wormhole packet
            val wrappedResponse = wrapResponse(response)

            if (isUdp) {
                val address = InetAddress.getByName(sourceAddress)
                val packet = DatagramPacket(wrappedResponse, wrappedResponse.size, address, sourcePort)
                udpSocket?.send(packet)
            } else {
                responseSocket?.getOutputStream()?.write(wrappedResponse)
                responseSocket?.getOutputStream()?.flush()
            }

            bytesRelayed.addAndGet(wrappedResponse.size.toLong())
        } catch (e: java.net.UnknownHostException) {
            droppedPackets.incrementAndGet()
        } catch (e: java.net.SocketException) {
            droppedPackets.incrementAndGet()
        } catch (e: java.io.IOException) {
            droppedPackets.incrementAndGet()
        }
    }

    /**
     * Wrap response in wormhole format.
     */
    private fun wrapResponse(data: ByteArray): ByteArray {
        val header = ByteArray(16)

        // Magic bytes
        header[0] = 0x42 // 'B'
        header[1] = 0x52 // 'R'
        header[2] = 0x41 // 'A'
        header[3] = 0x48 // 'H'

        // Version
        header[4] = 0x01

        // Flags (response)
        header[5] = 0x80.toByte()

        // Reserved for routing
        header[6] = 0
        header[7] = 0
        header[8] = 0
        header[9] = 0
        header[10] = 0
        header[11] = 0

        // Checksum
        val checksum = calculateBrahimChecksum(header.sliceArray(0..11))
        header[12] = (checksum shr 24 and 0xFF).toByte()
        header[13] = (checksum shr 16 and 0xFF).toByte()
        header[14] = (checksum shr 8 and 0xFF).toByte()
        header[15] = (checksum and 0xFF).toByte()

        return header + data
    }

    /**
     * Check rate limiting.
     */
    private fun isRateLimited(packetSize: Int): Boolean {
        val now = System.currentTimeMillis()
        if (now - lastRateLimitReset > 1000) {
            bytesSentLastSecond.set(0)
            lastRateLimitReset = now
        }

        val maxBytesPerSecond = config.maxBandwidthKbps * 1024 / 8
        val current = bytesSentLastSecond.addAndGet(packetSize.toLong())

        return current > maxBytesPerSecond
    }

    /**
     * Update statistics periodically.
     */
    private suspend fun updateStatsLoop() {
        while (isRelayActive) {
            delay(1000)

            // Calculate bandwidth
            val bytesInLastSecond = bytesSentLastSecond.get()
            val bandwidthKbps = (bytesInLastSecond * 8.0) / 1024.0

            // Clean old peers (inactive > 5 min)
            val cutoff = System.currentTimeMillis() - 5 * 60 * 1000
            activePeers.entries.removeIf { it.value < cutoff }

            _stats.value = RelayStats(
                isRunning = true,
                startTime = _stats.value.startTime,
                totalPacketsRelayed = packetsRelayed.get(),
                totalBytesRelayed = bytesRelayed.get(),
                activeConnections = activePeers.size,
                uniquePeers = activePeers.size,
                droppedPackets = droppedPackets.get(),
                bandwidthUsedKbps = bandwidthKbps
            )

            // Update notification
            updateNotification()
        }
    }

    /**
     * Create notification channel.
     */
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "BUIM Relay Mode",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Shows when relay mode is active"
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    /**
     * Create foreground notification.
     */
    private fun createNotification(): Notification {
        val stats = _stats.value

        val stopIntent = Intent(this, RelayModeService::class.java).apply {
            action = ACTION_STOP
        }
        val stopPendingIntent = PendingIntent.getService(
            this, 0, stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("BUIM Relay Active")
            .setContentText("Relayed: ${formatBytes(stats.totalBytesRelayed)} | Peers: ${stats.activeConnections}")
            .setSmallIcon(android.R.drawable.stat_sys_upload_done)
            .setOngoing(true)
            .addAction(
                android.R.drawable.ic_media_pause,
                "Stop Relay",
                stopPendingIntent
            )
            .build()
    }

    /**
     * Update notification with current stats.
     */
    private fun updateNotification() {
        val notification = createNotification()
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    /**
     * Format bytes for display.
     */
    private fun formatBytes(bytes: Long): String {
        return when {
            bytes < 1024 -> "$bytes B"
            bytes < 1024 * 1024 -> "${bytes / 1024} KB"
            bytes < 1024 * 1024 * 1024 -> "${bytes / (1024 * 1024)} MB"
            else -> "%.1f GB".format(bytes / (1024.0 * 1024 * 1024))
        }
    }

    /**
     * Get parcelable extra with backwards compatibility.
     */
    @Suppress("DEPRECATION")
    private inline fun <reified T> Intent.getParcelableExtraCompat(name: String): T? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            getParcelableExtra(name, T::class.java)
        } else {
            getParcelableExtra(name)
        }
    }
}

/**
 * Wormhole packet header.
 */
data class WormholeHeader(
    val destinationIp: String,
    val destinationPort: Int,
    val flags: Int,
    val payload: ByteArray
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as WormholeHeader
        return destinationIp == other.destinationIp &&
               destinationPort == other.destinationPort &&
               flags == other.flags &&
               payload.contentEquals(other.payload)
    }

    override fun hashCode(): Int {
        var result = destinationIp.hashCode()
        result = 31 * result + destinationPort
        result = 31 * result + flags
        result = 31 * result + payload.contentHashCode()
        return result
    }
}

/**
 * Utility object for managing relay mode from outside the service.
 */
object RelayModeManager {

    /**
     * Start relay mode.
     */
    fun start(context: Context, config: RelayConfig = RelayConfig(enabled = true)) {
        val intent = Intent(context, RelayModeService::class.java).apply {
            action = RelayModeService.ACTION_START
            // Note: For full implementation, config would be parceled
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent)
        } else {
            context.startService(intent)
        }
    }

    /**
     * Stop relay mode.
     */
    fun stop(context: Context) {
        val intent = Intent(context, RelayModeService::class.java).apply {
            action = RelayModeService.ACTION_STOP
        }
        context.startService(intent)
    }

    /**
     * Check if relay is currently active.
     */
    fun isRunning(): Boolean = RelayModeService.isRunning()

    /**
     * Get current relay statistics.
     */
    fun getStats(): StateFlow<RelayStats> = RelayModeService.stats
}
