import { beforeEach, afterEach, expect, test, vi } from 'vitest';

beforeEach(() => {
  vi.resetModules();
});

afterEach(() => {
  vi.unstubAllEnvs();
});

test('apiStartNode adds auth header', async () => {
  vi.stubEnv('VITE_API_TOKEN', 'test-token');
  vi.stubEnv('VITE_API_URL', 'http://api.test');
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({}) });
  (global as any).fetch = fetchMock;
  const { apiStartNode } = await import('./utils/api');
  await apiStartNode('node1');
  expect(fetchMock).toHaveBeenCalledWith('http://api.test/api/nodes/node1/start', {
    method: 'POST',
    headers: { Authorization: 'Bearer test-token' },
  });
});

test('WsClient appends token query param', async () => {
  vi.stubEnv('VITE_API_TOKEN', 'abc123');
  const urls: string[] = [];
  class MockWebSocket {
    readyState = 1;
    constructor(url: string) {
      urls.push(url);
    }
    send() {}
    close() {}
  }
  (global as any).WebSocket = MockWebSocket as any;
  const { WsClient } = await import('./utils/ws');
  new WsClient('ws://example.com/ws');
  expect(urls[0]).toContain('token=abc123');
});
