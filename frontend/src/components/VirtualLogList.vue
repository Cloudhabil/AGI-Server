<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { API_BASE } from '../config'

type LogEntry = {
  id: string
  content: string
  memory_type: string
  timestamp: string
  importance?: number
  context?: Record<string, unknown>
  kind?: string
  stage?: string
  duration_s?: number
  action?: string
  status?: 'ok' | 'error'
  thoughts?: string[]
}

const props = defineProps<{
  items: LogEntry[]
  itemHeight?: number
  height?: number
  autoScroll?: boolean
}>()

const emit = defineEmits<{
  (e: 'action', payload: { type: string; memory: LogEntry; result?: any }): void
}>()

const itemHeight = computed(() => props.itemHeight ?? 132) // Increased for action buttons
const containerHeight = computed(() => props.height)
const scrollTop = ref(0)
const scrollerRef = ref<HTMLDivElement | null>(null)
const expandedId = ref<string | null>(null)
const actionLoading = ref<string | null>(null)
const actionResult = ref<Record<string, any>>({})
const skillModalOpen = ref(false)
const skillModalMemory = ref<LogEntry | null>(null)
const skillDraft = ref({
  name: '',
  filePath: 'skills/new_capability.py',
  description: '',
})
let autoTimer: number | undefined

const totalHeight = computed(() => props.items.length * itemHeight.value + 24)

const startIndex = computed(() => Math.max(0, Math.floor(scrollTop.value / itemHeight.value) - 4))
const visibleCount = computed(() => Math.ceil((containerHeight.value || 600) / itemHeight.value) + 10)
const endIndex = computed(() => Math.min(props.items.length, startIndex.value + visibleCount.value))

const visibleItems = computed(() => props.items.slice(startIndex.value, endIndex.value))

const onScroll = (event: Event) => {
  const target = event.target as HTMLElement
  scrollTop.value = target.scrollTop
}

const scrollToBottom = () => {
  const el = scrollerRef.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

const toggleExpand = (id: string) => {
  expandedId.value = expandedId.value === id ? null : id
}

const readChatStream = async (res: Response) => {
  const reader = res.body?.getReader()
  const decoder = new TextDecoder('utf-8')
  if (!reader) return ''
  let buffer = ''
  let combined = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop() || ''
    lines.forEach((line) => {
      if (!line.startsWith('data:')) return
      try {
        const payload = JSON.parse(line.replace('data:', '').trim())
        if (payload.text) combined += payload.text
      } catch {
        // Ignore malformed lines
      }
    })
  }
  return combined.trim()
}

