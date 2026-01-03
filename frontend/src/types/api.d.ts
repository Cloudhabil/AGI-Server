export type AgentsList = { items: Array<{ id: string; name: string; status: string; model?: string; lastSeen?: number }> }
export type AgentAction = { status: string; agent: string; action: string }

export type KbRecent = { items: Array<{ id: number; kind: string; data: any; ts: string }> }
export type KbSearch = { items: Array<{ id: number; kind: string; data: any }> }
export type KbGet = { id: number; kind: string; data: any; ts: string }
export type KbSemantic = { items: Array<{ id: number; kind: string; score: number; data: any; ts?: string }> }

export type ChatResponse = { response: string }
export type SseToken = { sse: string; exp_s: number }

export type BusPublish = { status: string }
export type BusTail = { items: Array<{ id: number; topic: string; data: any; ts: string }> }

