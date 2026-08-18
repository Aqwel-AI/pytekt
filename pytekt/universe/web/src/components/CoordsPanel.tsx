import { useState } from "react";
import { api } from "../api";

interface Props {
  latitude: number;
  longitude: number;
}

export function CoordsPanel({ latitude, longitude }: Props) {
  const [ra, setRa] = useState("6h 45m 08s");
  const [dec, setDec] = useState("-16d 42m 58s");
  const [alt, setAlt] = useState("45");
  const [az, setAz] = useState("180");
  const [ra1, setRa1] = useState("6h 45m 08s");
  const [dec1, setDec1] = useState("-16d 42m 58s");
  const [ra2, setRa2] = useState("7h 45m 18s");
  const [dec2, setDec2] = useState("28d 01m 34s");
  const [result, setResult] = useState<string>("");

  const runEqToHor = async () => {
    const data = await api.coords({
      mode: "equatorial_to_horizontal",
      lat: latitude,
      lon: longitude,
      ra,
      dec,
    });
    const out = data.output as Record<string, number | string>;
    setResult(
      `Alt ${Number(out.altitude).toFixed(2)}° · Az ${Number(out.azimuth).toFixed(2)}° · ` +
        `Galactic l=${Number(out.galactic_l).toFixed(2)}° b=${Number(out.galactic_b).toFixed(2)}°`
    );
  };

  const runHorToEq = async () => {
    const data = await api.coords({
      mode: "horizontal_to_equatorial",
      lat: latitude,
      lon: longitude,
      alt,
      az,
    });
    const out = data.output as Record<string, string>;
    setResult(`RA ${out.ra} · Dec ${out.dec}`);
  };

  const runSep = async () => {
    const data = await api.coords({
      mode: "separation",
      ra1,
      dec1,
      ra2,
      dec2,
    });
    setResult(`Separation: ${Number(data.separation_deg).toFixed(4)}°`);
  };

  return (
    <div className="panel">
      <h2>Coordinate transforms</h2>
      <div className="field-row">
        <div className="field">
          <label>RA</label>
          <input value={ra} onChange={(e) => setRa(e.target.value)} />
        </div>
        <div className="field">
          <label>Dec</label>
          <input value={dec} onChange={(e) => setDec(e.target.value)} />
        </div>
        <button type="button" className="btn" onClick={runEqToHor}>
          RA/Dec → Alt/Az
        </button>
      </div>
      <div className="field-row">
        <div className="field">
          <label>Alt °</label>
          <input value={alt} onChange={(e) => setAlt(e.target.value)} />
        </div>
        <div className="field">
          <label>Az °</label>
          <input value={az} onChange={(e) => setAz(e.target.value)} />
        </div>
        <button type="button" className="btn secondary" onClick={runHorToEq}>
          Alt/Az → RA/Dec
        </button>
      </div>
      <div className="field-row">
        <div className="field">
          <label>RA₁</label>
          <input value={ra1} onChange={(e) => setRa1(e.target.value)} />
        </div>
        <div className="field">
          <label>Dec₁</label>
          <input value={dec1} onChange={(e) => setDec1(e.target.value)} />
        </div>
        <div className="field">
          <label>RA₂</label>
          <input value={ra2} onChange={(e) => setRa2(e.target.value)} />
        </div>
        <div className="field">
          <label>Dec₂</label>
          <input value={dec2} onChange={(e) => setDec2(e.target.value)} />
        </div>
        <button type="button" className="btn secondary" onClick={runSep}>
          Separation
        </button>
      </div>
      {result && <p style={{ marginTop: "0.75rem" }}>{result}</p>}
    </div>
  );
}
