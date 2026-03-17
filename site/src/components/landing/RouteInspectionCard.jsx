export default function RouteInspectionCard({ variant }) {
  const preview = variant.routeInspection;

  return (
    <section className="section-frame route-frame" id="route-inspection">
      <div className="section-copy">
        <p className="panel-label">{preview.eyebrow}</p>
        <h2 className="section-title">{preview.title}</h2>
        <p className="section-body">{preview.body}</p>
      </div>

      <div className="inspection-grid">
        <article className="inspection-card">
          <div className="inspection-card-top">
            <span>{preview.routeId}</span>
            <span>{preview.quality}</span>
          </div>

          <div className="inspection-route-block">
            <div>
              <span className="inspection-label">Route path</span>
              <strong>{preview.path}</strong>
            </div>
            <div>
              <span className="inspection-label">Snapshot origin</span>
              <strong>{preview.origin}</strong>
            </div>
            <div>
              <span className="inspection-label">Timestamp</span>
              <strong>{preview.snapshotAt}</strong>
            </div>
          </div>

          <div className="inspection-metric-grid">
            {preview.metrics.map((metric) => (
              <div key={metric.label} className="inspection-metric">
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
              </div>
            ))}
          </div>
        </article>

        <aside className="inspection-aside">
          <div className="inspection-assumptions">
            <span className="inspection-label">Assumptions</span>
            <ul>
              {preview.assumptions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="inspection-summary">
            <span className="inspection-label">Review state</span>
            <p>Deductions stay visible before paper entry. Nothing in this panel implies live readiness.</p>
          </div>
        </aside>
      </div>
    </section>
  );
}