const proposeAction = async (memory: LogEntry) => {
  actionLoading.value = `propose-${memory.id}`
  const prompt = `Generate a task to resolve this issue.\n\nMemory:\n${memory.content}`
  try {
    let res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: prompt }),
    })
    let responseText = ''
    if (res.ok) {
      const contentType = res.headers.get('content-type') || ''
      if (contentType.includes('application/json')) {
        const data = await res.json()
        responseText = data.reply || data.response || data.message || formatResultMessage(data)
        actionResult.value[memory.id] = { type: 'propose', message: responseText }
        emit('action', { type: 'propose', memory, result: data })
        return
      }
      responseText = formatResultMessage(await res.text())
      actionResult.value[memory.id] = { type: 'propose', message: responseText }
      emit('action', { type: 'propose', memory, result: responseText })
      return
    }
    res = await fetch(`${API_BASE}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: prompt }),
    })
    responseText = await readChatStream(res)
    actionResult.value[memory.id] = { type: 'propose', message: responseText || 'No response.' }
    emit('action', { type: 'propose', memory, result: responseText })
  } catch (e) {
    actionResult.value[memory.id] = { type: 'propose', error: String(e) }
  } finally {
    actionLoading.value = null
  }
}

const forceFix = async (memory: LogEntry) => {
  actionLoading.value = `fix-${memory.id}`
  try {
    const res = await fetch(`${API_BASE}/api/fix/embedding_model`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        memory_id: memory.id,
        content: memory.content,
        context: memory.context,
      }),
    })
    const contentType = res.headers.get('content-type') || ''
    const data = contentType.includes('application/json') ? await res.json() : await res.text()
    actionResult.value[memory.id] = { type: 'fix', message: formatResultMessage(data) }
    emit('action', { type: 'fix', memory, result: data })
  } catch (e) {
    actionResult.value[memory.id] = { type: 'fix', error: String(e) }
  } finally {
    actionLoading.value = null
  }
}

const openLearnSkill = (memory: LogEntry) => {
  skillModalMemory.value = memory
  skillDraft.value = {
    name: `Skill from ${memory.memory_type}`,
    filePath: 'skills/new_capability.py',
    description: memory.content.slice(0, 160),
  }
  skillModalOpen.value = true
}

const closeSkillModal = () => {
  skillModalOpen.value = false
  skillModalMemory.value = null
}

const submitLearnSkill = async () => {
  if (!skillModalMemory.value) return
  const memory = skillModalMemory.value
  actionLoading.value = `skill-${memory.id}`
  try {
    const res = await fetch(`${API_BASE}/api/skills/create-from-memory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        memory_id: memory.id,
        content: memory.content,
        context: memory.context,
        name: skillDraft.value.name,
        description: skillDraft.value.description,
        file_path: skillDraft.value.filePath,
      }),
    })
    const contentType = res.headers.get('content-type') || ''
    const data = contentType.includes('application/json') ? await res.json() : await res.text()
    actionResult.value[memory.id] = { type: 'skill', message: formatResultMessage(data) }
    emit('action', { type: 'skill', memory, result: data })
    closeSkillModal()
  } catch (e) {
    actionResult.value[memory.id] = { type: 'skill', error: String(e) }
  } finally {
    actionLoading.value = null
  }
}

const dismissResult = (id: string) => {
  delete actionResult.value[id]
}

const formatResultMessage = (data: unknown) => {
  if (typeof data === 'string') return data
  if (data && typeof data === 'object') return JSON.stringify(data, null, 2)
  return String(data ?? '')
}

const isError = (memory: LogEntry) => {
  return memory.content.toLowerCase().includes('error') ||
         memory.content.toLowerCase().includes('failed') ||
         memory.status === 'error'
}

const isActionable = (memory: LogEntry) => {
  // Memories that can have actions taken on them
  return memory.content.length > 20 && !memory.content.startsWith('Heartbeat #')
}

const getActionSuggestion = (memory: LogEntry): string => {
  if (memory.content.toLowerCase().includes('no action taken')) return 'Propose a task to resolve'
  if (isError(memory)) return 'Force a fix immediately'
  return 'Save as a reusable skill'
}

onMounted(() => {
  if (props.autoScroll) {
    autoTimer = window.setInterval(scrollToBottom, 3000)
  }
})

onBeforeUnmount(() => {
  if (autoTimer) window.clearInterval(autoTimer)
})

watch(
  () => props.items.length,
  () => {
    if (props.autoScroll) {
      scrollToBottom()
    }
  },
)
</script>

