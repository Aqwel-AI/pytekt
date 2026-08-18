import type { MoonData } from "../api";

interface Props {
  moon: MoonData | null;
}

export function MoonWidget({ moon }: Props) {
  if (!moon) return <p className="muted">Loading moon data…</p>;

  const illum = moon.illumination;
  const phase = moon.phase;
  const r = 80;
  const cx = 100;
  const cy = 100;

  // Simple phase: offset circle mask
  const offset = (phase - 0.5) * r * 1.6;

  return (
    <div className="grid-2">
      <div style={{ display: "flex", justifyContent: "center" }}>
        <svg width={200} height={200} viewBox="0 0 200 200">
          <defs>
            <clipPath id="moonClip">
              <circle cx={cx} cy={cy} r={r} />
            </clipPath>
          </defs>
          <circle cx={cx} cy={cy} r={r} fill="#1a2030" stroke="#12b981" strokeWidth={2} />
          <circle
            cx={cx + offset}
            cy={cy}
            r={r * 0.98}
            fill="#e8eef8"
            clipPath="url(#moonClip)"
          />
        </svg>
      </div>
      <div>
        <div className="stat-cards">
          <div className="stat-card">
            <div className="label">Phase</div>
            <div className="value">{moon.name}</div>
          </div>
          <div className="stat-card">
            <div className="label">Fraction</div>
            <div className="value">{(phase * 100).toFixed(0)}%</div>
          </div>
          <div className="stat-card">
            <div className="label">Illumination</div>
            <div className="value">{(illum * 100).toFixed(0)}%</div>
          </div>
        </div>
        <p className="muted" style={{ marginTop: "1rem" }}>
          Lunar position on the sky map requires a lunar ephemeris (planned v1.1).
          Phase shown here uses a mean elongation model.
        </p>
      </div>
    </div>
  );
}
