/**
 * Brahim Network Protocol (BNP)
 * =============================
 *
 * A geographic-aware, privacy-preserving network addressing system
 * built on Brahim Numbers, compatible with existing infrastructure.
 *
 * Features:
 * - Geographic routing (coordinates → address)
 * - Layered privacy (Wormhole encryption)
 * - Resonance-based QoS (Brahim sequence alignment)
 * - Backward compatible with IPv4/IPv6
 *
 * Address Format: BNP:{layer}:{geographic_bn}:{service_bn}:{check}
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.network

import com.brahim.buim.core.BrahimConstants
import kotlin.math.*

/**
 * Network layers based on Brahim sequence.
 *
 * B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}
 *
 * Each layer represents a network tier with specific properties.
 */
enum class NetworkLayer(val code: Int, val sequenceIndex: Int, val description: String) {
    // Physical/Infrastructure layers
    PHYSICAL(27, 0, "Physical infrastructure - data centers, cables"),
    LINK(42, 1, "Link layer - local network segments"),
    NETWORK(60, 2, "Network layer - routing between segments"),

    // Transport/Session layers
    TRANSPORT(75, 3, "Transport layer - reliable delivery"),
    SESSION(97, 4, "Session layer - connection management"),

    // Application layers
    PRESENTATION(121, 5, "Presentation layer - encryption/encoding"),
    APPLICATION(136, 6, "Application layer - user services"),

    // Extended layers (Brahim additions)
    IDENTITY(154, 7, "Identity layer - authentication/reputation"),
    PRIVACY(172, 8, "Privacy layer - onion routing"),
    RESONANCE(187, 9, "Resonance layer - QoS/priority");

    companion object {
        fun fromCode(code: Int): NetworkLayer? = values().find { it.code == code }
        fun fromIndex(index: Int): NetworkLayer? = values().find { it.sequenceIndex == index }
    }
}

/**
 * Brahim Network Address.
 *
 * Encodes geographic location + service type into a unique address.
 */
data class BrahimNetworkAddress(
    val layer: NetworkLayer,
    val geographicBN: Long,           // Brahim Number from coordinates
    val serviceBN: Long,              // Service type encoding
    val privacyLevel: Int,            // 0-9 (onion layers)
    val checkDigit: Char,
    val resonanceScore: Double        // 0-1, alignment with sequence
) {
    /**
     * Full address string.
     */
    val fullAddress: String
        get() = "BNP:${layer.code}:${geographicBN}:${serviceBN}:${privacyLevel}:$checkDigit"

    /**
     * Short address (for display).
     */
    val shortAddress: String
        get() = "BNP:${layer.code}:${geographicBN.toString(36).uppercase()}:$checkDigit"

    /**
     * Convert to IPv6-compatible format.
     * Maps Brahim address into IPv6 address space.
     */
    fun toIPv6Compatible(): String {
        // Use unique local address range (fc00::/7)
        val prefix = "fd${layer.code.toString(16).padStart(2, '0')}"

        // Geographic component (48 bits)
        val geoHex = (geographicBN % 0xFFFFFFFFFFFF).toString(16).padStart(12, '0')

        // Service component (16 bits)
        val svcHex = (serviceBN % 0xFFFF).toString(16).padStart(4, '0')

        // Privacy + check (16 bits)
        val privHex = (privacyLevel * 256 + checkDigit.code).toString(16).padStart(4, '0')

        return "$prefix:${geoHex.substring(0,4)}:${geoHex.substring(4,8)}:${geoHex.substring(8,12)}:$svcHex:$privHex"
    }

    /**
     * Convert to .onion-style address for Tor compatibility.
     */
    fun toOnionAddress(): String {
        val combined = geographicBN xor serviceBN xor (layer.code.toLong() * 1000000)
        val base32 = combined.toString(32).lowercase().padStart(16, '0').take(16)
        return "${base32}.brahimion"
    }
}

/**
 * Service types encoded as Brahim Numbers.
 */