<template>
  <div
    ref="scrollerRef"
    class="virtual-log"
    :style="containerHeight ? { height: `${containerHeight}px` } : { height: '100%' }"
    @scroll="onScroll"
  >
    <div class="spacer" :style="{ height: `${totalHeight}px` }">
      <div
        v-for="(item, idx) in visibleItems"
        :key="item.id + idx"
        class="log-row"
        :class="{ expanded: expandedId === item.id, error: isError(item) }"
        :style="{ transform: `translateY(${(startIndex + idx) * itemHeight}px)` }"
      >
        <!-- Header Row -->
        <div class="log-header" @click="toggleExpand(item.id)">
          <div class="log-meta">
            <div class="log-tags">
              <span class="log-tag" :class="item.memory_type">{{ item.memory_type }}</span>
              <span v-if="item.stage" class="log-tag stage">{{ item.stage }}</span>
              <span v-if="isError(item)" class="log-tag error-tag">ERROR</span>
            </div>
            <span class="log-time">{{ item.timestamp }}</span>
          </div>
          <div class="expand-arrow">{{ expandedId === item.id ? '▼' : '▶' }}</div>
        </div>

        <!-- Content -->
        <div class="log-content">{{ item.content }}</div>

        <!-- Thoughts (if any) -->
        <div v-if="item.thoughts && item.thoughts.length && expandedId === item.id" class="log-thoughts">
          <div v-for="line in item.thoughts" :key="line" class="log-thought">
            {{ line }}
          </div>
        </div>

        <!-- Sub info -->
        <div v-if="item.action || item.duration_s" class="log-sub">
          <span v-if="item.action">{{ item.action }}</span>
          <span v-if="item.duration_s">{{ item.duration_s.toFixed(2) }}s</span>
        </div>

        <!-- Action Buttons -->
        <div v-if="isActionable(item)" class="log-actions">
          <div class="action-hint">{{ getActionSuggestion(item) }}</div>
          <div class="action-buttons">
            <button
              class="action-btn propose"
              :disabled="actionLoading !== null"
              @click.stop="proposeAction(item)"
            >
              <span v-if="actionLoading === `propose-${item.id}`" class="loading-dot"></span>
              <span v-else>Propose Action</span>
            </button>
            <button
              class="action-btn fix"
              :disabled="actionLoading !== null"
              @click.stop="forceFix(item)"
            >
              <span v-if="actionLoading === `fix-${item.id}`" class="loading-dot"></span>
              <span v-else>Force Fix</span>
            </button>
            <button
              class="action-btn learn"
              :disabled="actionLoading !== null"
              @click.stop="openLearnSkill(item)"
            >
              <span v-if="actionLoading === `skill-${item.id}`" class="loading-dot"></span>
              <span v-else>Learn Skill</span>
            </button>
          </div>
        </div>

        <!-- Action Result -->
        <div v-if="actionResult[item.id]" class="action-result" :class="actionResult[item.id].error ? 'error' : 'success'">
          <div class="result-header">
            <span class="result-type">{{ actionResult[item.id].type }}</span>
            <button class="result-dismiss" @click.stop="dismissResult(item.id)">x</button>
          </div>
          <div v-if="actionResult[item.id].error" class="result-error">
            {{ actionResult[item.id].error }}
          </div>
          <div v-else class="result-content">
            <div v-if="actionResult[item.id].message" class="result-item">
              {{ actionResult[item.id].message }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="skillModalOpen" class="skill-modal-overlay" @click.self="closeSkillModal">
    <div class="skill-modal">
      <div class="modal-header">
        <div class="modal-title">Save Memory as Skill</div>
        <button class="modal-close" @click="closeSkillModal">x</button>
      </div>
      <div class="modal-body">
        <label>
          <span>Name</span>
          <input v-model="skillDraft.name" placeholder="Skill name" />
        </label>
        <label>
          <span>File path</span>
          <input v-model="skillDraft.filePath" placeholder="skills/new_capability.py" />
        </label>
        <label>
          <span>Description</span>
          <textarea v-model="skillDraft.description" rows="3" placeholder="Short description"></textarea>
        </label>
        <label>
          <span>Memory preview</span>
          <textarea :value="skillModalMemory?.content || ''" rows="6" readonly></textarea>
        </label>
      </div>
      <div class="modal-actions">
        <button class="modal-secondary" @click="closeSkillModal">Cancel</button>
        <button class="modal-primary" :disabled="actionLoading !== null" @click="submitLearnSkill">
          <span v-if="actionLoading === `skill-${skillModalMemory?.id}`" class="loading-dot"></span>
          <span v-else>Save Skill</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.virtual-log {
  position: relative;
  overflow: auto;
  background: linear-gradient(180deg, rgba(15, 20, 27, 0.04), rgba(15, 20, 27, 0.01));
  border-radius: var(--radius-md, 8px);
  padding: 12px;
}

.spacer {
  position: relative;
  width: 100%;
}

.log-row {
  position: absolute;
  left: 0;
  right: 0;
  padding: 12px;
  background: #fbfaf7;
  border-radius: var(--radius-sm, 6px);
  box-shadow: 0 4px 12px rgba(15, 20, 27, 0.06);
  border-left: 3px solid transparent;
  transition: all 0.2s ease;
}

.log-row:hover {
  box-shadow: 0 6px 16px rgba(15, 20, 27, 0.1);
}

.log-row.error {
  border-left-color: #ef4444;
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.05), transparent);
}

