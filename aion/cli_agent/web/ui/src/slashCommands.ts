/** Mirror of aion/cli_agent/command_vocab.py SLASH_COMMANDS */

export const SLASH_COMMANDS: { cmd: string; hint: string; desc: string }[] = [
  { cmd: "mode", hint: "[plain|agent|debug|plan|review|test]", desc: "Interaction mode" },
  { cmd: "connect", hint: "[provider] [model]", desc: "Connect to a provider" },
  { cmd: "reconnect", hint: "[model]", desc: "Reconnect to saved provider" },
  { cmd: "disconnect", hint: "[forget|keys]", desc: "Go offline" },
  { cmd: "status", hint: "", desc: "Show session status" },
  { cmd: "reset", hint: "", desc: "Clear conversation memory" },
  { cmd: "pin", hint: "<path>", desc: "Pin path to every turn" },
  { cmd: "unpin", hint: "[path]", desc: "Remove pin (or all)" },
  { cmd: "pins", hint: "", desc: "List pinned paths" },
  { cmd: "undo", hint: "", desc: "Restore last file snapshot" },
  { cmd: "audit", hint: "", desc: "Show recent audit log" },
  { cmd: "tools", hint: "[on|off]", desc: "Force tool use on/off" },
  { cmd: "approve", hint: "", desc: "Execute pending plan" },
  { cmd: "research", hint: "<query>", desc: "Read-only subagent research" },
  { cmd: "commit", hint: "[message]", desc: "Git commit" },
  { cmd: "branch", hint: "<name>", desc: "Create/switch branch" },
  { cmd: "init", hint: "", desc: "Create AION.md in workspace" },
  { cmd: "trust", hint: "[on|off]", desc: "Workspace trust for writes" },
  { cmd: "help", hint: "", desc: "Show all commands" },
  { cmd: "physics", hint: "[query|pendulum|tasks|web]", desc: "Physics formulas and simulations" },
];

export const CONNECT_PROVIDERS = ["ollama", "nvidia", "nim"];

export const INTERACTION_MODES = ["plain", "agent", "debug", "plan", "review", "test"] as const;

export function filterSlashCommands(text: string): string[] {
  if (!text.startsWith("/")) return [];
  const body = text.slice(1);
  if (!body.includes(" ")) {
    const partial = body.toLowerCase();
    return SLASH_COMMANDS.map((c) => `/${c.cmd}`)
      .filter((cmd) => !partial || cmd.slice(1).startsWith(partial));
  }
  const [cmd, ...rest] = body.split(" ");
  if (cmd.toLowerCase() === "connect") {
    const partial = (rest.join(" ") || "").toLowerCase();
    return CONNECT_PROVIDERS.filter((p) => !partial || p.startsWith(partial)).map(
      (p) => `/connect ${p}`
    );
  }
  if (cmd.toLowerCase() === "mode") {
    const partial = (rest.join(" ") || "").toLowerCase();
    return INTERACTION_MODES.filter((m) => !partial || m.startsWith(partial)).map(
      (m) => `/mode ${m}`
    );
  }
  return [];
}
