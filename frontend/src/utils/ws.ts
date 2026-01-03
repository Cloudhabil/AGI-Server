import { useStore } from '../state/store'
import { API_TOKEN } from '../config'

type HandlerOpts = {
  onOpen?: () => void
  onClose?: (ev: CloseEvent) => void
  onError?: (ev: Event) => void
  onMessage?: (data: any) => void
  pingIntervalMs?: number
}

export class WsClient {
  private url: string
  private ws: WebSocket | null = null
  private stopped = false
  private attempts = 0
  private heartbeatTimer: any = null
  private sendQueue: any[] = []
  private opts: HandlerOpts

  constructor(url: string, opts: Partial<HandlerOpts> = {}) {
    this.url = url
    this.opts = { pingIntervalMs: 15000, ...opts }
    this.start()
    window.addEventListener('online', () => this.tryReconnectNow())
  }

  private start() {
    if (this.stopped) return
    useStore.getState().setWsConnectionStatus('connecting')
    const u = new URL(this.url)
    const tok = API_TOKEN
    if (tok) u.searchParams.set('token', tok)
    this.ws = new WebSocket(u.toString())
    this.ws.onopen = () => {
      this.attempts = 0
      useStore.getState().setWsConnectionStatus('open')
      this.opts.onOpen?.()
      const q = [...this.sendQueue]
      this.sendQueue = []
      q.forEach((m) => this.safeSend(m))
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = setInterval(
        () => this.safeSend({ type: 'ping', ts: Date.now() }),
        this.opts.pingIntervalMs
      )
    }
    this.ws.onclose = (ev) => {
      this.opts.onClose?.(ev)
      clearInterval(this.heartbeatTimer)
      useStore.getState().setWsConnectionStatus('closed')
      if (!this.stopped) {
        this.attempts += 1
        const base = Math.min(500 * Math.pow(2, this.attempts), 15000)
        const jitter = Math.floor(Math.random() * 400)
        setTimeout(() => this.start(), base + jitter)
      }
    }
    this.ws.onerror = (ev) => this.opts.onError?.(ev)
    this.ws.onmessage = (ev) => {
      try {
        this.opts.onMessage?.(JSON.parse(ev.data))
      } catch {
        this.opts.onMessage?.(ev.data)
      }
    }
  }

  private safeSend(obj: any) {
    if (this.ws && this.ws.readyState === 1) {
      try {
        this.ws.send(JSON.stringify(obj))
      } catch {}
    } else {
      this.sendQueue.push(obj)
    }
  }

  send(obj: any) {
    this.safeSend(obj)
  }

  tryReconnectNow() {
    if (!this.stopped && (!this.ws || this.ws.readyState !== 1)) this.start()
  }

  stop() {
    this.stopped = true
    clearInterval(this.heartbeatTimer)
    useStore.getState().setWsConnectionStatus('closed')
    try {
      this.ws?.close()
    } catch {}
  }
}

export function connectWS(url: string, handlers: HandlerOpts) {
  return new WsClient(url, handlers)
}

