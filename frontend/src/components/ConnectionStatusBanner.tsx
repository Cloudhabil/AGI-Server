import { useStore } from '../state/store'

export function ConnectionStatusBanner() {
  const status = useStore((s) => s.wsConnectionStatus)
  if (status === 'open') return null
  const messages = {
    connecting: {
      text: 'Reconnecting to the mothership...',
      color: 'bg-yellow-500',
    },
    closed: {
      text: 'Connection lost. We are trying to reconnect.',
      color: 'bg-red-500',
    },
  } as const
  const m = messages[status as 'connecting' | 'closed']
  return (
    <div
      className={`fixed top-0 left-0 right-0 p-2 text-center text-white text-sm ${m.color} z-50`}
    >
      {m.text}
    </div>
  )
}

