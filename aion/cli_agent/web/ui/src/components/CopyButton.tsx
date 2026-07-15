import { useState } from "react";

interface Props {
  text: string;
  className?: string;
  label?: string;
}

export function CopyButton({ text, className = "copy-btn", label = "Copy" }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* ignore */
    }
  };

  return (
    <button type="button" className={className} onClick={handleCopy} aria-label="Copy">
      {copied ? "Copied" : label}
    </button>
  );
}
