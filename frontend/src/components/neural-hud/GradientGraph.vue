<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { API_BASE } from '@/config'

// Types matching backend GradientMetric
interface GradientMetric {
  step: number
  timestamp: string
  gradient_norm: number
  learning_rate: number
  memory_usage_mb: number
  is_clipped: boolean
}

interface TrainingStatus {
  type: 'status'
  session_id: string
  status: string
  step: number
  loss: number
}

// State
const gradients = ref<GradientMetric[]>([])
const isStreaming = ref(false)
const error = ref<string | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const sessionStatus = ref<TrainingStatus | null>(null)

let eventSource: EventSource | null = null
let pollInterval: number | null = null

// Computed
const latestGradient = computed(() => gradients.value[gradients.value.length - 1] || null)
const maxNorm = computed(() => Math.max(...gradients.value.map(g => g.gradient_norm), 0.001))
const avgNorm = computed(() => {
  if (gradients.value.length === 0) return 0
  return gradients.value.reduce((sum, g) => sum + g.gradient_norm, 0) / gradients.value.length
})
const clippedCount = computed(() => gradients.value.filter(g => g.is_clipped).length)

// Fetch initial data
async function fetchGradients() {
  try {
    const res = await fetch(`${API_BASE}/api/training/gradients?limit=200`)
    const data = await res.json()
    gradients.value = data.gradients || []
    drawChart()
  } catch (e) {
    error.value = `Failed to fetch gradients: ${e}`
  }
}

// Connect to SSE stream
function connectStream() {
  if (eventSource) {
    eventSource.close()
  }

  eventSource = new EventSource(`${API_BASE}/api/training/stream`)
  isStreaming.value = true

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      if (data.type === 'status') {
        sessionStatus.value = data as TrainingStatus
      } else {
        // It's a gradient metric
        gradients.value.push(data as GradientMetric)
        // Keep last 500 samples for performance
        if (gradients.value.length > 500) {
          gradients.value = gradients.value.slice(-500)
        }
        drawChart()
      }
    } catch (e) {
      console.error('Failed to parse stream data:', e)
    }
  }

  eventSource.onerror = () => {
    isStreaming.value = false
    // Fallback to polling
    startPolling()
  }
}

