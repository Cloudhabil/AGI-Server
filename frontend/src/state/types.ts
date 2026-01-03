export type Node3D = { id: string; label: string; orbitR: number; angle: number; y?: number }
export type Edge3D = { id: string; from: string; to: string }

export type UploadItem = { id: string; name: string; progress: number }

export type ChatMessage = { id: string; role: 'user' | 'assistant' | 'system'; text: string; ts: number }
export type ChatPane = {
  nodeId: string
  messages: ChatMessage[]
  status: 'idle' | 'connecting' | 'open' | 'error' | 'closed'
  seeded: boolean
}

export type NodeStatus = 'stopped' | 'starting' | 'running' | 'stopping' | 'error'
export type NodeRuntime = { status: NodeStatus }

