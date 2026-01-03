<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useDragAndDrop } from '@formkit/drag-and-drop/vue'
import { API_BASE } from '../config'
import ChatWindow from '../components/ChatWindow.vue'
import VirtualLogList from '../components/VirtualLogList.vue'
import SkillTimeline from '../components/SkillTimeline.vue'
import ResourceMonitor from '../components/ResourceMonitor.vue'
import LiveThoughts from '../components/LiveThoughts.vue'
import LogCarousel from '../components/LogCarousel.vue'
import WorkflowPanel from '../components/WorkflowPanel.vue'
import AlphaPanel from '../components/AlphaPanel.vue'

type LogEntry = {
  id: string
  content: string
  memory_type: string
  timestamp: string
  importance?: number
  context?: Record<string, unknown>
}

type HeartbeatSample = {
  timestamp: string
  ok: boolean
  duration_s?: number
  stage?: string
}

type SkillMeta = {
  id: string
  name: string
  description: string
  category: string
  level: string
}

type Goal = {
  id: string
  objective: string
  status: string
  priority: number
}

const status = ref({ stage: 'UNKNOWN', paused: false, action: 'idle' })
const logs = ref<LogEntry[]>([])
const heartbeats = ref<HeartbeatSample[]>([])
const skills = ref<SkillMeta[]>([])
const goals = ref<Goal[]>([])
const learnedSkills = ref<{ content: string; timestamp: string }[]>([])
const memoryStats = ref<{ total: number; by_type: Record<string, number>; last_consolidated?: string }>({
  total: 0,
  by_type: {},
})
const commandInput = ref('')
const commandOutput = ref<string[]>([])
const directiveInput = ref('')
const cognitiveOpen = ref(false)
const cognitiveInput = ref('')
const cognitiveStream = ref<string[]>([])

const [agencyParent, agencyGoals, updateAgencyConfig] = useDragAndDrop<Goal>([], {
  dragHandle: '.goal-handle',
})

let statusTimer: number | undefined
let heartbeatTimer: number | undefined
let eventSource: EventSource | null = null

const skillGroups = computed(() => {
  const groups: Record<string, SkillMeta[]> = {}
  skills.value.forEach((skill) => {
    const key = skill.category || 'misc'
    if (!groups[key]) groups[key] = []
    groups[key].push(skill)
  })
  return groups
})

const latestHeartbeat = computed(() => heartbeats.value[0])

const logFilter = ref<'all' | 'heartbeat' | 'errors' | 'semantic' | 'procedural' | 'identity'>('all')

const summarizeText = (text: string, limit: number) => {
  const plain = text.replace(/\s+/g, ' ').trim()
  if (plain.length <= limit) return plain
  return `${plain.slice(0, limit)}…`
}

const formatLogContent = (item: LogEntry) => {
  if (item.content.startsWith('Heartbeat')) {
    const stage = (item.context as any)?.observations_summary?.stage || 'MONITOR'
    const action = (item.context as any)?.action?.details || 'no action'
    return `Cycle complete. Stage ${stage}. Action: ${action}.`
  }
  if (item.content.startsWith('Learned skill created:')) {
    return item.content.replace('Learned skill created:', 'Learned new skill:')
  }
  if (item.content.startsWith('Extracted skill requirement from task:')) {
    return item.content.replace('Extracted skill requirement from task:', 'Skill requested from task:')
  }
  return summarizeText(item.content, 200)
}

const displayLogs = computed(() => {
  let heartbeatCount = 0
  return logs.value
    .filter((item) => {
      if (item.content.startsWith('Heartbeat')) {
        heartbeatCount += 1
        return heartbeatCount <= 12
      }
      return true
    })
    .filter((item) => {
      if (logFilter.value === 'all') return true
      if (logFilter.value === 'heartbeat') return item.content.startsWith('Heartbeat')
      if (logFilter.value === 'errors') return item.content.toLowerCase().includes('error')
      if (logFilter.value === 'semantic') return item.memory_type === 'semantic'
      if (logFilter.value === 'procedural') return item.memory_type === 'procedural'
      if (logFilter.value === 'identity') return item.memory_type === 'identity'
      return true
    })
    .map((item) => {
      const stage = (item.context as any)?.observations_summary?.stage
      const duration = (item.context as any)?.duration_s
      const action = (item.context as any)?.action?.details
      const trace = (item.context as any)?.model_trace
      const thoughts: string[] = []
      const appendTrace = (steps: any[], prefix: string) => {
        steps.forEach((step, index) => {
          if (!step?.thought) return
          const model = step.model || 'Model'
          const text = summarizeText(step.thought, 140)
          thoughts.push(`${prefix}${String(index + 1).padStart(2, '0')} ${model}: ${text}`)
        })
      }
      if (trace?.analysis) appendTrace(trace.analysis, 'A')
      if (trace?.decision) appendTrace(trace.decision, 'D')
      const status = item.content.toLowerCase().includes('error') ? 'error' : 'ok'
      const kind = item.content.startsWith('Heartbeat') ? 'heartbeat' : 'log'
      return {
        ...item,
        content: formatLogContent(item),
        thoughts,
        stage,
        duration_s: duration,
        action,
        status,
        kind,
      }
    })
})