enum class ServiceType(val code: Int, val port: Int, val description: String) {
    // Standard services mapped to Brahim values
    DNS(27, 53, "Domain Name Service"),
    HTTP(42, 80, "Hypertext Transfer"),
    HTTPS(60, 443, "Secure HTTP"),
    SSH(75, 22, "Secure Shell"),
    SMTP(97, 25, "Email Transfer"),

    // Extended services
    MESH(121, 8121, "Mesh networking"),
    RESONANCE(136, 8136, "Resonance routing"),
    IDENTITY(154, 8154, "Identity verification"),
    PRIVACY(172, 8172, "Privacy tunnel"),
    ORACLE(187, 8187, "Brahim oracle service");

    companion object {
        fun fromCode(code: Int): ServiceType? = values().find { it.code == code }
        fun fromPort(port: Int): ServiceType? = values().find { it.port == port }
    }
}

/**
 * Brahim Network Protocol implementation.
 */
object BrahimNetworkProtocol {

    // Constants
    private val B = BrahimConstants.BRAHIM_SEQUENCE
    private val S = BrahimConstants.BRAHIM_SUM  // 214
    private val PHI = BrahimConstants.PHI
    private val BETA = BrahimConstants.BETA_SECURITY

    // =========================================================================
    // ADDRESS GENERATION
    // =========================================================================

    /**
     * Create a Brahim Network Address from geographic coordinates.
     */
    fun createAddress(
        latitude: Double,
        longitude: Double,
        layer: NetworkLayer = NetworkLayer.APPLICATION,
        serviceType: ServiceType = ServiceType.HTTPS,
        privacyLevel: Int = 0
    ): BrahimNetworkAddress {
        // Geographic Brahim Number (same as BNv1)
        val latScaled = (abs(latitude) * 1_000_000).toLong()
        val lonScaled = (abs(longitude) * 1_000_000).toLong()
        val geographicBN = cantorPair(latScaled, lonScaled)

        // Service Brahim Number
        val serviceBN = cantorPair(serviceType.code.toLong(), serviceType.port.toLong())

        // Calculate resonance score
        val resonance = calculateResonance(geographicBN, serviceBN, layer)

        // Check digit
        val checkDigit = calculateCheckDigit(geographicBN, serviceBN, layer.code, privacyLevel)

        return BrahimNetworkAddress(
            layer = layer,
            geographicBN = geographicBN,
            serviceBN = serviceBN,
            privacyLevel = privacyLevel.coerceIn(0, 9),
            checkDigit = checkDigit,
            resonanceScore = resonance
        )
    }

    /**
     * Create address from existing IPv4.
     */
    fun fromIPv4(ipv4: String, serviceType: ServiceType = ServiceType.HTTPS): BrahimNetworkAddress? {
        val parts = ipv4.split(".")
        if (parts.size != 4) return null

        try {
            val octets = parts.map { it.toInt() }

            // Treat first two octets as "latitude-like" and last two as "longitude-like"
            val pseudo_lat = (octets[0] * 256 + octets[1]).toDouble() / 65535 * 180 - 90
            val pseudo_lon = (octets[2] * 256 + octets[3]).toDouble() / 65535 * 360 - 180

            return createAddress(pseudo_lat, pseudo_lon, NetworkLayer.NETWORK, serviceType)
        } catch (e: Exception) {
            return null
        }
    }

    /**
     * Create address from existing IPv6.
     */
    fun fromIPv6(ipv6: String, serviceType: ServiceType = ServiceType.HTTPS): BrahimNetworkAddress? {
        try {
            val clean = ipv6.replace(":", "").lowercase()
            val value = clean.toLong(16)

            // Extract geographic-like components
            val pseudo_lat = ((value shr 64) % 180000000).toDouble() / 1000000 - 90
            val pseudo_lon = ((value shr 32) % 360000000).toDouble() / 1000000 - 180

            return createAddress(pseudo_lat, pseudo_lon, NetworkLayer.NETWORK, serviceType)
        } catch (e: Exception) {
            return null
        }
    }

    // =========================================================================
    // ROUTING
    // =========================================================================

