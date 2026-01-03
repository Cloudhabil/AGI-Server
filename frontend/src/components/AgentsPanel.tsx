import React, { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { apiAgentAction, apiGetAgents, apiSseToken } from '../utils/api'
import { API_BASE } from '../config'
import { useStore } from '../state/store'
import Button from './ui/Button'

type NodeStatus = 'idle' | 'starting' | 'running' | 'degraded' | 'unknown' | 'error' | 'stopped'

function deriveStatus(a: { status: string; lastSeen?: number }): NodeStatus {
  const base = (a.status || 'stopped').toLowerCase()
  if (base === 'running' && a.lastSeen) {
    const age = (Date.now() / 1000) - a.lastSeen
    if (age <= 12) return 'running'
    if (age <= 30) return 'degraded'
    return 'unknown'
  }
  return (base as NodeStatus)
}

export default function AgentsPanel() {
  const qc = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const addToast = useStore(s => s.addToast)
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const res = await apiGetAgents()
      return res.items.map((a: any) => ({ id: a.id, name: a.name, status: deriveStatus(a) }))
    },
    staleTime: 10_000,
  })
  const items = data || []

  // Live updates via SSE with backoff
  useEffect(() => {
    let stop = () => {}
    ;(async () => {
      try {
        const tok = await apiSseToken()
        stop = (withBackoff as any)(
          () => new EventSource(`${API_BASE}/api/agents/sse?sse=${encodeURIComponent(tok.sse)}`),
          (ev: MessageEvent) => {
            try {
              const obj = JSON.parse(ev.data)
              if (Array.isArray(obj.items)) {
                const next = obj.items.map((a: any) => ({ id: a.id, name: a.name, status: deriveStatus(a) }))
                qc.setQueryData(['agents'], next)
              }
            } catch {}
          }
        )
      } catch {}
    })()
    return () => stop()
  }, [])

  async function act(id: string, action: 'start' | 'stop' | 'wake') {
    try {
      await apiAgentAction(id, action)
      qc.setQueryData(['agents'], (prev: any) =>
        Array.isArray(prev)
          ? prev.map((x: any) => (x.id === id ? { ...x, status: action === 'start' ? 'running' : action === 'stop' ? 'stopped' : x.status } : x))
          : prev
      )
      addToast({ title: `${action} ${id}`, tone: 'success' })
    } catch (e) {
      console.error(e)
      addToast({ title: `${action} failed for ${id}`, message: (e as any)?.message || String(e), tone: 'error' })
    }
  }

  return (
    <div className="border rounded-2xl bg-white">
      <div className="px-3 py-2 border-b flex items-center justify-between">
        <h3 className="text-sm font-semibold">Agents</h3>
        <Button onClick={() => { setError(null); refetch().catch((e) => setError(e.message || 'failed')) }} disabled={isLoading}>{isLoading ? '...' : 'Refresh'}</Button>
      </div>
      {error && <div className="px-3 py-2 text-xs text-red-600">{error}</div>}
      <ul className="divide-y">
        {items.map((a) => (
          <li key={a.id} className="px-3 py-2 text-sm flex items-center justify-between">
            <div>
              <div className="font-medium">{a.name}</div>
              <div className="text-xs text-slate-500">{a.id} · {a.status}</div>
            </div>
            <div className="flex gap-1">
              <Button onClick={() => act(a.id, 'start')}>Start</Button>
              <Button onClick={() => act(a.id, 'stop')}>Stop</Button>
              <Button onClick={() => act(a.id, 'wake')}>Wake</Button>
            </div>
          </li>
        ))}
        {items.length === 0 && !loading && <li className="px-3 py-3 text-xs text-slate-500">No agents</li>}
      </ul>
    </div>
  )
}
