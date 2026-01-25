/**
 * Killer Use Cases Screen
 * =======================
 *
 * Main dashboard for all Brahim Number use cases.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.brahim.buim.usecase.BrahimGeoIDFactory
import com.brahim.buim.usecase.BrahimGeoID
import com.brahim.buim.ui.theme.GoldenPrimary

/**
 * Use case definition.
 */
data class UseCase(
    val id: String,
    val title: String,
    val subtitle: String,
    val icon: ImageVector,
    val color: Color
)

private val useCases = listOf(
    UseCase("geo_id", "Geospatial IDs", "Create unique IDs from coordinates", Icons.Filled.Place, Color(0xFF4CAF50)),
    UseCase("verify", "Verify ID", "Check if an ID is valid", Icons.Filled.VerifiedUser, Color(0xFF2196F3)),
    UseCase("route", "Route Tracking", "Create tamper-proof routes", Icons.Filled.Route, Color(0xFFFF9800)),
    UseCase("fingerprint", "Dataset Fingerprint", "Detect data tampering", Icons.Filled.Fingerprint, Color(0xFF9C27B0)),
    UseCase("decode", "Decode Number", "Recover coordinates from BN", Icons.Filled.QrCode, Color(0xFFE91E63)),
    UseCase("blockchain", "Block Validator", "Check blockchain criteria", Icons.Filled.Link, Color(0xFF00BCD4))
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KillerUseCasesScreen(
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedUseCase by remember { mutableStateOf<String?>(null) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Brahim Tools", style = MaterialTheme.typography.titleMedium)
                        Text(
                            "BNv1 Specification",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = GoldenPrimary.copy(alpha = 0.1f)
                )
            )
        }
    ) { paddingValues ->
        if (selectedUseCase == null) {
            // Show use case list
            UseCaseList(
                useCases = useCases,
                onSelectUseCase = { selectedUseCase = it },
                modifier = Modifier.padding(paddingValues)
            )
        } else {
            // Show selected use case tool
            UseCaseTool(
                useCaseId = selectedUseCase!!,
                onBack = { selectedUseCase = null },
                modifier = Modifier.padding(paddingValues)
            )
        }
    }
}

