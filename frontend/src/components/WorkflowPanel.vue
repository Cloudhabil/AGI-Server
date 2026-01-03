<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { API_BASE } from '../config'

type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'paused' | 'waiting_user'
type WorkflowStatus = 'draft' | 'queued' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'

interface Task {
  id: string
  name: string
  description: string
  status: TaskStatus
  requires_approval: boolean
  error?: string
}

interface Workflow {
  id: string
  name: string
  description: string
  status: WorkflowStatus
  tasks: Task[]
  progress: { total: number; completed: number; percent: number }
  created_at: string
}

const workflows = ref<Workflow[]>([])
const selectedWorkflow = ref<Workflow | null>(null)
const loading = ref(true)
const showCreateModal = ref(false)
const newGoal = ref('')
const suggestions = ref<any[]>([])
let refreshTimer: number | undefined

const statusColors: Record<string, string> = {
  pending: '#64748b',
  queued: '#3b82f6',
  running: '#22c55e',
  paused: '#f59e0b',
  completed: '#10b981',
  failed: '#ef4444',
  cancelled: '#6b7280',
  waiting_user: '#a855f7',
}

const statusIcons: Record<string, string> = {
  pending: '...',
  queued: '~',
  running: '>',
  paused: '||',
  completed: 'v',
  failed: 'x',
  cancelled: '-',
  waiting_user: '?',
}

