import { useCallback, useEffect, useRef, useState } from "react";
import {
  ActivityEvent,
  PendingApproval,
  SessionInfo,
  api,
  streamChat,
  streamEvents,
} from "./api";
import { ActivityPanel } from "./components/ActivityPanel";
import { ChatPanel, Message } from "./components/ChatPanel";
import { DiffApprovalModal } from "./components/DiffApprovalModal";
import { FileTree } from "./components/FileTree";
import { InputBar } from "./components/InputBar";
import { PlanBanner, approvePlan } from "./components/PlanBanner";
import { SessionBar } from "./components/SessionBar";
import { SlashHelp } from "./components/SlashHelp";
import { ThinkingBar } from "./components/ThinkingBar";
import "./index.css";

function toolLabel(ev: Record<string, unknown>): string {
  return `${ev.action}: ${ev.preview}`;
}

export default function App() {
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [activity, setActivity] = useState<ActivityEvent[]>([]);
  const [files, setFiles] = useState<string[]>([]);
  const [pending, setPending] = useState<PendingApproval | null>(null);
  const [busy, setBusy] = useState(false);
  const [thinkingStatus, setThinkingStatus] = useState("");
  const [draft, setDraft] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const fileCache = useRef<string[]>([]);
  const tokenBuffer = useRef("");
  const rafId = useRef<number | null>(null);

  const clearChat = useCallback(() => setMessages([]), []);

  const refreshSession = useCallback(async () => {
    try {
      const [s, a] = await Promise.all([api.session(), api.activity(30)]);
      setSession(s);
      setActivity(a.events);
      const p = await api.pending();
      if (p.pending.length > 0) setPending(p.pending[0]);
    } catch {
      /* server may be starting or temporarily unreachable */
    }
  }, []);

  const refreshFiles = useCallback(async () => {
    const f = await api.files(".");
    fileCache.current = f.entries;
    setFiles(f.entries);
  }, []);

  const openDrawer = useCallback(() => {
    setDrawerOpen(true);
    refreshFiles();
  }, [refreshFiles]);

  const applyProgressEvent = useCallback((ev: Record<string, unknown>) => {
    if (ev.type === "chat_status") {
      setThinkingStatus(String(ev.text || "Thinking…"));
    }
    if (ev.type === "tool_step") {
      const label = toolLabel(ev);
      setThinkingStatus(label);
      setActivity((prev) => [
        ...prev,
        {
          kind: "tool",
          detail: label,
          ts: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    }
    if (ev.type === "plan_ready") {
      refreshSession();
    }
    if (ev.type === "approval_required") {
      setPending({
        id: String(ev.id),
        path: String(ev.path),
        tool: String(ev.tool),
        diff: String(ev.diff),
      });
    }
  }, [refreshSession]);

  useEffect(() => {
    refreshSession();
    const stop = streamEvents((ev) => {
      if (ev.type === "memory_cleared") clearChat();
      if (ev.type === "approval_required") {
        setPending({
          id: String(ev.id),
          path: String(ev.path),
          tool: String(ev.tool),
          diff: String(ev.diff),
        });
      }
      if (ev.type === "session_updated") refreshSession();
      if (ev.type === "chat_status" && busy) {
        setThinkingStatus(String(ev.text || "Thinking…"));
      }
      if (ev.type === "tool_step") {
        applyProgressEvent(ev);
      }
      if (ev.type === "plan_ready") {
        refreshSession();
      }
    });
    return stop;
  }, [refreshSession, clearChat, busy, applyProgressEvent]);

  const flushTokens = useCallback(() => {
    const chunk = tokenBuffer.current;
    if (!chunk) return;
    tokenBuffer.current = "";
    setMessages((msgs) => {
      const copy = [...msgs];
      const last = copy[copy.length - 1];
      if (last?.role === "assistant") {
        copy[copy.length - 1] = {
          ...last,
          content: last.content + chunk,
          streaming: true,
        };
      }
      return copy;
    });
  }, []);

  const scheduleTokenFlush = useCallback(() => {
    if (rafId.current != null) return;
    rafId.current = requestAnimationFrame(() => {
      rafId.current = null;
      flushTokens();
    });
  }, [flushTokens]);

  const handleNewChat = () => {
    api.reset();
    clearChat();
  };

  const handleSlash = async (line: string) => {
    if (line === "/help") {
      setShowHelp(true);
      return;
    }
    setMessages((m) => [...m, { role: "user", content: line }]);
    const r = await api.slash(line);
    if (r.action === "open_url" && r.url) {
      window.open(String(r.url), "_blank");
    }
    const text = r.response || r.message || r.error || "Done.";
    setMessages((m) => [...m, { role: "assistant", content: text }]);
    if (line.startsWith("/reset")) clearChat();
    refreshSession();
  };

  const handleSend = (text: string) => {
    if (!session?.connected) return;
    setBusy(true);
    setThinkingStatus("Thinking…");
    setMessages((m) => [
      ...m,
      { role: "user", content: text },
      { role: "assistant", content: "", streaming: true },
    ]);

    const stop = streamChat(text, (ev) => {
      applyProgressEvent(ev);
      if (ev.type === "chat_token") {
        tokenBuffer.current += String(ev.text);
        scheduleTokenFlush();
      }
      if (ev.type === "chat_done") {
        flushTokens();
        setMessages((msgs) => {
          const copy = [...msgs];
          const last = copy[copy.length - 1];
          if (last?.role === "assistant") {
            copy[copy.length - 1] = {
              role: "assistant",
              content: String(ev.response || last.content),
              streaming: false,
            };
          }
          return copy;
        });
        setBusy(false);
        setThinkingStatus("");
        refreshSession();
        stop();
      }
      if (ev.type === "error") {
        flushTokens();
        setMessages((msgs) => [
          ...msgs.slice(0, -1),
          { role: "assistant", content: `Something went wrong: ${ev.message}` },
        ]);
        setBusy(false);
        setThinkingStatus("");
        stop();
      }
    });
  };

  return (
    <div className="app">
      <SessionBar
        session={session}
        onRefresh={refreshSession}
        onNewChat={handleNewChat}
        drawerOpen={drawerOpen}
        onToggleDrawer={() => (drawerOpen ? setDrawerOpen(false) : openDrawer())}
        onShowHelp={() => setShowHelp(true)}
      />
      {session?.pending_plan && (
        <PlanBanner
          session={session}
          onApprove={() =>
            approvePlan((r) => {
              setMessages((m) => [...m, { role: "assistant", content: r }]);
              refreshSession();
            })
          }
        />
      )}
      <div className="chat-shell">
        <div className="messages-scroll">
          <ChatPanel
            messages={messages}
            connected={!!session?.connected}
            onSuggestion={handleSend}
          />
          {busy && <ThinkingBar status={thinkingStatus} />}
        </div>
        <InputBar
          disabled={busy || !session?.connected}
          onSend={handleSend}
          onSlash={handleSlash}
          draft={draft}
          onDraftChange={setDraft}
          fileEntries={fileCache.current.length ? fileCache.current : files}
          onRequestFiles={refreshFiles}
        />
      </div>

      {drawerOpen && (
        <>
          <div className="drawer-backdrop" onClick={() => setDrawerOpen(false)} />
          <aside className="drawer open">
            <div className="drawer-title">Workspace</div>
            <div className="drawer-body">
              <FileTree
                paths={files}
                pinned={session?.pinned_paths || []}
                onInsert={(p) => setDraft(p)}
                onRefresh={refreshFiles}
              />
              <div className="drawer-title" style={{ marginTop: 8 }}>
                Activity
              </div>
              <ActivityPanel events={activity} />
            </div>
          </aside>
        </>
      )}

      <SlashHelp open={showHelp} onClose={() => setShowHelp(false)} />
      <DiffApprovalModal pending={pending} onClose={() => { setPending(null); refreshSession(); }} />
    </div>
  );
}
