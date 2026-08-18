import { useEffect, useState } from "react";
import { api, type SkyObject } from "../api";

interface Props {
  onShowOnSky: (name: string) => void;
}

export function CatalogPanel({ onShowOnSky }: Props) {
  const [tab, setTab] = useState<"stars" | "messier" | "planets">("stars");
  const [stars, setStars] = useState<SkyObject[]>([]);
  const [messier, setMessier] = useState<SkyObject[]>([]);
  const [planets, setPlanets] = useState<Record<string, unknown>[]>([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    Promise.all([api.catalogStars(), api.catalogMessier(), api.catalogPlanets()])
      .then(([s, m, p]) => {
        setStars(s.objects);
        setMessier(m.objects);
        setPlanets(p.objects);
      })
      .catch(console.error);
  }, []);

  const rows =
    tab === "stars"
      ? stars
      : tab === "messier"
        ? messier
        : (planets as unknown as SkyObject[]);

  const filtered = rows.filter((r) => {
    const name = (r.name ?? r.id ?? "").toLowerCase();
    return name.includes(filter.toLowerCase());
  });

  return (
    <div className="panel">
      <h2>Catalogs</h2>
      <div className="field-row">
        {(["stars", "messier", "planets"] as const).map((t) => (
          <button
            key={t}
            type="button"
            className={`tab ${tab === t ? "active" : ""}`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
        <div className="field">
          <label>Search</label>
          <input value={filter} onChange={(e) => setFilter(e.target.value)} />
        </div>
      </div>
      <div className="table-wrap" style={{ marginTop: "1rem" }}>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>RA h</th>
              <th>Dec °</th>
              <th>Type</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => {
              const name = r.name ?? r.id ?? "?";
              return (
                <tr key={name}>
                  <td>{name}</td>
                  <td>{r.ra_hours?.toFixed(3) ?? "—"}</td>
                  <td>{r.dec_deg?.toFixed(2) ?? "—"}</td>
                  <td>{r.type ?? r.kind ?? "—"}</td>
                  <td>
                    <button
                      type="button"
                      className="btn secondary"
                      style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem" }}
                      onClick={() => onShowOnSky(name)}
                    >
                      Sky map
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
