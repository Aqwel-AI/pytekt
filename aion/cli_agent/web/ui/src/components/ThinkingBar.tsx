interface Props {
  status: string;
}

export function ThinkingBar({ status }: Props) {
  return (
    <div className="thinking-bar">
      <span className="thinking-dot" />
      <span className="thinking-text">{status || "Thinking…"}</span>
    </div>
  );
}
