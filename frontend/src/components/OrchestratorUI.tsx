import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { API_BASE, API_TOKEN } from "../config";
import { withBackoff } from "../utils/sse";
import { apiChat, apiKbSemanticSearch, apiSseToken } from "../utils/api";
import AgentsPanel from "./AgentsPanel";
import KBPanel from "./KBPanel";
import BusConsole from "./BusConsole";
import ConnectorsPanel from "./ConnectorsPanel";
import LoginModal from "./LoginModal";
import Button from "./ui/Button";
import { apiAgentAction, apiGetAgents } from "../utils/api";
import { useStore } from "../state/store";
import * as Checkbox from "@radix-ui/react-checkbox";
import * as Switch from "@radix-ui/react-switch";

// Types
type NodeStatus = "idle" | "starting" | "running" | "error" | "stopped";
type TTier = "Trace" | "Transform" | "Transfer" | "Translate" | "Transmit";

interface OrchestratorEvent {
  id: string;
  ts: string;
  tier: TTier;
  severity: "S1" | "S2" | "S3" | "S4";
  title: string;
  details?: string;
  traceId?: string;
  ticketKey?: string;
}

interface ServiceNode {
  id: string;
  name: string;
  status: NodeStatus;
  version?: string;
}

const T_TIERS: TTier[] = ["Trace", "Transform", "Transfer", "Translate", "Transmit"];

const statusColor: Record<NodeStatus, string> = {
  idle: "bg-gray-300",
  starting: "bg-amber-400 animate-pulse",
  running: "bg-green-500",
  error: "bg-red-500",
  stopped: "bg-slate-400",
};

function Pill({ children, active }: { children: React.ReactNode; active?: boolean }) {
  return (
    <span
      className={
        "px-3 py-1 rounded-full text-xs font-medium border " +
        (active ? "bg-black text-white border-black" : "bg-white text-slate-800 border-slate-200")
      }
    >
      {children}
    </span>
  );
}

function Badge({ tone = "default", children }: { tone?: "default" | "ok" | "warn" | "err"; children: React.ReactNode }) {
  const tones: Record<string, string> = {
    default: "bg-slate-100 text-slate-700",
    ok: "bg-green-100 text-green-700",
    warn: "bg-amber-100 text-amber-800",
    err: "bg-red-100 text-red-700",
  };
  return <span className={`px-2 py-0.5 rounded-md text-xs font-medium ${tones[tone]}`}>{children}</span>;
}

function NodeCard({ node, onAction }: { node: ServiceNode; onAction: (id: string, action: string) => void }) {
  return (
    <div className="group border rounded-2xl p-3 bg-white shadow-sm hover:shadow flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className={`inline-block w-2.5 h-2.5 rounded-full ${statusColor[node.status]}`} />
        <div>
          <div className="text-sm font-semibold">{node.name}</div>
          <div className="text-xs text-slate-500">{node.version ?? "v1.0.0"}</div>
        </div>
      </div>
      <div className="flex gap-1 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition">
        <button className="px-2 py-1 text-xs border rounded-md" onClick={() => onAction(node.id, "start")}>Start</button>
        <button className="px-2 py-1 text-xs border rounded-md" onClick={() => onAction(node.id, "stop")}>Stop</button>
        <button className="px-2 py-1 text-xs border rounded-md" onClick={() => onAction(node.id, "configure")}>Config</button>
        <button className="px-2 py-1 text-xs border rounded-md" onClick={() => onAction(node.id, "logs")}>Logs</button>
      </div>
    </div>
  );
}

