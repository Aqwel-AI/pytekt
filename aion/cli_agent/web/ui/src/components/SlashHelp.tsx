import { SLASH_COMMANDS } from "../slashCommands";

interface Props {
  open: boolean;
  onClose: () => void;
}

export function SlashHelp({ open, onClose }: Props) {
  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal slash-help-modal" onClick={(e) => e.stopPropagation()}>
        <h3>Slash commands</h3>
        <div className="slash-help-list">
          {SLASH_COMMANDS.map(({ cmd, hint, desc }) => (
            <div key={cmd} className="slash-help-row">
              <code>
                /{cmd}
                {hint ? ` ${hint}` : ""}
              </code>
              <span>{desc}</span>
            </div>
          ))}
        </div>
        <button type="button" className="btn btn-sm" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
}
