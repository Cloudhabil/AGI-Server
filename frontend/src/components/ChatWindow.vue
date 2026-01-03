<script setup lang="ts">
import { ref, nextTick, onMounted, watch, computed } from 'vue'
import { API_BASE } from '../config'

type MessageRole = 'user' | 'assistant' | 'system'

interface FileLink {
  path: string
  name: string
  line?: number
}

interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
  files?: FileLink[]
  status?: 'sending' | 'streaming' | 'complete' | 'error'
  model?: string
  duration?: number
  phase?: 'init' | 'understand' | 'execute' | 'result'
  success?: boolean
}

const messages = ref<Message[]>([])
const inputText = ref('')
const isStreaming = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

const generateId = () => `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

// Extract file paths from text and convert to hyperlinks
const extractFileLinks = (text: string): FileLink[] => {
  const links: FileLink[] = []

  // Match patterns like: path/to/file.ext:123 or C:\path\file.ext
  const patterns = [
    /([A-Za-z]:\\[^\s:]+\.[a-z]+)(?::(\d+))?/g,  // Windows paths
    /(?:^|\s)((?:\.\/|\.\.\/|\/)?[\w\-./]+\.[a-z]+)(?::(\d+))?/g,  // Unix paths
    /`([^`]+\.[a-z]+)`/g,  // Backtick wrapped
  ]

  for (const pattern of patterns) {
    let match
    while ((match = pattern.exec(text)) !== null) {
      const path = match[1]
      const line = match[2] ? parseInt(match[2]) : undefined
      const name = path.split(/[/\\]/).pop() || path

      if (!links.find(l => l.path === path)) {
        links.push({ path, name, line })
      }
    }
  }

  return links
}

