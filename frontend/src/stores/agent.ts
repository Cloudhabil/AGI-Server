import { defineStore } from 'pinia'
import axios from 'axios'
import { API_BASE, API_TOKEN } from '../config'

export const useAgentStore = defineStore('agent', {
  state: () => ({ response: '' }),
  actions: {
    async send(text: string) {
      const headers = API_TOKEN ? { Authorization: `Bearer ${API_TOKEN}` } : {}
      try {
        const res = await axios.post(`${API_BASE}/chat`, { text }, { headers })
        this.response = res.data.response
      } catch (error) {
        console.error('Failed to send message:', error)
        this.response = 'Error: Could not get a response from the server.'
      }
    },
  },
})
