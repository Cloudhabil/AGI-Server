import { defineStore } from 'pinia'
import type { Profile } from '../types/api'
import { apiGetProfile } from '../utils/api'
import { hasWebGL } from '../utils/webgl'
import { getTraceId } from '../utils/trace'

const applyTheme = (theme: 'dark' | 'light') => {
  if (typeof document === 'undefined') return
  document.documentElement.dataset.theme = theme
}

const savedTheme = (): 'dark' | 'light' | null => {
  try {
    const stored = localStorage.getItem('themePreference')
    if (stored === 'dark' || stored === 'light') return stored
  } catch {}
  return null
}

export const useSystemStore = defineStore('system', {
  state: () => ({
    profile: null as Profile | null,
    profileError: '',
    loadingProfile: false,
    theme: savedTheme() || 'light' as 'dark' | 'light',
    traceId: getTraceId(),
    webglSupported: false,
  }),
  actions: {
    setTheme(theme: 'dark' | 'light') {
      this.theme = theme
      applyTheme(theme)
      try { localStorage.setItem('themePreference', theme) } catch {}
    },
    toggleTheme() {
      this.setTheme(this.theme === 'dark' ? 'light' : 'dark')
    },
    refreshWebgl() {
      this.webglSupported = hasWebGL()
    },
    async initProfile() {
      this.loadingProfile = true
      this.profileError = ''
      try {
        const data = await apiGetProfile()
        this.profile = data
        const desired = savedTheme() || data.theme || this.theme
        if (desired === 'dark' || desired === 'light') this.setTheme(desired)
        this.webglSupported = hasWebGL()
      } catch (err: any) {
        this.profileError = err?.message || 'Failed to load profile'
        this.webglSupported = hasWebGL()
      } finally {
        this.loadingProfile = false
      }
    },
  },
})
