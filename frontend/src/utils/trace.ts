let cachedTraceId: string | null = null

const fallbackUuid = (): string => {
  const s4 = () => Math.floor((1 + Math.random()) * 0x10000).toString(16).slice(1)
  return `${s4()}${s4()}-${s4()}-${s4()}-${s4()}-${s4()}${s4()}${s4()}`
}

export const getTraceId = (): string => {
  if (cachedTraceId) return cachedTraceId
  try {
    cachedTraceId = crypto.randomUUID()
  } catch {
    cachedTraceId = fallbackUuid()
  }
  return cachedTraceId
}
