export type Range = "today" | "week" | "month";

export interface Summary {
  range: string;
  range_label: string;
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_cost_usd: number;
  cloud_cost_usd?: number;
  local_tokens?: number;
  cost_label?: string;
  cost_note?: string;
  only_local?: boolean;
  call_count: number;
  by_provider: {
    provider: string;
    tokens: number;
    cost_usd: number;
    calls: number;
    is_local?: boolean;
  }[];
  top_models: [string, number][];
}

export interface Timeseries {
  labels: string[];
  tokens: number[];
  cost_usd: number[];
  calls: number[];
}

export interface WeekData {
  labels: string[];
  tokens: number[];
  cost_usd: number[];
}

export interface UsageEvent {
  ts: string;
  provider: string;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  cost_usd: number;
  source?: string;
}

export interface SessionInfo {
  provider: string | null;
  model: string | null;
  trust: boolean;
  idle_disconnect_minutes: number;
  config_path?: string;
}

export interface MetaInfo {
  store_path: string;
  event_count: number;
  providers_with_keys: string[];
}

export interface SystemInfo {
  platform: string;
  platform_release: string;
  machine: string;
  processor: string;
  hostname: string;
  logical_cores: number;
  physical_cores: number;
  psutil_available: boolean;
  cpu_freq_mhz?: number;
  install_hint?: string;
}

export interface GpuLive {
  index: number;
  name: string;
  util: number;
  mem_used: number;
  mem_total: number;
  temp_c: number | null;
}

export interface HardwareLatest {
  t: number;
  cpu: number;
  cpu_cores: number[];
  ram_pct: number;
  ram_used: number;
  ram_total: number;
  disk_pct: number;
  disk_read_mbps: number;
  disk_write_mbps: number;
  gpus: GpuLive[];
}

export interface HardwareCharts {
  labels: string[];
  cpu: number[];
  ram: number[];
  per_core: Record<string, number[]>;
  core_count: number;
}

export interface HardwareSnapshot {
  ok: boolean;
  error?: string;
  system: SystemInfo;
  latest: HardwareLatest | null;
  history: HardwareLatest[];
  charts: HardwareCharts;
  processes?: { pid: number; name: string; memory_mb: number }[];
}

async function get<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`API ${path}: ${r.status}`);
  return r.json();
}

export const api = {
  summary: (range: Range) => get<Summary>(`/api/summary?range=${range}`),
  timeseries: (range: Range) => get<Timeseries>(`/api/timeseries?range=${range}`),
  week: () => get<WeekData>("/api/week"),
  recent: (limit = 30) => get<{ events: UsageEvent[] }>(`/api/recent?limit=${limit}`),
  session: () => get<SessionInfo>("/api/session"),
  meta: () => get<MetaInfo>("/api/meta"),
  info: () => get<{ version: string; developer: string }>("/api/info"),
  hardware: () => get<HardwareSnapshot>("/api/hardware"),
  system: () => get<SystemInfo>("/api/system"),
  context: () => get<AgentContext>("/api/context"),
};

export function fmtBytes(n: number): string {
  if (n >= 1e12) return `${(n / 1e12).toFixed(1)} TB`;
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)} GB`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)} MB`;
  return `${(n / 1e3).toFixed(0)} KB`;
}

export function fmtNum(n: number): string {
  if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)}k`;
  return String(Math.round(n));
}

export function fmtCost(c: number): string {
  if (c < 0.01) return `$${c.toFixed(4)}`;
  return `$${c.toFixed(3)}`;
}

export function fmtTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export const tooltipStyle = {
  background: "#1a2030",
  border: "1px solid #2a3348",
  borderRadius: "10px",
  fontSize: "0.8rem",
};

export const ACCENT = "#12b981";
export const CHART_COLORS = [ACCENT, "#5b9aff", "#34d399", "#e8b84a", "#a78bfa", "#f472b6"];

export interface AgentContext {
  datetime: {
    day: string;
    date: string;
    time: string;
    short: string;
    full: string;
  };
  country: { code: string; name: string; locale: string };
  timezone: string;
  line: string;
  line_short: string;
}