// Format message content with clickable file links
const formatContent = (content: string): string => {
  // Convert file paths to clickable spans (handled in template)
  // Convert markdown-style code blocks
  let formatted = content
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')

  return formatted
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const openFile = async (file: FileLink) => {
  try {
    // Try to open in VS Code or default editor
    const url = `vscode://file/${encodeURIComponent(file.path)}${file.line ? `:${file.line}` : ''}`
    window.open(url, '_blank')
  } catch (e) {
    console.error('Failed to open file:', e)
  }
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || isStreaming.value) return

  // Add user message
  const userMsg: Message = {
    id: generateId(),
    role: 'user',
    content: text,
    timestamp: new Date(),
    status: 'complete'
  }
  messages.value.push(userMsg)
  inputText.value = ''

  // Create assistant message placeholder
  const assistantMsg: Message = {
    id: generateId(),
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    status: 'streaming',
    files: []
  }
  messages.value.push(assistantMsg)

  await scrollToBottom()
  isStreaming.value = true

  const startTime = Date.now()

  try {
    const res = await fetch(`${API_BASE}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })

    if (!res.body) throw new Error('No response body')

    const reader = res.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data:')) continue
        try {
          const payload = JSON.parse(line.replace('data:', '').trim())

          if (payload.phase) {
            assistantMsg.phase = payload.phase
          }

          if (payload.text) {
            assistantMsg.content += payload.text
            assistantMsg.files = extractFileLinks(assistantMsg.content)
            await scrollToBottom()
          }

          if (payload.model) {
            assistantMsg.model = payload.model
          }

          if (payload.done) {
            assistantMsg.status = 'complete'
            assistantMsg.duration = (Date.now() - startTime) / 1000
            if (payload.success !== undefined) {
              assistantMsg.success = payload.success
            }
          }
        } catch (e) {
          // Skip malformed JSON
        }
      }
    }

    assistantMsg.status = 'complete'
    assistantMsg.duration = (Date.now() - startTime) / 1000

  } catch (error) {
    assistantMsg.content = `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`
    assistantMsg.status = 'error'
  } finally {
    isStreaming.value = false
    await scrollToBottom()
  }
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const clearChat = () => {
  messages.value = []
}

// Add welcome message on mount
onMounted(() => {
  messages.value.push({
    id: generateId(),
    role: 'system',
    content: 'GPIA Orchestrator Online. Multi-model routing active (DeepSeek-R1 | Qwen3 | CodeGemma). PASS Protocol enabled. Ready for tasks.',
    timestamp: new Date(),
    status: 'complete'
  })
  inputRef.value?.focus()
})
</script>

<template>
  <div class="chat-window">
    <div class="chat-header">
      <div class="chat-title">
        <span class="chat-icon">●</span>
        GPIA INTERFACE
      </div>
      <div class="chat-actions">
        <button class="action-btn" @click="clearChat" title="Clear chat">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z"/>
          </svg>
        </button>
      </div>
    </div>

    <div ref="messagesContainer" class="messages-container">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message"
        :class="[msg.role, msg.status]"
      >
        <div class="message-header">
          <span class="message-role">{{ msg.role === 'user' ? 'You' : msg.role === 'assistant' ? 'GPIA' : 'System' }}</span>
          <span v-if="msg.model" class="message-model">{{ msg.model }}</span>
          <span v-if="msg.success !== undefined" class="message-success" :class="{ success: msg.success, failure: !msg.success }">
            {{ msg.success ? '✓' : '✗' }}
          </span>
          <span v-if="msg.duration" class="message-duration">{{ msg.duration.toFixed(1) }}s</span>
        </div>

        <div class="message-content" v-html="formatContent(msg.content)"></div>

        <div v-if="msg.files && msg.files.length > 0" class="message-files">
          <div class="files-label">Referenced Files:</div>
          <div class="files-list">
            <button
              v-for="file in msg.files"
              :key="file.path"
              class="file-link"
              @click="openFile(file)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
              </svg>
              <span class="file-name">{{ file.name }}</span>
              <span v-if="file.line" class="file-line">:{{ file.line }}</span>
            </button>
          </div>
        </div>

        <div v-if="msg.status === 'streaming'" class="streaming-indicator">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>

    <div class="input-container">
      <input
        ref="inputRef"
        v-model="inputText"
        type="text"
        placeholder="Ask GPIA anything... (Enter to send)"
        class="chat-input"
        :disabled="isStreaming"
        @keydown="handleKeydown"
      />
      <button
        class="send-btn"
        :disabled="!inputText.trim() || isStreaming"
        @click="sendMessage"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  background: var(--surface-card);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--surface-panel);
  border-bottom: 1px solid rgba(248, 246, 242, 0.1);
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--text-inverse);
}

.chat-icon {
  color: #4dd4a5;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: rgba(248, 246, 242, 0.1);
  border: none;
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  color: var(--text-inverse);
  transition: background 0.2s;
}

.action-btn:hover {
  background: rgba(248, 246, 242, 0.2);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 90%;
}

.message.user {
  background: var(--c-ember);
  color: #1b2027;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

.message.assistant {
  background: rgba(16, 21, 28, 0.6);
  color: var(--text-primary);
  align-self: flex-start;
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(16, 21, 28, 0.2);
}

.message.system {
  background: rgba(77, 212, 165, 0.1);
  color: #4dd4a5;
  align-self: center;
  font-size: 12px;
  border: 1px solid rgba(77, 212, 165, 0.2);
}

.message.error {
  border-color: #f87171;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 11px;
  opacity: 0.7;
}

.message-role {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.message-model {
  padding: 2px 6px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  font-family: var(--font-mono);
}

.message-duration {
  margin-left: auto;
}

.message-success {
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.message-success.success {
  color: #4dd4a5;
  background: rgba(77, 212, 165, 0.2);
}

.message-success.failure {
  color: #f87171;
  background: rgba(248, 113, 113, 0.2);
}

.message-content {
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message-content :deep(.code-block) {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 12px;
  margin: 8px 0;
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 12px;
}

.message-content :deep(.inline-code) {
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 13px;
}

.message-files {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.files-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.6;
  margin-bottom: 8px;
}

.files-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.file-link {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(218, 108, 60, 0.2);
  border: 1px solid rgba(218, 108, 60, 0.3);
  border-radius: 6px;
  color: var(--c-ember);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.file-link:hover {
  background: rgba(218, 108, 60, 0.3);
  border-color: var(--c-ember);
}

.file-link svg {
  width: 14px;
  height: 14px;
}

.file-name {
  font-family: var(--font-mono);
}

.file-line {
  opacity: 0.7;
}

.streaming-indicator {
  display: flex;
  gap: 4px;
  margin-top: 8px;
}

.streaming-indicator .dot {
  width: 6px;
  height: 6px;
  background: var(--c-ember);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.streaming-indicator .dot:nth-child(1) { animation-delay: -0.32s; }
.streaming-indicator .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-container {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: var(--surface-panel);
  border-top: 1px solid rgba(248, 246, 242, 0.1);
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  background: rgba(15, 20, 27, 0.6);
  border: 1px solid rgba(248, 246, 242, 0.2);
  border-radius: 8px;
  color: var(--text-inverse);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: var(--c-ember);
}

.chat-input::placeholder {
  color: rgba(248, 246, 242, 0.4);
}

.chat-input:disabled {
  opacity: 0.6;
}

.send-btn {
  padding: 12px 16px;
  background: var(--c-ember);
  border: none;
  border-radius: 8px;
  color: #1b2027;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 18px;
  height: 18px;
}
</style>
