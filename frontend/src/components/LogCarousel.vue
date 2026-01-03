<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { API_BASE } from '../config'

type LogEntry = {
  id: string
  content: string
  memory_type: string
  timestamp: string
  importance?: number
  context?: Record<string, unknown>
}

const props = defineProps<{
  autoPlay?: boolean
  interval?: number
}>()

const items = ref<LogEntry[]>([])
const currentIndex = ref(0)
const isPlaying = ref(props.autoPlay ?? true)
const isHovered = ref(false)
const loading = ref(true)
let autoTimer: number | undefined
let refreshTimer: number | undefined

// Load memories from API
const loadMemories = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/memories?limit=50`)
    const data = await res.json()
    items.value = data.memories || []
    loading.value = false
  } catch (e) {
    console.error('Failed to load memories:', e)
    loading.value = false
  }
}

const displayItems = computed(() => {
  const total = items.value.length
  if (total === 0) return []

  const indices = []
  for (let i = -1; i <= 1; i++) {
    const idx = (currentIndex.value + i + total) % total
    indices.push(idx)
  }
  return indices.map(i => ({ ...items.value[i], _index: i }))
})

const currentItem = computed(() => items.value[currentIndex.value])

const typeColors: Record<string, string> = {
  episodic: '#4dd4a5',
  semantic: '#60a5fa',
  procedural: '#a78bfa',
  identity: '#fbbf24',
}

const typeLabels: Record<string, string> = {
  episodic: 'Experience',
  semantic: 'Knowledge',
  procedural: 'Skill',
  identity: 'Core Value',
}

const next = () => {
  if (items.value.length === 0) return
  currentIndex.value = (currentIndex.value + 1) % items.value.length
}

const prev = () => {
  if (items.value.length === 0) return
  currentIndex.value = (currentIndex.value - 1 + items.value.length) % items.value.length
}

const goTo = (index: number) => {
  currentIndex.value = index
}

const togglePlay = () => {
  isPlaying.value = !isPlaying.value
}

const formatTime = (ts: string) => {
  try {
    const date = new Date(ts)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return 'just now'
    if (minutes < 60) return `${minutes} min ago`
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
    if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return ts
  }
}

// Convert raw content to natural human language
const humanizeContent = (content: string, memoryType: string): string => {
  // Handle heartbeat entries
  if (content.startsWith('Heartbeat #')) {
    const cycleMatch = content.match(/Heartbeat #(\d+)/)
    const cycle = cycleMatch ? cycleMatch[1] : '?'

    // Extract key insights
    if (content.includes('Analysis:')) {
      const analysisStart = content.indexOf('Analysis:') + 9
      const analysisEnd = content.indexOf('\nDecision:') || content.length
      const analysis = content.slice(analysisStart, analysisEnd).trim()

      // Get first meaningful sentence
      const sentences = analysis.split(/[.!?]\s/).filter(s => s.length > 20)
      if (sentences.length > 0) {
        return `Cycle ${cycle}: ${sentences[0].slice(0, 150)}...`
      }
    }
    return `Completed thinking cycle ${cycle} - analyzed current state and made decisions`
  }

  // Handle test memories
  if (content.includes('Test memory:')) {
    return content.replace('Test memory:', 'System check:')
  }

  // Handle learned skills
  if (content.includes('Learned skill')) {
    return `Acquired new capability: ${content.split(':').slice(-1)[0].trim()}`
  }

  // Handle general content - make it more conversational
  const cleaned = content
    .replace(/###\s*/g, '')
    .replace(/\*\*/g, '')
    .replace(/\n+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  // Get first meaningful part
  if (cleaned.length > 200) {
    const firstPart = cleaned.slice(0, 200)
    const lastSpace = firstPart.lastIndexOf(' ')
    return firstPart.slice(0, lastSpace) + '...'
  }

  return cleaned
}

const formatContent = (content: string, memoryType: string) => {
  return humanizeContent(content, memoryType)
}

const getMemoryEmoji = (type: string): string => {
  const emojis: Record<string, string> = {
    episodic: '📝',
    semantic: '💡',
    procedural: '⚙️',
    identity: '🎯',
  }
  return emojis[type] || '📄'
}

const startAutoPlay = () => {
  if (autoTimer) clearInterval(autoTimer)
  if (isPlaying.value && !isHovered.value) {
    autoTimer = window.setInterval(next, props.interval ?? 5000)
  }
}

watch([isPlaying, isHovered], () => {
  if (isPlaying.value && !isHovered.value) {
    startAutoPlay()
  } else {
    if (autoTimer) clearInterval(autoTimer)
  }
})

watch(() => items.value.length, () => {
  if (currentIndex.value >= items.value.length) {
    currentIndex.value = 0
  }
})

onMounted(() => {
  loadMemories()
  startAutoPlay()
  // Refresh every 30 seconds
  refreshTimer = window.setInterval(loadMemories, 30000)
})

onBeforeUnmount(() => {
  if (autoTimer) clearInterval(autoTimer)
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<template>
  <div
    class="log-carousel"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <div class="carousel-header">
      <div class="carousel-title">
        <span class="title-icon">🧠</span>
        MEMORY STREAM
      </div>
      <div class="carousel-controls">
        <button class="ctrl-btn" @click="prev" title="Previous">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
        </button>
        <button class="ctrl-btn play" @click="togglePlay" :title="isPlaying ? 'Pause' : 'Play'">
          <svg v-if="isPlaying" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="4" width="4" height="16"/>
            <rect x="14" y="4" width="4" height="16"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </button>
        <button class="ctrl-btn" @click="next" title="Next">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </button>
      </div>
      <div class="carousel-counter">
        {{ items.length > 0 ? currentIndex + 1 : 0 }} / {{ items.length }}
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="carousel-loading">
      <div class="loading-spinner"></div>
      <div class="loading-text">Loading memories...</div>
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="carousel-empty">
      <div class="empty-icon">🔮</div>
      <div class="empty-text">No memories yet</div>
      <div class="empty-hint">The AI will start recording thoughts soon...</div>
    </div>

    <!-- Carousel -->
    <template v-else>
      <div class="carousel-stage">
        <TransitionGroup name="slide" tag="div" class="carousel-track">
          <div
            v-for="(item, idx) in displayItems"
            :key="item.id"
            class="carousel-card"
            :class="{
              'card-prev': idx === 0,
              'card-current': idx === 1,
              'card-next': idx === 2,
            }"
            :style="{ '--type-color': typeColors[item.memory_type] || '#888' }"
            @click="goTo(item._index)"
          >
            <div class="card-glow"></div>
            <div class="card-header">
              <span class="card-emoji">{{ getMemoryEmoji(item.memory_type) }}</span>
              <span class="card-type">{{ typeLabels[item.memory_type] || item.memory_type }}</span>
            </div>
            <div class="card-content">{{ formatContent(item.content, item.memory_type) }}</div>
            <div class="card-footer">
              <span class="card-time">{{ formatTime(item.timestamp) }}</span>
              <span v-if="item.importance" class="card-importance">
                {{ (item.importance * 100).toFixed(0) }}% important
              </span>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <div class="carousel-dots">
        <button
          v-for="(_, idx) in items.slice(0, 12)"
          :key="idx"
          class="dot"
          :class="{ active: idx === currentIndex }"
          @click="goTo(idx)"
        ></button>
        <span v-if="items.length > 12" class="dots-more">+{{ items.length - 12 }}</span>
      </div>

      <!-- Expanded view of current item -->
      <div v-if="currentItem" class="carousel-expanded">
        <div class="expanded-header">
          <span class="expanded-emoji">{{ getMemoryEmoji(currentItem.memory_type) }}</span>
          <span class="expanded-type" :style="{ background: typeColors[currentItem.memory_type] }">
            {{ typeLabels[currentItem.memory_type] || currentItem.memory_type }}
          </span>
          <span class="expanded-time">{{ formatTime(currentItem.timestamp) }}</span>
        </div>
        <div class="expanded-content">{{ humanizeContent(currentItem.content, currentItem.memory_type) }}</div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.log-carousel {
  background: linear-gradient(135deg, #0f141b 0%, #1a1f2e 100%);
  border-radius: var(--radius-lg);
  padding: 20px;
  color: #f8f6f2;
  min-height: 400px;
}

.carousel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.carousel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: rgba(248, 246, 242, 0.6);
}

.title-icon {
  font-size: 18px;
}

.carousel-controls {
  display: flex;
  gap: 8px;
}

.ctrl-btn {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(248, 246, 242, 0.2);
  background: rgba(248, 246, 242, 0.05);
  border-radius: 50%;
  color: rgba(248, 246, 242, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.ctrl-btn:hover {
  background: rgba(248, 246, 242, 0.15);
  border-color: rgba(248, 246, 242, 0.4);
  transform: scale(1.1);
}

.ctrl-btn svg {
  width: 18px;
  height: 18px;
}

.ctrl-btn.play {
  background: rgba(218, 108, 60, 0.2);
  border-color: rgba(218, 108, 60, 0.4);
}

.carousel-counter {
  font-size: 13px;
  color: rgba(248, 246, 242, 0.5);
  font-family: var(--font-mono);
}

.carousel-loading, .carousel-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(248, 246, 242, 0.1);
  border-top-color: #da6c3c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text, .empty-text {
  font-size: 14px;
  color: rgba(248, 246, 242, 0.6);
}

.empty-icon {
  font-size: 48px;
  opacity: 0.5;
}

.empty-hint {
  font-size: 12px;
  color: rgba(248, 246, 242, 0.3);
}

.carousel-stage {
  position: relative;
  height: 220px;
  perspective: 1000px;
  margin-bottom: 20px;
}

.carousel-track {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-card {
  position: absolute;
  width: 85%;
  max-width: 450px;
  padding: 20px;
  background: rgba(248, 246, 242, 0.06);
  border: 1px solid rgba(248, 246, 242, 0.12);
  border-left: 4px solid var(--type-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--type-color), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.carousel-card:hover .card-glow {
  opacity: 1;
}

.card-prev {
  transform: translateX(-55%) scale(0.85) rotateY(12deg);
  opacity: 0.4;
  z-index: 1;
}

.card-current {
  transform: translateX(0) scale(1);
  opacity: 1;
  z-index: 2;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

.card-next {
  transform: translateX(55%) scale(0.85) rotateY(-12deg);
  opacity: 0.4;
  z-index: 1;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.card-emoji {
  font-size: 20px;
}

.card-type {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--type-color);
}

.card-content {
  font-size: 14px;
  line-height: 1.6;
  color: rgba(248, 246, 242, 0.9);
  max-height: 100px;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  font-size: 12px;
  color: rgba(248, 246, 242, 0.4);
}

.card-importance {
  color: var(--type-color);
  font-weight: 600;
}

.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: rgba(248, 246, 242, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.dot.active {
  background: #da6c3c;
  transform: scale(1.3);
  box-shadow: 0 0 10px rgba(218, 108, 60, 0.5);
}

.dot:hover:not(.active) {
  background: rgba(248, 246, 242, 0.4);
}

.dots-more {
  font-size: 11px;
  color: rgba(248, 246, 242, 0.4);
  margin-left: 6px;
}

.carousel-expanded {
  background: rgba(248, 246, 242, 0.04);
  border-radius: var(--radius-md);
  padding: 18px;
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid rgba(248, 246, 242, 0.08);
}

.expanded-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.expanded-emoji {
  font-size: 22px;
}

.expanded-type {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 5px 12px;
  border-radius: 14px;
  color: #0f141b;
}

.expanded-time {
  font-size: 12px;
  color: rgba(248, 246, 242, 0.4);
  font-family: var(--font-mono);
  margin-left: auto;
}

.expanded-content {
  font-size: 14px;
  line-height: 1.7;
  color: rgba(248, 246, 242, 0.85);
}

/* Slide transitions */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.4s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-100px);
}
</style>
