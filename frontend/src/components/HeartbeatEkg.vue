<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

type HeartbeatSample = {
  timestamp: string
  ok: boolean
  duration_s?: number
  stage?: string
}

const props = defineProps<{
  samples: HeartbeatSample[]
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const hoverSample = ref<HeartbeatSample | null>(null)
const hoverX = ref(0)
let animationId = 0
let phase = 0

const normalizedSamples = computed(() => {
  const values = props.samples.map((s) => s.duration_s ?? 1)
  const max = Math.max(1, ...values)
  return props.samples.map((s) => ({
    ...s,
    value: Math.min(1, (s.duration_s ?? 1) / max),
  }))
})

const draw = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = canvas.clientWidth
  const height = canvas.clientHeight
  if (canvas.width !== width) canvas.width = width
  if (canvas.height !== height) canvas.height = height

  ctx.clearRect(0, 0, width, height)
  ctx.fillStyle = '#0f141b'
  ctx.fillRect(0, 0, width, height)

  const mid = height * 0.55
  const spacing = width / Math.max(1, normalizedSamples.value.length - 1)

  ctx.beginPath()
  ctx.strokeStyle = 'rgba(220, 230, 240, 0.15)'
  ctx.lineWidth = 1
  for (let i = 0; i < 5; i += 1) {
    const y = (height / 5) * i
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
  }
  ctx.stroke()

  ctx.beginPath()
  ctx.strokeStyle = 'rgba(218, 108, 60, 0.8)'
  ctx.lineWidth = 2

  normalizedSamples.value.forEach((sample, idx) => {
    const x = idx * spacing
    const pulse = Math.sin((idx + phase) * 0.8) * 6
    const y = mid - sample.value * (height * 0.35) + pulse
    if (idx === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()

  normalizedSamples.value.forEach((sample, idx) => {
    const x = idx * spacing
    const y = mid - sample.value * (height * 0.35)
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fillStyle = sample.ok ? '#4dd4a5' : '#f87171'
    ctx.fill()
  })

  const scanX = (phase * 12) % width
  ctx.fillStyle = 'rgba(218, 108, 60, 0.2)'
  ctx.fillRect(scanX, 0, 6, height)

  phase += 0.02
  animationId = requestAnimationFrame(draw)
}

const handleMove = (event: MouseEvent) => {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const idx = Math.round((x / rect.width) * (normalizedSamples.value.length - 1))
  const sample = normalizedSamples.value[idx]
  hoverSample.value = sample || null
  hoverX.value = x
}

const handleLeave = () => {
  hoverSample.value = null
}

onMounted(() => {
  draw()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationId)
})

watch(
  () => props.samples,
  () => {
    phase = 0
  },
)
</script>

<template>
  <div class="ekg">
    <canvas ref="canvasRef" @mousemove="handleMove" @mouseleave="handleLeave"></canvas>
    <div v-if="hoverSample" class="tooltip" :style="{ left: `${hoverX}px` }">
      <div class="tooltip-title">{{ hoverSample.stage || 'MONITOR' }}</div>
      <div class="tooltip-line">{{ hoverSample.timestamp }}</div>
      <div class="tooltip-line">
        {{ hoverSample.ok ? 'OK' : 'ERROR' }} · {{ hoverSample.duration_s?.toFixed(2) || 'n/a' }}s
      </div>
    </div>
  </div>
</template>

<style scoped>
.ekg {
  position: relative;
  background: #0f141b;
  border-radius: var(--radius-md);
  padding: 12px;
  min-height: 180px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

canvas {
  width: 100%;
  height: 180px;
  display: block;
}

.tooltip {
  position: absolute;
  top: 12px;
  transform: translateX(-50%);
  background: rgba(15, 20, 27, 0.9);
  color: var(--text-inverse);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  pointer-events: none;
  border: 1px solid rgba(218, 108, 60, 0.4);
}

.tooltip-title {
  font-weight: 600;
  color: #f4c7a2;
  margin-bottom: 2px;
}

.tooltip-line {
  color: rgba(248, 246, 242, 0.8);
}
</style>