    /**
     * Calculate routing distance between two addresses.
     * Uses hyperbolic geometry for efficient hierarchical routing.
     */
    fun routingDistance(from: BrahimNetworkAddress, to: BrahimNetworkAddress): Double {
        // Decode geographic components
        val fromCoords = cantorUnpair(from.geographicBN)
        val toCoords = cantorUnpair(to.geographicBN)

        // Euclidean distance in coordinate space
        val dx = (toCoords.first - fromCoords.first).toDouble()
        val dy = (toCoords.second - fromCoords.second).toDouble()
        val euclidean = sqrt(dx * dx + dy * dy)

        // Apply hyperbolic transformation for hierarchical routing
        // Closer addresses in same region are "much closer" than far addresses
        val hyperbolic = 2 * atanh(euclidean / (euclidean + S * 1000000))

        // Layer penalty (crossing layers adds distance)
        val layerPenalty = abs(from.layer.sequenceIndex - to.layer.sequenceIndex) * 0.1

        // Resonance bonus (aligned addresses route faster)
        val resonanceBonus = (from.resonanceScore + to.resonanceScore) / 2 * 0.1

        return hyperbolic + layerPenalty - resonanceBonus
    }

    /**
     * Find optimal route between two addresses.
     */
    fun findRoute(
        from: BrahimNetworkAddress,
        to: BrahimNetworkAddress,
        maxHops: Int = 10
    ): NetworkRoute {
        val hops = mutableListOf<RouteHop>()
        var currentDistance = routingDistance(from, to)

        // Simplified greedy routing
        var current = from
        var hopCount = 0

        while (hopCount < maxHops && currentDistance > 0.01) {
            // Find next hop (would query routing table in real implementation)
            val nextHop = calculateNextHop(current, to)

            hops.add(RouteHop(
                address = nextHop,
                distance = routingDistance(current, nextHop),
                latencyMs = estimateLatency(current, nextHop)
            ))

            currentDistance = routingDistance(nextHop, to)
            current = nextHop
            hopCount++
        }

        // Final hop to destination
        hops.add(RouteHop(
            address = to,
            distance = 0.0,
            latencyMs = estimateLatency(current, to)
        ))

        return NetworkRoute(
            from = from,
            to = to,
            hops = hops,
            totalDistance = hops.sumOf { it.distance },
            totalLatencyMs = hops.sumOf { it.latencyMs },
            resonanceAlignment = calculateRouteResonance(hops)
        )
    }

    private fun calculateNextHop(from: BrahimNetworkAddress, to: BrahimNetworkAddress): BrahimNetworkAddress {
        // Simplified: move halfway toward destination
        val fromCoords = cantorUnpair(from.geographicBN)
        val toCoords = cantorUnpair(to.geographicBN)

        val midLat = (fromCoords.first + toCoords.first) / 2
        val midLon = (fromCoords.second + toCoords.second) / 2

        return BrahimNetworkAddress(
            layer = from.layer,
            geographicBN = cantorPair(midLat, midLon),
            serviceBN = from.serviceBN,
            privacyLevel = from.privacyLevel,
            checkDigit = '0',
            resonanceScore = 0.5
        )
    }

    private fun estimateLatency(from: BrahimNetworkAddress, to: BrahimNetworkAddress): Double {
        // Rough estimate: 1ms per 100km + 10ms base
        val distance = routingDistance(from, to)
        return 10.0 + distance * 0.001
    }

    private fun calculateRouteResonance(hops: List<RouteHop>): Double {
        if (hops.isEmpty()) return 0.0
        return hops.map { it.address.resonanceScore }.average()
    }

    // =========================================================================
    // PRIVACY (ONION ROUTING)
    // =========================================================================

