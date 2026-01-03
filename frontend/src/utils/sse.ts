export function withBackoff(connect: () => EventSource, onEvent: (ev: MessageEvent) => void, onStatus?: (status: string) => void) {
  let es: EventSource | null = null
  let attempts = 0
  let closed = false
  const maxDelay = 15000

  function open() {
    if (closed) return
    try {
      es = connect()
      onStatus && onStatus('open')
      attempts = 0
      es.onmessage = onEvent
      es.onerror = () => {
        onStatus && onStatus('error')
        es && es.close()
        reconnect()
      }
    } catch {
      reconnect()
    }
  }

  function reconnect() {
    if (closed) return
    attempts++
    const delay = Math.min(maxDelay, 500 * Math.pow(2, attempts)) + Math.floor(Math.random() * 500)
    onStatus && onStatus(`reconnect in ${delay}ms`)
    setTimeout(open, delay)
  }

  open()
  return () => { closed = true; es && es.close() }
}

