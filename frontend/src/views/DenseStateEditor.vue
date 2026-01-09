<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiDenseStateCreate, apiDenseStateDelete, apiDenseStateGet, apiDenseStateUpdate } from '../utils/api'
import { renderMarkdown } from '../utils/markdown'
import { useSystemStore } from '../stores/system'

const route = useRoute()
const router = useRouter()
const system = useSystemStore()

const title = ref('')
const summary = ref('')
const content = ref('')
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const error = ref('')

const editingId = computed(() => route.params.id as string | undefined)
const previewHtml = computed(() => renderMarkdown(content.value))

const loadExisting = async () => {
  if (!editingId.value) return
  loading.value = true
  try {
    const data = await apiDenseStateGet(editingId.value)
    title.value = data.title || ''
    summary.value = data.summary || ''
    content.value = data.content || data.markdown || ''
    error.value = ''
  } catch (err: any) {
    error.value = err?.message || 'Failed to load post'
  } finally {
    loading.value = false
  }
}

const save = async () => {
  if (saving.value) return
  saving.value = true
  error.value = ''
  try {
    const payload = {
      title: title.value,
      summary: summary.value,
      content: content.value,
      markdown: content.value,
    }
    const result = editingId.value
      ? await apiDenseStateUpdate(editingId.value, payload)
      : await apiDenseStateCreate(payload)
    const targetId = result?.id ?? editingId.value
    if (targetId) router.push(`/posts/${targetId}`)
  } catch (err: any) {
    error.value = err?.message || 'Save failed'
  } finally {
    saving.value = false
  }
}

const deletePost = async () => {
  if (!editingId.value) return
  deleting.value = true
  try {
    await apiDenseStateDelete(editingId.value)
    router.push('/feed')
  } catch (err: any) {
    error.value = err?.message || 'Delete failed'
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  if (!system.profile && !system.loadingProfile) system.initProfile()
  loadExisting()
})
</script>

<template>
  <div class="editor-shell">
    <header class="editor-head">
      <div>
        <div class="eyebrow">Dense State Blog</div>
        <h1>{{ editingId ? 'Edit Post' : 'New Post' }}</h1>
      </div>
      <div class="actions">
        <button class="ghost" @click="router.push('/feed')">Back to feed</button>
        <button class="danger" v-if="editingId" :disabled="deleting" @click="deletePost">
          {{ deleting ? 'Deleting…' : 'Delete' }}
        </button>
        <button class="primary" :disabled="saving" @click="save">
          {{ saving ? 'Saving…' : 'Save' }}
        </button>
      </div>
    </header>

    <div v-if="loading" class="muted">Loading…</div>

    <div class="form-grid">
      <label>
        Title
        <input v-model="title" placeholder="Enter a clear headline" />
      </label>
      <label>
        Summary
        <input v-model="summary" placeholder="Optional synopsis" />
      </label>
    </div>

    <div class="editor-grid">
      <div class="input-col">
        <div class="label-row">
          <label>Markdown</label>
          <span class="muted">Trace: {{ system.traceId }}</span>
        </div>
        <textarea v-model="content" rows="16" placeholder="Write your dense-state story in markdown…" />
      </div>
      <div class="preview-col">
        <div class="label-row">
          <label>Preview</label>
          <span class="muted">Live</span>
        </div>
        <div class="preview" v-html="previewHtml"></div>
      </div>
    </div>

    <div v-if="error" class="error">
      {{ error }} · Trace {{ system.traceId }}
    </div>
  </div>
</template>

<style scoped>
.editor-shell {
  padding: clamp(14px, 2vw, 22px);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.editor-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.eyebrow {
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-weight: 600;
}

input,
textarea {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(16, 21, 28, 0.12);
  font-family: var(--font-body);
}

.editor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 12px;
}

.preview {
  min-height: 200px;
  border: 1px solid rgba(16, 21, 28, 0.12);
  border-radius: 10px;
  padding: 12px;
  background: var(--surface-card);
}

.preview :deep(h1),
.preview :deep(h2),
.preview :deep(h3) {
  margin: 12px 0 6px;
}

.preview :deep(p) {
  margin: 8px 0;
}

.preview :deep(code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: var(--font-mono);
}

.preview :deep(ul) {
  margin-left: 18px;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.muted {
  color: var(--text-muted);
}

.primary {
  border: none;
  background: var(--c-ember);
  color: #0f141b;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 700;
}

.ghost {
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: transparent;
  color: inherit;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}

.danger {
  border: 1px solid rgba(255, 138, 108, 0.5);
  background: transparent;
  color: #ff8a6c;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}

.error {
  padding: 10px;
  background: rgba(218, 108, 60, 0.12);
  border: 1px solid rgba(218, 108, 60, 0.6);
  border-radius: 10px;
  color: #8b3416;
}
</style>
