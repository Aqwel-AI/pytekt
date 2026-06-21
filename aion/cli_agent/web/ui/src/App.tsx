import { useCallback, useEffect, useState } from "react";
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
import "./index.css";

export default function App() {
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [activity, setActivity] = useState<ActivityEvent[]>([]);
  const [files, setFiles] = useState<string[]>([]);
  const [pending, setPending] = useState<PendingApproval | null>(null);
  const [busy, setBusy] = useState(false);
  const [draft, setDraft] = useState("");

  const refresh = useCallback(async () => {
    const [s, a, f] = await Promise.all([
      api.session(),
      api.activity(30),
      api.files("."),
    ]);
    setSession(s);
    setActivity(a.events);
    setFiles(f.entries);
    const p = await api.pending();
    if (p.pending.length > 0) setPending(p.pending[0]);
  }, []);

  useEffect(() => {
    refresh();
    const stop = streamEvents((ev) => {
      if (ev.type === "approval_required") {
        setPending({
          id: String(ev.id),
          path: String(ev.path),
          tool: String(ev.tool),
          diff: String(ev.diff),
        });
      }
      if (ev.type === "session_updated") refresh();
      if (ev.type === "tool_step") {
        setActivity((prev) => [
          ...prev,
          {
            kind: "tool",
            detail: `${ev.action}: ${ev.preview}`,
            ts: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          },
        ]);
      }
    });
    const id = setInterval(refresh, 8000);
    return () => {
      stop();
      clearInterval(id);
    };
  }, [refresh]);

  const handleSend = (text: string) => {
    if (!session?.connected) return;
    setBusy(true);
    setMessages((m) => [...m, { role: "user", content: text }]);
    setMessages((m) => [...m, { role: "assistant", content: "", streaming: true }]);

    const stop = streamChat(text, (ev) => {
      if (ev.type === "chat_token") {
        setMessages((msgs) => {
          const copy = [...msgs];
          const last = copy[copy.length - 1];
          if (last?.role === "assistant") {
            copy[copy.length - 1] = {
              ...last,
              content: last.content + String(ev.text),
              streaming: true,
            };
          }
          return copy;
        });
      }
      if (ev.type === "chat_done") {
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
        refresh();
        stop();
      }
      if (ev.type === "error") {
        setMessages((msgs) => [
          ...msgs.slice(0, -1),
          { role: "assistant", content: `Error: ${ev.message}` },
        ]);
        setBusy(false);
        stop();
      }
    });
  };

  return (
    <div className="app">
      <SessionBar session={session} onRefresh={refresh} />
      {session && (
        <PlanBanner
          session={session}
          onApprove={() => approvePlan((r) => setMessages((m) => [...m, { role: "assistant", content: r }]))}
        />
      )}
      <div className="main">
        <div className="panel">
          <FileTree
            paths={files}
            pinned={session?.pinned_paths || []}
            onInsert={(p) => setDraft((d) => (d ? d + " @" + p : "@" + p))}
            onRefresh={refresh}
          />
        </div>
        <div className="chat-area">
          <ChatPanel messages={messages} />
          <InputBar
            disabled={busy || !session?.connected}
            onSend={handleSend}
            draft={draft}
            onDraftChange={setDraft}
          />
        </div>
        <div className="panel">
          <ActivityPanel events={activity} />
        </div>
      </div>
      <DiffApprovalModal pending={pending} onClose={() => { setPending(null); refresh(); }} />
    </div>
  );
}
