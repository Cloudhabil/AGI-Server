import { useEffect, useRef, useState } from 'react'
import { useStore } from '../state/store'
import { LogsChannel } from '../channels/logs'
import { API_BASE } from '../config'

const LOGS = new LogsChannel(API_BASE)

type LogItem = { ts?: number; level?: string; line: string }

export function LogsDock() {
  const dock = useStore((s) => s.logsDock)
  const close = useStore((s) => s.closeLogs)
  const [items, setItems] = useState<LogItem[]>([])
  const [paused, setPaused] = useState(false)
  const [level, setLevel] = useState<'ALL' | 'INFO' | 'DEBUG' | 'WARN'>('ALL')
  const scroller = useRef<HTMLDivElement>(null)
  const unsubRef = useRef<null | (() => void)>(null)

  useEffect(() => {
    if (!dock.open || !dock.nodeId) return
    unsubRef.current?.()
    unsubRef.current = LOGS.subscribeNode(dock.nodeId, (data) => {
      if (paused) return
      if (data?.type === 'log') {
        if (level !== 'ALL' && data.level !== level) return
        setItems((prev) => {
          const next = [...prev, { ts: data.ts, level: data.level, line: data.line }]
          return next.length > 2000 ? next.slice(next.length - 2000) : next
        })
      }
    })
    return () => {
      unsubRef.current?.()
      unsubRef.current = null
    }
  }, [dock.open, dock.nodeId, paused, level])

  useEffect(() => {
    const el = scroller.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [items])

  if (!dock.open || !dock.nodeId) return null
  return (
    <div className="absolute left-4 top-4 w-[520px] h-[520px] bg-white rounded-2xl shadow-xl border flex flex-col">
      <div className="p-3 border-b flex items-center justify-between">
        <div className="font-semibold">Logs • {dock.nodeId}</div>
        <div className="flex items-center gap-2">
          <select
            className="border rounded px-2 py-1 text-xs"
            value={level}
            onChange={(e) => setLevel(e.target.value as any)}
          >
            <option>ALL</option>
            <option>INFO</option>
            <option>DEBUG</option>
            <option>WARN</option>
          </select>
          <button className="text-sm underline" onClick={() => setPaused((p) => !p)}>
            {paused ? 'Resume' : 'Pause'}
          </button>
          <button className="text-sm underline" onClick={() => setItems([])}>
            Clear
          </button>
          <button
            className="text-sm underline"
            onClick={() => navigator.clipboard.writeText(items.map((i) => i.line).join('\n'))}
          >
            Copy
          </button>
          <button className="text-sm underline" onClick={close}>
            Close
          </button>
        </div>
      </div>
      <div ref={scroller} className="flex-1 overflow-auto p-3 text-xs font-mono space-y-1">
        {items.map((i, idx) => (
          <div key={idx}>{i.line}</div>
        ))}
      </div>
    </div>
  )
}

