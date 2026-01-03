<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps({
  maxMinutes: {
    type: Number,
    default: 60
  }
})

const emit = defineEmits(['rollback'])

const selectedMinutes = ref(0)

const handleRollback = () => {
  emit('rollback', selectedMinutes.value)
}
</script>

<template>
  <div class="slider-container">
    <input 
      type="range" 
      min="0" 
      :max="maxMinutes" 
      v-model.number="selectedMinutes" 
      @input="handleRollback" 
      class="slider"
    />
  </div>
</template>

<style scoped>
.slider-container {
  background-color: #0f141b;
  padding: 10px;
  border-radius: 8px;
}

.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 12px;
  background: linear-gradient(to right, #0f141b, #da6c3c);
  border-radius: 6px;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: #da6c3c;
  border-radius: 50%;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #da6c3c;
  border-radius: 50%;
  cursor: pointer;
}
</style>