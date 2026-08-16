import { useCallback, useEffect, useState } from "react";
import {
  api,
  type AgentContext,
  type HardwareSnapshot,
  type MetaInfo,
  type Range,
  type SessionInfo,
  type Summary,
  type Timeseries,
  type UsageEvent,
  type WeekData,
} from "./api";
import { Header } from "./components/Header";
import { HardwarePanel } from "./components/HardwarePanel";
import { UsagePanel } from "./components/UsagePanel";
import "./App.css";

export default function App() {
  const [range, setRange] = useState<Range>("today");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [timeseries, setTimeseries] = useState<Timeseries | null>(null);
  const [week, setWeek] = useState<WeekData | null>(null);
  const [recent, setRecent] = useState<UsageEvent[]>([]);
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [meta, setMeta] = useState<MetaInfo | null>(null);
  const [hardware, setHardware] = useState<HardwareSnapshot | null>(null);
  const [context, setContext] = useState<AgentContext | null>(null);
  const [version, setVersion] = useState("—");

  const load = useCallback(async () => {
    try {
      const [s, t, w, r, sess, m, hw, ctx, info] = await Promise.all([
        api.summary(range),
        api.timeseries(range),
        api.week(),
        api.recent(30),
        api.session(),
        api.meta(),
        api.hardware(),
        api.context(),
        api.info(),
      ]);
      setSummary(s);
      setTimeseries(t);
      setWeek(w);
      setRecent(r.events);
      setSession(sess);
      setMeta(m);
      setHardware(hw);
      setContext(ctx);
      setVersion(info.version);
    } catch (e) {
      console.error(e);
    }
  }, [range]);

  useEffect(() => {
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, [load]);

  return (
    <div className="app">
      <Header range={range} onRange={setRange} context={context} />
      <div className="page">
        <HardwarePanel hw={hardware} />
        <UsagePanel
          summary={summary}
          timeseries={timeseries}
          week={week}
          recent={recent}
          session={session}
          meta={meta}
        />
      </div>
      <footer className="footer">
        <a href="https://aqwelai.xyz/" target="_blank" rel="noreferrer">
          Aqwel AI
        </a>
        {" · "}
        PyTekt v{version} · <code>pytekt usage</code> · port 3847
      </footer>
    </div>
  );
}
