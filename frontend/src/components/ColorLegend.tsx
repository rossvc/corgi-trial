const LEGEND_ITEMS = [
  { dbz: '70+', color: '#8040FF', label: 'Extreme' },
  { dbz: '60-70', color: '#FF00FF', label: 'Severe' },
  { dbz: '55-60', color: '#C00000', label: 'Very Heavy' },
  { dbz: '50-55', color: '#FF8000', label: 'Heavy' },
  { dbz: '45-50', color: '#FFC000', label: 'Mod-Heavy' },
  { dbz: '40-45', color: '#FFFF00', label: 'Moderate' },
  { dbz: '35-40', color: '#006400', label: 'Light-Mod' },
  { dbz: '30-35', color: '#009000', label: 'Light' },
  { dbz: '25-30', color: '#00C000', label: 'Very Light' },
  { dbz: '20-25', color: '#00ECEC', label: 'Drizzle' },
  { dbz: '10-20', color: '#40A8FF', label: 'Trace' },
];

export function ColorLegend() {
  return (
    <div className="color-legend">
      <h4>Reflectivity (dBZ)</h4>
      {LEGEND_ITEMS.map((item) => (
        <div key={item.dbz} className="legend-item">
          <span
            className="color-swatch"
            style={{ backgroundColor: item.color }}
          />
          <span className="dbz-value">{item.dbz}</span>
          <span className="legend-label">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
