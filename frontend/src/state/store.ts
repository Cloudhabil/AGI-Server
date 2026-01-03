import { create } from 'zustand'
import { createAgentsSlice, AgentsSlice } from './slices/agents'
import { createChatSlice, ChatSlice } from './slices/chat'
import { createUploadsSlice, UploadsSlice } from './slices/uploads'
import { createRuntimeSlice, RuntimeSlice } from './slices/runtime'
import { createConnectionSlice, ConnectionSlice } from './slices/connection'
import { createUiSlice, UiSlice } from './slices/ui'
import { createToastsSlice, ToastsSlice } from './slices/toasts'
export * from './types'

export type State = AgentsSlice & ChatSlice & UploadsSlice & RuntimeSlice & ConnectionSlice & UiSlice & ToastsSlice

export const useStore = create<State>()((...a) => ({
  ...createAgentsSlice(...a),
  ...createChatSlice(...a),
  ...createUploadsSlice(...a),
  ...createRuntimeSlice(...a),
  ...createConnectionSlice(...a),
  ...createUiSlice(...a),
  ...createToastsSlice(...a),
}))