const loadStatus = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/status`)
    const data = await res.json()
    const stage = data.control_plane?.stage || 'UNKNOWN'
    const paused = Boolean(data.heartbeat?.paused)
    status.value = {
      stage,
      paused,
      action: latestHeartbeat.value?.ok ? 'stable' : 'error',
    }
  } catch {
    status.value = { stage: 'OFFLINE', paused: false, action: 'offline' }
  }
}

const loadLogs = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/memories?limit=200`)
    const data = await res.json()
    logs.value = data.memories || []
    learnedSkills.value = (data.memories || [])
      .filter((mem: LogEntry) =>
        mem.content.includes('Learned skill created:') ||
        mem.content.includes('Extracted skill requirement from task:')
      )
      .map((mem: LogEntry) => ({
        content: mem.content,
        timestamp: mem.timestamp,
      }))
  } catch {
    logs.value = []
  }
}

const loadMemoryStats = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/memories/stats`)
    const data = await res.json()
    memoryStats.value = {
      total: data.stats?.total_memories || 0,
      by_type: data.stats?.by_type || {},
      last_consolidated: data.stats?.last_consolidated,
    }
  } catch {
    memoryStats.value = { total: 0, by_type: {} }
  }
}

const loadHeartbeats = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/heartbeat`)
    const data = await res.json()
    heartbeats.value = (data.heartbeats || []).map((hb: any) => ({
      timestamp: hb.timestamp,
      ok: !String(hb.content).toLowerCase().includes('error'),
      duration_s: hb.context?.duration_s,
      stage: hb.context?.observations_summary?.stage,
    }))
  } catch {
    heartbeats.value = []
  }
}

const loadSkills = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/skills`)
    const data = await res.json()
    skills.value = data.skills || []
  } catch {
    skills.value = []
  }
}

const loadGoals = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/goals`)
    const data = await res.json()
    goals.value = data.goals || []
    agencyGoals.value = [...goals.value]
  } catch {
    goals.value = []
    agencyGoals.value = []
  }
}

const syncGoalOrder = async (ordered: Goal[]) => {
  if (!ordered.length) return
  const total = ordered.length
  const reordered = ordered.map((goal, index) => {
    const priority = Number(((total - index) / total).toFixed(2))
    return { ...goal, priority }
  })
  agencyGoals.value = reordered

  await fetch(`${API_BASE}/api/goals/reorder`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      goals: reordered.map((goal) => ({ id: goal.id, priority: goal.priority })),
    }),
  })
}

const attachStream = () => {
  if (eventSource) eventSource.close()
  eventSource = new EventSource(`${API_BASE}/stream`)
  eventSource.onmessage = (event) => {
    const batch = JSON.parse(event.data || '[]') as LogEntry[]
    if (batch.length) {
      const merged = [...batch, ...logs.value]
      const unique = new Map<string, LogEntry>()
      merged.forEach((item) => unique.set(item.id, item))
      logs.value = Array.from(unique.values()).slice(0, 400)
    }
  }
}

const runCommand = async () => {
  const command = commandInput.value.trim()
  if (!command) return

  const output: string[] = []
  if (command.startsWith('/pause')) {
    await fetch(`${API_BASE}/api/control/pause`, { method: 'POST' })
    output.push('Heartbeat paused.')
  } else if (command.startsWith('/resume')) {
    await fetch(`${API_BASE}/api/control/resume`, { method: 'POST' })
    output.push('Heartbeat resumed.')
  } else if (command.startsWith('/inject ')) {
    const goal = command.replace('/inject ', '').trim()
    const form = new FormData()
    form.append('objective', goal)
    await fetch(`${API_BASE}/goal`, { method: 'POST', body: form })
    output.push(`Injected goal: ${goal}`)
  } else if (command.startsWith('/memory ')) {
    const note = command.replace('/memory ', '').trim()
    await fetch(`${API_BASE}/api/memories/store`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: note, memory_type: 'semantic', importance: 0.6 }),
    })
    output.push('Stored memory note.')
  } else {
    output.push(`Unknown command: ${command}`)
  }

  commandOutput.value = [...output, ...commandOutput.value].slice(0, 6)
  commandInput.value = ''
  await loadStatus()
  await loadGoals()
}

