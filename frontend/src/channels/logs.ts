import { WsClient } from '../utils/ws'

type Sub = (ev: any) => void

export class LogsChannel {
  private urlBase: string
  private nodeMap: Map<string, { ws: WsClient; subs: Set<Sub> }> = new Map()
  private global?: { ws: WsClient; subs: Set<Sub> }

  constructor(apiBase: string) {
    this.urlBase = apiBase.replace('http', 'ws')
  }

  subscribeNode(nodeId: string, sub: Sub) {
    let e = this.nodeMap.get(nodeId)
    if (!e) {
      const ws = new WsClient(`${this.urlBase}/ws/logs/${nodeId}`, {
        onMessage: (d) => this.emit(nodeId, d),
      })
      e = { ws, subs: new Set() }
      this.nodeMap.set(nodeId, e)
    }
    e.subs.add(sub)
    return () => this.unsubscribeNode(nodeId, sub)
  }

  subscribeGlobal(sub: Sub) {
    if (!this.global) {
      this.global = {
        ws: new WsClient(`${this.urlBase}/ws/logs`, {
          onMessage: (d) => this.emitGlobal(d),
        }),
        subs: new Set(),
      }
    }
    this.global.subs.add(sub)
    return () => {
      this.global?.subs.delete(sub)
      if (this.global && this.global.subs.size === 0) {
        this.global.ws.stop()
        this.global = undefined
      }
    }
  }

  private unsubscribeNode(nodeId: string, sub: Sub) {
    const e = this.nodeMap.get(nodeId)
    if (!e) return
    e.subs.delete(sub)
    if (e.subs.size === 0) {
      e.ws.stop()
      this.nodeMap.delete(nodeId)
    }
  }

  private emit(nodeId: string, d: any) {
    const e = this.nodeMap.get(nodeId)
    if (!e) return
    e.subs.forEach((fn) => fn(d))
  }

  private emitGlobal(d: any) {
    if (!this.global) return
    this.global.subs.forEach((fn) => fn(d))
  }
}

