import { useState } from 'react'
import { useStore } from '../state/store'
import { apiPutConfig } from '../utils/api'

export function NodeConfigDialog() {
  const dlg = useStore((s) => s.configDialog)
  const setDraft = useStore((s) => s.setConfigDraft)
  const setErr = useStore((s) => s.setConfigError)
  const close = useStore((s) => s.closeConfig)
  const [busy, setBusy] = useState(false)
  if (!dlg.open || !dlg.nodeId) return null

  const save = async () => {
    try {
      setBusy(true)
      const obj = JSON.parse(dlg.draft || '{}')
      await apiPutConfig(dlg.nodeId!, obj)
      close()
    } catch (e: any) {
      setErr(e?.message || 'Invalid JSON or save error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
      <div className="bg-white w-[680px] h-[520px] rounded-2xl shadow-xl border flex flex-col">
        <div className="p-3 border-b flex items-center justify-between">
          <div className="font-semibold">Configure • {dlg.nodeId}</div>
          <button className="text-sm underline" onClick={close}>
            Close
          </button>
        </div>
        <div className="p-3 flex-1 flex flex-col gap-2">
          <textarea
            className="flex-1 w-full border rounded p-2 font-mono text-sm"
            value={dlg.draft}
            onChange={(e) => setDraft(e.target.value)}
            spellCheck={false}
          />
          {dlg.error && <div className="text-red-600 text-sm">{dlg.error}</div>}
        </div>
        <div className="p-3 border-t flex justify-end gap-2">
          <button className="px-3 py-1 rounded border" onClick={close}>
            Cancel
          </button>
          <button
            className="px-3 py-1 rounded bg-black text-white disabled:opacity-50"
            disabled={busy}
            onClick={save}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}

