import { StateCreator } from 'zustand'
import { Edge3D, Node3D } from '../types'

export interface AgentsSlice {
  nodes: Node3D[]
  edges: Edge3D[]
  selectedNodeId: string | null
  setSelected: (id: string | null) => void
}

export const createAgentsSlice: StateCreator<AgentsSlice, [], [], AgentsSlice> = (set) => ({
  nodes: [
    { id: 'orchestrator', label: 'Orchestrator', orbitR: 0, angle: 0 },
    { id: 'agent-1', label: 'Agent 1', orbitR: 4, angle: 0 },
    { id: 'agent-2', label: 'Agent 2', orbitR: 6, angle: 1 },
  ],
  edges: [
    { id: 'e1', from: 'orchestrator', to: 'agent-1' },
    { id: 'e2', from: 'orchestrator', to: 'agent-2' },
  ],
  selectedNodeId: null,
  setSelected: (id) => set({ selectedNodeId: id }),
})

