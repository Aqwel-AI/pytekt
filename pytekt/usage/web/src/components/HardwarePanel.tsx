import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  ACCENT,
  CHART_COLORS,
  fmtBytes,
  tooltipStyle,
  type HardwareSnapshot,
} from "../api";

interface Props {
  hw: HardwareSnapshot | null;
}

export function HardwarePanel({ hw }: Props) {
  if (!hw) {
    return (
      <motion.section className="section-block" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h2 className="section-title">Hardware</h2>
        <p className="empty-state">Loading system metrics…</p>
      </motion.section>
    );
  }

  if (!hw.ok) {
    return (
      <motion.section className="section-block" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h2 className="section-title">Hardware</h2>
        <p className="empty-state">
          {hw.error || "Install monitor deps:"}{" "}
          <code>pip install &apos;aqwel-aion[monitor]&apos;</code>
        </p>
      </motion.section>
    );
  }

  const sys = hw.system;
  const latest = hw.latest;
  const cores = latest?.cpu_cores ?? [];
  const coreData = cores.map((pct, i) => ({
    name: `Core ${i}`,
    usage: pct,
  }));

  const lineData = (hw.charts?.labels ?? []).map((_, i) => {
    const row: Record<string, number | string> = { t: i };
    row.cpu = hw.charts.cpu[i] ?? 0;
    row.ram = hw.charts.ram[i] ?? 0;
    Object.entries(hw.charts.per_core ?? {}).forEach(([key, arr]) => {
      row[key] = arr[i] ?? 0;
    });
    return row;
  });

  const coreKeys = Object.keys(hw.charts?.per_core ?? {});

  return (
    <motion.section
      className="section-block"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="section-title">Computer & hardware</h2>
      <p className="section-desc">
        {sys.hostname} · {sys.platform} {sys.platform_release} · {sys.logical_cores} logical cores
        {sys.physical_cores ? ` (${sys.physical_cores} physical)` : ""}
        {sys.cpu_freq_mhz ? ` · ${sys.cpu_freq_mhz} MHz` : ""}
      </p>

      <div className="main hardware-grid">
        <div className="card span-3">
          <div className="kpi-label">CPU (overall)</div>
          <div className="kpi-value">{latest ? `${latest.cpu.toFixed(1)}%` : "—"}</div>
          <div className="kpi-hint">{cores.length} cores tracked live</div>
        </div>
        <div className="card span-3">
          <div className="kpi-label">Memory</div>
          <div className="kpi-value small">
            {latest ? `${latest.ram_pct.toFixed(1)}%` : "—"}
          </div>
          <div className="kpi-hint">
            {latest
              ? `${fmtBytes(latest.ram_used)} / ${fmtBytes(latest.ram_total)}`
              : "—"}
          </div>
        </div>
        <div className="card span-3">
          <div className="kpi-label">Disk</div>
          <div className="kpi-value small">
            {latest ? `${latest.disk_pct.toFixed(1)}%` : "—"}
          </div>
          <div className="kpi-hint">
            {latest
              ? `R ${latest.disk_read_mbps.toFixed(1)} · W ${latest.disk_write_mbps.toFixed(1)} MB/s`
              : "—"}
          </div>
        </div>
        <div className="card span-3">
          <div className="kpi-label">GPU</div>
          <div className="kpi-value small">
            {latest?.gpus?.length
              ? `${latest.gpus[0].util}%`
              : "No NVIDIA GPU"}
          </div>
          <div className="kpi-hint">
            {latest?.gpus?.[0]?.name?.slice(0, 36) ?? sys.processor.slice(0, 36)}
          </div>
        </div>

        <div className="card span-12">
          <div className="card-title">Per-core CPU usage (%)</div>
          <div className="cores-grid">
            {coreData.map((c, i) => (
              <motion.div
                key={c.name}
                className="core-cell"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.03 }}
              >
                <div className="core-label">{c.name}</div>
                <div className="core-bar-track">
                  <motion.div
                    className="core-bar-fill"
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, c.usage)}%` }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    style={{
                      background:
                        c.usage > 80
                          ? "#f14c4c"
                          : c.usage > 50
                            ? "#e8b84a"
                            : `linear-gradient(90deg, ${ACCENT}, #34d399)`,
                    }}
                  />
                </div>
                <div className="core-pct">{c.usage.toFixed(0)}%</div>
              </motion.div>
            ))}
            {!coreData.length && (
              <p className="empty-state">No per-core data yet — wait a few seconds.</p>
            )}
          </div>
        </div>

        <div className="card chart-card-full span-12">
          <div className="card-title">CPU & RAM history (live)</div>
          <div className="chart-wrap hero">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={lineData} margin={{ top: 12, right: 20, left: 4, bottom: 8 }}>
                <CartesianGrid stroke="#2a3348" strokeDasharray="3 3" />
                <XAxis dataKey="t" stroke="#8b95ab" fontSize={11} tickMargin={6} />
                <YAxis
                  stroke="#8b95ab"
                  fontSize={12}
                  domain={[0, 100]}
                  tickFormatter={(v) => `${v}%`}
                  width={44}
                />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: "0.85rem" }} />
                <Area
                  type="monotone"
                  dataKey="cpu"
                  stroke={ACCENT}
                  fill="rgba(18,185,129,0.25)"
                  strokeWidth={2.5}
                  name="CPU %"
                  animationDuration={600}
                />
                <Area
                  type="monotone"
                  dataKey="ram"
                  stroke="#5b9aff"
                  fill="rgba(91,154,255,0.2)"
                  strokeWidth={2.5}
                  name="RAM %"
                  animationDuration={600}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card chart-card-full span-12">
          <div className="card-title">
            Per-core over time
            {coreKeys.length > 0 && (
              <span className="chart-subtitle"> — {coreKeys.length} cores</span>
            )}
          </div>
          <div className="chart-wrap hero">
            {coreKeys.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={lineData} margin={{ top: 12, right: 20, left: 4, bottom: 8 }}>
                  <CartesianGrid stroke="#2a3348" strokeDasharray="3 3" />
                  <XAxis dataKey="t" stroke="#8b95ab" fontSize={11} tickMargin={6} />
                  <YAxis
                    domain={[0, 100]}
                    stroke="#8b95ab"
                    fontSize={12}
                    tickFormatter={(v) => `${v}%`}
                    width={44}
                  />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend
                    wrapperStyle={{ fontSize: "0.8rem", paddingTop: "8px" }}
                    iconSize={10}
                  />
                  {coreKeys.map((key, i) => (
                    <Area
                      key={key}
                      type="monotone"
                      dataKey={key}
                      stroke={CHART_COLORS[i % CHART_COLORS.length]}
                      fill="transparent"
                      strokeWidth={coreKeys.length > 10 ? 1.2 : 2}
                      name={key.replace("core_", "Core ")}
                      animationDuration={600}
                      dot={false}
                      activeDot={{ r: 3 }}
                    />
                  ))}
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <p className="empty-state">Collecting per-core samples…</p>
            )}
          </div>
        </div>

        {latest?.gpus && latest.gpus.length > 0 && (
          <div className="card span-12">
            <div className="card-title">GPU devices</div>
            <div className="gpu-grid">
              {latest.gpus.map((g, i) => (
                <motion.div
                  key={g.index}
                  className="gpu-card"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                >
                  <div className="gpu-name">{g.name}</div>
                  <div className="gpu-stat">
                    <span>Utilization</span>
                    <strong>{g.util}%</strong>
                  </div>
                  <div className="gpu-bar-track">
                    <div className="gpu-bar-fill" style={{ width: `${g.util}%` }} />
                  </div>
                  <div className="gpu-stat">
                    <span>VRAM</span>
                    <strong>
                      {fmtBytes(g.mem_used)} / {fmtBytes(g.mem_total)}
                    </strong>
                  </div>
                  <div className="gpu-bar-track mem">
                    <div
                      className="gpu-bar-fill mem"
                      style={{
                        width: `${g.mem_total ? (100 * g.mem_used) / g.mem_total : 0}%`,
                      }}
                    />
                  </div>
                  {g.temp_c != null && (
                    <div className="gpu-stat">
                      <span>Temp</span>
                      <strong>{g.temp_c}°C</strong>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {hw.processes && hw.processes.length > 0 && (
          <div className="card span-12">
            <div className="card-title">Top processes (memory)</div>
            <div className="chart-wrap" style={{ height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={hw.processes.slice(0, 12).map((p) => ({
                    ...p,
                    memory_mb: Math.round(
                      ((p as { rss?: number; memory_mb?: number }).rss ?? 0) /
                        (1024 * 1024)
                    ),
                  }))}
                  layout="vertical"
                  margin={{ left: 80 }}
                >
                  <CartesianGrid stroke="#2a3348" horizontal={false} />
                  <XAxis type="number" stroke="#8b95ab" fontSize={10} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    stroke="#8b95ab"
                    width={78}
                    fontSize={10}
                    tickFormatter={(v: string) =>
                      v.length > 14 ? `${v.slice(0, 12)}…` : v
                    }
                  />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="memory_mb" fill="#5b9aff" radius={[0, 6, 6, 0]} name="MB" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </motion.section>
  );
}
