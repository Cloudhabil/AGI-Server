import React, { useState } from 'react'
import { apiLogin } from '../utils/api'
import { useStore } from '../state/store'
import { Dialog, DialogContent } from './ui/Dialog'

export default function LoginModal({ open, onClose, onSuccess }: { open: boolean; onClose: () => void; onSuccess: (role: string) => void }) {
  const [username, setUsername] = useState('dev')
  const [role, setRole] = useState('admin')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const addToast = useStore(s => s.addToast)
  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent title="Developer Login" onClose={onClose}>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2">
            <label className="w-20">Username</label>
            <input className="flex-1 px-2 py-1 border rounded-md" value={username} onChange={e => setUsername(e.target.value)} />
          </div>
          <div className="flex items-center gap-2">
            <label className="w-20">Role</label>
            <select className="flex-1 px-2 py-1 border rounded-md" value={role} onChange={e => setRole(e.target.value)}>
              <option value="admin">admin</option>
              <option value="operator">operator</option>
              <option value="viewer">viewer</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="w-20">Password</label>
            <input type="password" className="flex-1 px-2 py-1 border rounded-md" placeholder="optional (DEV_LOGIN_PASSWORD)" value={password} onChange={e => setPassword(e.target.value)} />
          </div>
          {error && <div className="text-red-600">{error}</div>}
          <div className="flex items-center justify-end gap-2 pt-2">
            <button className="px-2 py-1 text-xs border rounded-md" onClick={onClose}>Cancel</button>
            <button className="px-2 py-1 text-xs border rounded-md disabled:opacity-50" disabled={loading} onClick={async () => {
              setLoading(true); setError(null)
              try {
                const res = await apiLogin(username, role, password || undefined)
                onSuccess(res.role)
                onClose()
                addToast({ title: `Logged in as ${res.role}`, tone: 'success' })
              } catch (e: any) { setError(e.message || 'login failed') }
              finally { setLoading(false) }
            }}>{loading ? '...' : 'Login'}</button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