const loadWorkflows = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/workflows`)
    const data = await res.json()
    workflows.value = data.workflows || []
    loading.value = false
  } catch (e) {
    console.error('Failed to load workflows:', e)
    loading.value = false
  }
}

const createWorkflow = async () => {
  if (!newGoal.value.trim()) return

  try {
    const res = await fetch(`${API_BASE}/api/workflows`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal: newGoal.value }),
    })
    const data = await res.json()
    if (data.workflow) {
      workflows.value.unshift(data.workflow)
      showCreateModal.value = false
      newGoal.value = ''
    }
  } catch (e) {
    console.error('Failed to create workflow:', e)
  }
}

const executeWorkflow = async (id: string) => {
  try {
    await fetch(`${API_BASE}/api/workflows/${id}/execute`, { method: 'POST' })
    await loadWorkflows()
  } catch (e) {
    console.error('Failed to execute workflow:', e)
  }
}

const pauseWorkflow = async (id: string) => {
  try {
    await fetch(`${API_BASE}/api/workflows/${id}/pause`, { method: 'POST' })
    await loadWorkflows()
  } catch (e) {
    console.error('Failed to pause workflow:', e)
  }
}

const resumeWorkflow = async (id: string) => {
  try {
    await fetch(`${API_BASE}/api/workflows/${id}/resume`, { method: 'POST' })
    await loadWorkflows()
  } catch (e) {
    console.error('Failed to resume workflow:', e)
  }
}

const cancelWorkflow = async (id: string) => {
  try {
    await fetch(`${API_BASE}/api/workflows/${id}/cancel`, { method: 'POST' })
    await loadWorkflows()
  } catch (e) {
    console.error('Failed to cancel workflow:', e)
  }
}

const approveTask = async (workflowId: string, taskId: string) => {
  try {
    await fetch(`${API_BASE}/api/workflows/${workflowId}/tasks/${taskId}/approve`, { method: 'POST' })
    await loadWorkflows()
  } catch (e) {
    console.error('Failed to approve task:', e)
  }
}

const rejectTask = async (workflowId: string, taskId: string) => {
  try {
    await fetch(`${API_BASE}/api/workflows/${workflowId}/tasks/${taskId}/reject`, { method: 'POST' })
    await loadWorkflows()
  } catch (e) {
    console.error('Failed to reject task:', e)
  }
}

const retryTask = async (workflowId: string, taskId: string) => {
  try {
    await fetch(`${API_BASE}/api/workflows/${workflowId}/tasks/${taskId}/retry`, { method: 'POST' })
    await loadWorkflows()
  } catch (e) {
    console.error('Failed to retry task:', e)
  }
}

const getAutocomplete = async (id: string) => {
  try {
    const res = await fetch(`${API_BASE}/api/workflows/${id}/autocomplete`)
    const data = await res.json()
    suggestions.value = data.suggestions || []
  } catch (e) {
    console.error('Failed to get suggestions:', e)
  }
}

const selectWorkflow = async (wf: Workflow) => {
  selectedWorkflow.value = wf
  await getAutocomplete(wf.id)
}

const activeWorkflows = computed(() =>
  workflows.value.filter(w => ['queued', 'running', 'paused'].includes(w.status))
)

const completedWorkflows = computed(() =>
  workflows.value.filter(w => ['completed', 'failed', 'cancelled'].includes(w.status))
)

onMounted(() => {
  loadWorkflows()
  refreshTimer = window.setInterval(loadWorkflows, 10000)
})

onBeforeUnmount(() => {
  if (refreshTimer) window.clearInterval(refreshTimer)
})
</script>

<template>
  <div class="workflow-panel">
    <div class="panel-header">
      <div class="panel-title">
        <span class="pulse-dot active"></span>
        TASK WORKFLOWS
      </div>
      <button class="btn-create" @click="showCreateModal = true">+ New</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading">Loading workflows...</div>

    <!-- Empty State -->
    <div v-else-if="workflows.length === 0" class="empty-state">
      <div class="empty-icon">~</div>
      <div>No workflows yet</div>
      <button class="btn-primary" @click="showCreateModal = true">Create First Workflow</button>
    </div>

    <!-- Workflow List -->
    <div v-else class="workflow-grid">
      <!-- Active Workflows -->
      <div v-if="activeWorkflows.length > 0" class="workflow-section">
        <div class="section-title">ACTIVE</div>
        <div
          v-for="wf in activeWorkflows"
          :key="wf.id"
          class="workflow-card"
          :class="{ selected: selectedWorkflow?.id === wf.id }"
          @click="selectWorkflow(wf)"
        >
          <div class="wf-header">
            <span class="wf-status" :style="{ color: statusColors[wf.status] }">
              {{ statusIcons[wf.status] }}
            </span>
            <span class="wf-name">{{ wf.name.slice(0, 40) }}</span>
          </div>
          <div class="wf-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: wf.progress.percent + '%' }"></div>
            </div>
            <span class="progress-text">{{ wf.progress.completed }}/{{ wf.progress.total }}</span>
          </div>
          <div class="wf-actions">
            <button v-if="wf.status === 'queued'" @click.stop="executeWorkflow(wf.id)" title="Execute">|></button>
            <button v-if="wf.status === 'running'" @click.stop="pauseWorkflow(wf.id)" title="Pause">||</button>
            <button v-if="wf.status === 'paused'" @click.stop="resumeWorkflow(wf.id)" title="Resume">|></button>
            <button @click.stop="cancelWorkflow(wf.id)" title="Cancel" class="btn-danger">x</button>
          </div>
        </div>
      </div>

      <!-- Selected Workflow Details -->
      <div v-if="selectedWorkflow" class="workflow-details">
        <div class="details-header">
          <h3>{{ selectedWorkflow.name }}</h3>
          <span class="status-badge" :style="{ background: statusColors[selectedWorkflow.status] }">
            {{ selectedWorkflow.status }}
          </span>
        </div>

        <!-- Tasks -->
        <div class="tasks-list">
          <div
            v-for="task in selectedWorkflow.tasks"
            :key="task.id"
            class="task-item"
            :class="task.status"
          >
            <span class="task-status" :style="{ color: statusColors[task.status] }">
              {{ statusIcons[task.status] }}
            </span>
            <div class="task-info">
              <div class="task-name">{{ task.name }}</div>
              <div v-if="task.error" class="task-error">{{ task.error }}</div>
            </div>
            <div class="task-actions">
              <template v-if="task.status === 'waiting_user'">
                <button @click="approveTask(selectedWorkflow!.id, task.id)" class="btn-approve">Approve</button>
                <button @click="rejectTask(selectedWorkflow!.id, task.id)" class="btn-reject">Reject</button>
              </template>
              <button v-if="task.status === 'failed'" @click="retryTask(selectedWorkflow!.id, task.id)">Retry</button>
            </div>
          </div>
        </div>

        <!-- AI Suggestions -->
        <div v-if="suggestions.length > 0" class="suggestions">
          <div class="suggestions-title">AI Suggestions:</div>
          <div v-for="(s, idx) in suggestions" :key="idx" class="suggestion-item">
            <span class="suggestion-action">{{ s.action }}:</span>
            {{ s.description }}
          </div>
        </div>
      </div>

      <!-- Completed Workflows (collapsed) -->
      <div v-if="completedWorkflows.length > 0" class="workflow-section completed">
        <div class="section-title">HISTORY ({{ completedWorkflows.length }})</div>
        <div
          v-for="wf in completedWorkflows.slice(0, 5)"
          :key="wf.id"
          class="workflow-card mini"
        >
          <span class="wf-status" :style="{ color: statusColors[wf.status] }">
            {{ statusIcons[wf.status] }}
          </span>
          <span class="wf-name">{{ wf.name.slice(0, 30) }}</span>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal" @click.stop>
        <h3>Create Workflow</h3>
        <p>Describe your goal and the AI will decompose it into tasks:</p>
        <textarea
          v-model="newGoal"
          placeholder="e.g., Deploy new version to production with tests"
          rows="4"
        ></textarea>
        <div class="modal-actions">
          <button @click="showCreateModal = false">Cancel</button>
          <button class="btn-primary" @click="createWorkflow">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workflow-panel {
  background: linear-gradient(135deg, #0f141b 0%, #1a1f2e 100%);
  border-radius: var(--radius-lg, 12px);
  padding: 20px;
  color: #f8f6f2;
  min-height: 400px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: rgba(248, 246, 242, 0.6);
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(248, 246, 242, 0.3);
}

.pulse-dot.active {
  background: #4dd4a5;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.btn-create {
  padding: 6px 14px;
  background: rgba(218, 108, 60, 0.2);
  border: 1px solid #da6c3c;
  border-radius: 6px;
  color: #da6c3c;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-create:hover {
  background: rgba(218, 108, 60, 0.3);
}

.loading, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 16px;
  color: rgba(248, 246, 242, 0.5);
}

.empty-icon {
  font-size: 40px;
  opacity: 0.4;
}

.btn-primary {
  padding: 10px 20px;
  background: #da6c3c;
  border: none;
  border-radius: 6px;
  color: #f8f6f2;
  font-weight: 600;
  cursor: pointer;
}

.workflow-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-title {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: rgba(248, 246, 242, 0.4);
}

.workflow-card {
  background: rgba(248, 246, 242, 0.05);
  border: 1px solid rgba(248, 246, 242, 0.1);
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.workflow-card:hover, .workflow-card.selected {
  border-color: #da6c3c;
  background: rgba(218, 108, 60, 0.1);
}

.workflow-card.mini {
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.wf-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.wf-status {
  font-family: monospace;
  font-size: 14px;
  font-weight: 700;
}

.wf-name {
  font-size: 13px;
  color: rgba(248, 246, 242, 0.9);
}

.wf-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: rgba(248, 246, 242, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #da6c3c, #4dd4a5);
  transition: width 0.3s;
}

.progress-text {
  font-size: 11px;
  color: rgba(248, 246, 242, 0.5);
}

.wf-actions {
  display: flex;
  gap: 8px;
}

.wf-actions button {
  padding: 4px 10px;
  background: rgba(248, 246, 242, 0.1);
  border: none;
  border-radius: 4px;
  color: rgba(248, 246, 242, 0.8);
  font-size: 11px;
  cursor: pointer;
  font-family: monospace;
}

.wf-actions button:hover {
  background: rgba(248, 246, 242, 0.2);
}

.wf-actions .btn-danger {
  color: #ef4444;
}

.workflow-details {
  background: rgba(248, 246, 242, 0.03);
  border-radius: 8px;
  padding: 16px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.details-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: rgba(248, 246, 242, 0.05);
  border-radius: 6px;
}

.task-item.waiting_user {
  border-left: 3px solid #a855f7;
}

.task-item.failed {
  border-left: 3px solid #ef4444;
}

.task-status {
  font-family: monospace;
  font-weight: 700;
}

.task-info {
  flex: 1;
}

.task-name {
  font-size: 12px;
  color: rgba(248, 246, 242, 0.9);
}

.task-error {
  font-size: 11px;
  color: #ef4444;
  margin-top: 4px;
}

.task-actions {
  display: flex;
  gap: 6px;
}

.task-actions button {
  padding: 4px 10px;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
}

.btn-approve {
  background: rgba(77, 212, 165, 0.2);
  color: #4dd4a5;
}

.btn-reject {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.suggestions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(248, 246, 242, 0.1);
}

.suggestions-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(248, 246, 242, 0.5);
  margin-bottom: 8px;
}

.suggestion-item {
  font-size: 12px;
  color: rgba(248, 246, 242, 0.7);
  padding: 6px 0;
}

.suggestion-action {
  color: #da6c3c;
  font-weight: 600;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #1a1f2e;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
}

.modal h3 {
  margin: 0 0 8px 0;
  color: #f8f6f2;
}

.modal p {
  color: rgba(248, 246, 242, 0.6);
  font-size: 13px;
  margin-bottom: 16px;
}

.modal textarea {
  width: 100%;
  padding: 12px;
  background: rgba(248, 246, 242, 0.05);
  border: 1px solid rgba(248, 246, 242, 0.1);
  border-radius: 8px;
  color: #f8f6f2;
  font-size: 13px;
  resize: vertical;
}

.modal textarea:focus {
  outline: none;
  border-color: #da6c3c;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.modal-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.modal-actions button:first-child {
  background: rgba(248, 246, 242, 0.1);
  color: rgba(248, 246, 242, 0.8);
}
</style>
