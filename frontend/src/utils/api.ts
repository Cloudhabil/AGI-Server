import { API_BASE, API_TOKEN, API_USER_ROLE } from '../config';
import type { AgentsList, AgentAction, KbRecent, KbSearch, KbGet, KbSemantic, ChatResponse, SseToken, BusTail } from '../types/api';
import { z } from 'zod'

const AgentSchema = z.object({ id: z.string(), name: z.string(), status: z.string(), model: z.string().optional(), lastSeen: z.number().optional() })
const AgentsListSchema: z.ZodType<AgentsList> = z.object({ items: z.array(AgentSchema) })
const KbItemSchema = z.object({ id: z.number(), kind: z.string(), data: z.any(), ts: z.string().optional() })
const KbRecentSchema: z.ZodType<KbRecent> = z.object({ items: z.array(KbItemSchema.extend({ ts: z.string() })) })
const KbSearchSchema: z.ZodType<KbSearch> = z.object({ items: z.array(KbItemSchema.omit({ ts: true })) })
const KbGetSchema: z.ZodType<KbGet> = z.object({ id: z.number(), kind: z.string(), data: z.any(), ts: z.string() })
const KbSemanticItemSchema = z.object({ id: z.number(), kind: z.string(), score: z.number(), data: z.any(), ts: z.string().optional() })
const KbSemanticSchema: z.ZodType<KbSemantic> = z.object({ items: z.array(KbSemanticItemSchema) })
const ChatResponseSchema: z.ZodType<ChatResponse> = z.object({ response: z.string() })
const SseTokenSchema: z.ZodType<SseToken> = z.object({ sse: z.string(), exp_s: z.number() })
const BusTailItemSchema = z.object({ id: z.number(), topic: z.string(), data: z.any(), ts: z.string() })
const BusTailSchema: z.ZodType<BusTail> = z.object({ items: z.array(BusTailItemSchema) })

function currentUserRole(): string {
  try {
    const r = localStorage.getItem('userRole')
    if (r) return r.toLowerCase()
  } catch {}
  return API_USER_ROLE
}

function apiBase(): string {
  const base = (API_BASE || '').replace(/\/+$/, '');
  return base.endsWith('/api') ? base : `${base}/api`;
}

export async function apiStartNode(id: string): Promise<any> {
  const r = await fetch(`${apiBase()}/nodes/${id}/start`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${API_TOKEN}` },
  });
  if (!r.ok) throw new Error(`start ${id} failed`);
  return r.json();
}

export async function apiStopNode(id: string): Promise<any> {
  const r = await fetch(`${apiBase()}/nodes/${id}/stop`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${API_TOKEN}` },
  });
  if (!r.ok) throw new Error(`stop ${id} failed`);
  return r.json();
}

export async function apiGetConfig(id: string): Promise<any> {
  const r = await fetch(`${apiBase()}/nodes/${id}/config`, {
    headers: { Authorization: `Bearer ${API_TOKEN}` },
  });
  if (!r.ok) throw new Error(`get config ${id} failed`);
  return r.json();
}

export async function apiPutConfig(id: string, cfg: any): Promise<any> {
  const r = await fetch(`${apiBase()}/nodes/${id}/config`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${API_TOKEN}`,
    },
    body: JSON.stringify(cfg),
  });
  if (!r.ok) throw new Error(`put config ${id} failed`);
  return r.json();
}

// New API helpers matching backend /api
export async function apiHealth(): Promise<any> {
  const r = await fetch(`${apiBase()}/health`, { credentials: 'include', headers: { Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() } });
  if (!r.ok) throw new Error('health failed');
  return r.json();
}

export async function apiGetAgents(): Promise<AgentsList> {
  const r = await fetch(`${apiBase()}/agents`, { credentials: 'include', headers: { Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() } });
  if (!r.ok) throw new Error('get agents failed');
  const data = await r.json()
  return AgentsListSchema.parse(data)
}

export async function apiAgentAction(id: string, action: 'start' | 'stop' | 'wake'): Promise<AgentAction> {
  const r = await fetch(`${apiBase()}/agents/${id}/${action}`, {
    method: 'POST',
    credentials: 'include',
    headers: { Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() },
  });
  if (!r.ok) throw new Error(`${action} ${id} failed`);
  return r.json();
}

// KB helpers
export async function apiKbRecent(limit = 20): Promise<KbRecent> {
  const r = await fetch(`${apiBase()}/kb/recent?limit=${encodeURIComponent(String(limit))}`, {
    credentials: 'include',
    headers: { Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() },
  });
  if (!r.ok) throw new Error('kb recent failed');
  const data = await r.json()
  return KbRecentSchema.parse(data)
}

export async function apiKbSearch(q: string): Promise<KbSearch> {
  const r = await fetch(`${apiBase()}/kb/search?q=${encodeURIComponent(q)}`, {
    credentials: 'include',
    headers: { Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() },
  });
  if (!r.ok) throw new Error('kb search failed');
  const data = await r.json()
  return KbSearchSchema.parse(data)
}

export async function apiKbGet(id: number): Promise<KbGet> {
  const r = await fetch(`${apiBase()}/kb/${id}`, { credentials: 'include', headers: { Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() } });
  if (!r.ok) throw new Error('kb get failed');
  const data = await r.json()
  return KbGetSchema.parse(data)
}

// Bus helpers
export async function apiBusPublish(topic: string, payload: any): Promise<any> {
  const body = new FormData();
  body.append('topic', topic);
  body.append('payload', typeof payload === 'string' ? payload : JSON.stringify(payload));
  const r = await fetch(`${apiBase()}/bus/publish`, { method: 'POST', credentials: 'include', headers: { Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() }, body });
  if (!r.ok) throw new Error('bus publish failed');
  return r.json();
}

export async function apiBusTail(topic?: string, limit = 50): Promise<BusTail> {
  const url = new URL(`${apiBase()}/bus/tail`);
  if (topic) url.searchParams.set('topic', topic);
  url.searchParams.set('limit', String(limit));
  const r = await fetch(url.toString(), { credentials: 'include', headers: { Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() } });
  if (!r.ok) throw new Error('bus tail failed');
  const data = await r.json()
  return BusTailSchema.parse(data)
}

export async function apiKbSemanticSearch(query: string, k = 5): Promise<KbSemantic> {
  const r = await fetch(`${apiBase()}/kb/semantic_search`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() },
    body: JSON.stringify({ query, k }),
  })
  if (!r.ok) throw new Error('semantic search failed')
  const data = await r.json()
  return KbSemanticSchema.parse(data)
}

export async function apiChat(text: string): Promise<ChatResponse> {
  const r = await fetch(`${apiBase()}/chat`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_TOKEN}`, 'X-User-Role': currentUserRole() },
    body: JSON.stringify({ text }),
  })
  if (!r.ok) throw new Error('chat failed')
  const data = await r.json()
  return ChatResponseSchema.parse(data)
}

export async function apiLogin(username: string, role: string, password?: string): Promise<{ token: string; role: string }> {
  const r = await fetch(`${apiBase()}/auth/login`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, role, password }),
  })
  if (!r.ok) throw new Error('login failed')
  const data = await r.json() as { token: string; role: string }
  try { localStorage.setItem('userRole', data.role) } catch {}
  return data
}

export async function apiSseToken(): Promise<SseToken> {
  const r = await fetch(`${apiBase()}/auth/sse_token`, { method: 'POST', credentials: 'include' })
  if (!r.ok) throw new Error('sse token failed')
  const data = await r.json()
  return SseTokenSchema.parse(data)
}
