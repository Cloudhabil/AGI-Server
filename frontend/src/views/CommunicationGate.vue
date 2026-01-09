<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SkillTree3D from '../components/SkillTree3D.vue'
import { apiDenseStateList } from '../utils/api'
import { useSystemStore } from '../stores/system'
import type { DenseStatePost } from '../types/api'

const router = useRouter()
const system = useSystemStore()

const previewPosts = ref<DenseStatePost[]>([])
const previewError = ref('')
const loadingPreview = ref(false)

const animationIntensity = computed(() => system.profile?.animation_intensity ?? 0.6)
const visualDensity = computed(() => system.profile?.visual_density ?? 0.6)
const prefersCli = computed(() => system.profile?.prefers_cli ?? false)
const shouldShowPortal = computed(() => system.webglSupported && !prefersCli.value)
const fallbackReason = computed(() => {
  if (!system.webglSupported) return 'WebGL unavailable on this device'
  if (prefersCli.value) return 'Profile prefers CLI-first mode'
  return 'Fallback requested'
})

const loadPreview = async () => {
  loadingPreview.value = true
  try {
    const res = await apiDenseStateList({ limit: 4 })
    previewPosts.value = res.items || []
    previewError.value = ''
  } catch (err: any) {
    previewError.value = err?.message || 'Failed to load feed preview'
  } finally {
    loadingPreview.value = false
  }
}

const goFeed = () => router.push('/feed')
const goEditor = () => router.push('/editor')
const goPost = (id?: string | number) => {
  if (!id) return
  router.push(`/posts/${id}`)
}

onMounted(() => {
  system.refreshWebgl()
  if (!system.profile && !system.loadingProfile) {
    system.initProfile()
  }
  loadPreview()
})
</script>

<template>
  <div class="gate-shell" :class="shouldShowPortal ? 'mode-portal' : 'mode-2d'">
    <section v-if="shouldShowPortal" class="portal">
      <div class="portal-scene">
        <SkillTree3D
          v-if="system.webglSupported"
          :animation-intensity="animationIntensity"
          :visual-density="visualDensity"
          :theme="system.theme"
        />
        <div class="portal-overlay">
          <div class="portal-chip">Profile v{{ system.profile?.profile_version ?? '—' }}</div>
          <h1>Communication Gate</h1>
          <p class="lede">
            Adaptive portal driven by your profile. WebGL enabled for a rich 3D entry, with fast access to the Dense State Blog.
          </p>
          <div class="meta-grid">
            <div class="meta">
              <div class="label">Verbosity</div>
              <div class="value">{{ system.profile?.verbosity ?? 'auto' }}</div>
            </div>
            <div class="meta">
              <div class="label">Visual density</div>
              <div class="value">{{ visualDensity.toFixed(2) }}</div>
            </div>
            <div class="meta">
              <div class="label">Animation</div>
              <div class="value">{{ animationIntensity.toFixed(2) }}</div>
            </div>
            <div class="meta">
              <div class="label">Theme</div>
              <div class="value">{{ system.theme }}</div>
            </div>
          </div>
          <div class="actions">
            <button class="primary" @click="goFeed">Enter Feed</button>
            <button class="ghost" @click="goEditor">New Post</button>
            <button class="ghost" @click="router.push('/feed')">Dense State 2D</button>
          </div>
        </div>
      </div>

      <div class="preview">
        <div class="preview-head">
          <div>
            <div class="eyebrow">Dense State Blog</div>
            <h3>Latest posts</h3>
          </div>
          <div class="preview-actions">
            <button class="ghost" @click="goFeed">Open Feed</button>
            <button class="ghost" @click="goEditor">Create</button>
          </div>
        </div>
        <div v-if="loadingPreview" class="muted">Loading feed…</div>
        <div v-else-if="previewPosts.length === 0" class="muted">
          No posts yet. Start by creating one.
        </div>
        <div class="preview-grid" v-else>
          <article v-for="post in previewPosts" :key="post.id" class="preview-card" @click="goPost(post.id)">
            <div class="card-title">
              {{ post.title || 'Untitled post' }}
              <span v-if="post.deleted" class="chip danger">deleted</span>
            </div>
            <div class="card-body">
              {{ post.summary || post.content || post.markdown || 'No content' }}
            </div>
            <div class="card-meta">
              <span>{{ post.author || 'unknown' }}</span>
              <span>{{ post.updated_at || post.created_at || '' }}</span>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section v-else class="fallback">
      <div class="fallback-head">
        <div class="eyebrow">2D Mode</div>
        <h1>Dense State Blog</h1>
        <p class="lede">
          {{ fallbackReason }}. You are in the full 2D experience with CRUD, markdown, and trace-ready calls.
        </p>
        <div class="actions">
          <button class="primary" @click="goEditor">Create Post</button>
          <button class="ghost" @click="goFeed">Open Feed</button>
        </div>
      </div>
      <div class="preview">
        <div class="preview-head">
          <h3>Recent entries</h3>
          <button class="ghost" @click="goFeed">See all</button>
        </div>
        <div v-if="loadingPreview" class="muted">Loading feed…</div>
        <div v-else-if="previewPosts.length === 0" class="muted">
          No posts available yet.
        </div>
        <div class="preview-grid" v-else>
          <article v-for="post in previewPosts" :key="post.id" class="preview-card" @click="goPost(post.id)">
            <div class="card-title">
              {{ post.title || 'Untitled post' }}
              <span v-if="post.deleted" class="chip danger">deleted</span>
            </div>
            <div class="card-body">
              {{ post.summary || post.content || post.markdown || 'No content' }}
            </div>
            <div class="card-meta">
              <span>{{ post.author || 'unknown' }}</span>
              <span>{{ post.updated_at || post.created_at || '' }}</span>
            </div>
          </article>
        </div>
      </div>
    </section>

    <div v-if="previewError || system.profileError" class="error-box">
      {{ previewError || system.profileError }} · Trace {{ system.traceId }}
    </div>
  </div>