@Composable
private fun UseCaseList(
    useCases: List<UseCase>,
    onSelectUseCase: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            // Header card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = GoldenPrimary.copy(alpha = 0.15f)
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "KILLER USE CASES",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        "Real applications that make Brahim Numbers useful",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }

        items(useCases) { useCase ->
            UseCaseCard(
                useCase = useCase,
                onClick = { onSelectUseCase(useCase.id) }
            )
        }

        item {
            Spacer(modifier = Modifier.height(8.dp))
            // Spec info
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Filled.Lock,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text("Specification: BNv1 (FROZEN)", style = MaterialTheme.typography.labelMedium)
                        Text(
                            "Algorithm is immutable • CC0 License",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun UseCaseCard(
    useCase: UseCase,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        onClick = onClick,
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = useCase.color.copy(alpha = 0.15f)
            ) {
                Icon(
                    imageVector = useCase.icon,
                    contentDescription = null,
                    modifier = Modifier.padding(12.dp),
                    tint = useCase.color
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = useCase.title,
                    style = MaterialTheme.typography.titleSmall
                )
                Text(
                    text = useCase.subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Icon(
                Icons.Filled.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun UseCaseTool(
    useCaseId: String,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    when (useCaseId) {
        "geo_id" -> GeoIdTool(onBack = onBack, modifier = modifier)
        "verify" -> VerifyIdTool(onBack = onBack, modifier = modifier)
        "route" -> RouteTrackingTool(onBack = onBack, modifier = modifier)
        "fingerprint" -> FingerprintTool(onBack = onBack, modifier = modifier)
        "decode" -> DecodeTool(onBack = onBack, modifier = modifier)
        "blockchain" -> BlockchainTool(onBack = onBack, modifier = modifier)
    }
}

// =========================================================================
// TOOL 1: Geospatial ID Creator
// =========================================================================

@Composable
private fun GeoIdTool(onBack: () -> Unit, modifier: Modifier = Modifier) {
    var latitude by remember { mutableStateOf("41.4037") }
    var longitude by remember { mutableStateOf("2.1735") }
    var locationHint by remember { mutableStateOf("SF") }
    var result by remember { mutableStateOf<BrahimGeoID?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Back button
        TextButton(onClick = onBack) {
            Icon(Icons.Filled.ArrowBack, contentDescription = null)
            Spacer(modifier = Modifier.width(4.dp))
            Text("Back to Tools")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text("Create Geospatial ID", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Generate unique ID from coordinates",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = latitude,
            onValueChange = { latitude = it },
            label = { Text("Latitude") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = longitude,
            onValueChange = { longitude = it },
            label = { Text("Longitude") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = locationHint,
            onValueChange = { locationHint = it.take(4) },
            label = { Text("Location Hint (optional, max 4 chars)") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                try {
                    val lat = latitude.toDoubleOrNull() ?: throw IllegalArgumentException("Invalid latitude")
                    val lon = longitude.toDoubleOrNull() ?: throw IllegalArgumentException("Invalid longitude")
                    result = BrahimGeoIDFactory.create(lat, lon, locationHint)
                    error = null
                } catch (e: Exception) {
                    error = e.message
                    result = null
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Filled.Add, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Generate ID")
        }

        error?.let {
            Spacer(modifier = Modifier.height(8.dp))
            Text(it, color = MaterialTheme.colorScheme.error)
        }

        result?.let { geoId ->
            Spacer(modifier = Modifier.height(24.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF4CAF50).copy(alpha = 0.1f)
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("RESULT", style = MaterialTheme.typography.labelMedium)
                    Spacer(modifier = Modifier.height(12.dp))

                    ResultRow("Full ID", geoId.fullId)
                    ResultRow("Short ID", geoId.shortId)
                    ResultRow("Human ID", geoId.humanId)
                    ResultRow("Brahim #", geoId.brahimNumber.toString())
                    ResultRow("Check Digit", geoId.checkDigit.toString())
                    ResultRow("Mod 214", geoId.mod214.toString())
                }
            }
        }
    }
}

// =========================================================================
// TOOL 2: Verify ID
// =========================================================================

@Composable
private fun VerifyIdTool(onBack: () -> Unit, modifier: Modifier = Modifier) {
    var idInput by remember { mutableStateOf("BN:949486203882100-7") }
    var verificationResult by remember { mutableStateOf<Boolean?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        TextButton(onClick = onBack) {
            Icon(Icons.Filled.ArrowBack, contentDescription = null)
            Spacer(modifier = Modifier.width(4.dp))
            Text("Back to Tools")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text("Verify Brahim ID", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Check if check digit is valid",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = idInput,
            onValueChange = { idInput = it },
            label = { Text("Brahim ID") },
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("BN:xxx-c or BN214:xxx-c") }
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                verificationResult = BrahimGeoIDFactory.verify(idInput)
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Filled.VerifiedUser, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Verify")
        }

        verificationResult?.let { isValid ->
            Spacer(modifier = Modifier.height(24.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = if (isValid) Color(0xFF4CAF50).copy(alpha = 0.1f)
                    else Color(0xFFF44336).copy(alpha = 0.1f)
                )
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        if (isValid) Icons.Filled.CheckCircle else Icons.Filled.Cancel,
                        contentDescription = null,
                        tint = if (isValid) Color(0xFF4CAF50) else Color(0xFFF44336),
                        modifier = Modifier.size(48.dp)
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Text(
                            if (isValid) "VALID" else "INVALID",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            if (isValid) "Check digit is correct"
                            else "Check digit does not match",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
        }
    }
}

// =========================================================================
// TOOL 3: Route Tracking
// =========================================================================

@Composable
private fun RouteTrackingTool(onBack: () -> Unit, modifier: Modifier = Modifier) {
    var routeId by remember { mutableStateOf("ROUTE-001") }
    var waypointsText by remember { mutableStateOf("41.3851,2.1734\n41.3902,2.1540\n41.4036,2.1744") }
    var routeResult by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        TextButton(onClick = onBack) {
            Icon(Icons.Filled.ArrowBack, contentDescription = null)
            Spacer(modifier = Modifier.width(4.dp))
            Text("Back to Tools")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text("Route Tracking", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Create tamper-proof route with checksum",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = routeId,
            onValueChange = { routeId = it },
            label = { Text("Route ID") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = waypointsText,
            onValueChange = { waypointsText = it },
            label = { Text("Waypoints (lat,lon per line)") },
            modifier = Modifier
                .fillMaxWidth()
                .height(150.dp),
            maxLines = 10
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                try {
                    val waypoints = waypointsText.lines()
                        .filter { it.isNotBlank() }
                        .map { line ->
                            val parts = line.split(",")
                            parts[0].trim().toDouble() to parts[1].trim().toDouble()
                        }

                    val route = BrahimGeoIDFactory.createRoute(routeId, waypoints)

                    routeResult = buildString {
                        appendLine("Route: ${route.routeId}")
                        appendLine("Waypoints: ${route.waypoints.size}")
                        appendLine("Checksum: ${route.checksum}")
                        appendLine()
                        route.waypoints.forEachIndexed { i, wp ->
                            appendLine("${i + 1}. ${wp.shortId}")
                        }
                    }
                } catch (e: Exception) {
                    routeResult = "Error: ${e.message}"
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Filled.Route, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Create Route")
        }

        routeResult?.let { result ->
            Spacer(modifier = Modifier.height(24.dp))

            Card(modifier = Modifier.fillMaxWidth()) {
                Text(
                    result,
                    modifier = Modifier.padding(16.dp),
                    fontFamily = FontFamily.Monospace,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

// =========================================================================
// TOOL 4: Fingerprint
// =========================================================================

@Composable
private fun FingerprintTool(onBack: () -> Unit, modifier: Modifier = Modifier) {
    var coordsText by remember { mutableStateOf("41.4037,2.1735\n40.7128,74.0060\n51.5074,0.1278") }
    var fingerprintResult by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        TextButton(onClick = onBack) {
            Icon(Icons.Filled.ArrowBack, contentDescription = null)
            Spacer(modifier = Modifier.width(4.dp))
            Text("Back to Tools")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text("Dataset Fingerprint", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Create unique fingerprint for data provenance",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = coordsText,
            onValueChange = { coordsText = it },
            label = { Text("Coordinates (lat,lon per line)") },
            modifier = Modifier
                .fillMaxWidth()
                .height(150.dp),
            maxLines = 10
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                try {
                    val coords = coordsText.lines()
                        .filter { it.isNotBlank() }
                        .map { line ->
                            val parts = line.split(",")
                            parts[0].trim().toDouble() to parts[1].trim().toDouble()
                        }

                    val fp = BrahimGeoIDFactory.fingerprintDataset(coords)

                    fingerprintResult = buildString {
                        appendLine("FINGERPRINT ID:")
                        appendLine(fp.fingerprintId)
                        appendLine()
                        appendLine("Points: ${fp.count}")
                        appendLine("XOR Hash: ${fp.xorFingerprint}")
                        appendLine("Digital Root: ${fp.digitalRoot}")
                        appendLine("Check Digit: ${fp.checkDigit}")
                    }
                } catch (e: Exception) {
                    fingerprintResult = "Error: ${e.message}"
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Filled.Fingerprint, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Generate Fingerprint")
        }

        fingerprintResult?.let { result ->
            Spacer(modifier = Modifier.height(24.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF9C27B0).copy(alpha = 0.1f)
                )
            ) {
                Text(
                    result,
                    modifier = Modifier.padding(16.dp),
                    fontFamily = FontFamily.Monospace,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

// =========================================================================
// TOOL 5: Decode
// =========================================================================

@Composable
private fun DecodeTool(onBack: () -> Unit, modifier: Modifier = Modifier) {
    var brahimNumber by remember { mutableStateOf("949486203882100") }
    var decodeResult by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        TextButton(onClick = onBack) {
            Icon(Icons.Filled.ArrowBack, contentDescription = null)
            Spacer(modifier = Modifier.width(4.dp))
            Text("Back to Tools")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text("Decode Brahim Number", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Recover original coordinates",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = brahimNumber,
            onValueChange = { brahimNumber = it },
            label = { Text("Brahim Number") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                try {
                    val bn = brahimNumber.toLongOrNull() ?: throw IllegalArgumentException("Invalid number")
                    val coords = BrahimGeoIDFactory.decode(bn)

                    decodeResult = if (coords != null) {
                        "Latitude: ${coords.first}°\nLongitude: ${coords.second}°"
                    } else {
                        "Could not decode (invalid range)"
                    }
                } catch (e: Exception) {
                    decodeResult = "Error: ${e.message}"
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Filled.QrCode, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Decode")
        }

        decodeResult?.let { result ->
            Spacer(modifier = Modifier.height(24.dp))

            Card(modifier = Modifier.fillMaxWidth()) {
                Text(
                    result,
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.bodyLarge
                )
            }
        }
    }
}

// =========================================================================
// TOOL 6: Blockchain Validator
// =========================================================================

@Composable
private fun BlockchainTool(onBack: () -> Unit, modifier: Modifier = Modifier) {
    var latitude by remember { mutableStateOf("41.4037") }
    var longitude by remember { mutableStateOf("2.1735") }
    var cultural by remember { mutableStateOf("UNESCO World Heritage Site") }
    var validationResult by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        TextButton(onClick = onBack) {
            Icon(Icons.Filled.ArrowBack, contentDescription = null)
            Spacer(modifier = Modifier.width(4.dp))
            Text("Back to Tools")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text("Block Validator", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Check if coordinates qualify as a block",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = latitude,
            onValueChange = { latitude = it },
            label = { Text("Latitude") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = longitude,
            onValueChange = { longitude = it },
            label = { Text("Longitude") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = cultural,
            onValueChange = { cultural = it },
            label = { Text("Cultural Significance") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                try {
                    val lat = latitude.toDoubleOrNull() ?: throw IllegalArgumentException("Invalid latitude")
                    val lon = longitude.toDoubleOrNull() ?: throw IllegalArgumentException("Invalid longitude")

                    val receipt = com.brahim.buim.blockchain.BrahimMiningProtocol.verifyBlock(
                        latitude = kotlin.math.abs(lat),
                        longitude = kotlin.math.abs(lon),
                        culturalDescription = cultural,
                        difficulty = com.brahim.buim.blockchain.MiningDifficulty.FOUNDER
                    )

                    validationResult = buildString {
                        appendLine(if (receipt.isValid) "✓ VALID BLOCK" else "✗ DOES NOT QUALIFY")
                        appendLine()
                        appendLine("Score: ${receipt.score}/${receipt.maxScore}")
                        appendLine("Brahim #: ${receipt.brahimNumber}")
                        appendLine("Digit Sum: ${receipt.digitSum}")
                        appendLine("Digital Root: ${receipt.digitalRoot}")
                        appendLine()
                        appendLine("Criteria:")
                        receipt.criteriaResults.forEach { (key, value) ->
                            appendLine("  ${if (value) "✓" else "✗"} ${key.replace("_", " ")}")
                        }
                    }
                } catch (e: Exception) {
                    validationResult = "Error: ${e.message}"
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Filled.Link, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Validate")
        }

        validationResult?.let { result ->
            Spacer(modifier = Modifier.height(24.dp))

            Card(modifier = Modifier.fillMaxWidth()) {
                Text(
                    result,
                    modifier = Modifier.padding(16.dp),
                    fontFamily = FontFamily.Monospace,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

// =========================================================================
// Helper Composables
// =========================================================================

@Composable
private fun ResultRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            value,
            style = MaterialTheme.typography.bodyMedium,
            fontFamily = FontFamily.Monospace,
            fontWeight = FontWeight.Medium
        )
    }
}
