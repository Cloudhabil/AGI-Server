import React, { useEffect, useState } from 'react'
import { API_BASE } from '../config'
import { apiBusPublish, apiBusTail, apiSseToken } from '../utils/api'
import { useStore } from '../state/store'
import { withBackoff } from '../utils/sse'
import Button from './ui/Button'

export default function BusConsole() {
  const [topic, setTopic] = useState('general')
  const [payload, setPayload] = useState('{"hello":"world"}')
  const [tail, setTail] = useState<Array<{ id: number; topic: string; data: any; ts: string }>>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const addToast = useStore(s => s.addToast)

  async function refresh() {
    setLoading(true); setError(null)
    try {
      const res = await apiBusTail(topic || undefined, 30)
      setTail(res.items)
    } catch (e: any) {
      setError(e.message || 'failed to tail bus')
    } finally { setLoading(false) }
  }

  async function publish() {
    setError(null)
    try {
      let data: any
      try { data = JSON.parse(payload) } catch { data = payload }
      await apiBusPublish(topic || 'general', data)
      await refresh()
      addToast({ title: `Published to ${topic || 'general'}`, tone: 'success' })
    } catch (e: any) { setError(e.message || 'publish failed') }
  }

  useEffect(() => { refresh() }, [])
  useEffect(() => {
    let stop = () => {}
    let lastId = 0
    let showedErrorToast = false
    try {
      (async () => {
        const tok = await apiSseToken()
        const disposer = withBackoff(() => {
          const url = new URL(`${API_BASE}/api/bus/sse`)
          if (topic) url.searchParams.set('topic', topic)
          url.searchParams.set('sse', tok.sse)
          if (lastId > 0) url.searchParams.set('last_id', String(lastId))
          return new EventSource(url.toString())
        }, (ev) => {
          try { const obj = JSON.parse(ev.data); lastId = Number(obj.id) || lastId; setTail((t) => [obj as any, ...t].slice(0, 50)) } catch {}
        }, (st) => {
          if (typeof st === 'string') {
            if (st === 'open') { showedErrorToast = false; addToast({ title: 'Bus stream connected', tone: 'success', timeoutMs: 2000 }) }
            if (st === 'error' && !showedErrorToast) { addToast({ title: 'Bus stream error', tone: 'warn' }); showedErrorToast = true }
          }
        })
        stop = disposer
      })()
    } catch {}
    return () => stop()
  }, [topic])

  return (
    <div className="border rounded-2xl bg-white">
      <div className="px-3 py-2 border-b flex items-center gap-2">
        <h3 className="text-sm font-semibold mr-auto">Bus Console</h3>
        <input className="text-xs px-2 py-1 border rounded-md" placeholder="topic" value={topic} onChange={e => setTopic(e.target.value)} />
        <button className="px-2 py-1 text-xs border rounded-md" onClick={refresh} disabled={loading}>{loading ? '...' : 'Refresh'}</button>
      </div>
      {error && <div className="px-3 py-2 text-xs text-red-600">{error}</div>}
      <div className="p-3 grid grid-cols-1 lg:grid-cols-2 gap-3">
        <div>
          <div className="text-xs font-semibold mb-1">Payload (JSON or text)</div>
          <textarea className="w-full h-28 border rounded-md p-2 text-xs" value={payload} onChange={e => setPayload(e.target.value)} />
          <div className="mt-2">
            <Button onClick={publish}>Publish</Button>
          </div>
        </div>
        <div>
          <div className="text-xs font-semibold mb-1">Tail {topic ? `(${topic})` : ''}</div>
          <ul className="h-40 overflow-auto text-xs space-y-1">
            {tail.map((m) => (
              <li key={m.id} className="border rounded-md px-2 py-1">
                <div className="font-medium">{m.topic}</div>
                <pre className="whitespace-pre-wrap break-words">{JSON.stringify(m.data)}</pre>
                <div className="text-[10px] text-slate-500">{new Date(m.ts).toLocaleTimeString()}</div>
              </li>
            ))}
            {tail.length === 0 && <li className="text-slate-500">No messages</li>}
          </ul>
        </div>
      </div>
    </div>
  )
}
