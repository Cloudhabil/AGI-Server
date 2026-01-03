<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { API_BASE } from '@/config'

interface Checkpoint {
  id: string
  name: string
  step: number
  val_loss: number
  created_at: string
  path: string
  is_active: boolean
}

// State
const checkpoints = ref<Checkpoint[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const savingCheckpoint = ref(false)
const newCheckpointName = ref('')

// Computed
const activeCheckpoint = computed(() => checkpoints.value.find(c => c.is_active))
const sortedCheckpoints = computed(() =>
  [...checkpoints.value].sort((a, b) => b.step - a.step)
)

// Fetch checkpoints
async function fetchCheckpoints() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`${API_BASE}/api/training/checkpoints`)
    const data = await res.json()
    checkpoints.value = data.checkpoints || []
  } catch (e) {
    error.value = `Failed to fetch checkpoints: ${e}`
  } finally {
    loading.value = false
  }
}

// Save new checkpoint
async function saveCheckpoint() {
  if (!newCheckpointName.value.trim()) {
    newCheckpointName.value = `checkpoint-${Date.now()}`
  }

  savingCheckpoint.value = true
  try {
    const res = await fetch(`${API_BASE}/api/training/checkpoints?name=${encodeURIComponent(newCheckpointName.value)}`, {
      method: 'POST'
    })
    const data = await res.json()
    checkpoints.value.push(data)
    newCheckpointName.value = ''
  } catch (e) {
    error.value = `Failed to save checkpoint: ${e}`
  } finally {
    savingCheckpoint.value = false
  }
}

// Load checkpoint
async function loadCheckpoint(checkpointId: string) {
  try {
    const res = await fetch(`${API_BASE}/api/training/checkpoints/${checkpointId}/load`, {
      method: 'POST'
    })
    const data = await res.json()
    if (data.loaded) {
      // Update local state
      checkpoints.value.forEach(c => {
        c.is_active = c.id === checkpointId
      })
    }
  } catch (e) {
    error.value = `Failed to load checkpoint: ${e}`
  }
}

// Format date
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchCheckpoints()
})
</script>

<template>
  <div class="checkpoint-container">
    <header class="checkpoint-header">
      <h3>Checkpoints</h3>
      <button
        class="refresh-btn"
        @click="fetchCheckpoints"
        :disabled="loading"
      >
        ↻
      </button>
    </header>

    <!-- Save new checkpoint -->
    <div class="save-checkpoint">
      <input
        v-model="newCheckpointName"
        type="text"
        placeholder="Checkpoint name..."
        class="checkpoint-input"
        @keyup.enter="saveCheckpoint"
      />
      <button
        class="save-btn"
        @click="saveCheckpoint"
        :disabled="savingCheckpoint"
      >
        {{ savingCheckpoint ? 'Saving...' : 'Save' }}
      </button>
    </div>

    <!-- Active checkpoint indicator -->
    <div v-if="activeCheckpoint" class="active-indicator">
      <span class="active-dot"></span>
      Active: {{ activeCheckpoint.name }} (step {{ activeCheckpoint.step }})
    </div>

    <!-- Checkpoint timeline -->
    <div class="checkpoint-timeline">
      <div v-if="loading" class="loading">Loading checkpoints...</div>
      <div v-else-if="sortedCheckpoints.length === 0" class="empty">
        No checkpoints saved yet
      </div>
      <div
        v-for="checkpoint in sortedCheckpoints"
        :key="checkpoint.id"
        class="checkpoint-item"
        :class="{ active: checkpoint.is_active }"
      >
        <div class="checkpoint-marker">
          <div class="marker-dot" :class="{ active: checkpoint.is_active }"></div>
          <div class="marker-line"></div>
        </div>
        <div class="checkpoint-content">
          <div class="checkpoint-name">{{ checkpoint.name }}</div>
          <div class="checkpoint-meta">
            <span class="step">Step {{ checkpoint.step }}</span>
            <span class="loss">Loss: {{ checkpoint.val_loss.toFixed(4) }}</span>
            <span class="time">{{ formatDate(checkpoint.created_at) }}</span>
          </div>
        </div>
        <button
          class="load-btn"
          @click="loadCheckpoint(checkpoint.id)"
          :disabled="checkpoint.is_active"
        >
          {{ checkpoint.is_active ? 'Active' : 'Load' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>
  </div>
</template>

<style scoped>
.checkpoint-container {
  background: linear-gradient(135deg, #0f141b 0%, #1a1f2e 100%);
  border: 1px solid rgba(218, 108, 60, 0.2);
  border-radius: 12px;
  padding: 16px;
}

.checkpoint-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.checkpoint-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #f8f6f2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.refresh-btn {
  background: transparent;
  border: 1px solid #333;
  color: #888;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:hover {
  background: #1a202c;
  color: #f8f6f2;
}

.save-checkpoint {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.checkpoint-input {
  flex: 1;
  background: #0a0e14;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 8px 12px;
  color: #f8f6f2;
  font-size: 13px;
}

.checkpoint-input:focus {
  outline: none;
  border-color: #da6c3c;
}

.save-btn {
  background: #da6c3c;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  color: #0f141b;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}

.save-btn:hover {
  background: #e07d4d;
}

.save-btn:disabled {
  background: #666;
  cursor: not-allowed;
}

.active-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(77, 212, 165, 0.1);
  border: 1px solid rgba(77, 212, 165, 0.3);
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 12px;
  color: #4dd4a5;
}

.active-dot {
  width: 8px;
  height: 8px;
  background: #4dd4a5;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.checkpoint-timeline {
  max-height: 300px;
  overflow-y: auto;
}

.loading, .empty {
  text-align: center;
  padding: 24px;
  color: #666;
  font-size: 13px;
}

.checkpoint-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.checkpoint-item:last-child {
  border-bottom: none;
}

.checkpoint-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 16px;
}

.marker-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #333;
  border: 2px solid #555;
}

.marker-dot.active {
  background: #4dd4a5;
  border-color: #4dd4a5;
}

.marker-line {
  width: 2px;
  flex: 1;
  min-height: 20px;
  background: #333;
}

.checkpoint-content {
  flex: 1;
}

.checkpoint-name {
  font-weight: 600;
  color: #f8f6f2;
  font-size: 13px;
  margin-bottom: 4px;
}

.checkpoint-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #666;
}

.checkpoint-meta .step {
  color: #da6c3c;
}

.load-btn {
  background: transparent;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 6px 12px;
  color: #888;
  font-size: 11px;
  cursor: pointer;
}

.load-btn:hover:not(:disabled) {
  background: #1a202c;
  color: #f8f6f2;
  border-color: #da6c3c;
}

.load-btn:disabled {
  background: rgba(77, 212, 165, 0.1);
  border-color: rgba(77, 212, 165, 0.3);
  color: #4dd4a5;
  cursor: default;
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