    /**
     * Wrap address in privacy layers (Brahim Onion).
     *
     * Each layer uses Wormhole cipher with β-based key derivation.
     */
    fun wrapPrivacyLayers(
        address: BrahimNetworkAddress,
        layers: Int = 3
    ): PrivacyWrappedAddress {
        val wrappedLayers = mutableListOf<PrivacyLayer>()

        var currentData = address.fullAddress.toByteArray()

        for (i in 0 until layers.coerceIn(1, 9)) {
            // Generate relay address for this layer
            val relayBN = generateRelayAddress(i)

            // Derive key from β and layer number
            val layerKey = deriveLayerKey(i, address.geographicBN)

            // Encrypt current data (simplified XOR for demonstration)
            val encrypted = xorEncrypt(currentData, layerKey)

            wrappedLayers.add(PrivacyLayer(
                layerIndex = i,
                relayAddress = relayBN,
                encryptedPayload = encrypted
            ))

            currentData = encrypted
        }

        return PrivacyWrappedAddress(
            originalAddress = address,
            layers = wrappedLayers,
            outerAddress = "BNP:${NetworkLayer.PRIVACY.code}:${wrappedLayers.last().relayAddress}:0:X"
        )
    }

    /**
     * Unwrap a single privacy layer.
     */
    fun unwrapLayer(
        wrapped: PrivacyWrappedAddress,
        layerIndex: Int,
        privateKey: ByteArray
    ): ByteArray? {
        val layer = wrapped.layers.getOrNull(layerIndex) ?: return null

        // Decrypt with private key
        return xorEncrypt(layer.encryptedPayload, privateKey)
    }

    private fun generateRelayAddress(layerIndex: Int): Long {
        // Use Brahim sequence element as base for relay
        val base = B[layerIndex % B.size].toLong()
        return cantorPair(base * 1000000, System.currentTimeMillis() % 1000000)
    }

    private fun deriveLayerKey(layerIndex: Int, seed: Long): ByteArray {
        // Derive key from β, layer index, and seed
        val keyMaterial = (BETA * (layerIndex + 1) * seed).toLong()
        return keyMaterial.toString().toByteArray().take(32).toByteArray()
    }

    private fun xorEncrypt(data: ByteArray, key: ByteArray): ByteArray {
        return data.mapIndexed { i, b ->
            (b.toInt() xor key[i % key.size].toInt()).toByte()
        }.toByteArray()
    }

    // =========================================================================
    // RESONANCE & QoS
    // =========================================================================

    /**
     * Calculate resonance score for an address.
     *
     * Higher resonance = better QoS, priority routing.
     */
    private fun calculateResonance(geographicBN: Long, serviceBN: Long, layer: NetworkLayer): Double {
        var score = 0.0

        // Check if geographic BN mod 214 matches sequence
        val geoMod = (geographicBN % S).toInt()
        if (B.contains(geoMod)) {
            score += 0.3
        }

        // Check if service BN aligns with layer
        if ((serviceBN % 10).toInt() == layer.sequenceIndex) {
            score += 0.2
        }

        // Check for golden ratio relationship
        val ratio = geographicBN.toDouble() / (serviceBN + 1).toDouble()
        if (abs(ratio - PHI) < 0.1 || abs(ratio - 1/PHI) < 0.1) {
            score += 0.2
        }

        // Check digit sum
        val digitSum = (geographicBN.toString() + serviceBN.toString()).sumOf { it.digitToInt() }
        val digitalRoot = if (digitSum == 0) 0 else ((digitSum - 1) % 9) + 1
        if (digitalRoot == 1 || digitalRoot == 9) {  // Aleph or completion
            score += 0.3
        }

        return score.coerceIn(0.0, 1.0)
    }

    /**
     * Priority classes based on resonance.
     */
    fun getQoSClass(address: BrahimNetworkAddress): QoSClass {
        return when {
            address.resonanceScore >= 0.8 -> QoSClass.RESONANT    // Highest priority
            address.resonanceScore >= 0.6 -> QoSClass.ALIGNED     // High priority
            address.resonanceScore >= 0.4 -> QoSClass.STANDARD    // Normal
            address.resonanceScore >= 0.2 -> QoSClass.BACKGROUND  // Low priority
            else -> QoSClass.BEST_EFFORT                          // Lowest
        }
    }

    enum class QoSClass(val priority: Int, val bandwidthMultiplier: Double) {
        RESONANT(5, 2.0),
        ALIGNED(4, 1.5),
        STANDARD(3, 1.0),
        BACKGROUND(2, 0.5),
        BEST_EFFORT(1, 0.25)
    }

    // =========================================================================
    // MESH NETWORKING
    // =========================================================================

