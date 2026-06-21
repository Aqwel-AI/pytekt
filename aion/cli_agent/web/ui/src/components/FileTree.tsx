import { api } from "../api";

interface Props {
  paths: string[];
  pinned: string[];
  onInsert: (path: string) => void;
  onRefresh: () => void;
}

export function FileTree({ paths, pinned, onInsert, onRefresh }: Props) {
  const togglePin = async (path: string, isPinned: boolean) => {
    if (isPinned) await api.unpin(path);
    else await api.pin(path);
    onRefresh();
  };

  const openFile = async (path: string) => {
    await api.openFiles([path]);
    onInsert(path);
  };

  return (
    <>
      <div className="panel-title">Workspace</div>
      {pinned.length > 0 && (
        <>
          <div className="panel-title" style={{ fontSize: 10 }}>
            Pinned
          </div>
          {pinned.map((p) => (
            <div key={p} className="file-item pinned" onClick={() => openFile(p)}>
              📌 {p}
            </div>
          ))}
        </>
      )}
      <div style={{ flex: 1, overflow: "auto" }}>
        {paths.slice(0, 200).map((p) => (
          <div
            key={p}
            className={`file-item ${pinned.includes(p) ? "pinned" : ""}`}
            onClick={() => openFile(p)}
            onContextMenu={(e) => {
              e.preventDefault();
              togglePin(p, pinned.includes(p));
            }}
            title="Click to attach · right-click to pin"
          >
            {p.endsWith("/") ? "📁" : "📄"} {p}
          </div>
        ))}
      </div>
    </>
  );
}
