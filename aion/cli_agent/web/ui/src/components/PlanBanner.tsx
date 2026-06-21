import { SessionInfo, api } from "../api";

interface Props {
  session: SessionInfo;
  onApprove: () => void;
}

export function PlanBanner({ session, onApprove }: Props) {
  if (!session.pending_plan || !session.plan_steps?.length) return null;

  return (
    <div className="plan-banner">
      <strong>Plan ready</strong> — review steps and approve to execute.
      <ol>
        {session.plan_steps.map((s, i) => (
          <li key={i}>{s}</li>
        ))}
      </ol>
      <button className="btn btn-sm" style={{ marginTop: 8 }} onClick={onApprove}>
        Approve plan
      </button>
    </div>
  );
}

export async function approvePlan(onMessage: (text: string) => void) {
  const r = await api.command("approve");
  if (r.response) onMessage(r.response);
}
