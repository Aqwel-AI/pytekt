import { useEffect, useState } from "react";

type Tab = "query" | "pendulum" | "projectile";

type Info = { app: string; version: string; native: boolean };

function LinePlot({
  xs,
  ys,
  xLabel,
  yLabel,
}: {
  xs: number[];
  ys: number[];
  xLabel: string;
  yLabel: string;
}) {
  const w = 480;
  const h = 220;
  const pad = 32;
  if (!xs.length) return null;
  const xMin = Math.min(...xs);
  const xMax = Math.max(...xs);
  const yMin = Math.min(...ys);
  const yMax = Math.max(...ys);
  const sx = (x: number) => pad + ((x - xMin) / (xMax - xMin || 1)) * (w - 2 * pad);
  const sy = (y: number) => h - pad - ((y - yMin) / (yMax - yMin || 1)) * (h - 2 * pad);
  const points = xs.map((x, i) => `${sx(x)},${sy(ys[i])}`).join(" ");
  return (
    <svg width={w} height={h} className="plot">
      <polyline fill="none" stroke="#22c55e" strokeWidth="2" points={points} />
      <text x={w / 2} y={h - 6} textAnchor="middle" className="axis-label">
        {xLabel}
      </text>
      <text
        x={12}
        y={h / 2}
        textAnchor="middle"
        transform={`rotate(-90 12 ${h / 2})`}
        className="axis-label"
      >
        {yLabel}
      </text>
    </svg>
  );
}

export default function App() {
  const [tab, setTab] = useState<Tab>("query");
  const [info, setInfo] = useState<Info | null>(null);
  const [tasks, setTasks] = useState<string[]>([]);
  const [queryText, setQueryText] = useState("kinetic energy mass=2 velocity=3");
  const [queryResult, setQueryResult] = useState<string>("");
  const [pendulum, setPendulum] = useState({ length: 1, angle: 15, steps: 500 });
  const [pendulumData, setPendulumData] = useState<{ times: number[]; theta: number[] } | null>(
    null
  );
  const [projectile, setProjectile] = useState({ v0: 20, angle: 45, drag: 0, steps: 500 });
  const [projectileData, setProjectileData] = useState<{ x: number[]; y: number[] } | null>(null);

  useEffect(() => {
    fetch("/api/info")
      .then((r) => r.json())
      .then(setInfo);
    fetch("/api/tasks")
      .then((r) => r.json())
      .then((d) => setTasks(d.tasks || []));
  }, []);

  async function runQuery() {
    const r = await fetch("/api/query?q=" + encodeURIComponent(queryText));
    const d = await r.json();
    setQueryResult(JSON.stringify(d, null, 2));
  }

  async function runPendulum() {
    const qs = new URLSearchParams({
      length: String(pendulum.length),
      angle_deg: String(pendulum.angle),
      steps: String(pendulum.steps),
    });
    const r = await fetch("/api/pendulum?" + qs);
    const d = await r.json();
    setPendulumData({ times: d.times, theta: d.theta });
  }

  async function runProjectile() {
    const qs = new URLSearchParams({
      v0: String(projectile.v0),
      angle_deg: String(projectile.angle),
      drag: String(projectile.drag),
      steps: String(projectile.steps),
    });
    const r = await fetch("/api/projectile?" + qs);
    const d = await r.json();
    setProjectileData({ x: d.x, y: d.y });
  }

  return (
    <div className="app">
      <header>
        <h1>PyTekt Physics</h1>
        {info && (
          <span className="badge">
            v{info.version} {info.native ? "· C++" : "· Python"}
          </span>
        )}
      </header>
      <nav>
        {(["query", "pendulum", "projectile"] as Tab[]).map((t) => (
          <button key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </nav>
      <main>
        {tab === "query" && (
          <section>
            <label>
              Query
              <input value={queryText} onChange={(e) => setQueryText(e.target.value)} />
            </label>
            <button onClick={runQuery}>Run</button>
            <pre>{queryResult}</pre>
            <aside>
              <h3>Supported tasks</h3>
              <ul>
                {tasks.map((t) => (
                  <li key={t}>{t}</li>
                ))}
              </ul>
            </aside>
          </section>
        )}
        {tab === "pendulum" && (
          <section>
            <label>
              Length (m)
              <input
                type="number"
                value={pendulum.length}
                onChange={(e) => setPendulum({ ...pendulum, length: +e.target.value })}
              />
            </label>
            <label>
              Angle (deg)
              <input
                type="number"
                value={pendulum.angle}
                onChange={(e) => setPendulum({ ...pendulum, angle: +e.target.value })}
              />
            </label>
            <button onClick={runPendulum}>Simulate</button>
            {pendulumData && (
              <LinePlot
                xs={pendulumData.times}
                ys={pendulumData.theta}
                xLabel="time (s)"
                yLabel="theta (rad)"
              />
            )}
          </section>
        )}
        {tab === "projectile" && (
          <section>
            <label>
              v0 (m/s)
              <input
                type="number"
                value={projectile.v0}
                onChange={(e) => setProjectile({ ...projectile, v0: +e.target.value })}
              />
            </label>
            <label>
              Angle (deg)
              <input
                type="number"
                value={projectile.angle}
                onChange={(e) => setProjectile({ ...projectile, angle: +e.target.value })}
              />
            </label>
            <label>
              Drag
              <input
                type="number"
                step="0.01"
                value={projectile.drag}
                onChange={(e) => setProjectile({ ...projectile, drag: +e.target.value })}
              />
            </label>
            <button onClick={runProjectile}>Simulate</button>
            {projectileData && (
              <LinePlot xs={projectileData.x} ys={projectileData.y} xLabel="x (m)" yLabel="y (m)" />
            )}
          </section>
        )}
      </main>
    </div>
  );
}
