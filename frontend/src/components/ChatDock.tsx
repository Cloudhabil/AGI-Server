import { useEffect, useRef, useState } from 'react';
import { useStore } from '../state/store';
import { ChatChannel } from '../channels/chat';
import { API_BASE, API_TOKEN } from '../config';

const CHAT = new ChatChannel(API_BASE);

export default function ChatDock() {
  const nodeId = useStore((s) => s.selectedNodeId);
  const setSelected = useStore((s) => s.setSelected);
  const ensureChat = useStore((s) => s.ensureChat);
  const setStatus = useStore((s) => s.setChatStatus);
  const append = useStore((s) => s.appendMsg);
  const markSeeded = useStore((s) => s.markSeeded);
  const chat = useStore((s) => (nodeId ? s.chat[nodeId] : undefined));

  const [input, setInput] = useState('');
  const unsubRef = useRef<null | (() => void)>(null);

  useEffect(() => {
    if (!nodeId) return;
    ensureChat(nodeId);
    setStatus(nodeId, 'connecting');
    unsubRef.current?.();
    unsubRef.current = CHAT.subscribe(nodeId, (data) => {
      if (!data || typeof data !== 'object') return;
      if (data.type === 'hello') setStatus(nodeId, 'open');
      if (data.type === 'message')
        append(nodeId, {
          id: crypto.randomUUID(),
          role: data.role || 'system',
          text: data.text || '',
          ts: Date.now(),
        });
      if (data.type === 'token') {
        append(nodeId, {
          id: 'stream',
          role: 'assistant',
          text:
            (chat?.messages?.filter((m) => m.id === 'stream')[0]?.text || '') +
            data.text,
          ts: Date.now(),
        });
      }
    });
    return () => {
      unsubRef.current?.();
      unsubRef.current = null;
    };
  }, [nodeId]);

  if (!nodeId || !chat) return null;

  const send = async () => {
    const text = input.trim();
    if (!text) return;
    if (!chat.seeded) {
      try {
        await fetch(`${API_BASE}/api/chat/${nodeId}/seed`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_TOKEN}` },
          body: JSON.stringify({ text, meta: { source: 'ui' } }),
        });
        markSeeded(nodeId);
      } catch (error) {
        console.error('Failed to seed chat:', error);
      }
    }
    append(nodeId, {
      id: crypto.randomUUID(),
      role: 'user',
      text,
      ts: Date.now(),
    });
    CHAT.send(nodeId, { type: 'send', msg_id: crypto.randomUUID(), text });
    setInput('');
  };

  return (
    <div className="absolute right-4 bottom-4 w-[460px] h-[460px] bg-white rounded-2xl shadow-xl border flex flex-col">
      <div className="p-3 border-b flex items-center justify-between">
        <div className="font-semibold">Chat • {nodeId}</div>
        <div className="text-xs text-gray-500">{chat.status}</div>
        <button className="text-sm underline" onClick={() => setSelected(null)}>
          Close
        </button>
      </div>
      <div className="flex-1 overflow-auto p-3 space-y-2 text-sm">
        {chat.messages.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <div
              className={`inline-block px-3 py-2 rounded-xl ${
                m.role === 'user' ? 'bg-black text-white' : 'bg-gray-100'
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
      </div>
      <div className="p-3 border-t flex gap-2">
        <input
          className="flex-1 border rounded px-2 py-1"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder={chat.seeded ? 'Type a message' : 'Type to seed and send'}
        />
        <button
          className="px-3 py-1 rounded bg-black text-white"
          onClick={send}
          disabled={chat.status !== 'open'}
        >
          Send
        </button>
      </div>
    </div>
  );
}
