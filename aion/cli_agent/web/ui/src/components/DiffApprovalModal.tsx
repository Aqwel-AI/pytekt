import { PendingApproval, api } from "../api";

interface Props {
  pending: PendingApproval | null;
  onClose: () => void;
}

export function DiffApprovalModal({ pending, onClose }: Props) {
  if (!pending) return null;

  const act = async (action: "accept" | "reject" | "accept_all") => {
    await api.approve(pending.id, action);
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)" }}>
          <strong>Approve change</strong> — {pending.tool} on {pending.path}
        </div>
        <pre>{pending.diff}</pre>
        <div className="modal-actions">
          <button className="btn" onClick={() => act("accept")}>
            Accept
          </button>
          <button className="btn btn-ghost" onClick={() => act("reject")}>
            Reject
          </button>
          <button className="btn btn-ghost" onClick={() => act("accept_all")}>
            Accept all
          </button>
        </div>
      </div>
    </div>
  );
}