const togglePause = async () => {
  if (status.value.paused) {
    await fetch(`${API_BASE}/api/control/resume`, { method: 'POST' })
  } else {
    await fetch(`${API_BASE}/api/control/pause`, { method: 'POST' })
  }
  await loadStatus()
}

const sendCognitivePing = async () => {
  const message = cognitiveInput.value.trim()
  if (!message) return
  cognitiveStream.value = ['Thinking...']
  try {
    const res = await fetch(`${API_BASE}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })
    const reader = res.body?.getReader()
    const decoder = new TextDecoder('utf-8')
    if (!reader) return
    let buffer = ''
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''
      lines.forEach((line) => {
        if (!line.startsWith('data:')) return
        const payload = JSON.parse(line.replace('data:', '').trim())
        if (payload.text) {
          cognitiveStream.value = [payload.text, ...cognitiveStream.value].slice(0, 6)
        }
      })
    }
  } catch {
    cognitiveStream.value = ['Failed to reach local model.']
  }
}

onMounted(async () => {
  await Promise.all([
    loadStatus(),
    loadLogs(),
    loadHeartbeats(),
    loadSkills(),
    loadGoals(),
    loadMemoryStats(),
  ])
  updateAgencyConfig({
    onSort: () => syncGoalOrder(agencyGoals.value),
  })
  attachStream()
  statusTimer = window.setInterval(loadStatus, 6000)
  heartbeatTimer = window.setInterval(loadHeartbeats, 8000)
})

onBeforeUnmount(() => {
  if (statusTimer) window.clearInterval(statusTimer)
  if (heartbeatTimer) window.clearInterval(heartbeatTimer)
  if (eventSource) eventSource.close()
})
</script>

<template>
  <div class="cortex">
    <header class="hud">
      <div class="hud-brand">
        <div class="hud-title">CORTEX-OS</div>
        <div class="hud-sub">Operator Console</div>
      </div>
      <div class="hud-metrics">
        <div class="hud-card">
          <div class="hud-label">Stage</div>
          <div class="hud-value">{{ status.stage }}</div>
        </div>
        <div class="hud-card">
          <div class="hud-label">Heartbeat</div>
          <div class="hud-value">{{ status.paused ? 'PAUSED' : 'ACTIVE' }}</div>
        </div>
        <div class="hud-card">
          <div class="hud-label">Action</div>
          <div class="hud-value">{{ status.action }}</div>
        </div>
      </div>
      <button class="pause-btn" :class="{ paused: status.paused }" @click="togglePause">
        {{ status.paused ? 'RESUME' : 'EMERGENCY PAUSE' }}
      </button>
    </header>

    <main class="grid">
      <section class="panel left">
        <div class="card directive">
          <div class="card-title">Directive</div>
          <textarea v-model="directiveInput" placeholder="Define the operator directive"></textarea>
          <div class="hint">This input does not auto-execute. Use /inject in Command Console.</div>
        </div>

        <div class="card console">
          <div class="card-title">Command Console</div>
          <div class="console-input">
            <input
              v-model="commandInput"
              placeholder="/inject goal · /pause · /resume · /memory note"
              @keyup.enter="runCommand"
            />
            <button @click="runCommand">Run</button>
          </div>
          <div class="console-output">
            <div v-for="line in commandOutput" :key="line" class="console-line">{{ line }}</div>
          </div>
        </div>

        <SkillTimeline :items="learnedSkills" />
      </section>

      <section class="panel center-panel">
        <div class="card chat-card">
          <div class="cognitive-strip" :class="{ open: cognitiveOpen }">
            <div class="cognitive-main">
              <div class="cognitive-title">Cognitive Loop</div>
              <div class="cognitive-inline">
                <input
                  v-model="cognitiveInput"
                  placeholder="Probe the mind..."
                  @keyup.enter="sendCognitivePing"
                />
                <button @click="sendCognitivePing">Probe</button>
              </div>
              <button class="cognitive-toggle" @click="cognitiveOpen = !cognitiveOpen">
                {{ cognitiveOpen ? 'Hide Trace' : 'Show Trace' }}
              </button>
            </div>
            <div v-if="cognitiveOpen" class="cognitive-stream">
              <div v-for="line in cognitiveStream" :key="line" class="stream-line">{{ line }}</div>
            </div>
          </div>
          <div class="chat-window-slot">
            <ChatWindow />
          </div>
        </div>

        <!-- Log Carousel - Memory Stream in Natural Language -->
        <LogCarousel :auto-play="true" :interval="6000" />

        <!-- Live Thoughts -->
        <LiveThoughts />

        <div class="card logs-card">
          <div class="card-title logs-title">
            <span>Live Logs</span>
            <div class="log-filters">
              <button
                v-for="tag in ['all', 'heartbeat', 'errors', 'semantic', 'procedural', 'identity']"
                :key="tag"
                :class="{ active: logFilter === tag }"
                @click="logFilter = tag as any"
              >
                {{ tag }}
              </button>
            </div>
          </div>
          <div class="logs-body">
            <div v-if="displayLogs.length === 0" class="logs-empty">
              No logs available. Check the backend or filters.
            </div>
            <VirtualLogList v-else :items="displayLogs" :item-height="132" :auto-scroll="true" />
          </div>
        </div>
      </section>

      <section class="panel right">
        <!-- Alpha Agent -->
        <AlphaPanel />

        <!-- Workflow Control Panel -->
        <WorkflowPanel />

        <!-- Resource Monitor -->
        <ResourceMonitor />

        <!-- Memory Core -->
        <div class="card">
          <div class="card-title">Memory Core</div>
          <div class="memory-total">Total: {{ memoryStats.total }}</div>
          <div class="memory-grid">
            <div v-for="(count, type) in memoryStats.by_type" :key="type" class="memory-chip">
              <span class="memory-type">{{ type }}</span>
              <span class="memory-count">{{ count }}</span>
            </div>
          </div>
          <div class="memory-foot">
            Last consolidated: {{ memoryStats.last_consolidated || 'n/a' }}
          </div>
        </div>

        <div class="card">
          <div class="card-title">Agency Stack</div>
          <div v-if="agencyGoals.length === 0" class="muted">No active goals.</div>
          <div ref="agencyParent" class="goal-list">
            <div v-for="goal in agencyGoals" :key="goal.id" class="goal-row">
              <div class="goal-handle" title="Drag to reprioritize">⠿</div>
              <div>
                <div class="goal-title">{{ goal.objective }}</div>
                <div class="goal-meta">Priority {{ goal.priority.toFixed(2) }} · {{ goal.status }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">Skill Tree</div>
          <div class="skill-tree">
            <div v-for="(group, category) in skillGroups" :key="category" class="skill-group">
              <div class="skill-group-title">{{ category }}</div>
              <div v-for="skill in group" :key="skill.id" class="skill-row">
                <div class="skill-name">{{ skill.name }}</div>
                <div class="skill-desc">{{ skill.description }}</div>
                <div class="skill-id">{{ skill.id }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.cortex {
  min-height: 100vh;
  padding: clamp(18px, 2.2vw, 32px);
  background: radial-gradient(circle at 20% 0%, rgba(218, 108, 60, 0.08), transparent 40%),
    radial-gradient(circle at 80% 0%, rgba(54, 68, 85, 0.2), transparent 45%);
}

.hud {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: clamp(12px, 2vw, 24px);
  background: var(--surface-panel);
  color: var(--text-inverse);
  padding: 18px 24px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  flex-wrap: wrap;
}

.hud-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.hud-sub {
  font-size: 12px;
  color: var(--text-dim);
  text-transform: uppercase;
}

.hud-metrics {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hud-card {
  background: rgba(248, 246, 242, 0.08);
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  min-width: 120px;
  flex: 1 1 120px;
}

.hud-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-dim);
}

.hud-value {
  font-size: 15px;
  font-weight: 600;
  margin-top: 4px;
}

.pause-btn {
  padding: 12px 18px;
  border-radius: 999px;
  border: none;
  font-weight: 600;
  letter-spacing: 0.04em;
  background: var(--c-ember);
  color: #1b2027;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(218, 108, 60, 0.35);
  white-space: nowrap;
}

.pause-btn.paused {
  background: #4dd4a5;
  box-shadow: 0 10px 25px rgba(77, 212, 165, 0.35);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: clamp(14px, 2vw, 22px);
  margin-top: 24px;
  align-items: start;
  min-height: calc(100vh - 160px);
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
  height: 100%;
}

.center-panel {
  min-height: calc(100vh - 200px);
}

.card {
  background: var(--surface-card);
  border-radius: var(--radius-md);
  padding: 16px;
  box-shadow: var(--shadow-soft);
  min-width: 0;
}

.chat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 50vh;
  max-height: 60vh;
  padding: 0;
  overflow: hidden;
}

.cognitive-strip {
  background: var(--surface-panel);
  color: var(--text-inverse);
  padding: 12px 16px;
  border-bottom: 1px solid rgba(248, 246, 242, 0.12);
}

.cognitive-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.cognitive-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 700;
}

.cognitive-inline {
  display: flex;
  gap: 8px;
  flex: 1;
  min-width: 220px;
}

.cognitive-inline input {
  flex: 1;
  min-width: 220px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(248, 246, 242, 0.2);
  background: rgba(15, 20, 27, 0.6);
  color: var(--text-inverse);
}

.cognitive-inline button {
  padding: 8px 12px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--c-ember);
  cursor: pointer;
}

.cognitive-toggle {
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(248, 246, 242, 0.2);
  background: transparent;
  color: var(--text-inverse);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  cursor: pointer;
}

.cognitive-stream {
  margin-top: 10px;
  font-size: 12px;
  color: rgba(248, 246, 242, 0.8);
  max-height: 120px;
  overflow: auto;
}

.chat-window-slot {
  flex: 1;
  min-height: 0;
}

.logs-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 40vh;
}

.logs-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.logs-body {
  flex: 1;
  min-height: 0;
  height: 100%;
}

.logs-empty {
  font-size: 13px;
  color: var(--text-muted);
  padding: 16px;
  border: 1px dashed rgba(16, 21, 28, 0.12);
  border-radius: var(--radius-sm);
}

.log-filters {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.log-filters button {
  border: 1px solid rgba(16, 21, 28, 0.12);
  background: transparent;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  cursor: pointer;
}

.log-filters button.active {
  background: var(--c-ember);
  color: #1b2027;
  border-color: transparent;
}

.card-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 12px;
}

.directive textarea {
  width: 100%;
  min-height: 110px;
  border: 1px solid rgba(16, 21, 28, 0.2);
  border-radius: var(--radius-sm);
  padding: 10px;
  font-family: var(--font-mono);
  background: #fbfaf7;
}

.hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 8px;
}

.console-input {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.console-input input {
  flex: 1;
  min-width: 200px;
  padding: 10px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(16, 21, 28, 0.2);
  font-family: var(--font-mono);
}

.console-input button {
  padding: 10px 14px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--surface-panel);
  color: var(--text-inverse);
  cursor: pointer;
}

.console-output {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-muted);
}

.console-line {
  padding: 4px 0;
}

.stream-line {
  padding: 4px 0;
}

.goal-row {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(16, 21, 28, 0.08);
  word-break: break-word;
}

.goal-row:last-child {
  border-bottom: none;
}

.goal-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.goal-handle {
  font-size: 18px;
  color: var(--text-muted);
  cursor: grab;
  user-select: none;
  line-height: 1;
  padding-top: 4px;
}

.goal-row:active .goal-handle {
  cursor: grabbing;
}

.goal-title {
  font-size: 13px;
  font-weight: 600;
}

.goal-meta {
  font-size: 11px;
  color: var(--text-muted);
}

.skill-tree {
  display: grid;
  gap: 14px;
}

.skill-group-title {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.skill-row {
  padding: 10px 0;
  border-bottom: 1px dashed rgba(16, 21, 28, 0.15);
  word-break: break-word;
}

.skill-row:last-child {
  border-bottom: none;
}

.skill-name {
  font-weight: 600;
  font-size: 13px;
}

.skill-desc {
  font-size: 11px;
  color: var(--text-muted);
  margin: 4px 0;
}

.skill-id {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--c-ember);
}

.memory-total {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 10px;
}

.memory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.memory-chip {
  background: rgba(16, 21, 28, 0.06);
  border-radius: var(--radius-sm);
  padding: 8px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.memory-type {
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.memory-count {
  font-weight: 600;
}

.memory-foot {
  margin-top: 10px;
  font-size: 11px;
  color: var(--text-muted);
}

.muted {
  color: var(--text-muted);
}

@media (max-width: 900px) {
  .hud {
    align-items: flex-start;
  }
}
</style>
