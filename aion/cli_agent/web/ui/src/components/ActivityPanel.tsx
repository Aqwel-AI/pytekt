import { ActivityEvent } from "../api";

interface Props {
  events: ActivityEvent[];
}

export function ActivityPanel({ events }: Props) {
  return (
    <>
      <div className="panel-title">Activity</div>
      <div style={{ flex: 1, overflow: "auto" }}>
        {events.length === 0 && (
          <div className="activity-item">No recent activity</div>
        )}
        {[...events].reverse().map((e, i) => (
          <div key={i} className="activity-item">
            <span className="kind">{e.ts} {e.kind}</span>
            <div>{e.detail}</div>
          </div>
        ))}
      </div>
    </>
  );
}
