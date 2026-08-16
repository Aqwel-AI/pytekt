import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

interface Props {
  latitude: number;
  longitude: number;
}

export function ObservationsPanel({ latitude, longitude }: Props) {
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState("");

  const load = useCallback(async () => {
    const data = await api.observations();
    setRows(data.observations);
  }, []);

  useEffect(() => {
    load().catch(console.error);
  }, [load]);

  const logTonight = async () => {
    const res = await api.logObservation(latitude, longitude, notes);
    setStatus(`Logged ${res.object_count} objects`);
    setNotes("");
    await load();
  };

  const exportJson = () => {
    const blob = new Blob([JSON.stringify(rows, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "pytekt-cosmos-observations.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="panel">
      <h2>Observation log</h2>
      <p className="muted">Sessions stored in ~/.pytekt/universe.db</p>
      <div className="field-row" style={{ marginTop: "1rem" }}>
        <div className="field" style={{ flex: 1 }}>
          <label>Notes</label>
          <input
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Optional session notes"
          />
        </div>
        <button type="button" className="btn" onClick={logTonight}>
          Log tonight
        </button>
        <button type="button" className="btn secondary" onClick={exportJson}>
          Export JSON
        </button>
      </div>
      {status && <p style={{ marginTop: "0.5rem" }}>{status}</p>}
      <div className="table-wrap" style={{ marginTop: "1rem" }}>
        <table>
          <thead>
            <tr>
              <th>Time (UTC)</th>
              <th>Lat</th>
              <th>Lon</th>
              <th>Objects</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                <td>{String(r.ts ?? "")}</td>
                <td>{String(r.latitude ?? "")}</td>
                <td>{String(r.longitude ?? "")}</td>
                <td>{String(r.object_count ?? "")}</td>
                <td>{String(r.notes ?? "")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
