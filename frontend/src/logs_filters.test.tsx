import { beforeEach, afterEach, expect, test, vi } from 'vitest'
import React from 'react'
import { createRoot } from 'react-dom/client'
import { act } from 'react-dom/test-utils'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

beforeEach(() => {
  vi.resetModules()
})

afterEach(() => {
  vi.unstubAllEnvs()
})

test('logs filters are Radix checkboxes and toggle', async () => {
  vi.stubEnv('VITE_API_TOKEN', 'test-token')
  vi.stubEnv('VITE_API_URL', 'http://api.example')
  const fetchMock = vi.fn((url: string, opts?: any) => {
    if (typeof url === 'string' && url.endsWith('/api/auth/sse_token')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ sse: 'sse123', exp_s: 300 }) })
    }
    if (typeof url === 'string' && url.endsWith('/api/agents')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [] }) })
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
  }) as any
  ;(global as any).fetch = fetchMock

  class MockEventSource {
    onmessage: any = null
    onerror: any = null
    constructor(public url: string) {}
    close() {}
  }
  ;(global as any).EventSource = MockEventSource as any

  const { default: OrchestratorUI } = await import('./components/OrchestratorUI')
  const div = document.createElement('div')
  document.body.appendChild(div)
  const root = createRoot(div)
  const qc = new QueryClient()
  await act(async () => {
    root.render(<QueryClientProvider client={qc}><OrchestratorUI /></QueryClientProvider>)
  })

  const checkboxes = Array.from(div.querySelectorAll('[role="checkbox"]')) as HTMLElement[]
  expect(checkboxes.length).toBeGreaterThanOrEqual(3)
  const busCb = checkboxes[0]
  expect(busCb.getAttribute('aria-checked')).toBe('true')
  await act(async () => { busCb.click() })
  expect(busCb.getAttribute('aria-checked')).toBe('false')

  root.unmount()
})

