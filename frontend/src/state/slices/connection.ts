import { StateCreator } from 'zustand'

export interface ConnectionSlice {
  wsConnectionStatus: 'connecting' | 'open' | 'closed'
  setWsConnectionStatus: (status: 'connecting' | 'open' | 'closed') => void
}

export const createConnectionSlice: StateCreator<ConnectionSlice, [], [], ConnectionSlice> = (set) => ({
  wsConnectionStatus: 'connecting',
  setWsConnectionStatus: (status) => set({ wsConnectionStatus: status }),
})

