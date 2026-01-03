<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { API_BASE } from '@/config'

interface ValidationMetric {
  type: string
  value: number
  timestamp: string
  status: 'pass' | 'warn' | 'fail'
}

interface TrainingStatus {
  type: 'status'
  session_id: string
  status: string
  step: number
  loss: number
}

// State
const metrics = ref<ValidationMetric[]>([])
const sessionStatus = ref<TrainingStatus | null>(null)
const isConnected = ref(false)
const error = ref<string | null>(null)

let eventSource: EventSource | null = null

// Computed
const latestMetrics = computed(() => {
  const byType: Record<string, ValidationMetric> = {}
  for (const m of metrics.value) {
    if (!byType[m.type] || new Date(m.timestamp) > new Date(byType[m.type].timestamp)) {
      byType[m.type] = m
    }
  }
  return Object.values(byType)
})

const overallStatus = computed(() => {
  if (latestMetrics.value.some(m => m.status === 'fail')) return 'fail'
  if (latestMetrics.value.some(m => m.status === 'warn')) return 'warn'
  return 'pass'
})

// Connect to training stream
function connectStream() {
  if (eventSource) {
    eventSource.close()
  }

  eventSource = new EventSource(`${API_BASE}/api/training/stream`)
  isConnected.value = true
  error.value = null

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      if (data.type === 'status') {
        sessionStatus.value = data as TrainingStatus

        // Generate validation metrics from training status
        const now = new Date().toISOString()
        const lossMetric: ValidationMetric = {
          type: 'loss',
          value: data.loss,
          timestamp: now,
          status: data.loss < 0.5 ? 'pass' : data.loss < 1.0 ? 'warn' : 'fail'
        }
        addMetric(lossMetric)
      } else if (data.gradient_norm !== undefined) {
        // Generate gradient health metric
        const now = new Date().toISOString()
        const gradMetric: ValidationMetric = {
          type: 'gradient_health',
          value: data.gradient_norm,
          timestamp: now,
          status: data.is_clipped ? 'warn' : data.gradient_norm < 10 ? 'pass' : 'fail'
        }
        addMetric(gradMetric)

        // Memory metric
        if (data.memory_usage_mb) {
          const memMetric: ValidationMetric = {
            type: 'memory',
            value: data.memory_usage_mb,
            timestamp: now,
            status: data.memory_usage_mb < 10000 ? 'pass' : data.memory_usage_mb < 11000 ? 'warn' : 'fail'
          }
          addMetric(memMetric)
        }
      }
    } catch (e) {
      console.error('Failed to parse stream data:', e)
    }
  }

  eventSource.onerror = () => {
    isConnected.value = false
    error.value = 'Connection lost. Reconnecting...'
    setTimeout(connectStream, 3000)
  }
}

function addMetric(metric: ValidationMetric) {
  metrics.value.push(metric)
  // Keep last 100 metrics
  if (metrics.value.length > 100) {
    metrics.value = metrics.value.slice(-100)
  }
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'pass': return '✓'
    case 'warn': return '⚠'
    case 'fail': return '✗'
    default: return '?'
  }
}

function formatValue(type: string, value: number): string {
  switch (type) {
    case 'loss': return value.toFixed(4)
    case 'gradient_health': return value.toFixed(2)
    case 'memory': return `${value.toFixed(0)} MB`
    default: return value.toString()
  }
}

onMounted(() => {
  connectStream()
})

onBeforeUnmount(() => {
  if (eventSource) {
    eventSource.close()
  }
})
</script>

