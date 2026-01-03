<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { API_BASE } from '../config'

type ThoughtStep = {
  model: string
  role: string
  thought: string
  duration_ms: number
}

type ReasoningTrace = {
  id: string
  timestamp: string
  cycle: number
  duration_s: number
  analysis: ThoughtStep[]
  decision: ThoughtStep[]
  observations?: Record<string, any>
  action?: Record<string, any>
}

const traces = ref<ReasoningTrace[]>([])
const isStreaming = ref(false)
const loading = ref(true)
const expandedTrace = ref<string | null>(null)
let eventSource: EventSource | null = null
let refreshTimer: number | undefined

const modelColors: Record<string, string> = {
  'DeepSeek-R1': '#60a5fa',
  'Qwen3': '#a78bfa',
  'CodeGemma': '#4dd4a5',
  'Unknown': '#6b7280',
}

const modelEmojis: Record<string, string> = {
  'DeepSeek-R1': '🔍',  // Analytical
  'Qwen3': '✨',        // Creative
  'CodeGemma': '⚡',    // Fast
  'Unknown': '🤖',
}

const roleLabels: Record<string, string> = {
  'analytical': 'ANALYZING',
  'creative': 'CREATING',
  'fast': 'CHECKING',
}

const loadTraces = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/reasoning/latest`)
    const data = await res.json()
    traces.value = data.traces || []
    loading.value = false
  } catch (e) {
    console.error('Failed to load reasoning traces:', e)
    loading.value = false
  }
}

const connectStream = () => {
  if (eventSource) eventSource.close()

  try {
    eventSource = new EventSource(`${API_BASE}/api/reasoning/stream`)
    isStreaming.value = true

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.analysis || data.decision) {
          // Add new trace to the top
          const newTrace: ReasoningTrace = {
            id: data.id,
            timestamp: data.timestamp,
            cycle: data.cycle,
            duration_s: 0,
            analysis: data.analysis || [],
            decision: data.decision || [],
          }
          traces.value = [newTrace, ...traces.value.filter(t => t.id !== data.id)].slice(0, 15)
        }
      } catch (e) {
        console.error('Stream parse error:', e)
      }
    }

    eventSource.onerror = () => {
      isStreaming.value = false
      setTimeout(connectStream, 5000)
    }
  } catch (e) {
    console.error('Failed to connect stream:', e)
    isStreaming.value = false
  }
}

const formatTime = (ts: string) => {
  try {
    const date = new Date(ts)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)

    if (minutes < 1) return 'just now'
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ts
  }
}

const truncateThought = (thought: string, max: number = 150) => {
  if (thought.length <= max) return thought
  return thought.slice(0, max) + '...'
}

const toggleExpand = (id: string) => {
  expandedTrace.value = expandedTrace.value === id ? null : id
}

const getTotalSteps = (trace: ReasoningTrace) => {
  return (trace.analysis?.length || 0) + (trace.decision?.length || 0)
}

const getModelsUsed = (trace: ReasoningTrace) => {
  const models = new Set<string>()
  trace.analysis?.forEach(s => models.add(s.model))
  trace.decision?.forEach(s => models.add(s.model))
  return Array.from(models)
}

onMounted(() => {
  loadTraces()
  connectStream()
  refreshTimer = window.setInterval(loadTraces, 15000)
})

onBeforeUnmount(() => {
  if (eventSource) eventSource.close()
  if (refreshTimer) window.clearInterval(refreshTimer)
})
</script>

<template>
  <div class="live-thoughts">
    <div class="thoughts-header">
      <div class="thoughts-title">
        <span class="pulse-dot" :class="{ active: isStreaming }"></span>
        MODEL REASONING CHAINS
      </div>
      <div class="thoughts-status">
        {{ isStreaming ? 'Live' : 'Reconnecting...' }}
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="thoughts-loading">
      <div class="loading-spinner"></div>
      <div>Loading reasoning traces...</div>
    </div>

    <!-- Empty -->
    <div v-else-if="traces.length === 0" class="thoughts-empty">
      <div class="empty-icon">🧠</div>
      <div>Waiting for model reasoning...</div>
      <div class="empty-hint">Reasoning traces appear when thinking is enabled in the heartbeat loop</div>
    </div>

    <!-- Reasoning Traces -->
    <div v-else class="traces-stream">
      <TransitionGroup name="trace">
        <div
          v-for="trace in traces"
          :key="trace.id"
          class="trace-card"
          :class="{ expanded: expandedTrace === trace.id }"
        >
          <!-- Trace Header -->
          <div class="trace-header" @click="toggleExpand(trace.id)">
            <div class="trace-meta">
              <span class="trace-cycle">Cycle {{ trace.cycle }}</span>
              <span class="trace-steps">{{ getTotalSteps(trace) }} steps</span>
              <span class="trace-time">{{ formatTime(trace.timestamp) }}</span>
            </div>
            <div class="trace-models">
              <span
                v-for="model in getModelsUsed(trace)"
                :key="model"
                class="model-badge"
                :style="{ background: modelColors[model] + '30', color: modelColors[model] }"
              >
                {{ modelEmojis[model] }} {{ model }}
              </span>
            </div>
            <div class="expand-icon">{{ expandedTrace === trace.id ? '▼' : '▶' }}</div>
          </div>

          <!-- Collapsed Preview -->
          <div v-if="expandedTrace !== trace.id" class="trace-preview">
            <div v-if="trace.analysis?.length" class="preview-section">
              <span class="preview-label">Analysis:</span>
              {{ truncateThought(trace.analysis[trace.analysis.length - 1]?.thought || '', 100) }}
            </div>
            <div v-if="trace.decision?.length" class="preview-section">
              <span class="preview-label">Decision:</span>
              {{ truncateThought(trace.decision[trace.decision.length - 1]?.thought || '', 100) }}
            </div>
          </div>

          <!-- Expanded Chain -->
          <div v-if="expandedTrace === trace.id" class="trace-chain">
            <!-- Analysis Phase -->
            <div v-if="trace.analysis?.length" class="chain-phase">
              <div class="phase-header">
                <span class="phase-icon">🔍</span>
                <span class="phase-title">ORIENT (Analysis)</span>
              </div>
              <div class="chain-steps">
                <div
                  v-for="(step, idx) in trace.analysis"
                  :key="'a-' + idx"
                  class="chain-step"
                  :style="{ borderLeftColor: modelColors[step.model] }"
                >
                  <div class="step-header">
                    <span class="step-model" :style="{ color: modelColors[step.model] }">
                      {{ modelEmojis[step.model] }} {{ step.model }}
                    </span>
                    <span class="step-role">{{ roleLabels[step.role] || step.role }}</span>
                    <span class="step-duration">{{ step.duration_ms?.toFixed(0) }}ms</span>
                  </div>
                  <div class="step-thought">{{ step.thought }}</div>
                </div>
              </div>
            </div>

            <!-- Decision Phase -->
            <div v-if="trace.decision?.length" class="chain-phase">
              <div class="phase-header">
                <span class="phase-icon">⚡</span>
                <span class="phase-title">DECIDE (Reasoning)</span>
              </div>
              <div class="chain-steps">
                <div
                  v-for="(step, idx) in trace.decision"
                  :key="'d-' + idx"
                  class="chain-step"
                  :style="{ borderLeftColor: modelColors[step.model] }"
                >
                  <div class="step-header">
                    <span class="step-model" :style="{ color: modelColors[step.model] }">
                      {{ modelEmojis[step.model] }} {{ step.model }}
                    </span>
                    <span class="step-role">{{ roleLabels[step.role] || step.role }}</span>
                    <span class="step-duration">{{ step.duration_ms?.toFixed(0) }}ms</span>
                  </div>
                  <div class="step-thought">{{ step.thought }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<style scoped>
.live-thoughts {
  background: linear-gradient(180deg, #0f141b 0%, #161b22 100%);
  border-radius: var(--radius-lg, 12px);
  padding: 20px;
  color: #f8f6f2;
  min-height: 400px;
}

.thoughts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.thoughts-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: rgba(248, 246, 242, 0.6);
}

.pulse-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(248, 246, 242, 0.3);
  transition: all 0.3s ease;
}

.pulse-dot.active {
  background: #4dd4a5;
  box-shadow: 0 0 12px rgba(77, 212, 165, 0.6);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
}

.thoughts-status {
  font-size: 11px;
  color: rgba(248, 246, 242, 0.4);
}

.thoughts-loading, .thoughts-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 16px;
  color: rgba(248, 246, 242, 0.5);
  font-size: 14px;
}

.empty-hint {
  font-size: 11px;
  color: rgba(248, 246, 242, 0.3);
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(248, 246, 242, 0.1);
  border-top-color: #da6c3c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 40px;
  opacity: 0.4;
}

.traces-stream {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.traces-stream::-webkit-scrollbar {
  width: 6px;
}

.traces-stream::-webkit-scrollbar-track {
  background: rgba(248, 246, 242, 0.05);
  border-radius: 3px;
}

.traces-stream::-webkit-scrollbar-thumb {
  background: rgba(248, 246, 242, 0.15);
  border-radius: 3px;
}

.trace-card {
  background: rgba(248, 246, 242, 0.03);
  border: 1px solid rgba(248, 246, 242, 0.08);
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.trace-card:hover {
  background: rgba(248, 246, 242, 0.05);
  border-color: rgba(248, 246, 242, 0.12);
}

.trace-card.expanded {
  border-color: rgba(218, 108, 60, 0.4);
}

.trace-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  cursor: pointer;
  flex-wrap: wrap;
}

.trace-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.trace-cycle {
  font-size: 12px;
  font-weight: 700;
  color: #da6c3c;
}

.trace-steps {
  font-size: 10px;
  padding: 2px 8px;
  background: rgba(248, 246, 242, 0.1);
  border-radius: 10px;
  color: rgba(248, 246, 242, 0.6);
}

.trace-time {
  font-size: 10px;
  color: rgba(248, 246, 242, 0.35);
}

.trace-models {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-left: auto;
}

.model-badge {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.expand-icon {
  font-size: 10px;
  color: rgba(248, 246, 242, 0.4);
  transition: transform 0.2s;
}

.trace-preview {
  padding: 0 16px 14px;
}

.preview-section {
  font-size: 12px;
  line-height: 1.5;
  color: rgba(248, 246, 242, 0.6);
  margin-bottom: 8px;
}

.preview-section:last-child {
  margin-bottom: 0;
}

.preview-label {
  font-weight: 600;
  color: rgba(248, 246, 242, 0.8);
}

.trace-chain {
  padding: 0 16px 16px;
}

.chain-phase {
  margin-bottom: 20px;
}

.chain-phase:last-child {
  margin-bottom: 0;
}

.phase-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(248, 246, 242, 0.1);
}

.phase-icon {
  font-size: 16px;
}

.phase-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: rgba(248, 246, 242, 0.5);
}

.chain-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chain-step {
  background: rgba(248, 246, 242, 0.02);
  border-left: 3px solid;
  border-radius: 0 8px 8px 0;
  padding: 12px 14px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.step-model {
  font-size: 12px;
  font-weight: 700;
}

.step-role {
  font-size: 9px;
  padding: 2px 6px;
  background: rgba(248, 246, 242, 0.08);
  border-radius: 4px;
  color: rgba(248, 246, 242, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.step-duration {
  font-size: 10px;
  color: rgba(248, 246, 242, 0.3);
  margin-left: auto;
  font-family: monospace;
}

.step-thought {
  font-size: 13px;
  line-height: 1.6;
  color: rgba(248, 246, 242, 0.85);
  white-space: pre-wrap;
  word-break: break-word;
}

/* Transitions */
.trace-enter-active {
  transition: all 0.4s ease-out;
}

.trace-leave-active {
  transition: all 0.3s ease-in;
}

.trace-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}

.trace-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.trace-move {
  transition: transform 0.3s ease;
}
</style>
