export default function ProductPreview({ variant }) {
  return (
    <section className="product-frame" id="how">
      <div className="product-head">
        <span>{variant.product.eyebrow}</span>
        <p>{variant.product.line}</p>
      </div>

      <div className="product-bullets">
        {variant.product.bullets.map((item) => (
          <div key={item} className="product-bullet">
            {item}
          </div>
        ))}
      </div>

      <div className="product-lower">
        <article className="route-card" aria-label="Route example">
          <div className="detail-head">
            <span>{variant.routePreview.eyebrow}</span>
            <span>{variant.routePreview.routeId}</span>
          </div>
          <p className="route-note">{variant.routePreview.note}</p>
          <div className="route-path">
            <span>PATH</span>
            <strong>{variant.routePreview.path}</strong>
          </div>
          <div className="route-metrics">
            {variant.routePreview.metrics.map((metric) => (
              <div key={metric.label} className="route-metric">
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
              </div>
            ))}
          </div>
        </article>

        <aside className="lock-card" aria-label="Live lock">
          <div className="detail-head">
            <span>{variant.lockPanel.eyebrow}</span>
            <span>OFF</span>
          </div>
          <p className="lock-note">{variant.lockPanel.line}</p>
          <div className="lock-rows">
            {variant.lockPanel.rows.map((row) => (
              <div key={row.label} className="lock-row">
                <span>{row.label}</span>
                <strong>{row.value}</strong>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </section>
  );
}