<template>
  <div class="validation-stream-container">
    <header class="stream-header">
      <h3>Validation Stream</h3>
      <div class="status-badge" :class="overallStatus">
        {{ getStatusIcon(overallStatus) }} {{ overallStatus.toUpperCase() }}
      </div>
    </header>

    <!-- Connection status -->
    <div class="connection-status" :class="{ connected: isConnected }">
      <span class="connection-dot"></span>
      {{ isConnected ? 'Connected' : 'Disconnected' }}
    </div>

    <!-- Session info -->
    <div v-if="sessionStatus" class="session-info">
      <span class="session-label">Session:</span>
      <span class="session-id">{{ sessionStatus.session_id }}</span>
      <span class="session-status">{{ sessionStatus.status }}</span>
      <span class="session-step">Step {{ sessionStatus.step }}</span>
    </div>

    <!-- Metric cards -->
    <div class="metrics-grid">
      <div
        v-for="metric in latestMetrics"
        :key="metric.type"
        class="metric-card"
        :class="metric.status"
      >
        <div class="metric-header">
          <span class="metric-type">{{ metric.type.replace('_', ' ') }}</span>
          <span class="metric-status">{{ getStatusIcon(metric.status) }}</span>
        </div>
        <div class="metric-value">{{ formatValue(metric.type, metric.value) }}</div>
      </div>
    </div>

    <!-- Recent events log -->
    <div class="events-log">
      <div class="log-header">Recent Events</div>
      <div class="log-scroll">
        <div
          v-for="(metric, i) in [...metrics].reverse().slice(0, 20)"
          :key="i"
          class="log-entry"
          :class="metric.status"
        >
          <span class="log-time">{{ new Date(metric.timestamp).toLocaleTimeString() }}</span>
          <span class="log-type">{{ metric.type }}</span>
          <span class="log-value">{{ formatValue(metric.type, metric.value) }}</span>
          <span class="log-status">{{ getStatusIcon(metric.status) }}</span>
        </div>
        <div v-if="metrics.length === 0" class="log-empty">
          Waiting for validation events...
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>
  </div>
</template>

<style scoped>
.validation-stream-container {
  background: linear-gradient(135deg, #0f141b 0%, #1a1f2e 100%);
  border: 1px solid rgba(218, 108, 60, 0.2);
  border-radius: 12px;
  padding: 16px;
}

.stream-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stream-header h3 {
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
}

.status-badge.pass {
  background: rgba(77, 212, 165, 0.2);
  color: #4dd4a5;
}

.status-badge.warn {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.status-badge.fail {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #666;
  margin-bottom: 12px;
}

.connection-status.connected {
  color: #4dd4a5;
}

.connection-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #666;
}

.connection-status.connected .connection-dot {
  background: #4dd4a5;
  animation: pulse 2s infinite;
}

.session-info {
  display: flex;
  gap: 12px;
  padding: 8px 12px;
  background: #0a0e14;
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 11px;
}

.session-label {
  color: #666;
}

.session-id {
  color: #da6c3c;
  font-family: monospace;
}

.session-status {
  color: #4dd4a5;
}

.session-step {
  color: #888;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}

.metric-card {
  background: #0a0e14;
  border-radius: 8px;
  padding: 12px;
  border-left: 3px solid #333;
}

.metric-card.pass {
  border-left-color: #4dd4a5;
}

.metric-card.warn {
  border-left-color: #f59e0b;
}

.metric-card.fail {
  border-left-color: #ef4444;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.metric-type {
  font-size: 10px;
  color: #666;
  text-transform: uppercase;
}

.metric-status {
  font-size: 12px;
}

.metric-card.pass .metric-status { color: #4dd4a5; }
.metric-card.warn .metric-status { color: #f59e0b; }
.metric-card.fail .metric-status { color: #ef4444; }

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #f8f6f2;
  font-family: monospace;
}

.events-log {
  background: #0a0e14;
  border-radius: 8px;
  overflow: hidden;
}

.log-header {
  padding: 8px 12px;
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
  border-bottom: 1px solid #1a202c;
}

.log-scroll {
  max-height: 150px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  gap: 12px;
  padding: 6px 12px;
  font-size: 11px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.02);
}

.log-entry:last-child {
  border-bottom: none;
}

.log-time {
  color: #555;
  font-family: monospace;
}

.log-type {
  color: #888;
  min-width: 100px;
}

.log-value {
  color: #f8f6f2;
  font-family: monospace;
  flex: 1;
}

.log-status {
  width: 16px;
  text-align: center;
}

.log-entry.pass .log-status { color: #4dd4a5; }
.log-entry.warn .log-status { color: #f59e0b; }
.log-entry.fail .log-status { color: #ef4444; }

.log-empty {
  padding: 20px;
  text-align: center;
  color: #555;
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

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
