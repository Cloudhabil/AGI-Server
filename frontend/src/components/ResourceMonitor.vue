<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { API_BASE } from '../config'

type ComputeStatus = {
  gpu: { available: boolean; name: string; memory: string }
  npu: { available: boolean }
  models: string[]
}

type ResourceData = {
  status: string
  compute: ComputeStatus
  memory: { total: number; by_type: Record<string, number> }
  control_plane: { stage: string }
  heartbeat: { paused: boolean }
}

const resources = ref<ResourceData | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
let refreshTimer: number | undefined

const loadResources = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/status`)
    resources.value = await res.json()
    error.value = null
  } catch (e) {
    error.value = 'Failed to load resources'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadResources()
  refreshTimer = window.setInterval(loadResources, 5000)
})

onBeforeUnmount(() => {
  if (refreshTimer) window.clearInterval(refreshTimer)
})
</script>

<template>
  <div class="resource-monitor">
    <div class="monitor-header">
      <div class="monitor-title">COMPUTE RESOURCES</div>
      <div class="monitor-status" :class="{ online: resources?.status === 'online' }">
        {{ resources?.status || 'offline' }}
      </div>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="resources" class="resources-grid">
      <!-- GPU Card -->
      <div class="resource-card gpu">
        <div class="resource-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="6" width="20" height="12" rx="2"/>
            <path d="M6 10h4v4H6z"/>
            <path d="M14 10h4v4h-4z"/>
          </svg>
        </div>
        <div class="resource-info">
          <div class="resource-name">GPU</div>
          <div class="resource-value" :class="{ active: resources.compute.gpu.available }">
            {{ resources.compute.gpu.available ? 'ACTIVE' : 'N/A' }}
          </div>
          <div v-if="resources.compute.gpu.available" class="resource-detail">
            {{ resources.compute.gpu.name.split(' ').slice(-3).join(' ') }}
          </div>
          <div v-if="resources.compute.gpu.memory" class="resource-memory">
            {{ resources.compute.gpu.memory }}
          </div>
        </div>
        <div class="resource-bar">
          <div class="bar-fill gpu-fill" :style="{ width: resources.compute.gpu.available ? '75%' : '0%' }"></div>
        </div>
      </div>

      <!-- NPU Card -->
      <div class="resource-card npu">
        <div class="resource-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v4m0 12v4M2 12h4m12 0h4"/>
            <path d="M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
          </svg>
        </div>
        <div class="resource-info">
          <div class="resource-name">NPU</div>
          <div class="resource-value" :class="{ active: resources.compute.npu.available }">
            {{ resources.compute.npu.available ? 'ACTIVE' : 'N/A' }}
          </div>
          <div class="resource-detail">Intel AI Boost</div>
          <div class="resource-memory">13 TOPS INT8</div>
        </div>
        <div class="resource-bar">
          <div class="bar-fill npu-fill" :style="{ width: resources.compute.npu.available ? '60%' : '0%' }"></div>
        </div>
      </div>

      <!-- CPU Card -->
      <div class="resource-card cpu">
        <div class="resource-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="4" y="4" width="16" height="16" rx="2"/>
            <path d="M9 1v3m6-3v3M9 20v3m6-3v3M1 9h3m-3 6h3M20 9h3m-3 6h3"/>
          </svg>
        </div>
        <div class="resource-info">
          <div class="resource-name">CPU</div>
          <div class="resource-value active">ACTIVE</div>
          <div class="resource-detail">Intel Core Ultra 5</div>
          <div class="resource-memory">14 Cores</div>
        </div>
        <div class="resource-bar">
          <div class="bar-fill cpu-fill" style="width: 45%"></div>
        </div>
      </div>
    </div>

    <!-- Models Section -->
    <div v-if="resources?.compute.models.length" class="models-section">
      <div class="models-title">LOADED MODELS</div>
      <div class="models-grid">
        <div v-for="model in resources.compute.models" :key="model" class="model-chip">
          <span class="model-dot"></span>
          {{ model.replace(':latest', '') }}
        </div>
      </div>
    </div>

    <!-- Stage Indicator -->
    <div v-if="resources" class="stage-section">
      <div class="stage-label">CONTROL PLANE</div>
      <div class="stage-value">{{ resources.control_plane.stage }}</div>
      <div class="heartbeat-status" :class="{ paused: resources.heartbeat.paused }">
        {{ resources.heartbeat.paused ? 'PAUSED' : 'HEARTBEAT ACTIVE' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.resource-monitor {
  background: linear-gradient(135deg, #0f141b 0%, #1a1f2e 100%);
  border-radius: var(--radius-lg);
  padding: 20px;
  color: #f8f6f2;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.monitor-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: rgba(248, 246, 242, 0.6);
}

.monitor-status {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(248, 246, 242, 0.1);
  text-transform: uppercase;
}

.monitor-status.online {
  background: rgba(77, 212, 165, 0.2);
  color: #4dd4a5;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.resource-card {
  background: rgba(248, 246, 242, 0.05);
  border-radius: var(--radius-md);
  padding: 16px;
  border: 1px solid rgba(248, 246, 242, 0.08);
  transition: all 0.3s ease;
}

.resource-card:hover {
  border-color: rgba(218, 108, 60, 0.4);
  transform: translateY(-2px);
}

.resource-icon {
  width: 32px;
  height: 32px;
  margin-bottom: 12px;
  color: rgba(248, 246, 242, 0.5);
}

.resource-icon svg {
  width: 100%;
  height: 100%;
}

.gpu .resource-icon { color: #4dd4a5; }
.npu .resource-icon { color: #a78bfa; }
.cpu .resource-icon { color: #60a5fa; }

.resource-name {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: rgba(248, 246, 242, 0.5);
  margin-bottom: 4px;
}

.resource-value {
  font-size: 14px;
  font-weight: 700;
  color: rgba(248, 246, 242, 0.3);
  margin-bottom: 8px;
}

.resource-value.active {
  color: #4dd4a5;
}

.resource-detail {
  font-size: 11px;
  color: rgba(248, 246, 242, 0.6);
  margin-bottom: 2px;
}

.resource-memory {
  font-size: 12px;
  font-weight: 600;
  color: rgba(248, 246, 242, 0.8);
}

.resource-bar {
  height: 4px;
  background: rgba(248, 246, 242, 0.1);
  border-radius: 2px;
  margin-top: 12px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

.gpu-fill { background: linear-gradient(90deg, #4dd4a5, #22c55e); }
.npu-fill { background: linear-gradient(90deg, #a78bfa, #8b5cf6); }
.cpu-fill { background: linear-gradient(90deg, #60a5fa, #3b82f6); }

.models-section {
  border-top: 1px solid rgba(248, 246, 242, 0.1);
  padding-top: 16px;
  margin-bottom: 16px;
}

.models-title {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: rgba(248, 246, 242, 0.5);
  margin-bottom: 12px;
}

.models-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.model-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 6px 12px;
  background: rgba(248, 246, 242, 0.08);
  border-radius: 20px;
  color: rgba(248, 246, 242, 0.8);
}

.model-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4dd4a5;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.stage-section {
  border-top: 1px solid rgba(248, 246, 242, 0.1);
  padding-top: 16px;
  text-align: center;
}

.stage-label {
  font-size: 10px;
  letter-spacing: 0.12em;
  color: rgba(248, 246, 242, 0.4);
  margin-bottom: 4px;
}

.stage-value {
  font-size: 24px;
  font-weight: 700;
  color: #da6c3c;
  margin-bottom: 8px;
}

.heartbeat-status {
  font-size: 11px;
  font-weight: 600;
  color: #4dd4a5;
}

.heartbeat-status.paused {
  color: #f87171;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: rgba(248, 246, 242, 0.5);
}

.error {
  color: #f87171;
}
</style>
