<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue'
import { API_BASE } from '../config'

const props = defineProps({
  originalResponse: {
    type: String,
    required: true
  },
  visible: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits<{
  (e: 'submit', corrected: string): void,
  (e: 'close'): void
}>()

const correctedText = ref('')

const handleClose = () => {
  emit('close')
}

const handleSubmit = () => {
  emit('submit', correctedText.value)
}
</script>

<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal">
      <div class="modal-header">
        <h2>Correct AI Response</h2>
        <button @click="handleClose">X</button>
      </div>
      <div class="diff-view">
        <div class="diff-left">
          <textarea readonly :value="originalResponse" rows="10" placeholder="Original Response"></textarea>
        </div>
        <div class="diff-right">
          <textarea v-model="correctedText" rows="10" placeholder="Corrected Response"></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button @click="handleSubmit" class="accent-button">Submit</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background-color: #0f141b;
  color: #f8f6f2;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 1000px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-footer {
  margin-top: 20px;
  text-align: right;
}

.diff-view {
  display: flex;
  flex-direction: row;
  gap: 10px;
}

.diff-left, .diff-right {
  flex: 1;
}

textarea {
  width: 100%;
  height: 100%;
  background-color: #1e262e;
  color: #f8f6f2;
  border: none;
  padding: 10px;
  font-family: monospace;
  resize: none;
}

textarea::placeholder {
  color: #6a737d;
}

.accent-button {
  background-color: #da6c3c;
  color: #0f141b;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 4px;
}
</style>