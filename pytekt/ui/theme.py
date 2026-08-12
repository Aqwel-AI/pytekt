"""Default dark theme CSS for React-style apps."""

REACT_THEME_CSS = """
:root {
  --bg: #0a0e14; --surface: #131921; --card: #1a2332; --border: #2d3a4d;
  --text: #e7edf4; --muted: #8b9cb3; --accent: #3d8bfd; --accent2: #3ecf8e;
  --danger: #f85149; --radius: 8px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
  background: var(--bg); color: var(--text);
  line-height: 1.6; min-height: 100vh;
}
.aion-app { max-width: 1200px; margin: 0 auto; padding: 1.5rem; }
.aion-header { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border); }
.aion-header h1 { font-size: 1.75rem; font-weight: 700; }
.aion-subtitle { color: var(--muted); margin-top: 0.35rem; }
.aion-stack { display: flex; flex-direction: column; gap: 1rem; }
.aion-row { display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-start; }
.aion-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1rem; flex: 1; min-width: 200px;
}
.aion-card h3 { font-size: 0.95rem; color: var(--accent); margin-bottom: 0.5rem; }
.aion-metrics {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
}
.aion-metric {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 0.75rem; text-align: center;
}
.aion-metric .val { font-size: 1.35rem; font-weight: 700; color: var(--accent2); }
.aion-metric .lbl { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; }
.aion-btn {
  display: inline-block; padding: 0.5rem 1rem; border-radius: var(--radius);
  border: 1px solid var(--accent); background: var(--accent); color: #fff;
  font-size: 0.875rem; cursor: pointer; text-decoration: none;
}
.aion-btn:hover { filter: brightness(1.1); }
.aion-btn-secondary {
  background: transparent; color: var(--accent);
}
table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
th, td { text-align: left; padding: 0.5rem 0.65rem; border-bottom: 1px solid var(--border); }
th { color: var(--muted); }
pre, code {
  font-family: ui-monospace, monospace; font-size: 0.82rem;
  background: rgba(0,0,0,0.35); border-radius: var(--radius);
}
pre { padding: 0.85rem; overflow-x: auto; }
.aion-footer {
  margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border);
  font-size: 0.8rem; color: var(--muted);
}
"""
