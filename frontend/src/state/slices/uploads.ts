import { StateCreator } from 'zustand'
import { UploadItem } from '../types'

export interface UploadsSlice {
  uploads: UploadItem[]
  addUpload: (item: UploadItem) => void
  markUpload: (id: string, patch: Partial<UploadItem>) => void
}

export const createUploadsSlice: StateCreator<UploadsSlice, [], [], UploadsSlice> = (set) => ({
  uploads: [],
  addUpload: (item) => set((s) => ({ uploads: [...(s as any).uploads, item] })),
  markUpload: (id, patch) =>
    set((s) => ({ uploads: (s as any).uploads.map((u: UploadItem) => (u.id === id ? { ...u, ...patch } : u)) })),
})

