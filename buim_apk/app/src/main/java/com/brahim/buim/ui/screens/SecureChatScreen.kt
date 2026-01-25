/**
 * BUIM - Secure Chat UI
 * Signal-like encrypted messaging interface
 */
package com.brahim.buim.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.brahim.buim.chat.*
import com.brahim.buim.core.BrahimConstants
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

/**
 * Main Secure Chat Screen
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SecureChatScreen(
    peerName: String = "Contact",
    peerBnpAddress: String = "BNP:136:0:60:3:0",
    onBack: () -> Unit = {}
) {
    var messageText by remember { mutableStateOf("") }
    var messages by remember { mutableStateOf(listOf<ChatMessage>()) }
    var isWalkieTalkieMode by remember { mutableStateOf(false) }
    var isPttPressed by remember { mutableStateOf(false) }
    var showEncryptionInfo by remember { mutableStateOf(false) }

    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()

    // Colors from Brahim theme
    val primaryGold = Color(0xFFFFD700)
    val deepBlue = Color(0xFF0F0F23)
    val surfaceColor = Color(0xFF1A1A2E)

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = peerName,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Text(
                            text = "End-to-end encrypted",
                            fontSize = 12.sp,
                            color = primaryGold.copy(alpha = 0.7f)
                        )
                    }
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
                actions = {
                    // Walkie-talkie toggle
                    IconButton(
                        onClick = { isWalkieTalkieMode = !isWalkieTalkieMode }
                    ) {
                        Icon(
                            if (isWalkieTalkieMode) Icons.Default.Mic else Icons.Default.MicOff,
                            contentDescription = "Walkie Talkie",
                            tint = if (isWalkieTalkieMode) primaryGold else Color.White
                        )
                    }
                    // Encryption info
                    IconButton(
                        onClick = { showEncryptionInfo = true }
                    ) {
                        Icon(
                            Icons.Default.Lock,
                            contentDescription = "Encryption",
                            tint = primaryGold
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
            // Messages list
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                state = listState,
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Encryption header
                item {
                    EncryptionBanner()
                }

                items(messages) { message ->
                    MessageBubble(
                        message = message,
                        isFromMe = message.isFromMe
                    )
                }
            }

            // Walkie-talkie mode or text input
            AnimatedVisibility(
                visible = isWalkieTalkieMode,
                enter = slideInVertically() + fadeIn(),
                exit = slideOutVertically() + fadeOut()
            ) {
                WalkieTalkieControls(
                    isPttPressed = isPttPressed,
                    onPttChange = { isPttPressed = it }
                )
            }

            AnimatedVisibility(
                visible = !isWalkieTalkieMode,
                enter = slideInVertically() + fadeIn(),
                exit = slideOutVertically() + fadeOut()
            ) {
                // Text input
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(surfaceColor)
                        .padding(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Attach button
                    IconButton(onClick = { /* Attach file */ }) {
                        Icon(
                            Icons.Default.AttachFile,
                            contentDescription = "Attach",
                            tint = Color.White.copy(alpha = 0.7f)
                        )
                    }

                    // Text field
                    TextField(
                        value = messageText,
                        onValueChange = { messageText = it },
                        modifier = Modifier.weight(1f),
                        placeholder = {
                            Text(
                                "Message",
                                color = Color.White.copy(alpha = 0.5f)
                            )
                        },
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent,
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White,
                            cursorColor = primaryGold,
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent
                        ),
                        maxLines = 4
                    )

                    // Send button
                    IconButton(
                        onClick = {
                            if (messageText.isNotBlank()) {
                                messages = messages + ChatMessage(
                                    id = UUID.randomUUID().toString(),
                                    text = messageText,
                                    timestamp = System.currentTimeMillis(),
                                    isFromMe = true,
                                    isEncrypted = true
                                )
                                messageText = ""
                                scope.launch {
                                    listState.animateScrollToItem(messages.size)
                                }
                            }
                        },
                        enabled = messageText.isNotBlank()
                    ) {
                        Icon(
                            Icons.Default.Send,
                            contentDescription = "Send",
                            tint = if (messageText.isNotBlank()) primaryGold else Color.White.copy(alpha = 0.3f)
                        )
                    }
                }
            }
        }
    }

    // Encryption info dialog
    if (showEncryptionInfo) {
        EncryptionInfoDialog(
            peerBnpAddress = peerBnpAddress,
            onDismiss = { showEncryptionInfo = false }
        )
    }
}

@Composable
fun EncryptionBanner() {
    val primaryGold = Color(0xFFFFD700)

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = primaryGold.copy(alpha = 0.1f)
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                Icons.Default.Lock,
                contentDescription = null,
                tint = primaryGold,
                modifier = Modifier.size(20.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Column {
                Text(
                    "Brahim End-to-End Encryption",
                    color = primaryGold,
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp
                )
                Text(
                    "Messages secured with β = √5 - 2 Wormhole Cipher",
                    color = Color.White.copy(alpha = 0.7f),
                    fontSize = 12.sp
                )
            }
        }
    }
}

