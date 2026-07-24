import { useCallback, useEffect, useState } from "react";
import { api, type MoonData, type ObserverState, type SkyObject, type TabId } from "./api";
import "./App.css";
import { CatalogPanel } from "./components/CatalogPanel";
import { CoordsPanel } from "./components/CoordsPanel";
import { CosmoPanel } from "./components/CosmoPanel";
import { Header } from "./components/Header";
import { MoonWidget } from "./components/MoonWidget";
import { ObjectTable } from "./components/ObjectTable";
import { ObservationsPanel } from "./components/ObservationsPanel";
import { ObserverBar } from "./components/ObserverBar";
import { SkyMapCanvas } from "./components/SkyMapCanvas";

export default function App() {
  const [tab, setTab] = useState<TabId>("tonight");
  const [version, setVersion] = useState("—");
  const [observer, setObserver] = useState<ObserverState | null>(null);
  const [lat, setLat] = useState(40.18);
  const [lon, setLon] = useState(44.51);
  const [jd, setJd] = useState(0);
  const [sky, setSky] = useState<SkyObject[]>([]);
  const [moon, setMoon] = useState<MoonData | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [catalog, setCatalog] = useState("all");
  const [minAlt, setMinAlt] = useState(10);

  const refresh = useCallback(async () => {
    const [info, obs, skyData, moonData] = await Promise.all([
      api.info(),
      api.observer(lat, lon),
      api.sky(lat, lon, catalog, minAlt),
      api.moon(),
    ]);
    setVersion(info.version);
    setObserver(obs);
    setLat(obs.latitude);
    setLon(obs.longitude);
    setJd(obs.jd);
    setSky(skyData.objects);
    setMoon(moonData);
  }, [lat, lon, catalog, minAlt]);

  useEffect(() => {
    refresh().catch(console.error);
    const id = setInterval(() => refresh().catch(console.error), 60000);
    return () => clearInterval(id);
  }, [refresh]);

  const saveObserver = async () => {
    await api.saveObserver(lat, lon);
    await refresh();
  };

  const geolocate = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition((pos) => {
      setLat(pos.coords.latitude);
      setLon(pos.coords.longitude);
    });
  };

  const showOnSky = (name: string) => {
    setSelected(name);
    setTab("tonight");
  };

  return (
    <div className="app">
      <Header tab={tab} onTab={setTab} observer={observer} version={version} />
      <div className="page">
        {(tab === "tonight" || tab === "moon" || tab === "coords" || tab === "log") && (
          <ObserverBar
            latitude={lat}
            longitude={lon}
            jd={jd}
            onChange={(la, lo) => {
              setLat(la);
              setLon(lo);
            }}
            onSave={saveObserver}
            onGeolocate={geolocate}
          />
        )}

        {tab === "tonight" && (
          <>
            <div className="field-row" style={{ marginBottom: "1rem" }}>
              <div className="field">
                <label>Catalog</label>
                <select value={catalog} onChange={(e) => setCatalog(e.target.value)}>
                  <option value="all">All</option>
                  <option value="stars">Bright stars</option>
                  <option value="messier">Messier</option>
                  <option value="planets">Planets</option>
                </select>
              </div>
              <div className="field">
                <label>Min altitude °</label>
                <input
                  type="number"
                  value={minAlt}
                  onChange={(e) => setMinAlt(parseFloat(e.target.value) || 0)}
                />
              </div>
              <button type="button" className="btn secondary" onClick={() => refresh()}>
                Refresh
              </button>
            </div>
            <div className="grid-2">
              <div className="panel">
                <h2>Sky map (Alt / Az)</h2>
                <SkyMapCanvas
                  objects={sky}
                  selected={selected}
                  onSelect={setSelected}
                />
                {selected && (
                  <p style={{ marginTop: "0.75rem" }}>
                    Selected: <strong>{selected}</strong>
                  </p>
                )}
              </div>
              <div className="panel">
                <h2>Above horizon ({sky.length})</h2>
                <ObjectTable
                  objects={sky}
                  selected={selected}
                  onSelect={setSelected}
                />
              </div>
            </div>
          </>
        )}

        {tab === "moon" && (
          <div className="panel">
            <h2>Moon</h2>
            <MoonWidget moon={moon} />
          </div>
        )}

        {tab === "coords" && <CoordsPanel latitude={lat} longitude={lon} />}

        {tab === "cosmology" && <CosmoPanel />}

        {tab === "catalogs" && <CatalogPanel onShowOnSky={showOnSky} />}

        {tab === "log" && (
          <ObservationsPanel latitude={lat} longitude={lon} />
        )}
      </div>
      <footer className="footer">
        <a href="https://aqwelai.xyz/" target="_blank" rel="noreferrer">
          Aqwel AI
        </a>
        {" · "}Educational astronomy — not observatory-grade precision
      </footer>
    </div>
  );
}
