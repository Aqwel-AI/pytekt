import { useCallback, useEffect, useState } from "react";
import { api, type CosmoPoint } from "../api";

export function CosmoPanel() {
  const [z, setZ] = useState(0.1);
  const [h0, setH0] = useState(70);
  const [om0, setOm0] = useState(0.3);
  const [dL, setDL] = useState(0);
  const [lookback, setLookback] = useState(0);
  const [velocity, setVelocity] = useState(0);
  const [curve, setCurve] = useState<CosmoPoint[]>([]);

  const load = useCallback(async () => {
    const [main, cur] = await Promise.all([
      api.cosmology(z, h0, om0),
      api.cosmologyCurve(Math.max(z, 1), h0, om0),
    ]);
    setDL(main.luminosity_distance_mpc);
    setLookback(main.lookback_time_gyr);
    setVelocity(main.hubble_velocity_kms);
    setCurve(cur.points);
  }, [z, h0, om0]);

  useEffect(() => {
    load().catch(console.error);
  }, [load]);

  const points = curve
    .map((p, i) => {
      const x = (i / Math.max(curve.length - 1, 1)) * 280;
      const maxD = Math.max(...curve.map((c) => c.luminosity_distance_mpc), 1);
      const y = 70 - (p.luminosity_distance_mpc / maxD) * 60;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="panel">
      <h2>Cosmology (flat ΛCDM)</h2>
      <div className="field-row">
        <div className="field">
          <label>Redshift z</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={z}
            onChange={(e) => setZ(parseFloat(e.target.value) || 0)}
          />
        </div>
        <div className="field">
          <label>H₀ km/s/Mpc</label>
          <input
            type="number"
            value={h0}
            onChange={(e) => setH0(parseFloat(e.target.value) || 70)}
          />
        </div>
        <div className="field">
          <label>Ωₘ</label>
          <input
            type="number"
            step="0.01"
            value={om0}
            onChange={(e) => setOm0(parseFloat(e.target.value) || 0.3)}
          />
        </div>
      </div>
      <div className="stat-cards" style={{ marginTop: "1rem" }}>
        <div className="stat-card">
          <div className="label">Luminosity distance</div>
          <div className="value">{dL.toFixed(1)} Mpc</div>
        </div>
        <div className="stat-card">
          <div className="label">Lookback time</div>
          <div className="value">{lookback.toFixed(2)} Gyr</div>
        </div>
        <div className="stat-card">
          <div className="label">Hubble flow</div>
          <div className="value">{velocity.toFixed(0)} km/s</div>
        </div>
      </div>
      {curve.length > 1 && (
        <svg className="sparkline" viewBox="0 0 280 80">
          <polyline
            fill="none"
            stroke="#12b981"
            strokeWidth="2"
            points={points}
          />
        </svg>
      )}
    </div>
  );
}
