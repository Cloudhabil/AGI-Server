import React, { useEffect, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { apiKbGet, apiKbRecent, apiKbSearch } from '../utils/api'
import Button from './ui/Button'

type KbItem = { id: number; kind: string; data: any; ts?: string }

export default function KBPanel() {
  const [query, setQuery] = useState('')
  const [active, setActive] = useState<KbItem | null>(null)
  const qc = useQueryClient()
  const isSearch = useMemo(() => !!query.trim(), [query])
  const { data: recent, isLoading: loadingRecent, error: errRecent, refetch: refetchRecent } = useQuery({
    queryKey: ['kb', 'recent', 20],
    queryFn: () => apiKbRecent(20).then(r => r.items),
    enabled: !isSearch,
    staleTime: 30_000,
  })
  const { data: searchItems, isLoading: loadingSearch, error: errSearch, refetch: refetchSearch } = useQuery({
    queryKey: ['kb', 'search', query.trim()],
    queryFn: () => apiKbSearch(query.trim()).then(r => r.items as any),
    enabled: isSearch,
  })
  const items = (isSearch ? (searchItems || []) : (recent || [])) as KbItem[]
  const loading = isSearch ? loadingSearch : loadingRecent
  const error = (errRecent || errSearch) as any as Error | null
  const [activeFull, setActiveFull] = useState<any>(null)

  async function search() {
    if (!isSearch) return refetchRecent()
    await refetchSearch()
  }
  async function openItem(it: KbItem) {
    setActive(it)
    try { const full = await apiKbGet(it.id); setActiveFull(full) } catch { setActiveFull(it) }
  }

  return (
    <div className="border rounded-2xl bg-white">
      <div className="px-3 py-2 border-b flex items-center gap-2">
        <h3 className="text-sm font-semibold mr-auto">Knowledge Base</h3>
        <input className="text-xs px-2 py-1 border rounded-md" placeholder="Search..." value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === 'Enter' && search()} />
        <Button onClick={search}>Search</Button>
        <Button onClick={() => refetchRecent()}>Recent</Button>
      </div>
      {error && <div className="px-3 py-2 text-xs text-red-600">{(error as any)?.message || 'failed'}</div>}
      <div className="grid grid-cols-1 lg:grid-cols-2">
        <ul className="divide-y">
          {items.map((it) => (
            <li key={it.id} className="px-3 py-2 text-sm cursor-pointer hover:bg-slate-50" onMouseEnter={() => qc.prefetchQuery({ queryKey: ['kb', 'get', it.id], queryFn: () => apiKbGet(it.id) })} onClick={() => openItem(it)}>
              <div className="font-medium">{it.kind}</div>
              <div className="text-xs text-slate-500 truncate">{JSON.stringify(it.data)}</div>
            </li>
          ))}
          {items.length === 0 && !loading && <li className="px-3 py-3 text-xs text-slate-500">No entries</li>}
        </ul>
        <div className="border-l min-h-[220px] p-3">
          {active ? (
            <div className="text-xs">
              <div className="text-sm font-semibold mb-1">{active.kind}</div>
              <pre className="text-xs whitespace-pre-wrap break-words">{JSON.stringify(activeFull || active, null, 2)}</pre>
            </div>
          ) : (
            <div className="text-xs text-slate-500">Select an item</div>
          )}
        </div>
      </div>
    </div>
  )
}
