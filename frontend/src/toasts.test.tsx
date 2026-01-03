import { describe, test, expect } from 'vitest'
import React from 'react'
import { createRoot } from 'react-dom/client'
import Toaster from './components/Toaster'
import { useStore } from './state/store'

describe('Toasts', () => {
  test('renders and dismisses toast', async () => {
    const div = document.createElement('div')
    document.body.appendChild(div)
    const root = createRoot(div)
    root.render(<Toaster />)

    const id = useStore.getState().addToast({ title: 'Hello Toast', message: 'details', tone: 'success', timeoutMs: 0 })
    // DOM update microtask
    await Promise.resolve()
    expect(div.textContent).toContain('Hello Toast')

    useStore.getState().dismissToast(id)
    await Promise.resolve()
    expect(div.textContent).not.toContain('Hello Toast')

    root.unmount()
  })
})

