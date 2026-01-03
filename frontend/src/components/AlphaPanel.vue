<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { API_BASE } from '../config'

type AlphaStatus = {
  running: boolean
  config: { mode: string; interval_s: number; max_memory: number }
  status: { cycle?: number; mode?: string; interval_s?: number; max_memory?: number }
  last_error?: string | null
}

const status = ref<AlphaStatus | null>(null)
const loading = ref(false)
const message = ref('')
const mode = ref('propose')
const interval = ref(300)
const maxMemory = ref(20000)
let timer: number | undefined

const loadStatus = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/alpha/status`)
    const data = await res.json()
    status.value = data
    mode.value = data?.config?.mode || 'propose'
    interval.value = data?.config?.interval_s || 300
    maxMemory.value = data?.config?.max_memory || 20000
  } catch {
    status.value = null
  }
}

const startAlpha = async () => {
  loading.value = true
  await fetch(`${API_BASE}/api/alpha/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mode: mode.value,
      interval_s: interval.value,
      max_memory: maxMemory.value,
    }),
  })
  loading.value = false
  await loadStatus()
}

const stopAlpha = async () => {
  loading.value = true
  await fetch(`${API_BASE}/api/alpha/stop`, { method: 'POST' })
  loading.value = false
  await loadStatus()
}

const runOnce = async () => {
  loading.value = true
  await fetch(`${API_BASE}/api/alpha/once`, { method: 'POST' })
  loading.value = false
  await loadStatus()
}

const updateConfig = async () => {
  loading.value = true
  await fetch(`${API_BASE}/api/alpha/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mode: mode.value,
      interval_s: interval.value,
      max_memory: maxMemory.value,
    }),
  })
  loading.value = false
  await loadStatus()
}

const sendMessage = async () => {
  const payload = message.value.trim()
  if (!payload) return
  loading.value = true
  await fetch(`${API_BASE}/api/alpha/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: payload }),
  })
  message.value = ''
  loading.value = false
  await loadStatus()
}

onMounted(() => {
  loadStatus()
  timer = window.setInterval(loadStatus, 8000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div class="card alpha-panel">
    <div class="card-title">Alpha Agent</div>
    <div class="alpha-status">
      <div class="status-chip" :class="status?.running ? 'running' : 'stopped'">
        {{ status?.running ? 'RUNNING' : 'STOPPED' }}
      </div>
      <div class="status-text">
        Cycle {{ status?.status?.cycle ?? 0 }} · Mode {{ status?.status?.mode ?? mode }}
      </div>
    </div>

    <div class="alpha-controls">
      <label>
        <span>Mode</span>
        <select v-model="mode">
          <option value="observe">observe</option>
          <option value="propose">propose</option>
          <option value="execute">execute</option>
        </select>
      </label>
      <label>
        <span>Interval (s)</span>
        <input v-model.number="interval" type="number" min="30" step="10" />
      </label>
      <label>
        <span>Max Memory</span>
        <input v-model.number="maxMemory" type="number" min="100" step="100" />
      </label>
      <div class="alpha-buttons">
        <button :disabled="loading" @click="startAlpha">Start</button>
        <button :disabled="loading" @click="stopAlpha">Stop</button>
        <button :disabled="loading" @click="runOnce">Run Once</button>
        <button :disabled="loading" @click="updateConfig">Apply</button>
      </div>
    </div>

    <div class="alpha-message">
      <input v-model="message" placeholder="Send message to Alpha..." />
      <button :disabled="loading" @click="sendMessage">Send</button>
    </div>
    <div v-if="status?.last_error" class="alpha-error">Last error: {{ status.last_error }}</div>
  </div>
</template>

<style scoped>
.alpha-panel {
  display: grid;
  gap: 12px;
}

.alpha-status {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.status-chip {
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 999px;
  font-weight: 700;
  letter-spacing: 0.06em;
  background: rgba(16, 21, 28, 0.08);
  color: rgba(16, 21, 28, 0.7);
}

.status-chip.running {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.status-chip.stopped {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.status-text {
  font-size: 12px;
  color: var(--text-muted);
}

.alpha-controls {
  display: grid;
  gap: 8px;
}

.alpha-controls label {
  display: grid;
  gap: 6px;
  font-size: 11px;
  color: var(--text-muted);
}

.alpha-controls select,
.alpha-controls input {
  padding: 8px;
  border-radius: 6px;
  border: 1px solid rgba(16, 21, 28, 0.15);
  background: #fbfaf7;
  font-size: 12px;
}

.alpha-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.alpha-buttons button {
  padding: 8px 10px;
  border: none;
  border-radius: 6px;
  background: var(--surface-panel);
  color: var(--text-inverse);
  font-size: 11px;
  cursor: pointer;
}

.alpha-message {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.alpha-message input {
  flex: 1;
  min-width: 160px;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid rgba(16, 21, 28, 0.15);
  background: #fbfaf7;
  font-size: 12px;
}

.alpha-message button {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: var(--c-ember);
  color: #1b2027;
  font-size: 11px;
  cursor: pointer;
}

.alpha-error {
  font-size: 11px;
  color: #ef4444;
}
</style>
