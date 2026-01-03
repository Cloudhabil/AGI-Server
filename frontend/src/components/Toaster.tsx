import React from 'react'
import { useStore } from '../state/store'

const toneStyles: Record<string, string> = {
  success: 'bg-green-600 text-white',
  error: 'bg-red-600 text-white',
  info: 'bg-slate-800 text-white',
  warn: 'bg-amber-500 text-black',
}

export default function Toaster() {
  const toasts = useStore(s => s.toasts)
  const dismiss = useStore(s => s.dismissToast)
  return (
    <div className="fixed bottom-4 right-4 z-[1000] flex flex-col gap-2 w-80">
      {toasts.map(t => (
        <div key={t.id} className={`rounded-lg shadow px-3 py-2 text-sm ${toneStyles[t.tone || 'info']}`}>
          <div className="flex items-start gap-2">
            <div className="flex-1">
              <div className="font-semibold">{t.title}</div>
              {t.message && <div className="opacity-90 text-xs mt-0.5 whitespace-pre-wrap break-words">{t.message}</div>}
            </div>
            <button className="text-xs opacity-80 hover:opacity-100" onClick={() => dismiss(t.id)}>×</button>
          </div>
        </div>
      ))}
    </div>
  )
}

