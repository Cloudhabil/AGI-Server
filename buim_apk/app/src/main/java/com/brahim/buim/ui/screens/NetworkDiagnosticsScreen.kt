/**
 * BUIM - Network Diagnostics Screen
 * ==================================
 *
 * UI for ping, traceroute, and network testing.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.brahim.buim.network.*
import kotlinx.coroutines.launch

/**
 * Network Diagnostics Screen
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NetworkDiagnosticsScreen(
    onBack: () -> Unit = {}
) {
    var targetAddress by remember { mutableStateOf("8.8.8.8") }
    var packetCount by remember { mutableStateOf("10") }
    var isRunning by remember { mutableStateOf(false) }
    var pingResults by remember { mutableStateOf<List<PingResult>>(emptyList()) }
    var statistics by remember { mutableStateOf<PingStatistics?>(null) }
    var selectedTab by remember { mutableStateOf(0) }

    val scope = rememberCoroutineScope()
    val listState = rememberLazyListState()

    val primaryGold = Color(0xFFFFD700)
    val deepBlue = Color(0xFF0F0F23)
    val surfaceColor = Color(0xFF1A1A2E)
    val successGreen = Color(0xFF4CAF50)
    val errorRed = Color(0xFFE53935)

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Network Diagnostics",
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.Default.ArrowBack,
                            contentDescription = "Back",
                            tint = Color.White
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = surfaceColor
                )
            )
        },
        containerColor = deepBlue
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Tabs
            TabRow(
                selectedTabIndex = selectedTab,
                containerColor = surfaceColor,
                contentColor = primaryGold
            ) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = { Text("Ping") }
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text("Quick Test") }
                )
                Tab(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    text = { Text("BNP Relays") }
                )
            }

            when (selectedTab) {
                0 -> {
                    // Ping Tab
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp)
                    ) {
                        // Input section
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = surfaceColor),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Column(
                                modifier = Modifier.padding(16.dp)
                            ) {
                                // Target address input
                                OutlinedTextField(
                                    value = targetAddress,
                                    onValueChange = { targetAddress = it },
                                    label = { Text("Target (IP, hostname, or BNP)", color = Color.White.copy(alpha = 0.7f)) },
                                    placeholder = { Text("8.8.8.8 or BNP:136:...", color = Color.White.copy(alpha = 0.3f)) },
                                    modifier = Modifier.fillMaxWidth(),
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedBorderColor = primaryGold,
                                        unfocusedBorderColor = Color.White.copy(alpha = 0.3f),
                                        focusedTextColor = Color.White,
                                        unfocusedTextColor = Color.White,
                                        cursorColor = primaryGold
                                    ),
                                    singleLine = true,
                                    enabled = !isRunning,
                                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                                    keyboardActions = KeyboardActions(
                                        onDone = {
                                            if (!isRunning && targetAddress.isNotBlank()) {
                                                // Start ping
                                            }
                                        }
                                    )
                                )

                                Spacer(modifier = Modifier.height(12.dp))

                                // Packet count
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    OutlinedTextField(
                                        value = packetCount,
                                        onValueChange = { packetCount = it.filter { c -> c.isDigit() } },
                                        label = { Text("Packets", color = Color.White.copy(alpha = 0.7f)) },
                                        modifier = Modifier.width(100.dp),
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedBorderColor = primaryGold,
                                            unfocusedBorderColor = Color.White.copy(alpha = 0.3f),
                                            focusedTextColor = Color.White,
                                            unfocusedTextColor = Color.White
                                        ),
                                        singleLine = true,
                                        enabled = !isRunning,
                                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                                    )

                                    Spacer(modifier = Modifier.weight(1f))

                                    // Start/Stop button
                                    Button(
                                        onClick = {
                                            if (isRunning) {
                                                NetworkDiagnostics.cancelPing()
                                                isRunning = false
                                            } else {
                                                isRunning = true
                                                pingResults = emptyList()
                                                statistics = null

                                                scope.launch {
                                                    val count = packetCount.toIntOrNull() ?: 10
                                                    statistics = NetworkDiagnostics.ping(
                                                        target = targetAddress,
                                                        count = count,
                                                        onProgress = { result ->
                                                            pingResults = pingResults + result
                                                        }
                                                    )
                                                    isRunning = false
                                                }
                                            }
                                        },
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (isRunning) errorRed else primaryGold
                                        ),
                                        enabled = targetAddress.isNotBlank()
                                    ) {
                                        Icon(
                                            if (isRunning) Icons.Default.Stop else Icons.Default.PlayArrow,
                                            contentDescription = null,
                                            tint = if (isRunning) Color.White else Color.Black
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            if (isRunning) "Stop" else "Ping",
                                            color = if (isRunning) Color.White else Color.Black
                                        )
                                    }
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        // Statistics card (if available)
                        statistics?.let { stats ->
                            StatisticsCard(stats, primaryGold, surfaceColor, successGreen, errorRed)
                            Spacer(modifier = Modifier.height(16.dp))
                        }

                        // Results list
                        Text(
                            "Results",
                            color = Color.White,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(bottom = 8.dp)
                        )

                        LazyColumn(
                            state = listState,
                            modifier = Modifier.weight(1f),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            items(pingResults) { result ->
                                PingResultItem(result, primaryGold, successGreen, errorRed)
                            }

                            if (isRunning) {
                                item {
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(8.dp),
                                        horizontalArrangement = Arrangement.Center
                                    ) {
                                        CircularProgressIndicator(
                                            color = primaryGold,
                                            modifier = Modifier.size(24.dp)
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            "Pinging...",
                                            color = Color.White.copy(alpha = 0.7f)
                                        )
                                    }
                                }
                            }
                        }

                        // Auto-scroll to bottom
                        LaunchedEffect(pingResults.size) {
                            if (pingResults.isNotEmpty()) {
                                listState.animateScrollToItem(pingResults.size - 1)
                            }
                        }
                    }
                }

                1 -> {
                    // Quick Test Tab
                    QuickTestTab(primaryGold, surfaceColor, successGreen, errorRed)
                }

                2 -> {
                    // BNP Relays Tab
                    BnpRelaysTab(primaryGold, surfaceColor, successGreen, errorRed)
                }
            }
        }
    }
}

@Composable
fun StatisticsCard(
    stats: PingStatistics,
    primaryGold: Color,
    surfaceColor: Color,
    successGreen: Color,
    errorRed: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = surfaceColor),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "Statistics",
                    color = primaryGold,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
                Surface(
                    shape = RoundedCornerShape(4.dp),
                    color = when {
                        stats.lossPercentage == 0.0 -> successGreen.copy(alpha = 0.2f)
                        stats.lossPercentage < 20 -> primaryGold.copy(alpha = 0.2f)
                        else -> errorRed.copy(alpha = 0.2f)
                    }
                ) {
                    Text(
                        "${stats.lossPercentage.toInt()}% loss",
                        color = when {
                            stats.lossPercentage == 0.0 -> successGreen
                            stats.lossPercentage < 20 -> primaryGold
                            else -> errorRed
                        },
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        fontSize = 12.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Packet counts
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem("Sent", stats.packetsSent.toString(), Color.White)
                StatItem("Received", stats.packetsReceived.toString(), successGreen)
                StatItem("Lost", stats.packetsLost.toString(), errorRed)
            }

            Spacer(modifier = Modifier.height(12.dp))

            Divider(color = Color.White.copy(alpha = 0.1f))

            Spacer(modifier = Modifier.height(12.dp))

            // Latency stats
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem("Min", "${stats.minLatencyMs.toInt()} ms", Color.White)
                StatItem("Avg", "${stats.avgLatencyMs.toInt()} ms", primaryGold)
                StatItem("Max", "${stats.maxLatencyMs.toInt()} ms", Color.White)
            }

            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem("Jitter", "${stats.jitterMs.toInt()} ms", Color.White.copy(alpha = 0.7f))
                StatItem("StdDev", "${stats.stdDevMs.toInt()} ms", Color.White.copy(alpha = 0.7f))
                if (stats.targetType == TargetType.BNP) {
                    StatItem("Resonance", "${(stats.resonanceScore * 100).toInt()}%", primaryGold)
                }
            }
        }
    }
}

@Composable
fun StatItem(label: String, value: String, valueColor: Color) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            value,
            color = valueColor,
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp
        )
        Text(
            label,
            color = Color.White.copy(alpha = 0.5f),
            fontSize = 12.sp
        )
    }
}

@Composable
fun PingResultItem(
    result: PingResult,
    primaryGold: Color,
    successGreen: Color,
    errorRed: Color
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                if (result.success) Color.Transparent
                else errorRed.copy(alpha = 0.1f),
                RoundedCornerShape(4.dp)
            )
            .padding(horizontal = 8.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Status indicator
        Box(
            modifier = Modifier
                .size(8.dp)
                .clip(CircleShape)
                .background(if (result.success) successGreen else errorRed)
        )

        Spacer(modifier = Modifier.width(8.dp))

        // Sequence number
        Text(
            "seq=${result.sequenceNumber}",
            color = Color.White.copy(alpha = 0.7f),
            fontFamily = FontFamily.Monospace,
            fontSize = 13.sp,
            modifier = Modifier.width(60.dp)
        )

        if (result.success) {
            // TTL
            Text(
                "ttl=${result.ttl}",
                color = Color.White.copy(alpha = 0.7f),
                fontFamily = FontFamily.Monospace,
                fontSize = 13.sp,
                modifier = Modifier.width(60.dp)
            )

            // Bytes
            Text(
                "${result.bytes} bytes",
                color = Color.White.copy(alpha = 0.5f),
                fontFamily = FontFamily.Monospace,
                fontSize = 13.sp,
                modifier = Modifier.width(70.dp)
            )

            Spacer(modifier = Modifier.weight(1f))

            // Latency
            Text(
                "${result.latencyMs.toInt()} ms",
                color = when {
                    result.latencyMs < 50 -> successGreen
                    result.latencyMs < 100 -> primaryGold
                    else -> errorRed
                },
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                fontSize = 13.sp
            )
        } else {
            // Error message
            Text(
                result.error ?: "Request timeout",
                color = errorRed,
                fontSize = 13.sp
            )
        }
    }
}

@Composable
fun QuickTestTab(
    primaryGold: Color,
    surfaceColor: Color,
    successGreen: Color,
    errorRed: Color
) {
    var testResults by remember { mutableStateOf<Map<String, Boolean>?>(null) }
    var isRunning by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            "Quick Connectivity Test",
            color = Color.White,
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp
        )

        Text(
            "Test connection to common servers",
            color = Color.White.copy(alpha = 0.5f),
            fontSize = 14.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                isRunning = true
                scope.launch {
                    testResults = NetworkDiagnostics.quickConnectivityTest()
                    isRunning = false
                }
            },
            colors = ButtonDefaults.buttonColors(containerColor = primaryGold),
            enabled = !isRunning,
            modifier = Modifier.fillMaxWidth()
        ) {
            if (isRunning) {
                CircularProgressIndicator(
                    color = Color.Black,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
            }
            Text(
                if (isRunning) "Testing..." else "Run Test",
                color = Color.Black
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        testResults?.let { results ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = surfaceColor),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    results.forEach { (name, success) ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 8.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(name, color = Color.White)
                            Row(
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    if (success) Icons.Default.CheckCircle else Icons.Default.Cancel,
                                    contentDescription = null,
                                    tint = if (success) successGreen else errorRed,
                                    modifier = Modifier.size(20.dp)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    if (success) "OK" else "FAIL",
                                    color = if (success) successGreen else errorRed,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }

                        if (results.keys.last() != name) {
                            Divider(color = Color.White.copy(alpha = 0.1f))
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun BnpRelaysTab(
    primaryGold: Color,
    surfaceColor: Color,
    successGreen: Color,
    errorRed: Color
) {
    var relayResults by remember { mutableStateOf<Map<String, PingResult>?>(null) }
    var isRunning by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            "BNP Relay Network",
            color = Color.White,
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp
        )

        Text(
            "Test connectivity to Brahim Network Protocol relays",
            color = Color.White.copy(alpha = 0.5f),
            fontSize = 14.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                isRunning = true
                scope.launch {
                    relayResults = NetworkDiagnostics.testBnpRelays()
                    isRunning = false
                }
            },
            colors = ButtonDefaults.buttonColors(containerColor = primaryGold),
            enabled = !isRunning,
            modifier = Modifier.fillMaxWidth()
        ) {
            if (isRunning) {
                CircularProgressIndicator(
                    color = Color.Black,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
            }
            Text(
                if (isRunning) "Testing Relays..." else "Test BNP Relays",
                color = Color.Black
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Relay list
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = surfaceColor),
            shape = RoundedCornerShape(12.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    "Available Relays",
                    color = primaryGold,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 8.dp)
                )

                TransportBridge.DEFAULT_RELAYS.forEach { relay ->
                    val host = relay.removePrefix("wss://").split("/").first()
                    val result = relayResults?.get(host)

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                host,
                                color = Color.White,
                                fontSize = 14.sp
                            )
                            Text(
                                relay,
                                color = Color.White.copy(alpha = 0.5f),
                                fontSize = 11.sp
                            )
                        }

                        result?.let { r ->
                            Row(
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                if (r.success) {
                                    Text(
                                        "${r.latencyMs.toInt()} ms",
                                        color = successGreen,
                                        fontWeight = FontWeight.Bold
                                    )
                                } else {
                                    Icon(
                                        Icons.Default.CloudOff,
                                        contentDescription = null,
                                        tint = errorRed,
                                        modifier = Modifier.size(20.dp)
                                    )
                                }
                            }
                        } ?: run {
                            if (isRunning) {
                                CircularProgressIndicator(
                                    color = primaryGold,
                                    modifier = Modifier.size(16.dp),
                                    strokeWidth = 2.dp
                                )
                            } else {
                                Text(
                                    "Not tested",
                                    color = Color.White.copy(alpha = 0.3f),
                                    fontSize = 12.sp
                                )
                            }
                        }
                    }

                    Divider(color = Color.White.copy(alpha = 0.1f))
                }
            }
        }
    }
}
