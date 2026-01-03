<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { API_BASE } from '@/config'

interface Adapter {
  id: string
  name: string
  base_model: string
  rank: number
  alpha: number
  is_active: boolean
  version: number
  created_at: string
  path: string
}

// State
const adapters = ref<Adapter[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const activating = ref<string | null>(null)

// Form state for new adapter
const showCreateForm = ref(false)
const newAdapter = ref({
  id: '',
  name: '',
  base_model: 'qwen3:latest',
  rank: 16,
  alpha: 32
})

// Computed
const activeAdapter = computed(() => adapters.value.find(a => a.is_active))
const sortedAdapters = computed(() =>
  [...adapters.value].sort((a, b) => {
    if (a.is_active) return -1
    if (b.is_active) return 1
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })
)

// Fetch adapters
async function fetchAdapters() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/adapters`)
    const data = await res.json()
    adapters.value = data.adapters || []
  } catch (e) {
    error.value = `Failed to fetch adapters: ${e}`
  } finally {
    loading.value = false
  }
}

// Create adapter
async function createAdapter() {
  if (!newAdapter.value.name) {
    error.value = 'Name is required'
    return
  }

  try {
    const res = await fetch(`${API_BASE}/api/adapters`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: newAdapter.value.id || `adapter-${Date.now()}`,
        name: newAdapter.value.name,
        base_model: newAdapter.value.base_model,
        rank: newAdapter.value.rank,
        alpha: newAdapter.value.alpha,
        is_active: false,
        version: 1,
        path: ''
      })
    })

    const data = await res.json()
    adapters.value.push(data)
    showCreateForm.value = false
    newAdapter.value = { id: '', name: '', base_model: 'qwen3:latest', rank: 16, alpha: 32 }
  } catch (e) {
    error.value = `Failed to create adapter: ${e}`
  }
}

// Activate adapter
async function activateAdapter(adapterId: string) {
  activating.value = adapterId
  try {
    const res = await fetch(`${API_BASE}/api/adapters/${adapterId}/activate`, {
      method: 'POST'
    })
    const data = await res.json()

    if (data.activated) {
      // Update local state
      adapters.value.forEach(a => {
        a.is_active = a.id === adapterId
      })
    }
  } catch (e) {
    error.value = `Failed to activate adapter: ${e}`
  } finally {
    activating.value = null
  }
}

// Deactivate adapter
async function deactivateAdapter(adapterId: string) {
  try {
    const res = await fetch(`${API_BASE}/api/adapters/${adapterId}/deactivate`, {
      method: 'POST'
    })
    const data = await res.json()

    if (data.deactivated) {
      const adapter = adapters.value.find(a => a.id === adapterId)
      if (adapter) adapter.is_active = false
    }
  } catch (e) {
    error.value = `Failed to deactivate adapter: ${e}`
  }
}

// Delete adapter
async function deleteAdapter(adapterId: string) {
  if (!confirm('Are you sure you want to delete this adapter?')) return

  try {
    await fetch(`${API_BASE}/api/adapters/${adapterId}`, {
      method: 'DELETE'
    })
    adapters.value = adapters.value.filter(a => a.id !== adapterId)
  } catch (e) {
    error.value = `Failed to delete adapter: ${e}`
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  fetchAdapters()
})
</script>

<template>
  <div class="adapter-stack-container">
    <header class="adapter-header">
      <h3>LoRA Adapters</h3>
      <button class="add-btn" @click="showCreateForm = !showCreateForm">
        {{ showCreateForm ? '×' : '+' }}
      </button>
    </header>

    <!-- Active adapter indicator -->
    <div v-if="activeAdapter" class="active-adapter-banner">
      <span class="active-dot"></span>
      <span class="active-name">{{ activeAdapter.name }}</span>
      <span class="active-model">{{ activeAdapter.base_model }}</span>
    </div>

    <!-- Create form -->
    <div v-if="showCreateForm" class="create-form">
      <div class="form-row">
        <div class="form-group">
          <label>Name</label>
          <input v-model="newAdapter.name" type="text" placeholder="my-adapter" />
        </div>
        <div class="form-group">
          <label>Base Model</label>
          <select v-model="newAdapter.base_model">
            <option value="qwen3:latest">qwen3:latest</option>
            <option value="deepseek-r1:latest">deepseek-r1:latest</option>
            <option value="codegemma:latest">codegemma:latest</option>
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Rank</label>
          <input v-model.number="newAdapter.rank" type="number" />
        </div>
        <div class="form-group">
          <label>Alpha</label>
          <input v-model.number="newAdapter.alpha" type="number" />
        </div>
      </div>
      <button class="create-btn" @click="createAdapter">Create Adapter</button>
    </div>

    <div v-if="loading" class="loading">Loading adapters...</div>

    <!-- Adapter list -->
    <div v-else class="adapter-list">
      <div v-if="sortedAdapters.length === 0" class="empty-state">
        No adapters registered yet
      </div>
      <div
        v-for="adapter in sortedAdapters"
        :key="adapter.id"
        class="adapter-card"
        :class="{ active: adapter.is_active }"
      >
        <div class="adapter-main">
          <div class="adapter-info">
            <div class="adapter-name">
              {{ adapter.name }}
              <span v-if="adapter.is_active" class="active-badge">ACTIVE</span>
            </div>
            <div class="adapter-meta">
              <span class="meta-item">{{ adapter.base_model }}</span>
              <span class="meta-item">r={{ adapter.rank }}</span>
              <span class="meta-item">α={{ adapter.alpha }}</span>
              <span class="meta-item">v{{ adapter.version }}</span>
            </div>
          </div>
          <div class="adapter-actions">
            <button
              v-if="!adapter.is_active"
              class="action-btn activate"
              @click="activateAdapter(adapter.id)"
              :disabled="activating === adapter.id"
            >
              {{ activating === adapter.id ? '...' : 'Activate' }}
            </button>
            <button
              v-else
              class="action-btn deactivate"
              @click="deactivateAdapter(adapter.id)"
            >
              Deactivate
            </button>
            <button
              class="action-btn delete"
              @click="deleteAdapter(adapter.id)"
              :disabled="adapter.is_active"
            >
              ×
            </button>
          </div>
        </div>
        <div class="adapter-footer">
          <span class="created-date">Created {{ formatDate(adapter.created_at) }}</span>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>
  </div>
</template>

<style scoped>
.adapter-stack-container {
  background: linear-gradient(135deg, #0f141b 0%, #1a1f2e 100%);
  border: 1px solid rgba(218, 108, 60, 0.2);
  border-radius: 12px;
  padding: 16px;
}

.adapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.adapter-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #f8f6f2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.add-btn {
  width: 28px;
  height: 28px;
  background: transparent;
  border: 1px solid #da6c3c;
  border-radius: 6px;
  color: #da6c3c;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-btn:hover {
  background: rgba(218, 108, 60, 0.1);
}

.active-adapter-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(77, 212, 165, 0.1);
  border: 1px solid rgba(77, 212, 165, 0.3);
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 12px;
}

.active-dot {
  width: 8px;
  height: 8px;
  background: #4dd4a5;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.active-name {
  color: #4dd4a5;
  font-weight: 600;
}

.active-model {
  color: #888;
}

.create-form {
  background: #0a0e14;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 10px;
  color: #666;
  text-transform: uppercase;
}

.form-group input,
.form-group select {
  background: #1a202c;
  border: 1px solid #333;
  border-radius: 4px;
  padding: 6px 10px;
  color: #f8f6f2;
  font-size: 12px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #da6c3c;
}

.create-btn {
  width: 100%;
  padding: 8px;
  background: #da6c3c;
  border: none;
  border-radius: 6px;
  color: #0f141b;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
}

.create-btn:hover {
  background: #e07d4d;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.adapter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  padding: 24px;
  color: #555;
}

.adapter-card {
  background: #0a0e14;
  border-radius: 8px;
  padding: 12px;
  border-left: 3px solid #333;
  transition: border-color 0.2s;
}

.adapter-card.active {
  border-left-color: #4dd4a5;
}

.adapter-card:hover {
  border-left-color: #da6c3c;
}

.adapter-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.adapter-info {
  flex: 1;
}

.adapter-name {
  font-weight: 600;
  color: #f8f6f2;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.active-badge {
  padding: 2px 6px;
  background: rgba(77, 212, 165, 0.2);
  color: #4dd4a5;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 600;
}

.adapter-meta {
  display: flex;
  gap: 12px;
  margin-top: 4px;
}

.meta-item {
  font-size: 11px;
  color: #666;
}

.adapter-actions {
  display: flex;
  gap: 6px;
}

.action-btn {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  border: 1px solid #333;
  background: transparent;
  color: #888;
  transition: all 0.2s;
}

.action-btn:hover:not(:disabled) {
  background: #1a202c;
  color: #f8f6f2;
}

.action-btn.activate {
  border-color: #4dd4a5;
  color: #4dd4a5;
}

.action-btn.activate:hover {
  background: rgba(77, 212, 165, 0.1);
}

.action-btn.deactivate {
  border-color: #f59e0b;
  color: #f59e0b;
}

.action-btn.delete {
  border-color: #ef4444;
  color: #ef4444;
  padding: 4px 8px;
}

.action-btn.delete:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.adapter-footer {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.created-date {
  font-size: 10px;
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
