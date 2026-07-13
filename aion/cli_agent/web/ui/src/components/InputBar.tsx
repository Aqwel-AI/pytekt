import { useEffect, useRef, useState } from "react";
import { filterSlashCommands } from "../slashCommands";

interface Props {
  disabled: boolean;
  onSend: (text: string) => void;
  onSlash?: (text: string) => void;
  draft?: string;
  onDraftChange?: (v: string) => void;
  fileEntries?: string[];
  onRequestFiles?: () => void;
}

export function InputBar({
  disabled,
  onSend,
  onSlash,
  draft = "",
  onDraftChange,
  fileEntries = [],
  onRequestFiles,
}: Props) {
  const [text, setText] = useState("");
  const [pathSuggestions, setPathSuggestions] = useState<string[]>([]);
  const [slashSuggestions, setSlashSuggestions] = useState<string[]>([]);
  const ref = useRef<HTMLTextAreaElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (draft && onDraftChange) {
      setText((t) => (t ? t + " @" + draft : "@" + draft));
      onDraftChange("");
    }
  }, [draft, onDraftChange]);

  useEffect(() => {
    const at = text.lastIndexOf("@");
    if (at >= 0 && !text.slice(at).includes(" ")) {
      const partial = text.slice(at + 1).toLowerCase();
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        if (fileEntries.length === 0 && onRequestFiles) onRequestFiles();
        const matches = fileEntries
          .filter((e) => e.toLowerCase().includes(partial))
          .slice(0, 6);
        setPathSuggestions(matches);
      }, 300);
    } else {
      setPathSuggestions([]);
    }
    setSlashSuggestions(filterSlashCommands(text));
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [text, fileEntries, onRequestFiles]);

  const insertPath = (path: string) => {
    const at = text.lastIndexOf("@");
    setText(text.slice(0, at) + "@" + path + " ");
    setPathSuggestions([]);
    ref.current?.focus();
  };

  const insertSlash = (cmd: string) => {
    setText(cmd + (cmd.endsWith(" ") ? "" : " "));
    setSlashSuggestions([]);
    ref.current?.focus();
  };

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    if (trimmed.startsWith("/") && onSlash) {
      onSlash(trimmed);
    } else {
      onSend(trimmed);
    }
    setText("");
    if (ref.current) ref.current.style.height = "auto";
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const pasted = e.clipboardData.getData("text");
    if (!pasted) return;
    const lines = pasted.split("\n");
    const looksLikeCode =
      lines.length >= 3 ||
      /^(import |from |def |class |function |const |#include|\{|\})/m.test(pasted);
    if (looksLikeCode) {
      e.preventDefault();
      const el = ref.current;
      if (!el) return;
      const start = el.selectionStart;
      const end = el.selectionEnd;
      const next = text.slice(0, start) + pasted + text.slice(end);
      setText(next);
    }
  };

  const activeSuggestions = slashSuggestions.length > 0 ? slashSuggestions : [];

  const onInput = (value: string) => {
    setText(value);
    const el = ref.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 160) + "px";
    }
  };

  return (
    <div className="composer-wrap">
      {activeSuggestions.length > 0 && (
        <div className="autocomplete">
          {activeSuggestions.map((s) => (
            <div key={s} onClick={() => insertSlash(s)}>
              {s}
            </div>
          ))}
        </div>
      )}
      {pathSuggestions.length > 0 && slashSuggestions.length === 0 && (
        <div className="autocomplete">
          {pathSuggestions.map((s) => (
            <div key={s} onClick={() => insertPath(s)}>
              @{s}
            </div>
          ))}
        </div>
      )}
      <div className="composer">
        <textarea
          ref={ref}
          rows={1}
          value={text}
          onChange={(e) => onInput(e.target.value)}
          onPaste={handlePaste}
          onKeyDown={(e) => {
            if (e.key === "Tab" && slashSuggestions.length > 0) {
              e.preventDefault();
              insertSlash(slashSuggestions[0]);
              return;
            }
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Message Aion… Shift+Enter newline · @ file · / commands"
          disabled={disabled}
        />
        <button
          type="button"
          className="composer-send"
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          aria-label="Send"
        >
          ↑
        </button>
      </div>
      <p className="disclaimer">
        Aion can make mistakes — verify important information. Chat clears when you exit the
        terminal session.
      </p>
    </div>
  );
}
