<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { apiDenseStateList } from '../utils/api'
import type { DenseStatePost } from '../types/api'
import { useSystemStore } from '../stores/system'

const router = useRouter()
const system = useSystemStore()

const posts = ref<DenseStatePost[]>([])
const loading = ref(false)
const error = ref('')
const limit = ref(10)
const offset = ref(0)
const total = ref(0)
const includeDeleted = ref(false)

const page = computed(() => Math.floor(offset.value / limit.value) + 1)
const totalPages = computed(() => Math.max(1, Math.ceil((total.value || 0) / limit.value)))

const loadPosts = async () => {
  loading.value = true
  try {
    const res = await apiDenseStateList({ limit: limit.value, offset: offset.value, includeDeleted: includeDeleted.value })
    posts.value = res.items || []
    total.value = res.total || posts.value.length
    error.value = ''
  } catch (err: any) {
    error.value = err?.message || 'Failed to load posts'
    posts.value = []
  } finally {
    loading.value = false
  }
}

watch([limit, offset, includeDeleted], loadPosts, { immediate: true })

onMounted(() => {
  if (!system.profile && !system.loadingProfile) system.initProfile()
})

const nextPage = () => {
  if (page.value >= totalPages.value) return
  offset.value += limit.value
}

const prevPage = () => {
  offset.value = Math.max(0, offset.value - limit.value)
}

const goEditor = () => router.push('/editor')
const openPost = (id?: string | number) => {
  if (!id) return
  router.push(`/posts/${id}`)
}

const formatDate = (value?: string) => {
  if (!value) return ''
  try {
    return new Date(value).toLocaleString()
  } catch {
    return value
  }
}
</script>

<template>
  <div class="feed-shell">
    <header class="feed-head">
      <div>
        <div class="eyebrow">Dense State Blog</div>
        <h1>Feed</h1>
      </div>
      <div class="head-actions">
        <label class="toggle">
          <input v-model="includeDeleted" type="checkbox" />
          <span>Include deleted</span>
        </label>
        <button class="ghost" @click="loadPosts" :disabled="loading">Refresh</button>
        <button class="primary" @click="goEditor">Create</button>
      </div>
    </header>

    <div class="controls">
      <label>
        Page size
        <select v-model.number="limit">
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>
      </label>
      <div class="pager">
        <button class="ghost" :disabled="page === 1 || loading" @click="prevPage">Prev</button>
        <span>Page {{ page }} / {{ totalPages }}</span>
        <button class="ghost" :disabled="page === totalPages || loading" @click="nextPage">Next</button>
      </div>
      <div class="muted">Trace: {{ system.traceId }}</div>
    </div>

    <div v-if="loading" class="muted">Loading posts…</div>
    <div v-else-if="posts.length === 0" class="muted">
      No posts found.
    </div>

    <div class="grid">
      <article v-for="post in posts" :key="post.id" class="card" @click="openPost(post.id)">
        <div class="title-row">
          <div class="title">{{ post.title || 'Untitled post' }}</div>
          <span v-if="post.deleted" class="chip danger">deleted</span>
        </div>
        <p class="body">
          {{ post.summary || post.content || post.markdown || 'No content' }}
        </p>
        <div class="meta">
          <span>{{ post.author || 'unknown author' }}</span>
          <span>{{ formatDate(post.updated_at || post.created_at) }}</span>
        </div>
      </article>
    </div>

    <div v-if="error" class="error">
      {{ error }} · Trace {{ system.traceId }}
    </div>
  </div>
</template>

<style scoped>
.feed-shell {
  padding: clamp(14px, 2vw, 22px);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feed-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.head-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.eyebrow {
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.controls select {
  margin-left: 8px;
}

.pager {
  display: flex;
  gap: 8px;
  align-items: center;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.card {
  background: var(--surface-card);
  border-radius: 12px;
  padding: 12px;
  box-shadow: var(--shadow-soft);
  border: 1px solid rgba(16, 21, 28, 0.08);
  cursor: pointer;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.title {
  font-weight: 700;
}

.body {
  margin: 6px 0;
  color: var(--text-muted);
}

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-muted);
}

.chip {
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
  letter-spacing: 0.04em;
  border: 1px solid currentColor;
}

.danger {
  color: #ff8a6c;
  border-color: rgba(255, 138, 108, 0.4);
}

.ghost {
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: transparent;
  color: inherit;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
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

.toggle {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  font-size: 14px;
}

.muted {
  color: var(--text-muted);
}

.error {
  margin-top: 10px;
  padding: 10px;
  background: rgba(218, 108, 60, 0.12);
  border: 1px solid rgba(218, 108, 60, 0.6);
  border-radius: 10px;
  color: #8b3416;
}
</style>
