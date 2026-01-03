import { WsClient } from '../utils/ws'

type Sub = (ev: any) => void

export class ChatChannel {
  private urlBase: string
  private clients: Map<string, { ws: WsClient; subs: Set<Sub> }> = new Map()

  constructor(apiBase: string) {
    this.urlBase = apiBase.replace('http', 'ws')
  }

  subscribe(nodeId: string, sub: Sub) {
    let entry = this.clients.get(nodeId)
    if (!entry) {
      const ws = new WsClient(`${this.urlBase}/ws/chat/${nodeId}`, {
        onMessage: (d) => this.emit(nodeId, d),
      })
      entry = { ws, subs: new Set() }
      this.clients.set(nodeId, entry)
    }
    entry.subs.add(sub)
    return () => this.unsubscribe(nodeId, sub)
  }

  send(nodeId: string, obj: any) {
    const entry = this.clients.get(nodeId)
    entry?.ws.send(obj)
  }

  private unsubscribe(nodeId: string, sub: Sub) {
    const entry = this.clients.get(nodeId)
    if (!entry) return
    entry.subs.delete(sub)
    if (entry.subs.size === 0) {
      entry.ws.stop()
      this.clients.delete(nodeId)
    }
  }

  private emit(nodeId: string, d: any) {
    const entry = this.clients.get(nodeId)
    if (!entry) return
    entry.subs.forEach((fn) => fn(d))
  }
}