function CommandPalette({ open, onClose, onRun }: { open: boolean; onClose: () => void; onRun: (cmd: string) => void }) {
  const [query, setQuery] = useState("");
  const options = useMemo(
    () =>
      ["SesamAwake", "Start all nodes", "Stop all nodes", "Open incident dashboard", "Ping health"].filter((x) =>
        x.toLowerCase().includes(query.toLowerCase())
      ),
    [query]
  );
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-start justify-center pt-24" onClick={onClose}>
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-xl border" onClick={(e) => e.stopPropagation()}>
        <div className="p-3 border-b">
          <input
            autoFocus
            className="w-full outline-none text-sm px-3 py-2 rounded-md bg-slate-50"
            placeholder="Type a command..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Escape") onClose();
            }}
          />
        </div>
        <ul className="max-h-64 overflow-auto">
          {options.map((opt) => (
            <li key={opt}>
              <button
                className="w-full text-left px-4 py-2 hover:bg-slate-50"
                onClick={() => {
                  onRun(opt);
                  onClose();
                }}
              >
                {opt}
              </button>
            </li>
          ))}
          {options.length === 0 && <li className="px-4 py-6 text-sm text-slate-500">No results</li>}
        </ul>
        <div className="p-2 border-t text-xs text-slate-500">Esc to close</div>
      </div>
    </div>
  );
}