    /**
     * Generate mesh network topology using Brahim sequence.
     *
     * Each node connects to neighbors at sequence-defined distances.
     */
    fun generateMeshTopology(
        centerLat: Double,
        centerLon: Double,
        nodeCount: Int
    ): MeshNetwork {
        val nodes = mutableListOf<MeshNode>()

        // Center node
        val centerAddress = createAddress(centerLat, centerLon, NetworkLayer.MESH, ServiceType.MESH)
        nodes.add(MeshNode(centerAddress, isGateway = true, neighbors = mutableListOf()))

        // Generate nodes at Brahim-sequence distances
        for (i in 0 until nodeCount - 1) {
            val sequenceIndex = i % B.size
            val distanceKm = B[sequenceIndex].toDouble() / 10  // Scale sequence to km

            val angle = (i * 360.0 / (nodeCount - 1)) * PI / 180
            val nodeLat = centerLat + (distanceKm / 111) * cos(angle)
            val nodeLon = centerLon + (distanceKm / (111 * cos(centerLat * PI / 180))) * sin(angle)

            val nodeAddress = createAddress(nodeLat, nodeLon, NetworkLayer.MESH, ServiceType.MESH)
            nodes.add(MeshNode(nodeAddress, isGateway = false, neighbors = mutableListOf()))
        }

        // Connect neighbors (each node connects to nodes within range)
        for (i in nodes.indices) {
            for (j in nodes.indices) {
                if (i != j) {
                    val distance = routingDistance(nodes[i].address, nodes[j].address)
                    if (distance < 0.5) {  // Threshold for neighbor
                        nodes[i].neighbors.add(j)
                    }
                }
            }
        }

        return MeshNetwork(
            nodes = nodes,
            totalCoverage = calculateCoverage(nodes),
            redundancy = calculateRedundancy(nodes)
        )
    }

    private fun calculateCoverage(nodes: List<MeshNode>): Double {
        // Simplified: assume each node covers area proportional to its connections
        return nodes.sumOf { it.neighbors.size.toDouble() } / (nodes.size * nodes.size)
    }

    private fun calculateRedundancy(nodes: List<MeshNode>): Double {
        // Average number of paths between any two nodes
        return nodes.map { it.neighbors.size }.average() / 2
    }

    // =========================================================================
    // HELPER FUNCTIONS
    // =========================================================================

    private fun cantorPair(a: Long, b: Long): Long {
        return ((a + b) * (a + b + 1)) / 2 + b
    }

    private fun cantorUnpair(z: Long): Pair<Long, Long> {
        val w = ((sqrt(8.0 * z + 1) - 1) / 2).toLong()
        val t = (w * w + w) / 2
        val b = z - t
        val a = w - b
        return Pair(a, b)
    }

    private fun calculateCheckDigit(geobn: Long, svcbn: Long, layer: Int, privacy: Int): Char {
        val combined = geobn + svcbn + layer + privacy
        val checksum = (combined % 36).toInt()
        return if (checksum < 10) ('0' + checksum) else ('A' + checksum - 10)
    }
}

// =========================================================================
// DATA CLASSES
// =========================================================================

data class RouteHop(
    val address: BrahimNetworkAddress,
    val distance: Double,
    val latencyMs: Double
)

data class NetworkRoute(
    val from: BrahimNetworkAddress,
    val to: BrahimNetworkAddress,
    val hops: List<RouteHop>,
    val totalDistance: Double,
    val totalLatencyMs: Double,
    val resonanceAlignment: Double
)

data class PrivacyLayer(
    val layerIndex: Int,
    val relayAddress: Long,
    val encryptedPayload: ByteArray
)

data class PrivacyWrappedAddress(
    val originalAddress: BrahimNetworkAddress,
    val layers: List<PrivacyLayer>,
    val outerAddress: String
)

data class MeshNode(
    val address: BrahimNetworkAddress,
    val isGateway: Boolean,
    val neighbors: MutableList<Int>
)

data class MeshNetwork(
    val nodes: List<MeshNode>,
    val totalCoverage: Double,
    val redundancy: Double
)
