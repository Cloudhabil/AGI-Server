import { useEffect, useState } from 'react'
import { useStore } from '../state/store'
import { apiStartNode, apiStopNode, apiGetConfig } from '../utils/api'

export function ContextMenuRoot() {
  const ctx = useStore((s) => s.contextMenu)
  const close = useStore((s) => s.closeMenu)
  const setRuntime = useStore((s) => s.setRuntime)
  const openConfig = useStore((s) => s.openConfig)
  const setConfigDraft = useStore((s) => s.setConfigDraft)
  const openLogs = useStore((s) => s.openLogs)
  const runtime = useStore((s) => s.runtime)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const handler = () => close()
    window.addEventListener('click', handler)
    return () => window.removeEventListener('click', handler)
  }, [close])

  if (!ctx) return null
  return (
    <div className="absolute z-50" style={{ left: ctx.x, top: ctx.y }}>
      <div className="rounded-2xl shadow-lg p-2 bg-white border w-56">
        <div className="font-medium mb-2">{ctx.id}</div>
        <button
          disabled={busy || runtime[ctx.id]?.status === 'running'}
          onClick={async () => {
            try {
              setBusy(true)
              setRuntime(ctx.id, { status: 'starting' })
              await apiStartNode(ctx.id)
              setRuntime(ctx.id, { status: 'running' })
            } catch {
              setRuntime(ctx.id, { status: 'error' })
            } finally {
              setBusy(false)
              close()
            }
          }}
          className="w-full text-left px-2 py-1 rounded hover:bg-gray-100 disabled:opacity-50"
        >
          Start
        </button>
        <button
          disabled={busy || runtime[ctx.id]?.status === 'stopped'}
          onClick={async () => {
            try {
              setBusy(true)
              setRuntime(ctx.id, { status: 'stopping' })
              await apiStopNode(ctx.id)
              setRuntime(ctx.id, { status: 'stopped' })
            } catch {
              setRuntime(ctx.id, { status: 'error' })
            } finally {
              setBusy(false)
              close()
            }
          }}
          className="w-full text-left px-2 py-1 rounded hover:bg-gray-100 disabled:opacity-50"
        >
          Stop
        </button>
        <button
          onClick={async () => {
            try {
              setBusy(true)
              const cfg = await apiGetConfig(ctx.id)
              openConfig(ctx.id)
              setConfigDraft(JSON.stringify(cfg, null, 2))
            } catch (e) {
              console.error('Failed to get node config:', e)
            } finally {
              setBusy(false)
              close()
            }
          }}
          className="w-full text-left px-2 py-1 rounded hover:bg-gray-100"
        >
          Configure...
        </button>
        <button
          onClick={() => {
            openLogs(ctx.id)
            close()
          }}
          className="w-full text-left px-2 py-1 rounded hover:bg-gray-100"
        >
          Inspect logs
        </button>
      </div>
    </div>
  )
}

