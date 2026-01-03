<script setup lang="ts">
type TimelineItem = {
  content: string
  timestamp: string
}

defineProps<{
  items: TimelineItem[]
}>()
</script>

<template>
  <div class="timeline">
    <div class="timeline-header">
      <span>Skill Timeline</span>
      <span class="timeline-sub">Newest first</span>
    </div>
    <div v-if="items.length === 0" class="timeline-empty">No learned skills yet.</div>
    <div v-for="item in items" :key="item.timestamp + item.content" class="timeline-row">
      <div class="dot"></div>
      <div class="timeline-body">
        <div class="timeline-text">{{ item.content }}</div>
        <div class="timeline-time">{{ item.timestamp }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline {
  background: var(--surface-card);
  border-radius: var(--radius-md);
  padding: 14px;
  box-shadow: var(--shadow-soft);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 10px;
}

.timeline-sub {
  color: var(--text-muted);
  font-weight: 400;
}

.timeline-row {
  display: grid;
  grid-template-columns: 14px 1fr;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed rgba(16, 21, 28, 0.12);
}

.timeline-row:last-child {
  border-bottom: none;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--c-ember);
  margin-top: 4px;
}

.timeline-text {
  font-size: 12px;
  color: var(--text-primary);
}

.timeline-time {
  font-size: 11px;
  color: var(--text-muted);
}

.timeline-empty {
  font-size: 12px;
  color: var(--text-muted);
}
</style>
