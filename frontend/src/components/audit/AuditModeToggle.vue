<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { API_BASE } from '@/config'

interface AuditLogEntry {
  id: string
  timestamp: string
  actor: string
  action: string
  severity: string
  details: Record<string, any>
}

interface AuditStatus {
  enabled: boolean
  log_count: number
  last_entry: AuditLogEntry | null
}

// State
const status = ref<AuditStatus | null>(null)
const recentLogs = ref<AuditLogEntry[]>([])
const loading = ref(true)
const toggling = ref(false)
const error = ref<string | null>(null)

let eventSource: EventSource | null = null

// Computed
const isEnabled = computed(() => status.value?.enabled ?? false)

// Fetch audit status
async function fetchStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/audit/status`)
    status.value = await res.json()
  } catch (e) {
    error.value = `Failed to fetch audit status: ${e}`
  } finally {
    loading.value = false
  }
}

// Fetch recent logs
async function fetchLogs() {
  try {
    const res = await fetch(`${API_BASE}/api/audit/logs?limit=10`)
    const data = await res.json()
    recentLogs.value = data.logs || []
  } catch (e) {
    console.error('Failed to fetch audit logs:', e)
  }
}

// Toggle audit mode
async function toggleAudit() {
  toggling.value = true
  error.value = null

  try {
    const endpoint = isEnabled.value ? 'disable' : 'enable'
    const res = await fetch(`${API_BASE}/api/audit/${endpoint}`, {
      method: 'POST'
    })
    const data = await res.json()

    if (status.value) {
      status.value.enabled = data.enabled
    }

    // Reconnect stream if enabled
    if (data.enabled) {
      connectStream()
    } else if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  } catch (e) {
    error.value = `Failed to toggle audit mode: ${e}`
  } finally {
    toggling.value = false
  }
}

// Connect to audit stream
function connectStream() {
  if (eventSource) {
    eventSource.close()
  }

  eventSource = new EventSource(`${API_BASE}/api/audit/stream`)

  eventSource.onmessage = (event) => {
    try {
      const entry = JSON.parse(event.data) as AuditLogEntry
      recentLogs.value.unshift(entry)
      // Keep last 20
      if (recentLogs.value.length > 20) {
        recentLogs.value = recentLogs.value.slice(0, 20)
      }
      // Update count
      if (status.value) {
        status.value.log_count++
        status.value.last_entry = entry
      }
    } catch (e) {
      console.error('Failed to parse audit event:', e)
    }
  }

  eventSource.onerror = () => {
    // Will auto-reconnect
  }
}

// Generate compliance report
async function generateReport() {
  try {
    const res = await fetch(`${API_BASE}/api/audit/report`, {
      method: 'POST'
    })
    const report = await res.json()
    // Open in new window as JSON
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } catch (e) {
    error.value = `Failed to generate report: ${e}`
  }
}

function getSeverityIcon(severity: string): string {
  switch (severity) {
    case 'info': return 'ℹ'
    case 'warning': return '⚠'
    case 'critical': return '🚨'
    default: return '•'
  }
}

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString()
}

onMounted(() => {
  fetchStatus()
  fetchLogs()
})

onBeforeUnmount(() => {
  if (eventSource) {
    eventSource.close()
  }
})
</script>

<template>
  <div class="audit-toggle-container">
    <header class="audit-header">
      <h3>Audit Mode</h3>
      <div class="toggle-wrapper">
        <button
          class="toggle-btn"
          :class="{ enabled: isEnabled, toggling }"
          @click="toggleAudit"
          :disabled="loading || toggling"
        >
          <span class="toggle-track">
            <span class="toggle-thumb"></span>
          </span>
          <span class="toggle-label">{{ isEnabled ? 'ON' : 'OFF' }}</span>
        </button>
      </div>
    </header>

    <div v-if="loading" class="loading">Loading audit status...</div>

    <template v-else>
      <!-- Status summary -->
      <div class="status-summary">
        <div class="stat">
          <span class="stat-value">{{ status?.log_count || 0 }}</span>
          <span class="stat-label">Total Events</span>
        </div>
        <div class="stat" v-if="status?.last_entry">
          <span class="stat-value">{{ formatTime(status.last_entry.timestamp) }}</span>
          <span class="stat-label">Last Event</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="audit-actions">
        <button class="action-btn" @click="fetchLogs">
          Refresh
        </button>
        <button class="action-btn primary" @click="generateReport">
          Generate Report
        </button>
      </div>

      <!-- Recent logs -->
      <div class="recent-logs">
        <div class="logs-header">Recent Activity</div>
        <div class="logs-scroll">
          <div
            v-for="log in recentLogs"
            :key="log.id"
            class="log-entry"
            :class="log.severity"
          >
            <span class="log-icon">{{ getSeverityIcon(log.severity) }}</span>
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-action">{{ log.action }}</span>
            <span class="log-actor">{{ log.actor }}</span>
          </div>
          <div v-if="recentLogs.length === 0" class="logs-empty">
            No audit events recorded yet
          </div>
        </div>
      </div>
    </template>

    <div v-if="error" class="error-banner">{{ error }}</div>
  </div>
</template>

<style scoped>
.audit-toggle-container {
  background: linear-gradient(135deg, #0f141b 0%, #1a1f2e 100%);
  border: 1px solid rgba(218, 108, 60, 0.2);
  border-radius: 12px;
  padding: 16px;
}

.audit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.audit-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #f8f6f2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-track {
  width: 44px;
  height: 24px;
  background: #333;
  border-radius: 12px;
  position: relative;
  transition: background 0.2s;
}

.toggle-btn.enabled .toggle-track {
  background: #4dd4a5;
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #f8f6f2;
  border-radius: 50%;
  transition: transform 0.2s;
}

.toggle-btn.enabled .toggle-thumb {
  transform: translateX(20px);
}

.toggle-btn.toggling .toggle-thumb {
  animation: pulse 0.5s infinite;
}

.toggle-label {
  font-size: 12px;
  font-weight: 600;
  color: #888;
}

.toggle-btn.enabled .toggle-label {
  color: #4dd4a5;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.status-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #f8f6f2;
  font-family: monospace;
}

.stat-label {
  font-size: 10px;
  color: #666;
  text-transform: uppercase;
}

.audit-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid #333;
  border-radius: 6px;
  color: #888;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #1a202c;
  color: #f8f6f2;
}

.action-btn.primary {
  background: #da6c3c;
  border-color: #da6c3c;
  color: #0f141b;
  font-weight: 600;
}

.action-btn.primary:hover {
  background: #e07d4d;
}

.recent-logs {
  background: #0a0e14;
  border-radius: 8px;
  overflow: hidden;
}

.logs-header {
  padding: 8px 12px;
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
  border-bottom: 1px solid #1a202c;
}

.logs-scroll {
  max-height: 200px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 11px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.02);
}

.log-entry:last-child {
  border-bottom: none;
}

.log-icon {
  width: 16px;
  text-align: center;
}

.log-entry.info .log-icon { color: #60a5fa; }
.log-entry.warning .log-icon { color: #f59e0b; }
.log-entry.critical .log-icon { color: #ef4444; }

.log-time {
  color: #555;
  font-family: monospace;
  min-width: 70px;
}

.log-action {
  color: #f8f6f2;
  flex: 1;
}

.log-actor {
  color: #da6c3c;
  font-size: 10px;
}

.logs-empty {
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
