import { memo, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

export interface Message {
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
}

const SUGGESTIONS = [
  "Explain this project",
  "Help me debug an error",
  "Write a function for…",
  "Review my code",
];

interface Props {
  messages: Message[];
  connected: boolean;
  onSuggestion: (text: string) => void;
}

const MessageBubble = memo(function MessageBubble({ m }: { m: Message }) {
  return (
    <div className={`msg-row ${m.role}`}>
      <div className={`msg-avatar ${m.role}`}>{m.role === "user" ? "You" : "A"}</div>
      <div className="msg-body">
        {m.streaming ? (
          <pre className="msg-plain">{m.content}{m.content ? "" : "…"}</pre>
        ) : (
          <ReactMarkdown>{m.content}</ReactMarkdown>
        )}
      </div>
    </div>
  );
});

export function ChatPanel({ messages, connected, onSuggestion }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const prevCount = useRef(messages.length);

  useEffect(() => {
    const last = messages[messages.length - 1];
    const countChanged = messages.length !== prevCount.current;
    prevCount.current = messages.length;
    if (countChanged || (last && !last.streaming)) {
      bottomRef.current?.scrollIntoView({ behavior: countChanged ? "smooth" : "auto" });
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="welcome">
        <h1>What can I help with?</h1>
        <p>
          {connected
            ? "Ask questions, design ideas, or get help with your code."
            : "Connect to Ollama or NVIDIA to start."}
        </p>
        {connected && (
          <div className="suggestion-chips">
            {SUGGESTIONS.map((s) => (
              <button key={s} type="button" className="chip" onClick={() => onSuggestion(s)}>
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="messages-list">
      {messages.map((m, i) => (
        <MessageBubble key={i} m={m} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
