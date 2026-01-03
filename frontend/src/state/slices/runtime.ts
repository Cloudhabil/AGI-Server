import { StateCreator } from 'zustand'
import { NodeRuntime } from '../types'

export interface RuntimeSlice {
  runtime: Record<string, NodeRuntime>
  setRuntime: (nodeId: string, rt: Partial<NodeRuntime>) => void
}

export const createRuntimeSlice: StateCreator<RuntimeSlice, [], [], RuntimeSlice> = (set) => ({
  runtime: { orchestrator: { status: 'running' }, 'agent-1': { status: 'stopped' }, 'agent-2': { status: 'stopped' } },
  setRuntime: (nodeId, rt) =>
    set((s) => ({ runtime: { ...(s as any).runtime, [nodeId]: { ...((s as any).runtime?.[nodeId] || { status: 'stopped' }), ...rt } } })),
})

