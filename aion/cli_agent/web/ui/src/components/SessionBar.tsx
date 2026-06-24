import { useEffect, useState } from "react";
import { api, ProviderInfo, SessionInfo } from "../api";

interface Props {
  session: SessionInfo | null;
  onRefresh: () => void;
  onNewChat: () => void;
  drawerOpen: boolean;
  onToggleDrawer: () => void;
}

export function SessionBar({
  session,
  onRefresh,
  onNewChat,
  drawerOpen,
  onToggleDrawer,
}: Props) {
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
    onNewChat();
    onRefresh();
  };

  const modelLabel = session?.connected
    ? session.model?.split("/").pop() || session.model || session.provider
    : "Offline";

  return (
    <>
      <header className="gemini-header">
        <span className="gemini-logo">Aion</span>
        <span className={`gemini-badge ${session?.connected ? "connected" : ""}`}>
          {session?.connected && <span className="status-dot" />}
          {modelLabel}
        </span>
        <div className="gemini-header-actions">
          <button type="button" className="btn btn-sm btn-ghost" onClick={onNewChat}>
            New chat
          </button>
          <button type="button" className="drawer-toggle" onClick={onToggleDrawer}>
            {drawerOpen ? "Close" : "Files"}
          </button>
          {session?.connected ? (
            <button type="button" className="btn btn-sm btn-ghost" onClick={handleDisconnect}>
              Disconnect
            </button>
          ) : (
            <button type="button" className="btn btn-sm" onClick={() => setShowConnect(true)}>
              Connect
            </button>
          )}
        </div>
      </header>

      {showConnect && (
        <div className="modal-overlay" onClick={() => setShowConnect(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Connect</h3>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
            >
              {providers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label} {p.ready ? "" : "(needs API key)"}
                </option>
              ))}
            </select>
            <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
              {models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <input
              type="password"
              placeholder="NVIDIA API key (if not saved)"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <button type="button" className="btn" onClick={handleConnect} disabled={connecting}>
              {connecting ? "Connecting…" : "Connect"}
            </button>
          </div>
        </div>
      )}
    </>
  );
}
