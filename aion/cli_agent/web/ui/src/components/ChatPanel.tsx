import ReactMarkdown from "react-markdown";

export interface Message {
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
}

interface Props {
  messages: Message[];
}

export function ChatPanel({ messages }: Props) {
  return (
    <div className="messages">
      {messages.length === 0 && (
        <div style={{ color: "var(--text-muted)", textAlign: "center", marginTop: 40 }}>
          Ask the agent to inspect or edit your codebase. Use @path to attach files.
        </div>
      )}
      {messages.map((m, i) => (
        <div key={i} className={`msg ${m.role}`}>
          <ReactMarkdown>{m.content + (m.streaming ? "▌" : "")}</ReactMarkdown>
        </div>
      ))}
    </div>
  );
}
