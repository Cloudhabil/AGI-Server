import React, { useEffect, useMemo, useState } from 'react'
import { API_BASE, API_TOKEN } from '../config'
import { useStore } from '../state/store'
import Button from './ui/Button'

type Connector = { key: string; name: string; params: Record<string, any>; schema?: any }

export default function ConnectorsPanel() {
  const [items, setItems] = useState<Connector[]>([])
  const [active, setActive] = useState<Connector | null>(null)
  const [params, setParams] = useState('')
  const [formVals, setFormVals] = useState<Record<string, any>>({})
  const [followRunId, setFollowRunId] = useState<string | null>(null)
  const [runLogs, setRunLogs] = useState<string[]>([])
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [msg, setMsg] = useState<string | null>(null)
  const addToast = useStore(s => s.addToast)

  async function load() {
    try {
      const r = await fetch(`${API_BASE}/api/connectors`, { headers: { Authorization: `Bearer ${API_TOKEN}` } })
      if (!r.ok) throw new Error('failed')
      const data = await r.json()
      setItems(data.items || [])
    } catch {}
  }

  async function run() {
    if (!active) return
    setMsg(null)
    let bodyParams: any = {}
    try { bodyParams = params ? JSON.parse(params) : (Object.keys(formVals).length ? formVals : active.params) } catch { bodyParams = params }
    try {
      const r = await fetch(`${API_BASE}/api/connectors/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_TOKEN}` },
        body: JSON.stringify({ key: active.key, params: bodyParams }),
      })
      if (!r.ok) throw new Error('run failed')
      const data = await r.json()
      setMsg(`${data.status || 'accepted'}: ${active.key}`)
      if (data.run_id) {
        setFollowRunId(data.run_id as string)
        setRunLogs([])
      }
      addToast({ title: `Connector: ${active.key}`, message: data.status || 'ok', tone: 'success' })
    } catch (e: any) {
      setMsg(`error: ${e.message}`)
      addToast({ title: `Connector error`, message: e.message || 'failed', tone: 'error' })
    }
  }

  useEffect(() => { load() }, [])
  useEffect(() => {
    if (active) setParams(JSON.stringify(active.params, null, 2))
    if (active?.schema?.properties) {
      const initVals: Record<string, any> = {}
      for (const [k, v] of Object.entries<any>(active.schema.properties)) {
        if ('default' in (v as any)) initVals[k] = (v as any).default
      }
      setFormVals(initVals)
    } else {
      setFormVals({})
    }
    setErrors({})
  }, [active])

  // Follow logs for a specific run (SSE)
  useEffect(() => {
    if (!followRunId) return
    let es: EventSource | null = null
    try {
      const url = new URL(`${API_BASE}/api/logs/sse`)
      url.searchParams.set('run_id', followRunId)
      url.searchParams.set('token', API_TOKEN)
      es = new EventSource(url.toString())
      es.onmessage = (ev) => {
        try {
          const obj = JSON.parse(ev.data)
          if (obj?.data?.message) {
            setRunLogs((l) => [...l, obj.data.message].slice(-200))
          } else {
            setRunLogs((l) => [...l, ev.data].slice(-200))
          }
        } catch { setRunLogs((l) => [...l, ev.data].slice(-200)) }
      }
    } catch {}
    return () => es?.close()
  }, [followRunId])

  const schemaProps = useMemo(() => active?.schema?.properties ?? {}, [active?.schema])
  const schemaKeys = useMemo(() => Object.keys(schemaProps), [schemaProps])

  // Basic schema-driven validation
  useEffect(() => {
    const e: Record<string, string> = {}
    if (active?.schema) {
      const required: string[] = active.schema.required || []
      for (const key of schemaKeys) {
        const def: any = schemaProps[key] || {}
        const v = (formVals as any)[key]
        if (required.includes(key) && (v === undefined || v === null || v === '')) {
          e[key] = 'Required'
          continue
        }
        if (def.enum && Array.isArray(def.enum) && v !== undefined && !def.enum.includes(v)) {
          e[key] = `Must be one of: ${def.enum.join(', ')}`
          continue
        }
        if (def.type === 'object' && v !== undefined) {
          if (typeof v !== 'object') e[key] = 'Must be JSON object'
        }
        if (def.type === 'string' && v !== undefined) {
          if (typeof v !== 'string') e[key] = 'Must be string'
        }
      }
    }
    setErrors(e)
  }, [formVals, active, schemaKeys.length])

  function renderField(k: string) {
    const def = schemaProps[k] || {}
    const type = def.type as string | undefined
    const hasEnum = Array.isArray(def.enum)
    const value = formVals[k] ?? ''
    if (hasEnum) {
      return (
        <select className="text-xs px-2 py-1 border rounded-md" value={value} onChange={e => setFormVals(v => ({...v, [k]: e.target.value}))}>
          {def.enum.map((opt: any) => <option key={opt} value={opt}>{opt}</option>)}
        </select>
      )
    }
    if (type === 'object') {
      return (
        <textarea className="w-full h-20 border rounded-md p-2 text-xs" value={JSON.stringify(value)} onChange={e => {
          try { setFormVals(v => ({...v, [k]: JSON.parse(e.target.value)})) } catch { setFormVals(v => ({...v, [k]: e.target.value})) }
        }} />
      )
    }
    return (
      <input className="text-xs px-2 py-1 border rounded-md w-full" value={value} onChange={e => setFormVals(v => ({...v, [k]: e.target.value}))} />
    )
  }

  return (
    <div className="border rounded-2xl bg-white">
      <div className="px-3 py-2 border-b flex items-center justify-between">
        <h3 className="text-sm font-semibold">Connectors</h3>
        <Button onClick={load}>Refresh</Button>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2">
        <ul className="divide-y">
          {items.map((c) => (
            <li key={c.key} className={`px-3 py-2 text-sm cursor-pointer hover:bg-slate-50 ${active?.key === c.key ? 'bg-slate-50' : ''}`} onClick={() => setActive(c)}>
              <div className="font-medium">{c.name}</div>
              <div className="text-xs text-slate-500">{c.key}</div>
            </li>
          ))}
          {items.length === 0 && <li className="px-3 py-3 text-xs text-slate-500">No connectors</li>}
        </ul>
        <div className="border-l p-3 space-y-3">
          {active ? (
            <div className="text-xs space-y-2">
              <div className="text-sm font-semibold">{active.name}</div>
              <div className="text-[11px] text-slate-500">{active.key}</div>
              {schemaKeys.length > 0 ? (
                <div className="space-y-2">
                  <div className="font-medium">Parameters</div>
                  {schemaKeys.map(k => (
                    <div key={k} className="flex items-start gap-2">
                      <label className="w-24 text-[11px] text-slate-600 pt-1">{k}</label>
                      <div className="flex-1">
                        {renderField(k)}
                        {errors[k] && <div className="text-[11px] text-red-600 mt-0.5">{errors[k]}</div>}
                      </div>
                    </div>
                  ))}
                  <div className="text-[11px] text-slate-500">Advanced JSON editor:</div>
                  <textarea className="w-full h-20 border rounded-md p-2" value={params} onChange={e => setParams(e.target.value)} />
                </div>
              ) : (
                <div>
                  <div className="font-medium mb-1">Params (JSON)</div>
                  <textarea className="w-full h-28 border rounded-md p-2" value={params} onChange={e => setParams(e.target.value)} />
                </div>
              )}
              <div>
                <Button onClick={run} disabled={Object.keys(errors).length > 0}>Run</Button>
              </div>
              {msg && <div className="text-xs text-slate-600">{msg}</div>}
              {followRunId && (
                <div className="border rounded-md p-2">
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-xs font-semibold">Run logs</div>
                    <Button className="text-[11px]" onClick={() => { setFollowRunId(null); setRunLogs([]) }}>Stop</Button>
                  </div>
                  <div className="h-24 overflow-auto font-mono text-[11px]">
                    {runLogs.map((l, i) => <div key={i}>{l}</div>)}
                    {runLogs.length === 0 && <div className="text-slate-500">Waiting for logs...</div>}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs text-slate-500">Select a connector</div>
          )}
        </div>
      </div>
    </div>
  )
}