</template>

<style scoped>
.gate-shell {
  padding: clamp(14px, 2vw, 22px);
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.portal-scene {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.35);
  background: radial-gradient(circle at 20% 20%, rgba(218, 108, 60, 0.2), transparent 40%), #0b0e12;
}

.portal-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(120deg, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0.12) 60%, transparent 90%);
  color: #f8f6f2;
  padding: clamp(16px, 3vw, 32px);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.portal-overlay * {
  pointer-events: auto;
}

.portal-chip {
  align-self: flex-start;
  padding: 6px 10px;
  background: rgba(248, 246, 242, 0.16);
  border-radius: 999px;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.lede {
  max-width: 640px;
  color: rgba(248, 246, 242, 0.85);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.meta {
  background: rgba(248, 246, 242, 0.1);
  border-radius: 12px;
  padding: 10px;
}

.label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.7;
}

.value {
  font-weight: 700;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.primary {
  border: none;
  background: var(--c-ember);
  color: #0f141b;
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 700;
}

.ghost {
  border: 1px solid rgba(255, 255, 255, 0.24);
  background: transparent;
  color: inherit;
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 700;
}

:global([data-theme='light']) .ghost {
  border-color: rgba(0, 0, 0, 0.16);
}

.preview {
  background: var(--surface-card);
  border-radius: 16px;
  padding: 16px;
  box-shadow: var(--shadow-soft);
}

.preview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.eyebrow {
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.preview-card {
  background: rgba(15, 20, 27, 0.85);
  color: #f8f6f2;
  border-radius: 12px;
  padding: 12px;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

:global([data-theme='light']) .preview-card {
  background: #f8f6f2;
  color: #0f172a;
  border: 1px solid rgba(16, 21, 28, 0.08);
}

.card-title {
  font-weight: 700;
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: space-between;
}

.card-body {
  margin-top: 6px;
  color: var(--text-muted);
  font-size: 14px;
}

.card-meta {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  opacity: 0.8;
}

.chip {
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
  letter-spacing: 0.04em;
  border: 1px solid currentColor;
}

.chip.danger {
  color: #ff8a6c;
  border-color: rgba(255, 138, 108, 0.4);
}

.fallback {
  background: var(--surface-card);
  border-radius: 16px;
  padding: clamp(16px, 3vw, 26px);
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.fallback-head h1 {
  margin: 4px 0;
}

.muted {
  color: var(--text-muted);
}

.error-box {
  padding: 10px 12px;
  border: 1px solid rgba(218, 108, 60, 0.4);
  color: #8b3416;
  background: rgba(218, 108, 60, 0.08);
  border-radius: 12px;
}

@media (max-width: 960px) {
  .portal-overlay {
    position: static;
    background: linear-gradient(180deg, rgba(0, 0, 0, 0.72), rgba(0, 0, 0, 0.8));
  }
}
</style>
