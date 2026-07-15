import { useEffect, useState } from "react";
import { api, ProviderInfo, SessionInfo } from "../api";
import { INTERACTION_MODES } from "../slashCommands";

interface Props {
  session: SessionInfo | null;
  onRefresh: () => void;
  onNewChat: () => void;
  drawerOpen: boolean;
  onToggleDrawer: () => void;
  onShowHelp: () => void;
}

export function SessionBar({
  session,
  onRefresh,
  onNewChat,
  drawerOpen,
  onToggleDrawer,
  onShowHelp,
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

  const handleMode = async (mode: string) => {
    await api.setMode(mode);
    onRefresh();
  };

  const handleTrust = async () => {
    await api.setTrust(!session?.trust);
    onRefresh();
  };

  const handleUndo = async () => {
    const r = await api.undo();
    if (r.message) {
      /* refresh after undo */
    }
    onRefresh();
  };

  const modelLabel = session?.connected
    ? session.model?.split("/").pop() || session.model || session.provider
    : "Offline";

  const interactionMode = session?.mode || "agent";

  return (
    <>
      <header className="gemini-header">
        <span className="gemini-logo">Aion</span>
        <span className={`gemini-badge ${session?.connected ? "connected" : ""}`}>
          {session?.connected && <span className="status-dot" />}
          {modelLabel}
        </span>
        {session?.connected && (
          <>
            <select
              className="header-select"
              value={interactionMode}
              onChange={(e) => handleMode(e.target.value)}
              aria-label="Interaction mode"
            >
              {INTERACTION_MODES.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <button
              type="button"
              className={`trust-pill ${session.trust ? "on" : ""}`}
              onClick={handleTrust}
              title="Workspace trust (allow file writes)"
            >
              {session.trust ? "Trust on" : "Trust off"}
            </button>
          </>
        )}
        <div className="gemini-header-actions">
          <button type="button" className="btn btn-sm btn-ghost" onClick={onShowHelp} title="Slash commands">
            ?
          </button>
          {session?.connected && (
            <button type="button" className="btn btn-sm btn-ghost" onClick={handleUndo} title="Undo last edit">
              Undo
            </button>
          )}
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
