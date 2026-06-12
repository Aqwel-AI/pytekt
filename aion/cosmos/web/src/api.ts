export type TabId = "tonight" | "moon" | "coords" | "cosmology" | "catalogs" | "log";

export interface SkyObject {
  name?: string;
  id?: string;
  kind?: string;
  type?: string;
  ra_hours?: number;
  dec_deg?: number;
  vmag?: number;
  altitude: number;
  azimuth: number;
}

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

export interface ObserverState {
  latitude: number;
  longitude: number;
  jd: number;
  utc_iso?: string;
  context?: AgentContext;
}

export interface MoonData {
  phase: number;
  name: string;
  illumination: number;
  jd: number;
}

export interface SkyData {
  objects: SkyObject[];
  count: number;
  catalog: string;
  min_altitude: number;
}

export interface CosmoPoint {
  z: number;
  luminosity_distance_mpc: number;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export const api = {
  info: () => get<{ app: string; version: string }>("/api/info"),
  observer: (lat?: number, lon?: number) =>
    get<ObserverState>(
      `/api/observer${lat != null ? `?lat=${lat}&lon=${lon}` : ""}`
    ),
  saveObserver: (latitude: number, longitude: number) =>
    post<ObserverState>("/api/observer", { latitude, longitude }),
  moon: () => get<MoonData>("/api/moon"),
  sky: (lat: number, lon: number, catalog = "all", minAlt = 10) =>
    get<SkyData>(
      `/api/sky?lat=${lat}&lon=${lon}&catalog=${catalog}&min_alt=${minAlt}`
    ),
  coords: (params: Record<string, string | number>) => {
    const q = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params).map(([k, v]) => [k, String(v)])
      )
    );
    return get<Record<string, unknown>>(`/api/coords?${q}`);
  },
  cosmology: (z: number, H0: number, Om0: number) =>
    get<{
      luminosity_distance_mpc: number;
      lookback_time_gyr: number;
      hubble_velocity_kms: number;
    }>(`/api/cosmology?z=${z}&H0=${H0}&Om0=${Om0}`),
  cosmologyCurve: (zMax: number, H0: number, Om0: number) =>
    get<{ points: CosmoPoint[] }>(
      `/api/cosmology?curve=1&z=${zMax}&H0=${H0}&Om0=${Om0}`
    ),
  catalogStars: () => get<{ objects: SkyObject[] }>("/api/catalog/stars"),
  catalogMessier: () => get<{ objects: SkyObject[] }>("/api/catalog/messier"),
  catalogPlanets: () => get<{ objects: Record<string, unknown>[] }>("/api/catalog/planets"),
  observations: () =>
    get<{ observations: Record<string, unknown>[]; count: number }>(
      "/api/observations"
    ),
  logObservation: (latitude: number, longitude: number, notes = "") =>
    post<{ ok: boolean; object_count: number }>("/api/observations", {
      latitude,
      longitude,
      notes,
      catalog: "all",
    }),
};
