import { StateCreator } from 'zustand'
import { ChatMessage, ChatPane } from '../types'

export interface ChatSlice {
  chat: Record<string, ChatPane>
  ensureChat: (nodeId: string) => ChatPane
  setChatStatus: (nodeId: string, status: ChatPane['status']) => void
  appendMsg: (nodeId: string, msg: ChatMessage) => void
  markSeeded: (nodeId: string) => void
}

export const createChatSlice: StateCreator<ChatSlice, [], [], ChatSlice> = (set, get) => ({
  chat: {},
  ensureChat: (nodeId) => {
    const s = get()
    if (!s.chat[nodeId]) {
      const pane: ChatPane = { nodeId, messages: [], status: 'idle', seeded: false }
      set({ chat: { ...s.chat, [nodeId]: pane } })
      return pane
    }
    return s.chat[nodeId]
  },
  setChatStatus: (nodeId, status) =>
    set((s) => ({
      chat: { ...s.chat, [nodeId]: { ...(s.chat[nodeId] || { nodeId, messages: [], status: 'idle', seeded: false }), status } },
    })),
  appendMsg: (nodeId, msg) =>
    set((s) => ({
      chat: {
        ...s.chat,
        [nodeId]: {
          ...(s.chat[nodeId] || { nodeId, messages: [], status: 'idle', seeded: false }),
          messages: [...(s.chat[nodeId]?.messages || []), msg],
        },
      },
    })),
  markSeeded: (nodeId) =>
    set((s) => ({
      chat: { ...s.chat, [nodeId]: { ...(s.chat[nodeId] || { nodeId, messages: [], status: 'idle', seeded: false }), seeded: true } },
    })),
})

