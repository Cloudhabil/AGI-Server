import { beforeEach, afterEach, expect, test, vi } from 'vitest';
import React from 'react';
import { createRoot } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';


beforeEach(() => {
  vi.resetModules();
});

afterEach(() => {
  vi.unstubAllEnvs();
});

test('uses auth token for fetch and opens logs SSE with sse token', async () => {
  vi.stubEnv('VITE_API_TOKEN', 'test-token');
  vi.stubEnv('VITE_API_URL', 'http://api.example');
  const fetchMock = vi.fn((url: string, opts?: any) => {
    if (typeof url === 'string' && url.endsWith('/api/auth/sse_token')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ sse: 'sse123', exp_s: 300 }) })
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
  }) as any
  ;(global as any).fetch = fetchMock

  const esUrls: string[] = []
  class MockEventSource {
    url: string
    onmessage: any = null
    onerror: any = null
    constructor(url: string) {
      this.url = url
      esUrls.push(url)
    }
    close() {}
  }
  ;(global as any).EventSource = MockEventSource as any
  ;(global as any).alert = vi.fn()

  const { default: OrchestratorUI } = await import('./components/OrchestratorUI');
  const div = document.createElement('div');
  document.body.appendChild(div);
  const root = createRoot(div);
  const qc = new QueryClient()
  await act(async () => {
    root.render(<QueryClientProvider client={qc}><OrchestratorUI /></QueryClientProvider>);
  });

  // Should have opened logs SSE with sse token param
  expect(esUrls.some(u => u.includes('/api/logs/sse') && u.includes('sse=sse123'))).toBe(true)

  const btn = Array.from(div.querySelectorAll('button')).find((b) =>
    b.textContent?.includes('SesamAwake')
  ) as HTMLButtonElement;
  await act(async () => {
    btn.click();
  });

  expect(fetchMock).toHaveBeenCalledWith('http://api.example/api/actions/sesamawake', {
    method: 'POST',
    headers: { Authorization: 'Bearer test-token' },
  });

  root.unmount();
});

