import { StateCreator } from 'zustand'

export type ToastTone = 'success' | 'error' | 'info' | 'warn'
export type Toast = { id: string; title: string; message?: string; tone?: ToastTone; ts: number; timeoutMs?: number }

export interface ToastsSlice {
  toasts: Toast[]
  addToast: (t: Omit<Toast, 'id' | 'ts'> & { id?: string }) => string
  dismissToast: (id: string) => void
  clearToasts: () => void
}

function uid() { return Math.random().toString(36).slice(2) }

export const createToastsSlice: StateCreator<ToastsSlice, [], [], ToastsSlice> = (set, get) => ({
  toasts: [],
  addToast: (t) => {
    const id = t.id || uid()
    const tone = t.tone || 'info'
    const toast: Toast = { id, title: t.title, message: t.message, tone, ts: Date.now(), timeoutMs: t.timeoutMs ?? (tone === 'error' ? 8000 : 4000) }
    set((s) => ({ toasts: [...(s as any).toasts, toast] as Toast[] }))
    if (toast.timeoutMs && toast.timeoutMs > 0) {
      setTimeout(() => get().dismissToast(id), toast.timeoutMs)
    }
    return id
  },
  dismissToast: (id) => set((s) => ({ toasts: (s as any).toasts.filter((x: Toast) => x.id !== id) })),
  clearToasts: () => set({ toasts: [] }),
})

