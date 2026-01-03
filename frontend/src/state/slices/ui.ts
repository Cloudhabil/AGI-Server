import { StateCreator } from 'zustand'

type ContextMenu = { id: string; x: number; y: number } | null

export interface UiSlice {
  contextMenu: ContextMenu
  configDialog: { open: boolean; nodeId: string | null; draft: string; error: string | null }
  logsDock: { open: boolean; nodeId: string | null }
  openMenu: (id: string, x: number, y: number) => void
  closeMenu: () => void
  openConfig: (nodeId: string) => void
  closeConfig: () => void
  setConfigDraft: (v: string) => void
  setConfigError: (v: string | null) => void
  openLogs: (nodeId: string) => void
  closeLogs: () => void
}

export const createUiSlice: StateCreator<UiSlice, [], [], UiSlice> = (set) => ({
  contextMenu: null,
  configDialog: { open: false, nodeId: null, draft: '', error: null },
  logsDock: { open: false, nodeId: null },
  openMenu: (id, x, y) => set({ contextMenu: { id, x, y } }),
  closeMenu: () => set({ contextMenu: null }),
  openConfig: (nodeId) => set({ configDialog: { open: true, nodeId, draft: '', error: null } }),
  closeConfig: () => set({ configDialog: { open: false, nodeId: null, draft: '', error: null } }),
  setConfigDraft: (v) => set((s) => ({ configDialog: { ...s.configDialog, draft: v } } as any)),
  setConfigError: (v) => set((s) => ({ configDialog: { ...s.configDialog, error: v } } as any)),
  openLogs: (nodeId) => set({ logsDock: { open: true, nodeId } }),
  closeLogs: () => set({ logsDock: { open: false, nodeId: null } }),
})

