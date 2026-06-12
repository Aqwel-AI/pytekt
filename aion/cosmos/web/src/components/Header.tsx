import type { ObserverState, TabId } from "../api";

const TABS: { id: TabId; label: string }[] = [
  { id: "tonight", label: "Tonight" },
  { id: "moon", label: "Moon" },
  { id: "coords", label: "Coordinates" },
  { id: "cosmology", label: "Cosmology" },
  { id: "catalogs", label: "Catalogs" },
  { id: "log", label: "Log" },
];

interface Props {
  tab: TabId;
  onTab: (t: TabId) => void;
  observer: ObserverState | null;
  version: string;
}

export function Header({ tab, onTab, observer, version }: Props) {
  const ctx = observer?.context;
  return (
    <header className="header">
      <div className="brand">
        <div className="logo">✦</div>
        <div>
          <h1>Aion Cosmos</h1>
          <p className="brand-tagline">Astronomy dashboard · v{version}</p>
          {ctx && (
            <p className="context-line">
              <span className="context-day">{ctx.datetime.day}</span>
              {" · "}
              <span>{ctx.datetime.date}</span>
              {" · "}
              <span className="context-time">{ctx.datetime.time}</span>
              {" · "}
              <span className="context-country">
                {ctx.country.name}
                {ctx.country.code ? ` (${ctx.country.code})` : ""}
              </span>
              {" · "}
              <span className="context-tz">{ctx.timezone}</span>
            </p>
          )}
        </div>
      </div>
      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`tab ${tab === t.id ? "active" : ""}`}
            onClick={() => onTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>
    </header>
  );
}
