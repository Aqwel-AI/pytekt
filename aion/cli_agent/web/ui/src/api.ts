export interface SessionInfo {
  connected: boolean;
  provider: string | null;
  model: string | null;
  mode: string;
  trust: boolean;
  tools_enabled: boolean;
  force_tools: boolean;
  pinned_paths: string[];
  pending_plan: boolean;
  workspace: string;
  project: string | null;
  plan_steps: string[];
}

export interface ProviderInfo {
  id: string;
  label: string;
  env_var?: string;
  ready: boolean;
}

export interface ActivityEvent {
  kind: string;
  detail: string;
  ts: string;
}

export interface PendingApproval {
  id: string;
  path: string;
  tool: string;
  diff: string;
}

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init);
  return res.json() as Promise<T>;
}

export const api = {
  info: () => json<{ version: string; workspace: string }>("/api/info"),
  session: () => json<SessionInfo>("/api/session"),
  providers: () => json<{ providers: ProviderInfo[] }>("/api/providers"),
  models: (id: string) => json<{ ok: boolean; models?: string[]; error?: string }>(`/api/providers/${id}/models`),
  connect: (provider: string, model?: string, api_key?: string) =>
    json<{ ok: boolean; error?: string }>("/api/connect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, model, api_key }),
    }),
  disconnect: () => json("/api/disconnect", { method: "POST" }),
  setMode: (mode: string) =>
    json("/api/mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    }),
  setTrust: (trusted: boolean) =>
    json("/api/trust", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ trusted }),
    }),
  chat: (message: string) =>
    json<{ ok: boolean; response?: string; error?: string }>("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    }),
  pin: (path: string) =>
    json("/api/pin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    }),
  unpin: (path?: string) =>
    json("/api/unpin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    }),
  undo: () => json<{ ok: boolean; message?: string }>("/api/undo", { method: "POST" }),
  reset: () => json("/api/reset", { method: "POST" }),
  slash: (line: string) =>
    json<{ ok: boolean; response?: string; message?: string; error?: string; action?: string; url?: string }>(
      "/api/slash",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ line }),
      },
    ),
  activity: (limit = 20) => json<{ events: ActivityEvent[] }>(`/api/activity?limit=${limit}`),
  files: (path = ".") => json<{ entries: string[] }>(`/api/files?path=${encodeURIComponent(path)}`),
  file: (path: string) => json<{ content: string }>(`/api/file?path=${encodeURIComponent(path)}`),
  pending: () => json<{ pending: PendingApproval[] }>("/api/pending"),
  approve: (id: string, action: "accept" | "reject" | "accept_all") =>
    json("/api/approve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, action }),
    }),
  command: (cmd: string, args = "") =>
    json<{ ok: boolean; response?: string; error?: string }>("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd, args }),
    }),
  openFiles: (paths: string[]) =>
    json("/api/open-files", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paths }),
    }),
};

export function streamChat(
  message: string,
  onEvent: (data: Record<string, unknown>) => void,
): () => void {
  const url = `/api/chat/stream?message=${encodeURIComponent(message)}`;
  const es = new EventSource(url);
  es.onmessage = (ev) => {
    try {
      onEvent(JSON.parse(ev.data));
    } catch {
      /* ignore */
    }
  };
  es.onerror = () => es.close();
  return () => es.close();
}

export function streamEvents(onEvent: (data: Record<string, unknown>) => void): () => void {
  let es: EventSource | null = null;
  let closed = false;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  const connect = () => {
    if (closed) return;
    es = new EventSource("/api/events/stream");
    es.onmessage = (ev) => {
      try {
        onEvent(JSON.parse(ev.data));
      } catch {
        /* ignore */
      }
    };
    es.onerror = () => {
      es?.close();
      es = null;
      if (!closed) {
        reconnectTimer = setTimeout(connect, 2000);
      }
    };
  };

  connect();
  return () => {
    closed = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    es?.close();
  };
}
