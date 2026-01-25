/**
 * Message Bubble Component
 * ========================
 *
 * Chat message bubble with Brahim aesthetics.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.brahim.buim.ui.theme.*

/**
 * Message sender type.
 */
enum class MessageSender {
    USER, ASSISTANT, SYSTEM
}

/**
 * Chat message data class.
 */
data class ChatMessage(
    val id: String,
    val content: String,
    val sender: MessageSender,
    val timestamp: Long = System.currentTimeMillis(),
    val metadata: Map<String, Any> = emptyMap()
)

/**
 * Message bubble composable.
 */
@Composable
fun MessageBubble(
    message: ChatMessage,
    modifier: Modifier = Modifier
) {
    val isUser = message.sender == MessageSender.USER
    val isSystem = message.sender == MessageSender.SYSTEM

    val alignment = when (message.sender) {
        MessageSender.USER -> Alignment.CenterEnd
        MessageSender.ASSISTANT -> Alignment.CenterStart
        MessageSender.SYSTEM -> Alignment.Center
    }

    val backgroundColor = when (message.sender) {
        MessageSender.USER -> GoldenPrimary
        MessageSender.ASSISTANT -> MaterialTheme.colorScheme.surfaceVariant
        MessageSender.SYSTEM -> MaterialTheme.colorScheme.tertiaryContainer
    }

    val textColor = when (message.sender) {
        MessageSender.USER -> Color.Black
        MessageSender.ASSISTANT -> MaterialTheme.colorScheme.onSurfaceVariant
        MessageSender.SYSTEM -> MaterialTheme.colorScheme.onTertiaryContainer
    }

    val shape = when (message.sender) {
        MessageSender.USER -> RoundedCornerShape(16.dp, 16.dp, 4.dp, 16.dp)
        MessageSender.ASSISTANT -> RoundedCornerShape(16.dp, 16.dp, 16.dp, 4.dp)
        MessageSender.SYSTEM -> RoundedCornerShape(8.dp)
    }

    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp),
        contentAlignment = alignment
    ) {
        Surface(
            modifier = Modifier
                .widthIn(max = 300.dp)
                .clip(shape),
            color = backgroundColor,
            shape = shape,
            tonalElevation = if (isUser) 0.dp else 2.dp
        ) {
            Column(
                modifier = Modifier.padding(12.dp)
            ) {
                Text(
                    text = message.content,
                    style = MaterialTheme.typography.bodyMedium,
                    color = textColor,
                    textAlign = if (isSystem) TextAlign.Center else TextAlign.Start
                )

                // Show metadata if present (skill used, safety verdict, etc.)
                if (message.metadata.isNotEmpty() && !isUser) {
                    Spacer(modifier = Modifier.height(4.dp))

                    message.metadata["skill"]?.let { skill ->
                        Text(
                            text = "Skill: $skill",
                            style = MaterialTheme.typography.labelSmall,
                            color = textColor.copy(alpha = 0.7f)
                        )
                    }

                    message.metadata["safety"]?.let { safety ->
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            val safetyColor = when (safety.toString()) {
                                "SAFE" -> SafeColor
                                "NOMINAL" -> NominalColor
                                "CAUTION" -> CautionColor
                                "UNSAFE" -> UnsafeColor
                                "BLOCKED" -> BlockedColor
                                else -> Color.Gray
                            }
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .background(safetyColor, RoundedCornerShape(4.dp))
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = safety.toString(),
                                style = MaterialTheme.typography.labelSmall,
                                color = textColor.copy(alpha = 0.7f)
                            )
                        }
                    }
                }
            }
        }
    }
}

/**
 * Typing indicator for assistant.
 */
@Composable
fun TypingIndicator(
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp),
        contentAlignment = Alignment.CenterStart
    ) {
        Surface(
            modifier = Modifier.clip(RoundedCornerShape(16.dp)),
            color = MaterialTheme.colorScheme.surfaceVariant,
            tonalElevation = 2.dp
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                repeat(3) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .background(
                                GoldenPrimary.copy(alpha = 0.6f),
                                RoundedCornerShape(4.dp)
                            )
                    )
                }
            }
        }
    }
}
