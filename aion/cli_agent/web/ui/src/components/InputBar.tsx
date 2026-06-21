import { useEffect, useRef, useState } from "react";
import { api } from "../api";

const SLASH_COMMANDS = [
  { cmd: "/reset", desc: "Clear memory" },
  { cmd: "/undo", desc: "Undo last edit" },
  { cmd: "/approve", desc: "Execute plan" },
  { cmd: "/research", desc: "Research subagent" },
  { cmd: "/commit", desc: "Git commit" },
];

interface Props {
  disabled: boolean;
  onSend: (text: string) => void;
  draft?: string;
  onDraftChange?: (v: string) => void;
}

export function InputBar({ disabled, onSend, draft = "", onDraftChange }: Props) {
  const [text, setText] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSlash, setShowSlash] = useState(false);
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (draft && onDraftChange) {
      setText((t) => (t ? t + " " + draft : draft));
      onDraftChange("");
    }
  }, [draft, onDraftChange]);

  useEffect(() => {
    const at = text.lastIndexOf("@");
    if (at >= 0 && !text.slice(at).includes(" ")) {
      const partial = text.slice(at + 1);
      api.files(".").then((r) => {
        const matches = r.entries
          .filter((e) => e.toLowerCase().includes(partial.toLowerCase()))
          .slice(0, 8);
        setSuggestions(matches);
      });
    } else {
      setSuggestions([]);
    }
    setShowSlash(text.startsWith("/"));
  }, [text]);

  const insertSuggestion = (path: string) => {
    const at = text.lastIndexOf("@");
    setText(text.slice(0, at) + "@" + path + " ");
    setSuggestions([]);
    ref.current?.focus();
  };

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    if (trimmed === "/undo") {
      api.undo();
      setText("");
      return;
    }
    if (trimmed === "/reset") {
      api.reset();
      setText("");
      return;
    }
    if (trimmed.startsWith("/")) {
      const parts = trimmed.slice(1).split(/\s+/);
      const cmd = parts[0];
      const args = parts.slice(1).join(" ");
      api.command(cmd, args).then((r) => {
        if (r.response) onSend(`[/${cmd}] ${r.response}`);
      });
      setText("");
      return;
    }
    onSend(trimmed);
    setText("");
  };

  return (
    <div className="input-area" style={{ position: "relative" }}>
      {suggestions.length > 0 && (
        <div className="autocomplete">
          {suggestions.map((s) => (
            <div key={s} onClick={() => insertSuggestion(s)}>
              @{s}
            </div>
          ))}
        </div>
      )}
      {showSlash && (
        <div className="suggestions">
          {SLASH_COMMANDS.map((s) => (
            <span
              key={s.cmd}
              className="suggestion"
              onClick={() => setText(s.cmd + " ")}
              title={s.desc}
            >
              {s.cmd}
            </span>
          ))}
        </div>
      )}
      <textarea
        ref={ref}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
        placeholder="Message… @file for context · / for commands"
        disabled={disabled}
      />
      <div className="input-actions">
        <button className="btn" onClick={handleSend} disabled={disabled || !text.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
