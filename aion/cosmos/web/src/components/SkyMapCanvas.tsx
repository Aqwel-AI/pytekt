import { useEffect, useRef } from "react";
import type { SkyObject } from "../api";

interface Props {
  objects: SkyObject[];
  selected?: string | null;
  onSelect?: (name: string) => void;
}

export function SkyMapCanvas({ objects, selected, onSelect }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const size = canvas.width;
    const cx = size / 2;
    const cy = size / 2;
    const r = size * 0.42;

    ctx.fillStyle = "#080a0f";
    ctx.fillRect(0, 0, size, size);

    // horizon circle
    ctx.strokeStyle = "#12b981";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();

    // zenith
    ctx.fillStyle = "#12b981";
    ctx.font = "11px DM Sans";
    ctx.fillText("Zenith", cx - 18, cy - 4);

    const labels = [
      { label: "N", az: 0 },
      { label: "E", az: 90 },
      { label: "S", az: 180 },
      { label: "W", az: 270 },
    ];
    for (const { label, az } of labels) {
      const rad = ((az - 90) * Math.PI) / 180;
      const lx = cx + (r + 14) * Math.cos(rad);
      const ly = cy + (r + 14) * Math.sin(rad);
      ctx.fillStyle = "#8b95ab";
      ctx.fillText(label, lx - 4, ly + 4);
    }

    for (const obj of objects) {
      const alt = obj.altitude;
      const az = obj.azimuth;
      if (alt < 0) continue;
      const rho = r * (1 - alt / 90);
      const rad = ((az - 90) * Math.PI) / 180;
      const x = cx + rho * Math.cos(rad);
      const y = cy + rho * Math.sin(rad);
      const mag = obj.vmag ?? 3;
      const radius = Math.max(3, 10 - mag * 1.2);
      const name = obj.name ?? obj.id ?? "?";
      const isSel = selected === name;

      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = isSel ? "#20d492" : obj.kind === "messier" ? "#5b9aff" : obj.kind === "planet" ? "#e8b84a" : "#12b981";
      ctx.fill();
      if (isSel) {
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    }
  }, [objects, selected]);

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!onSelect || !canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const scale = canvasRef.current.width / rect.width;
    const px = (e.clientX - rect.left) * scale;
    const py = (e.clientY - rect.top) * scale;
    const size = canvasRef.current.width;
    const cx = size / 2;
    const cy = size / 2;
    const r = size * 0.42;

    let best: SkyObject | null = null;
    let bestD = 20;
    for (const obj of objects) {
      const rho = r * (1 - obj.altitude / 90);
      const rad = ((obj.azimuth - 90) * Math.PI) / 180;
      const x = cx + rho * Math.cos(rad);
      const y = cy + rho * Math.sin(rad);
      const d = Math.hypot(px - x, py - y);
      if (d < bestD) {
        bestD = d;
        best = obj;
      }
    }
    if (best) onSelect(best.name ?? best.id ?? "");
  };

  return (
    <canvas
      ref={canvasRef}
      width={420}
      height={420}
      style={{ width: "100%", maxWidth: 420, cursor: "crosshair" }}
      onClick={handleClick}
      aria-label="Alt-Az sky map"
    />
  );
}