export default function OrchestratorUI() {
  const [nodes, setNodes] = useState<ServiceNode[]>([]);
  const [events, setEvents] = useState<OrchestratorEvent[]>([]);
  const [activeTier, setActiveTier] = useState<TTier>("Trace");
  const [kpis, setKpis] = useState({ mttr: 0, sla: 0, cost: 0 });
  const [logs, setLogs] = useState<string[]>([]);
  const logsEndRef = useRef<HTMLDivElement | null>(null);
  const [logKinds, setLogKinds] = useState<{ [k: string]: boolean }>({ bus_message: true, connector_log: true, http_response: true });
  const [logRunId, setLogRunId] = useState<string>("");
  const [logsPaused, setLogsPaused] = useState(false);
  const [chatNode, setChatNode] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<{ from: string; text: string; ts: string }[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [useMemory, setUseMemory] = useState(true);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const dropRef = useRef<HTMLDivElement | null>(null);
  const [loginOpen, setLoginOpen] = useState(false);
  const [userRole, setUserRole] = useState<string>(() => {
    try { return localStorage.getItem('userRole') || 'admin' } catch { return 'admin' }
  });
  const addToast = useStore(s => s.addToast)

  const postEvent = useCallback(
    (tier: TTier, title: string, severity: OrchestratorEvent["severity"], details?: string) => {
      const evt: OrchestratorEvent = {
        id: crypto.randomUUID(),
        ts: new Date().toISOString(),
        tier,
        severity,
        title,
        details,
      };
      setEvents((e) => [evt, ...e].slice(0, 200));
      setActiveTier(tier);
    },
    []
  );

  const wsBase = API_BASE.replace(/^http/i, "ws");

  // Logs SSE stream with filters + backoff (dev SSE token) + resumable last_id + status toasts
  useEffect(() => {
    if (logsPaused) return
    let stop = () => {}
    let lastId = 0
    let showedErrorToast = false
    ;(async () => {
      try {
        const tok = await apiSseToken()
        const disposer = withBackoff(() => {
          const url = new URL(`${API_BASE}/api/logs/sse`)
          const kinds = Object.entries(logKinds).filter(([k, v]) => v).map(([k]) => k)
          if (kinds.length) url.searchParams.set('kinds', kinds.join(','))
          if (logRunId.trim()) url.searchParams.set('run_id', logRunId.trim())
          url.searchParams.set('sse', tok.sse)
          if (lastId > 0) url.searchParams.set('last_id', String(lastId))
          return new EventSource(url.toString())
        }, (ev) => {
          try { const obj = JSON.parse(ev.data); lastId = Number(obj.id) || lastId; setLogs(l => [...l, `${obj.kind}: ${JSON.stringify(obj.data)}`].slice(-500)) }
          catch { setLogs(l => [...l, String(ev.data)].slice(-500)) }
        }, (st) => {
          if (typeof st === 'string') {
            setLogs(l => [...l, `[sse] ${st}`].slice(-500))
            if (st === 'error' && !showedErrorToast) { addToast({ title: 'Logs stream error', tone: 'warn' }); showedErrorToast = true }
            if (st === 'open') { showedErrorToast = false; addToast({ title: 'Logs stream connected', tone: 'success', timeoutMs: 2000 }) }
          }
        })
        stop = disposer
      } catch (e: any) {
        setLogs(l => [...l, `[sse] token error: ${e?.message || e}`].slice(-500))
        addToast({ title: 'Logs SSE token error', message: e?.message || String(e), tone: 'error' })
      }
    })()
    return () => stop()
  }, [logKinds.bus_message, logKinds.connector_log, logKinds.http_response, logRunId, logsPaused])

  // Auto scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [logs]);

  // Initial agents fetch
  useEffect(() => {
    (async () => {
      try {
        const res = await apiGetAgents();
        const items = res.items.map((a: any) => ({ id: a.id, name: a.name, status: (a.status || 'stopped') as NodeStatus }));
        setNodes(items);
      } catch {
        // fallback placeholders
        setNodes([
          { id: "orchestrator", name: "Orchestrator", status: "running" },
          { id: "agent-1", name: "Agent 1", status: "stopped" },
          { id: "agent-2", name: "Agent 2", status: "stopped" },
        ]);
      }
    })();
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const isMod = e.ctrlKey || e.metaKey;
      if (isMod && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen((v) => !v);
      }
      if (e.key === "?" && !isMod) {
        alert("Shortcuts:\nCtrl or Cmd K: Command palette\n/ focus search\nS start all nodes\nX stop all nodes");
      }
      if (e.key.toLowerCase() === "s" && !isMod) {
        startAll();
      }
      if (e.key.toLowerCase() === "x" && !isMod) {
        stopAll();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // Drag and drop upload
  useEffect(() => {
    const el = dropRef.current;
    if (!el) return;
    const prevent = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
    };
    const drop = async (e: DragEvent) => {
      prevent(e);
      if (!e.dataTransfer) return;
      const files = Array.from(e.dataTransfer.files);
      if (files.length === 0) return;
      const form = new FormData();
      files.forEach((f) => form.append("files", f));
      postEvent("Trace", `Uploading ${files.length} file(s)`, "S4");
      try {
        const res = await fetch(`${API_BASE}/api/files/upload`, {
          method: "POST",
          headers: { Authorization: `Bearer ${API_TOKEN}` },
          body: form,
        });
        if (!res.ok) throw new Error(`upload failed ${res.status}`);
        postEvent("Transform", "Files indexed in KB", "S4");
      } catch (err: any) {
        postEvent("Transfer", `Upload error: ${err.message}`, "S3");
      }
    };
    el.addEventListener("dragenter", prevent);
    el.addEventListener("dragover", prevent);
    el.addEventListener("drop", drop);
    return () => {
      el.removeEventListener("dragenter", prevent);
      el.removeEventListener("dragover", prevent);
      el.removeEventListener("drop", drop);
    };
  }, [postEvent]);

  const runSesamAwake = useCallback(async () => {
    postEvent("Trace", "SesamAwake requested", "S4");
    try {
      const res = await fetch(`${API_BASE}/api/actions/sesamawake`, {
        method: "POST",
        headers: { Authorization: `Bearer ${API_TOKEN}` },
      });
      if (!res.ok) throw new Error(`status ${res.status}`);
      postEvent("Transform", "Services configured", "S4");
      postEvent("Transfer", "Ticket created OPS-123", "S4");
      postEvent("Translate", "Slack summary posted", "S4");
      postEvent("Transmit", "KPIs updated", "S4");
      addToast({ title: 'SesamAwake executed', tone: 'success' })
    } catch (e: any) {
      postEvent("Trace", `SesamAwake failed: ${e.message}`, "S2");
      addToast({ title: 'SesamAwake failed', message: e.message || 'error', tone: 'error' })
    }
  }, [postEvent]);

  const startAll = () => {
    setNodes((n) => n.map((x) => ({ ...x, status: x.status === "running" ? "running" : "starting" })));
    postEvent("Trace", "Starting all nodes", "S4");
    setTimeout(() => setNodes((n) => n.map((x) => ({ ...x, status: x.status === "starting" ? "running" : x.status }))), 1200);
  };
  const stopAll = () => {
    setNodes((n) => n.map((x) => ({ ...x, status: "stopped" })));
    postEvent("Trace", "Stopped all nodes", "S4");
  };

  const handleNodeAction = async (id: string, action: string) => {
    if (action === "configure") return alert(`Configure ${id}`);
    if (action === "logs") return setActiveTier("Trace");
    if (action !== "start" && action !== "stop" && action !== "wake") return;
    try {
      await apiAgentAction(id, action as any);
      setNodes((n) => n.map((x) => (x.id === id ? { ...x, status: action === 'start' ? 'running' : action === 'stop' ? 'stopped' : x.status } : x)));
      postEvent("Trace", `${action} ${id}`, "S4");
    } catch (e: any) {
      postEvent("Trace", `${action} failed for ${id}: ${e.message}`, "S2");
    }
  };

  // Reset chat when node changes
  useEffect(() => { setChatMessages([]) }, [chatNode])

  // KPI simulation from events
  useEffect(() => {
    const mttr = Math.min(3600, events.length * 12);
    const sla = events.filter((e) => e.severity === "S1" || e.severity === "S2").length;
    const cost = events.length * 3.5;
    setKpis({ mttr, sla, cost: Number(cost.toFixed(2)) });
  }, [events.length]);

  const onRunCommand = (cmd: string) => {
    if (cmd === "SesamAwake") runSesamAwake();
    if (cmd === "Start all nodes") startAll();
    if (cmd === "Stop all nodes") stopAll();
    if (cmd === "Open incident dashboard") setActiveTier("Transmit");
    if (cmd === "Ping health") postEvent("Trace", "Health ok", "S4");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Top bar */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur border-b">
        <div className="max-w-7xl mx-auto px-4 py-2 flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-xl bg-black text-white grid place-items-center font-bold">CH</div>
            <div className="font-semibold">Cloudhabil Orchestrator</div>
          </div>
          <div className="flex-1" />
          <div className="hidden md:flex items-center gap-2">
            <Pill>MTTR {kpis.mttr}s</Pill>
            <Pill>SLA breaches {kpis.sla}</Pill>
            <Pill>Cost €{kpis.cost}</Pill>
          </div>
          <Button tone="primary" size="md" className="ml-3" onClick={runSesamAwake} title="Start the company">SesamAwake</Button>
        </div>
        {/* Five T pipeline */}
        <div className="max-w-7xl mx-auto px-4 pb-2">
          <div className="flex items-center gap-2 overflow-x-auto">
            {T_TIERS.map((t, i) => (
              <div key={t} className="flex items-center gap-2">
                <button
                  className={`px-3 py-1.5 rounded-full text-sm border ${
                    activeTier === t ? "bg-black text-white border-black" : "bg-white"
                  }`}
                  onClick={() => setActiveTier(t)}
                >
                  {t}
                </button>
                {i < T_TIERS.length - 1 && <div className="w-8 h-px bg-slate-300" />}
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* Role bar */}
      <div className="max-w-7xl mx-auto px-4 -mb-2 mt-2 flex items-center justify-between text-xs">
        <div className="text-slate-600">Role: <span className="font-medium">{userRole}</span></div>
        <div className="flex items-center gap-2">
          <button className="px-2 py-1 border rounded-md" onClick={() => setLoginOpen(true)}>Login</button>
          <button className="px-2 py-1 border rounded-md" onClick={() => { try { localStorage.removeItem('userRole') } catch {}; setUserRole('viewer') }}>Logout</button>
        </div>
      </div>

      {/* Main three-panel layout */}
      <main className="max-w-7xl mx-auto px-4 py-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left: Nodes */}
        <section className="lg:col-span-3 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Nodes</h2>
            <div className="flex gap-2">
              <button className="px-2 py-1 text-xs border rounded-md" onClick={startAll}>Start all</button>
              <button className="px-2 py-1 text-xs border rounded-md" onClick={stopAll}>Stop all</button>
            </div>
          </div>
          <div className="flex flex-col gap-2">
            {nodes.map((n) => (
              <NodeCard key={n.id} node={n} onAction={handleNodeAction} />
            ))}
          </div>
          <div className="mt-2">
            <h3 className="text-xs font-semibold mb-1">Chat dock</h3>
            <div className="flex flex-wrap gap-2">
              {nodes.map((n) => (
                <button
                  key={n.id}
                  className={`px-2 py-1 text-xs rounded-md border ${
                    chatNode === n.id ? "bg-black text-white border-black" : "bg-white"
                  }`}
                  onClick={() => setChatNode(n.id)}
                >
                  {n.name}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Center: Green field drop zone */}
        <section className="lg:col-span-6">
          <div
            ref={dropRef}
            className="border-2 border-dashed rounded-3xl bg-white shadow-sm p-6 min-h-[340px] grid place-items-center text-center hover:bg-slate-50"
          >
            <div>
              <div className="text-lg font-semibold">Green field</div>
              <p className="text-sm text-slate-500">
                Drop files here to upload and index. They will be sent to /api/files/upload.
              </p>
              <div className="mt-4 flex items-center justify-center gap-2">
                <Badge tone="default">Trace</Badge>
                <Badge tone="ok">Transform</Badge>
                <Badge tone="default">Transfer</Badge>
                <Badge tone="default">Translate</Badge>
                <Badge tone="default">Transmit</Badge>
              </div>
            </div>
          </div>

          {/* Incident timeline */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-semibold">Incident timeline</h2>
              <span className="text-xs text-slate-500">Newest first</span>
            </div>
            <ul className="space-y-2">
              {events.slice(0, 12).map((e) => (
                <li key={e.id} className="border rounded-2xl bg-white p-3">
                  <div className="flex items-center gap-2">
                    <Badge tone={e.severity === "S1" ? "err" : e.severity === "S2" ? "warn" : "default"}>{e.severity}</Badge>
                    <span className="text-xs text-slate-500">{new Date(e.ts).toLocaleTimeString()}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100">{e.tier}</span>
                    <span className="text-sm font-medium">{e.title}</span>
                  </div>
                  {e.details && <div className="text-xs mt-1 text-slate-600">{e.details}</div>}
                </li>
              ))}
              {events.length === 0 && <li className="text-sm text-slate-500">No events yet</li>}
            </ul>
          </div>

          {/* Bus Console */}
          <div className="mt-4">
            <BusConsole />
          </div>
        </section>

        {/* Right: Live logs and chat */}
        <section className="lg:col-span-3 flex flex-col gap-3">
          <AgentsPanel />
          <div className="border rounded-2xl bg-white overflow-hidden">
            <div className="px-3 py-2 border-b flex items-center justify-between">
              <h3 className="text-sm font-semibold">Live logs</h3>
              <div className="flex items-center gap-2">
                <label className="text-[11px] text-slate-600">Kinds:</label>
                <label className="text-[11px] flex items-center gap-1">
                  <Checkbox.Root checked={!!logKinds.bus_message} onCheckedChange={v => setLogKinds(x => ({...x, bus_message: !!v}))} className="w-3.5 h-3.5 border rounded" /> bus
                </label>
                <label className="text-[11px] flex items-center gap-1">
                  <Checkbox.Root checked={!!logKinds.connector_log} onCheckedChange={v => setLogKinds(x => ({...x, connector_log: !!v}))} className="w-3.5 h-3.5 border rounded" /> connector
                </label>
                <label className="text-[11px] flex items-center gap-1">
                  <Checkbox.Root checked={!!logKinds.http_response} onCheckedChange={v => setLogKinds(x => ({...x, http_response: !!v}))} className="w-3.5 h-3.5 border rounded" /> http
                </label>
                <input className="text-[11px] px-2 py-1 border rounded-md" placeholder="run_id" value={logRunId} onChange={e => setLogRunId(e.target.value)} />
                <label className="text-[11px] flex items-center gap-1">
                  <Switch.Root checked={logsPaused} onCheckedChange={(v) => setLogsPaused(!!v)} className="w-9 h-5 bg-slate-300 data-[state=checked]:bg-black rounded-full relative">
                    <Switch.Thumb className="block w-4 h-4 bg-white rounded-full transform translate-x-0.5 data-[state=checked]:translate-x-[18px] transition" />
                  </Switch.Root>
                  {logsPaused ? 'Paused' : 'Live'}
                </label>
                <button className="px-2 py-1 text-[11px] border rounded-md" onClick={() => setLogs([])}>Clear</button>
              </div>
            </div>
            <div className="h-48 overflow-auto font-mono text-xs px-3 py-2 space-y-1">
              {logs.map((l, i) => (
                <div key={i} className="whitespace-pre-wrap break-words">{l}</div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>

          <div className="border rounded-2xl bg-white overflow-hidden">
            <div className="px-3 py-2 border-b flex items-center justify-between">
              <h3 className="text-sm font-semibold">Chat</h3>
              <Badge tone="default">{chatNode ? chatNode : "select node"}</Badge>
            </div>
            <div className="h-48 overflow-auto px-3 py-2 space-y-2">
              {chatMessages.map((m, idx) => (
                <div key={idx} className="text-xs">
                  <span className="font-semibold">{m.from}</span>{" "}
                  <span className="text-slate-500">{new Date(m.ts).toLocaleTimeString()}</span>
                  <div>{m.text}</div>
                </div>
              ))}
              {chatMessages.length === 0 && <div className="text-sm text-slate-500">No chat yet</div>}
            </div>
            <div className="px-3 py-2 border-t space-y-2">
              <div className="flex items-center gap-2">
                <input className="flex-1 text-xs px-2 py-1 border rounded-md" placeholder="Type a message..." value={chatInput} onChange={e => setChatInput(e.target.value)} />
                <label className="text-[11px] flex items-center gap-1">
                  <Switch.Root checked={useMemory} onCheckedChange={setUseMemory as any} className="w-9 h-5 bg-slate-300 data-[state=checked]:bg-black rounded-full relative">
                    <Switch.Thumb className="block w-4 h-4 bg-white rounded-full transform translate-x-0.5 data-[state=checked]:translate-x-[18px] transition" />
                  </Switch.Root>
                  Use memory
                </label>
                <button className="px-2 py-1 text-xs border rounded-md" onClick={async () => {
                  if (!chatInput.trim()) return
                  let text = chatInput.trim()
                  if (useMemory) {
                    try {
                      const res = await apiKbSemanticSearch(text, 3)
                      const cites = res.items.map((it, i) => `(${i+1}) [${it.kind}] ${JSON.stringify(it.data).slice(0,200)}`).join('\n')
                      text = `Context:\n${cites}\n\nUser: ${text}`
                    } catch {}
                  }
                  try {
                    const r = await apiChat(text)
                    const now = new Date().toISOString()
                    setChatMessages(m => [{ from: 'assistant', text: r.response, ts: now }, { from: 'user', text: chatInput, ts: now }, ...m].slice(0, 200))
                    setChatInput('')
                  } catch (e: any) {
                    setChatMessages(m => [{ from: 'system', text: `error: ${e.message}`, ts: new Date().toISOString() }, ...m])
                  }
                }}>Send</button>
              </div>
              <div className="text-[11px] text-slate-500">When enabled, top summaries from the Knowledge Base are included as context.</div>
            </div>
          </div>

          <KBPanel />
          <ConnectorsPanel />
        </section>
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-slate-500">
        Press Ctrl or Cmd K for the command palette. S to start all, X to stop all.
      </footer>

      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} onRun={onRunCommand} />
      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} onSuccess={(r) => { try { localStorage.setItem('userRole', r) } catch {}; setUserRole(r) }} />
    </div>
  );
}

