<script setup lang="ts">
import { ref } from 'vue'
import { useAgentStore } from '../stores/agent'

const store = useAgentStore()
const text = ref('')
const send = async () => {
  await store.send(text.value)
}
</script>

<template>
  <div class="chat-box">
    <el-input v-model="text" placeholder="Say something" />
    <el-button type="primary" @click="send">Send</el-button>
    <p v-if="store.response">Response: {{ store.response }}</p>
  </div>
</template>
