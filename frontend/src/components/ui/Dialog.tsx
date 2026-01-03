import * as RD from '@radix-ui/react-dialog'
import React from 'react'

export function Dialog({ open, onOpenChange, children }: { open: boolean; onOpenChange: (o: boolean) => void; children: React.ReactNode }) {
  return (
    <RD.Root open={open} onOpenChange={onOpenChange}>
      {children}
    </RD.Root>
  )
}

export function DialogContent({ title, children, onClose }: { title: string; children: React.ReactNode; onClose?: () => void }) {
  return (
    <RD.Portal>
      <RD.Overlay className="fixed inset-0 bg-black/40" />
      <RD.Content className="fixed inset-0 z-50 grid place-items-center">
        <div className="bg-white rounded-2xl shadow-xl border w-full max-w-sm p-4">
          <div className="flex items-center justify-between mb-2">
            <RD.Title className="text-sm font-semibold">{title}</RD.Title>
            <RD.Close asChild>
              <button className="text-xs px-2 py-1 border rounded-md" onClick={onClose}>Close</button>
            </RD.Close>
          </div>
          {children}
        </div>
      </RD.Content>
    </RD.Portal>
  )
}

