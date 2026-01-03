<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { API_BASE } from '@/config'

interface TrainingSession {
  session_id: string
  name: string
  status: string
  current_step: number
  total_steps: number
  current_loss: number
  config: {
    name: string
    target_module: string
    learning_rate: number
    max_steps: number
    gradient_clip: number
  } | null
  created_at: string
  logs: string[]
}

// State
const session = ref<TrainingSession | null>(null)
const loading = ref(true)
const starting = ref(false)
const error = ref<string | null>(null)

// Form state for new session
const newSessionName = ref('lora-tune')
const learningRate = ref(0.0001)
const maxSteps = ref(1000)

let pollInterval: number | null = null

// Computed
const progress = computed(() => {
  if (!session.value || session.value.total_steps === 0) return 0
  return Math.round((session.value.current_step / session.value.total_steps) * 100)
})

const statusColor = computed(() => {
  switch (session.value?.status) {
    case 'training': return '#4dd4a5'
    case 'completed': return '#60a5fa'
    case 'failed': return '#ef4444'
    case 'stopped': return '#f59e0b'
    default: return '#666'
  }
})

const isActive = computed(() =>
  session.value?.status === 'training' || session.value?.status === 'initializing'
)

// Fetch training status
async function fetchStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/training/status`)
    const data = await res.json()

    if (data.session_id) {
      // Fetch full session details
      const sessionRes = await fetch(`${API_BASE}/api/training/session/${data.session_id}`)
      session.value = await sessionRes.json()
    } else {
      session.value = null
    }
  } catch (e) {
    console.error('Failed to fetch training status:', e)
  } finally {
    loading.value = false
  }
}

// Start new training session
async function startSession() {
  starting.value = true
  error.value = null

  try {
    const res = await fetch(`${API_BASE}/api/training/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newSessionName.value,
        learning_rate: learningRate.value,
        max_steps: maxSteps.value,
        target_module: 'attn',
        gradient_clip: 1.0
      })
    })

    const data = await res.json()
    if (data.error) {
      error.value = data.error
    } else {
      await fetchStatus()
      startPolling()
    }
  } catch (e) {
    error.value = `Failed to start session: ${e}`
  } finally {
    starting.value = false
  }
}

// Stop training session
async function stopSession() {
  if (!session.value) return

  try {
    await fetch(`${API_BASE}/api/training/session/${session.value.session_id}/stop`, {
      method: 'POST'
    })
    await fetchStatus()
  } catch (e) {
    error.value = `Failed to stop session: ${e}`
  }
}

function startPolling() {
  if (pollInterval) return
  pollInterval = window.setInterval(fetchStatus, 2000)
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleString()
}

