interface Props {
  latitude: number;
  longitude: number;
  jd: number;
  onChange: (lat: number, lon: number) => void;
  onSave: () => void;
  onGeolocate: () => void;
}

export function ObserverBar({
  latitude,
  longitude,
  jd,
  onChange,
  onSave,
  onGeolocate,
}: Props) {
  return (
    <div className="panel">
      <h2>Observer</h2>
      <div className="field-row">
        <div className="field">
          <label>Latitude °</label>
          <input
            type="number"
            step="0.01"
            value={latitude}
            onChange={(e) => onChange(parseFloat(e.target.value) || 0, longitude)}
          />
        </div>
        <div className="field">
          <label>Longitude ° (east +)</label>
          <input
            type="number"
            step="0.01"
            value={longitude}
            onChange={(e) => onChange(latitude, parseFloat(e.target.value) || 0)}
          />
        </div>
        <button type="button" className="btn secondary" onClick={onGeolocate}>
          Use my location
        </button>
        <button type="button" className="btn" onClick={onSave}>
          Save to ~/.pytekt.yaml
        </button>
      </div>
      <p className="muted">Julian Date: {jd.toFixed(5)}</p>
    </div>
  );
}
