import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  CHART_COLORS,
  ACCENT,
  fmtCost,
  fmtNum,
  fmtTime,
  tooltipStyle,
  type MetaInfo,
  type SessionInfo,
  type Summary,
  type Timeseries,
  type UsageEvent,
  type WeekData,
} from "../api";
import { KpiCard } from "./KpiCard";

interface Props {
  summary: Summary | null;
  timeseries: Timeseries | null;
  week: WeekData | null;
  recent: UsageEvent[];
  session: SessionInfo | null;
  meta: MetaInfo | null;
}

export function UsagePanel({
  summary,
  timeseries,
  week,
  recent,
  session,
  meta,
}: Props) {
  const hourlyData =
    timeseries?.labels.map((label, i) => ({
      label: label.slice(11) || label,
      tokens: timeseries.tokens[i] ?? 0,
      cost: timeseries.cost_usd[i] ?? 0,
    })) ?? [];

  const weekData =
    week?.labels.map((label, i) => ({
      day: label,
      tokens: week.tokens[i] ?? 0,
    })) ?? [];

  const pieData =
    summary?.by_provider.map((p) => ({
      name: p.provider,
      value: p.tokens,
    })) ?? [];

  const splitData = summary
    ? [
        { name: "Prompt", tokens: summary.prompt_tokens },
        { name: "Completion", tokens: summary.completion_tokens },
      ]
    : [];

  const maxProv = Math.max(...(summary?.by_provider.map((p) => p.tokens) ?? [1]), 1);

  return (
    <motion.section
      className="section-block"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
    >
      <h2 className="section-title">LLM usage ({summary?.range_label ?? "Today"})</h2>
      <p className="section-desc">Tokens and estimated cost from <code>aion agent</code> sessions</p>

      <div className="main">
        <KpiCard
          label={`Tokens (${summary?.range_label ?? "Today"})`}
          value={fmtNum(summary?.total_tokens ?? 0)}
          hint={`${fmtNum(summary?.prompt_tokens ?? 0)} in · ${fmtNum(summary?.completion_tokens ?? 0)} out`}
          delay={0}
        />
        <KpiCard
          label={summary?.cost_label ?? "Cloud API cost"}
          value={
            summary?.only_local
              ? "Free"
              : fmtCost(summary?.cloud_cost_usd ?? summary?.total_cost_usd ?? 0)
          }
          hint={summary?.cost_note ?? "Cloud providers only · Ollama is $0"}
          accent={!summary?.only_local}
          delay={0.05}
        />
        <KpiCard
          label="API calls"
          value={String(summary?.call_count ?? 0)}
          hint={`${meta?.event_count ?? 0} events in log`}
          delay={0.1}
        />
        <KpiCard
          label="Agent session"
          value={session?.provider ?? "offline"}
          hint={session?.model ?? (session?.trust ? "trust on" : "not connected")}
          small
          delay={0.15}
        />

        <div className="card span-8">
          <div className="card-title">Tokens & cost over time</div>
          {hourlyData.length > 0 ? (
            <div className="chart-wrap tall">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={hourlyData}>
                  <defs>
                    <linearGradient id="tokGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={ACCENT} stopOpacity={0.4} />
                      <stop offset="100%" stopColor={ACCENT} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="#2a3348" strokeDasharray="3 3" />
                  <XAxis dataKey="label" stroke="#8b95ab" fontSize={11} />
                  <YAxis yAxisId="left" stroke="#8b95ab" fontSize={11} />
                  <YAxis yAxisId="right" orientation="right" stroke="#5b9aff" fontSize={11} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend />
                  <Area
                    yAxisId="left"
                    type="monotone"
                    dataKey="tokens"
                    stroke={ACCENT}
                    fill="url(#tokGrad)"
                    strokeWidth={2}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="cost"
                    stroke="#5b9aff"
                    strokeWidth={2}
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="empty-state">
              No LLM usage logged yet. Use <code>aion agent</code> and chat after <code>/connect</code>.
            </p>
          )}
        </div>

        <div className="card span-4">
          <div className="card-title">By provider</div>
          {pieData.length > 0 ? (
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={3}
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="empty-state">—</p>
          )}
        </div>

        <div className="card span-6">
          <div className="card-title">Last 7 days</div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weekData}>
                <CartesianGrid stroke="#2a3348" strokeDasharray="3 3" />
                <XAxis dataKey="day" stroke="#8b95ab" fontSize={11} />
                <YAxis stroke="#8b95ab" fontSize={11} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="tokens" fill={ACCENT} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card span-6">
          <div className="card-title">Prompt vs completion</div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={splitData} layout="vertical">
                <CartesianGrid stroke="#2a3348" horizontal={false} />
                <XAxis type="number" stroke="#8b95ab" fontSize={11} />
                <YAxis type="category" dataKey="name" stroke="#8b95ab" width={90} fontSize={11} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="tokens" radius={[0, 8, 8, 0]}>
                  <Cell fill="#5b9aff" />
                  <Cell fill={ACCENT} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card span-4">
          <div className="card-title">Provider breakdown</div>
          <div className="provider-bars">
            {(summary?.by_provider ?? []).map((p, i) => (
              <motion.div
                key={p.provider}
                className="provider-row"
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + i * 0.05 }}
              >
                <span>{p.provider}</span>
                <div className="provider-bar-track">
                  <div
                    className="provider-bar-fill"
                    style={{ width: `${(p.tokens / maxProv) * 100}%` }}
                  />
                </div>
                <span>{fmtNum(p.tokens)}</span>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="card span-8">
          <div className="card-title">Recent API calls</div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Provider</th>
                  <th>Model</th>
                  <th>In</th>
                  <th>Out</th>
                  <th>Total</th>
                  <th>Cost</th>
                </tr>
              </thead>
              <tbody>
                {recent.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="empty-state">
                      No events yet.
                    </td>
                  </tr>
                ) : (
                  recent.map((e, i) => (
                    <motion.tr
                      key={`${e.ts}-${i}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: i * 0.02 }}
                    >
                      <td>{fmtTime(e.ts)}</td>
                      <td>
                        <span className="pill">{e.provider}</span>
                      </td>
                      <td>{(e.model || "—").slice(0, 28)}</td>
                      <td>{fmtNum(e.prompt_tokens)}</td>
                      <td>{fmtNum(e.completion_tokens)}</td>
                      <td>{fmtNum(e.total_tokens)}</td>
                      <td>
                        {e.provider === "ollama" ? "—" : fmtCost(e.cost_usd)}
                      </td>
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </motion.section>
  );
}
