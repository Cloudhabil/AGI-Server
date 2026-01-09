<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiDenseStateDelete, apiDenseStateGet } from '../utils/api'
import type { DenseStatePost } from '../types/api'
import { renderMarkdown } from '../utils/markdown'
import { useSystemStore } from '../stores/system'

const route = useRoute()
const router = useRouter()
const system = useSystemStore()

const post = ref<DenseStatePost | null>(null)
const loading = ref(false)
const deleting = ref(false)
const error = ref('')

const rendered = computed(() => renderMarkdown(post.value?.content || post.value?.markdown || ''))

const loadPost = async () => {
  const id = route.params.id
  if (!id) {
    error.value = 'Missing post id'
    return
  }
  loading.value = true
  try {
    post.value = await apiDenseStateGet(id as string)
    error.value = ''
  } catch (err: any) {
    error.value = err?.message || 'Failed to load post'
    post.value = null
  } finally {
    loading.value = false
  }
}

const deletePost = async () => {
  if (!post.value?.id) return
  deleting.value = true
  try {
    await apiDenseStateDelete(post.value.id)
    router.push('/feed')
  } catch (err: any) {
    error.value = err?.message || 'Delete failed'
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  if (!system.profile && !system.loadingProfile) system.initProfile()
  loadPost()
})
</script>

<template>
  <div class="detail-shell">
    <div class="header">
      <div>
        <div class="eyebrow">Dense State Post</div>
        <h1>{{ post?.title || 'Untitled post' }}</h1>
        <div class="meta">
          <span>Author: {{ post?.author || 'unknown' }}</span>
          <span>Updated: {{ post?.updated_at || post?.created_at || 'n/a' }}</span>
          <span v-if="post?.deleted" class="chip danger">deleted</span>
        </div>
      </div>
      <div class="actions">
        <button class="ghost" @click="router.push('/feed')">Back to feed</button>
        <button class="ghost" @click="router.push(`/editor/${post?.id ?? ''}`)" :disabled="!post?.id">Edit</button>
        <button class="danger" @click="deletePost" :disabled="deleting || !post?.id">
          {{ deleting ? 'Deleting…' : 'Delete' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="muted">Loading post…</div>
    <div v-else-if="!post" class="muted">Post not found.</div>
    <div v-else class="body">
      <p class="summary" v-if="post.summary">{{ post.summary }}</p>
      <div class="markdown" v-html="rendered"></div>
    </div>

    <div v-if="error" class="error">
      {{ error }} · Trace {{ system.traceId }}
    </div>
  </div>
</template>

<style scoped>
.detail-shell {
  padding: clamp(14px, 2vw, 22px);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
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

.meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 13px;
  color: var(--text-muted);
}

.chip {
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid currentColor;
}

.danger {
  color: #ff8a6c;
  border-color: rgba(255, 138, 108, 0.5);
  background: transparent;
  cursor: pointer;
  border-radius: 10px;
  padding: 8px 12px;
}

.ghost {
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: transparent;
  color: inherit;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}

.body {
  background: var(--surface-card);
  border-radius: 14px;
  padding: 16px;
  box-shadow: var(--shadow-soft);
}

.summary {
  font-weight: 600;
  margin-bottom: 10px;
}

.markdown :deep(h1),
.markdown :deep(h2),
.markdown :deep(h3) {
  margin: 12px 0 6px;
}

.markdown :deep(p) {
  margin: 8px 0;
}

.markdown :deep(code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: var(--font-mono);
}

.markdown :deep(ul) {
  margin-left: 18px;
}

.muted {
  color: var(--text-muted);
}

.error {
  padding: 10px;
  background: rgba(218, 108, 60, 0.12);
  border: 1px solid rgba(218, 108, 60, 0.6);
  border-radius: 10px;
  color: #8b3416;
}
</style>