.log-row.expanded {
  border-left-color: #da6c3c;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  margin-bottom: 6px;
}

.log-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1;
  font-size: 11px;
  color: var(--text-muted, #666);
}

.expand-arrow {
  font-size: 10px;
  color: rgba(24, 32, 40, 0.4);
  margin-left: 8px;
}

.log-tag {
  font-family: var(--font-mono, monospace);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(24, 32, 40, 0.08);
}

.log-tag.episodic { background: rgba(96, 165, 250, 0.15); color: #3b82f6; }
.log-tag.semantic { background: rgba(168, 85, 247, 0.15); color: #a855f7; }
.log-tag.procedural { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.log-tag.identity { background: rgba(251, 191, 36, 0.15); color: #f59e0b; }
.log-tag.stage { background: rgba(24, 32, 40, 0.05); color: rgba(24, 32, 40, 0.5); }
.log-tag.error-tag { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.log-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.log-time {
  font-size: 10px;
  color: rgba(24, 32, 40, 0.4);
}

.log-content {
  font-size: 13px;
  color: var(--text-primary, #1a1a1a);
  line-height: 1.5;
  margin-bottom: 8px;
}

.log-sub {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--text-muted, #666);
  margin-bottom: 8px;
}

.log-thoughts {
  margin: 8px 0;
  display: grid;
  gap: 6px;
  font-size: 12px;
}

.log-thought {
  padding: 8px 10px;
  background: rgba(218, 108, 60, 0.08);
  border-radius: 6px;
  border-left: 2px solid #da6c3c;
}

/* Action Buttons */
.log-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid rgba(24, 32, 40, 0.08);
  flex-wrap: wrap;
}

.action-hint {
  font-size: 10px;
  color: rgba(24, 32, 40, 0.4);
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-left: auto;
}

.action-btn {
  padding: 4px 10px;
  border: none;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.propose {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}
.action-btn.propose:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.25);
}

.action-btn.fix {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}
.action-btn.fix:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.25);
}

.action-btn.learn {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}
.action-btn.learn:hover:not(:disabled) {
  background: rgba(34, 197, 94, 0.25);
}

.loading-dot {
  width: 12px;
  height: 12px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Action Results */
.action-result {
  margin-top: 10px;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 12px;
}

.action-result.success {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.action-result.error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.result-type {
  font-weight: 700;
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.05em;
}

.result-dismiss {
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  color: rgba(24, 32, 40, 0.4);
  padding: 0 4px;
}

.result-error {
  color: #ef4444;
}

.result-content {
  color: var(--text-primary, #1a1a1a);
}

.result-item {
  padding: 4px 0;
}

.skill-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 20, 27, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.skill-modal {
  width: min(520px, 92vw);
  background: #fbfaf7;
  border-radius: var(--radius-md, 8px);
  box-shadow: 0 20px 40px rgba(15, 20, 27, 0.2);
  padding: 16px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.modal-title {
  font-weight: 700;
  font-size: 14px;
}

.modal-close {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: rgba(24, 32, 40, 0.5);
}

.modal-body {
  display: grid;
  gap: 10px;
}

.modal-body label {
  display: grid;
  gap: 6px;
  font-size: 11px;
  color: rgba(24, 32, 40, 0.6);
}

.modal-body input,
.modal-body textarea {
  width: 100%;
  border: 1px solid rgba(16, 21, 28, 0.15);
  border-radius: 6px;
  padding: 8px;
  font-size: 12px;
  background: #fffdf7;
  font-family: var(--font-mono, monospace);
}

.modal-body textarea[readonly] {
  background: rgba(24, 32, 40, 0.03);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.modal-primary,
.modal-secondary {
  padding: 8px 12px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
}

.modal-primary {
  background: #22c55e;
  color: #0f1a12;
}

.modal-secondary {
  background: rgba(24, 32, 40, 0.08);
  color: rgba(24, 32, 40, 0.7);
}
</style>
