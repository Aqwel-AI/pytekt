import { useEffect, useState } from "react";
import { api, ProviderInfo, SessionInfo } from "../api";

const MODES = ["plain", "agent", "debug", "plan", "review", "test"];

interface Props {
  session: SessionInfo | null;
  onRefresh: () => void;
}

export function SessionBar({ session, onRefresh }: Props) {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [showConnect, setShowConnect] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState("ollama");
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    api.providers().then((r) => setProviders(r.providers));
  }, []);

  useEffect(() => {
    if (selectedProvider) {
      api.models(selectedProvider).then((r) => {
        if (r.ok && r.models) {
          setModels(r.models);
          setSelectedModel(r.models[0] || "");
        }
      });
    }
  }, [selectedProvider]);

  const handleConnect = async () => {
    setConnecting(true);
    await api.connect(selectedProvider, selectedModel, apiKey || undefined);
    setConnecting(false);
    setShowConnect(false);
    onRefresh();
  };

  const handleDisconnect = async () => {
    await api.disconnect();
    onRefresh();
  };

  const handleMode = async (mode: string) => {
    await api.setMode(mode);
    onRefresh();
  };

  const handleTrust = async () => {
    await api.setTrust(!session?.trust);
    onRefresh();
  };

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "10px 16px",
        background: "var(--bg-panel)",
        borderBottom: "1px solid var(--border)",
        flexWrap: "wrap",
      }}
    >
      <strong style={{ color: "var(--accent)" }}>Aion Agent</strong>
      <span style={{ color: "var(--text-muted)", fontSize: 13 }}>
        {session?.connected
          ? `${session.provider} · ${session.model}`
          : "Not connected"}
      </span>
      <select
        value={session?.mode || "agent"}
        onChange={(e) => handleMode(e.target.value)}
        style={{ background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 6, padding: "4px 8px" }}
      >
        {MODES.map((m) => (
          <option key={m} value={m}>
            {m}
          </option>
        ))}
      </select>
      <button className="btn btn-sm btn-ghost" onClick={handleTrust}>
        Trust: {session?.trust ? "ON" : "OFF"}
      </button>
      {session?.connected ? (
        <button className="btn btn-sm btn-ghost" onClick={handleDisconnect}>
          Disconnect
        </button>
      ) : (
        <button className="btn btn-sm" onClick={() => setShowConnect(true)}>
          Connect
        </button>
      )}
      <span style={{ marginLeft: "auto", fontSize: 12, color: "var(--text-muted)" }}>
        {session?.workspace?.replace(/^.*\//, ".../")}
      </span>

      {showConnect && (
        <div className="modal-overlay" onClick={() => setShowConnect(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ padding: 16 }}>
            <h3 style={{ margin: "0 0 12px" }}>Connect provider</h3>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              style={{ width: "100%", marginBottom: 8, padding: 8 }}
            >
              {providers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label} {p.ready ? "" : "(needs key)"}
                </option>
              ))}
            </select>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              style={{ width: "100%", marginBottom: 8, padding: 8 }}
            >
              {models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <input
              type="password"
              placeholder="API key (optional if saved)"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              style={{ width: "100%", marginBottom: 12, padding: 8 }}
            />
            <button className="btn" onClick={handleConnect} disabled={connecting}>
              {connecting ? "Connecting…" : "Connect"}
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