function startPolling() {
  if (pollInterval) return
  pollInterval = window.setInterval(fetchGradients, 2000)
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

// Canvas drawing
function drawChart() {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = canvas.width
  const height = canvas.height
  const padding = 40

  // Clear
  ctx.fillStyle = '#0f141b'
  ctx.fillRect(0, 0, width, height)

  if (gradients.value.length < 2) {
    ctx.fillStyle = '#666'
    ctx.font = '14px monospace'
    ctx.textAlign = 'center'
    ctx.fillText('Waiting for gradient data...', width / 2, height / 2)
    return
  }

  const data = gradients.value
  const max = Math.max(...data.map(d => d.gradient_norm)) * 1.1
  const min = Math.min(...data.map(d => d.gradient_norm)) * 0.9
  const range = max - min || 1

  // Draw grid
  ctx.strokeStyle = '#1a202c'
  ctx.lineWidth = 1
  for (let i = 0; i <= 4; i++) {
    const y = padding + (height - padding * 2) * (i / 4)
    ctx.beginPath()
    ctx.moveTo(padding, y)
    ctx.lineTo(width - padding, y)
    ctx.stroke()
  }

  // Y-axis labels
  ctx.fillStyle = '#666'
  ctx.font = '10px monospace'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 4; i++) {
    const val = max - (range * i / 4)
    const y = padding + (height - padding * 2) * (i / 4)
    ctx.fillText(val.toFixed(2), padding - 5, y + 3)
  }

  // Draw gradient line
  ctx.strokeStyle = '#da6c3c'
  ctx.lineWidth = 2
  ctx.beginPath()

  data.forEach((point, i) => {
    const x = padding + (i / (data.length - 1)) * (width - padding * 2)
    const y = padding + ((max - point.gradient_norm) / range) * (height - padding * 2)

    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()

  // Draw clipped points (red dots)
  data.forEach((point, i) => {
    if (point.is_clipped) {
      const x = padding + (i / (data.length - 1)) * (width - padding * 2)
      const y = padding + ((max - point.gradient_norm) / range) * (height - padding * 2)

      ctx.beginPath()
      ctx.arc(x, y, 4, 0, Math.PI * 2)
      ctx.fillStyle = '#ef4444'
      ctx.fill()
    }
  })

  // Draw latest point indicator
  if (data.length > 0) {
    const last = data[data.length - 1]
    const x = width - padding
    const y = padding + ((max - last.gradient_norm) / range) * (height - padding * 2)

    ctx.beginPath()
    ctx.arc(x, y, 6, 0, Math.PI * 2)
    ctx.fillStyle = last.is_clipped ? '#ef4444' : '#4dd4a5'
    ctx.fill()
  }
}

// Lifecycle
onMounted(() => {
  fetchGradients()
  connectStream()
})

onBeforeUnmount(() => {
  if (eventSource) {
    eventSource.close()
  }
  stopPolling()
})
</script>

<template>
  <div class="gradient-graph-container">
    <header class="graph-header">
      <h3>Gradient Norms</h3>
      <div class="status-indicators">
        <span class="indicator" :class="{ active: isStreaming }">
          {{ isStreaming ? 'LIVE' : 'POLLING' }}
        </span>
        <span v-if="sessionStatus" class="session-badge">
          {{ sessionStatus.status }}
        </span>
      </div>
    </header>

    <div class="canvas-wrapper">
      <canvas
        ref="canvasRef"
        width="600"
        height="300"
        class="gradient-canvas"
      />
    </div>

    <footer class="graph-footer">
      <div class="metric">
        <span class="label">Latest</span>
        <span class="value" :class="{ clipped: latestGradient?.is_clipped }">
          {{ latestGradient?.gradient_norm?.toFixed(4) || '—' }}
        </span>
      </div>
      <div class="metric">
        <span class="label">Avg</span>
        <span class="value">{{ avgNorm.toFixed(4) }}</span>
      </div>
      <div class="metric">
        <span class="label">Max</span>
        <span class="value">{{ maxNorm.toFixed(4) }}</span>
      </div>
      <div class="metric">
        <span class="label">Clipped</span>
        <span class="value warning">{{ clippedCount }}</span>
      </div>
      <div class="metric">
        <span class="label">Memory</span>
        <span class="value">{{ latestGradient?.memory_usage_mb?.toFixed(0) || 0 }} MB</span>
      </div>
    </footer>

    <div v-if="error" class="error-banner">{{ error }}</div>
  </div>
</template>

<style scoped>
.gradient-graph-container {
  background: linear-gradient(135deg, #0f141b 0%, #1a1f2e 100%);
  border: 1px solid rgba(218, 108, 60, 0.2);
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(10px);
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.graph-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #f8f6f2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-indicators {
  display: flex;
  gap: 8px;
}

.indicator {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  background: #333;
  color: #666;
}

.indicator.active {
  background: rgba(77, 212, 165, 0.2);
  color: #4dd4a5;
  animation: pulse 2s infinite;
}

.session-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  background: rgba(218, 108, 60, 0.2);
  color: #da6c3c;
}

.canvas-wrapper {
  background: #0a0e14;
  border-radius: 8px;
  overflow: hidden;
}

.gradient-canvas {
  display: block;
  width: 100%;
  height: auto;
}

.graph-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.metric .label {
  font-size: 10px;
  color: #666;
  text-transform: uppercase;
}

.metric .value {
  font-size: 14px;
  font-weight: 600;
  color: #f8f6f2;
  font-family: monospace;
}

.metric .value.clipped {
  color: #ef4444;
}

.metric .value.warning {
  color: #f59e0b;
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
  50% { opacity: 0.6; }
}
</style>
