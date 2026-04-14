export default function MetricCard({ icon, title, value, isRevenue }) {
  return (
    <div className={`metric-card ${isRevenue ? 'revenue' : ''}`}>
      <div className="metric-glow"></div>
      <div className="metric-content">
        <div className="metric-title">
          <i className={`fas fa-${icon}`}></i> {title}
        </div>
        <div className="metric-value">{value}</div>
      </div>
    </div>
  );
}