onMounted(() => {
  fetchStatus()
  startPolling()
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<template>
  <div class="tuning-progress-container">
    <header class="tuning-header">
      <h3>LoRA Tuning</h3>
      <div class="status-badge" :style="{ background: statusColor + '33', color: statusColor }">
        {{ session?.status || 'idle' }}
      </div>
    </header>

    <div v-if="loading" class="loading">Loading training status...</div>

    <template v-else>
      <!-- Active session view -->
      <template v-if="session">
        <div class="session-info">
          <div class="session-name">{{ session.name }}</div>
          <div class="session-id">{{ session.session_id }}</div>
          <div class="session-time">Started: {{ formatTime(session.created_at) }}</div>
        </div>

        <!-- Progress bar -->
        <div class="progress-section">
          <div class="progress-header">
            <span>Step {{ session.current_step }} / {{ session.total_steps }}</span>
            <span class="progress-percent">{{ progress }}%</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: progress + '%', background: statusColor }"
            ></div>
          </div>
        </div>

        <!-- Metrics -->
        <div class="metrics-row">
          <div class="metric">
            <span class="metric-label">Loss</span>
            <span class="metric-value">{{ session.current_loss.toFixed(4) }}</span>
          </div>
          <div class="metric" v-if="session.config">
            <span class="metric-label">LR</span>
            <span class="metric-value">{{ session.config.learning_rate }}</span>
          </div>
          <div class="metric" v-if="session.config">
            <span class="metric-label">Target</span>
            <span class="metric-value">{{ session.config.target_module }}</span>
          </div>
        </div>

        <!-- Logs -->
        <div class="logs-section">
          <div class="logs-header">Training Logs</div>
          <div class="logs-scroll">
            <div v-for="(log, i) in session.logs" :key="i" class="log-line">
              {{ log }}
            </div>
            <div v-if="session.logs.length === 0" class="logs-empty">
              No logs yet
            </div>
          </div>
        </div>

        <!-- Stop button -->
        <button
          v-if="isActive"
          class="stop-btn"
          @click="stopSession"
        >
          Stop Training
        </button>
      </template>

      <!-- No session - start form -->
      <template v-else>
        <div class="start-form">
          <div class="form-group">
            <label>Session Name</label>
            <input v-model="newSessionName" type="text" placeholder="lora-tune" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Learning Rate</label>
              <input v-model.number="learningRate" type="number" step="0.0001" />
            </div>
            <div class="form-group">
              <label>Max Steps</label>
              <input v-model.number="maxSteps" type="number" />
            </div>
          </div>
          <button
            class="start-btn"
            @click="startSession"
            :disabled="starting"
          >
            {{ starting ? 'Starting...' : 'Start Training' }}
          </button>
        </div>
      </template>
    </template>

    <div v-if="error" class="error-banner">{{ error }}</div>
  </div>
</template>

<style scoped>
.tuning-progress-container {
  background: linear-gradient(135deg, #0f141b 0%, #1a1f2e 100%);
  border: 1px solid rgba(218, 108, 60, 0.2);
  border-radius: 12px;
  padding: 16px;
}

.tuning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tuning-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #f8f6f2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.session-info {
  margin-bottom: 16px;
}

.session-name {
  font-size: 16px;
  font-weight: 600;
  color: #f8f6f2;
}

.session-id {
  font-size: 11px;
  color: #da6c3c;
  font-family: monospace;
}

.session-time {
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.progress-section {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #888;
  margin-bottom: 6px;
}

.progress-percent {
  font-weight: 600;
  color: #f8f6f2;
}

.progress-bar {
  height: 8px;
  background: #1a202c;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 4px;
}

.metrics-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.metric {
  display: flex;
  flex-direction: column;
  padding: 8px 12px;
  background: #0a0e14;
  border-radius: 6px;
  flex: 1;
}

.metric-label {
  font-size: 10px;
  color: #666;
  text-transform: uppercase;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #f8f6f2;
  font-family: monospace;
}

.logs-section {
  background: #0a0e14;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
}

.logs-header {
  padding: 8px 12px;
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
  border-bottom: 1px solid #1a202c;
}

.logs-scroll {
  max-height: 120px;
  overflow-y: auto;
  padding: 8px 12px;
}

.log-line {
  font-size: 11px;
  color: #888;
  font-family: monospace;
  padding: 2px 0;
}

.logs-empty {
  color: #555;
  text-align: center;
  padding: 12px;
}

.stop-btn {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid #ef4444;
  border-radius: 6px;
  color: #ef4444;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.stop-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}

.start-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
}

.form-group input {
  background: #0a0e14;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 8px 12px;
  color: #f8f6f2;
  font-size: 13px;
}

.form-group input:focus {
  outline: none;
  border-color: #da6c3c;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-row .form-group {
  flex: 1;
}

.start-btn {
  width: 100%;
  padding: 10px;
  background: #da6c3c;
  border: none;
  border-radius: 6px;
  color: #0f141b;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.start-btn:hover {
  background: #e07d4d;
}

.start-btn:disabled {
  background: #666;
  cursor: not-allowed;
}

.error-banner {
  margin-top: 12px;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #ef4444;
  font-size: 12px;
}
</style>
