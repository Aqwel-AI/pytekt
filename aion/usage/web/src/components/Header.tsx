import { motion } from "framer-motion";
import type { AgentContext, Range } from "../api";

interface Props {
  range: Range;
  onRange: (r: Range) => void;
  context: AgentContext | null;
}

export function Header({ range, onRange, context }: Props) {
  return (
    <header className="header">
      <div className="brand">
        <motion.div
          className="logo"
          initial={{ rotate: -8, scale: 0.8 }}
          animate={{ rotate: 0, scale: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 14 }}
        >
          A
        </motion.div>
        <div>
          <h1>Aion Command Center</h1>
          <p className="brand-tagline">LLM usage · CPU · GPU · memory — Aqwel AI</p>
          {context && (
            <p className="context-line">
              <span className="context-day">{context.datetime.day}</span>
              {" · "}
              {context.datetime.date}
              {" · "}
              <span className="context-time">{context.datetime.time}</span>
              {" · "}
              <span className="context-country">
                {context.country.name}
                {context.country.code ? ` (${context.country.code})` : ""}
              </span>
              {" · "}
              <span className="context-tz">{context.timezone}</span>
            </p>
          )}
        </div>
      </div>
      <div className="header-actions">
        <div className="range-toggle">
          {(["today", "week", "month"] as Range[]).map((r) => (
            <button
              key={r}
              type="button"
              className={range === r ? "active" : ""}
              onClick={() => onRange(r)}
            >
              {r === "today" ? "Today" : r === "week" ? "7 days" : "30 days"}
            </button>
          ))}
        </div>
        <div className="live-badge">
          <span className="live-dot" />
          Live · 5s refresh
        </div>
      </div>
    </header>
  );
}
