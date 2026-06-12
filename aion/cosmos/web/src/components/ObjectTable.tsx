import type { SkyObject } from "../api";

interface Props {
  objects: SkyObject[];
  selected?: string | null;
  onSelect?: (name: string) => void;
}

export function ObjectTable({ objects, selected, onSelect }: Props) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Kind</th>
            <th>Alt °</th>
            <th>Az °</th>
            <th>V mag</th>
          </tr>
        </thead>
        <tbody>
          {objects.map((o) => {
            const name = o.name ?? o.id ?? "?";
            return (
              <tr
                key={name}
                className={selected === name ? "selected" : ""}
                onClick={() => onSelect?.(name)}
                style={{ cursor: onSelect ? "pointer" : undefined }}
              >
                <td>{name}</td>
                <td>{o.kind ?? o.type ?? "—"}</td>
                <td>{o.altitude.toFixed(1)}</td>
                <td>{o.azimuth.toFixed(1)}</td>
                <td>{o.vmag != null ? o.vmag.toFixed(1) : "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