@Composable
fun MessageBubble(
    message: ChatMessage,
    isFromMe: Boolean
) {
    val primaryGold = Color(0xFFFFD700)
    val bubbleColor = if (isFromMe) primaryGold.copy(alpha = 0.2f) else Color(0xFF2A2A3E)

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isFromMe) Arrangement.End else Arrangement.Start
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .clip(
                    RoundedCornerShape(
                        topStart = 16.dp,
                        topEnd = 16.dp,
                        bottomStart = if (isFromMe) 16.dp else 4.dp,
                        bottomEnd = if (isFromMe) 4.dp else 16.dp
                    )
                )
                .background(bubbleColor)
                .padding(12.dp)
        ) {
            Text(
                text = message.text,
                color = Color.White,
                fontSize = 15.sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = formatTime(message.timestamp),
                    color = Color.White.copy(alpha = 0.5f),
                    fontSize = 11.sp
                )
                if (isFromMe && message.isEncrypted) {
                    Spacer(modifier = Modifier.width(4.dp))
                    Icon(
                        Icons.Default.Lock,
                        contentDescription = "Encrypted",
                        tint = primaryGold.copy(alpha = 0.7f),
                        modifier = Modifier.size(12.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun WalkieTalkieControls(
    isPttPressed: Boolean,
    onPttChange: (Boolean) -> Unit
) {
    val primaryGold = Color(0xFFFFD700)
    val surfaceColor = Color(0xFF1A1A2E)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(surfaceColor)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Status indicator
        Text(
            text = if (isPttPressed) "Transmitting..." else "Push to Talk",
            color = if (isPttPressed) primaryGold else Color.White,
            fontWeight = FontWeight.Bold,
            fontSize = 16.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        // PTT Button
        Box(
            modifier = Modifier
                .size(100.dp)
                .clip(CircleShape)
                .background(
                    if (isPttPressed) primaryGold else primaryGold.copy(alpha = 0.3f)
                )
                .pointerInput(Unit) {
                    detectTapGestures(
                        onPress = {
                            onPttChange(true)
                            tryAwaitRelease()
                            onPttChange(false)
                        }
                    )
                },
            contentAlignment = Alignment.Center
        ) {
            Icon(
                Icons.Default.Mic,
                contentDescription = "Push to Talk",
                tint = if (isPttPressed) Color.Black else Color.White,
                modifier = Modifier.size(48.dp)
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Encryption indicator
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                Icons.Default.Lock,
                contentDescription = null,
                tint = primaryGold.copy(alpha = 0.7f),
                modifier = Modifier.size(14.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = "Voice encrypted with Wormhole Cipher",
                color = Color.White.copy(alpha = 0.5f),
                fontSize = 12.sp
            )
        }
    }
}

@Composable
fun EncryptionInfoDialog(
    peerBnpAddress: String,
    onDismiss: () -> Unit
) {
    val primaryGold = Color(0xFFFFD700)

    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = Color(0xFF1A1A2E),
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Default.Lock,
                    contentDescription = null,
                    tint = primaryGold
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    "Brahim Encryption",
                    color = Color.White
                )
            }
        },
        text = {
            Column {
                EncryptionInfoRow("Protocol", "Brahim Double Ratchet")
                EncryptionInfoRow("Cipher", "Wormhole (β = √5 - 2)")
                EncryptionInfoRow("Key Exchange", "Brahim X3DH")
                EncryptionInfoRow("Privacy Layers", "Onion Protocol")

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    "Peer BNP Address:",
                    color = Color.White.copy(alpha = 0.7f),
                    fontSize = 12.sp
                )
                Text(
                    peerBnpAddress,
                    color = primaryGold,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Mono
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Security properties
                Text(
                    "Security Properties:",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp
                )
                Spacer(modifier = Modifier.height(8.dp))
                SecurityProperty("Forward Secrecy", true)
                SecurityProperty("Post-Compromise Security", true)
                SecurityProperty("Deniability", true)
                SecurityProperty("Geographic Routing", true)
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Close", color = primaryGold)
            }
        }
    )
}

@Composable
fun EncryptionInfoRow(label: String, value: String) {
    val primaryGold = Color(0xFFFFD700)

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            color = Color.White.copy(alpha = 0.7f),
            fontSize = 14.sp
        )
        Text(
            text = value,
            color = primaryGold,
            fontSize = 14.sp,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun SecurityProperty(name: String, enabled: Boolean) {
    val primaryGold = Color(0xFFFFD700)

    Row(
        modifier = Modifier.padding(vertical = 2.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            if (enabled) Icons.Default.CheckCircle else Icons.Default.Cancel,
            contentDescription = null,
            tint = if (enabled) primaryGold else Color.Red,
            modifier = Modifier.size(16.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = name,
            color = Color.White.copy(alpha = 0.8f),
            fontSize = 13.sp
        )
    }
}

// Helper function
private fun formatTime(timestamp: Long): String {
    val sdf = SimpleDateFormat("HH:mm", Locale.getDefault())
    return sdf.format(Date(timestamp))
}

// Data class for UI
data class ChatMessage(
    val id: String,
    val text: String,
    val timestamp: Long,
    val isFromMe: Boolean,
    val isEncrypted: Boolean = true,
    val messageType: MessageType = MessageType.TEXT
)
