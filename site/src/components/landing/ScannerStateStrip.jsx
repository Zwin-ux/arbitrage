export default function ScannerStateStrip({ variant }) {
  return (
    <section className="section-frame" id="system-state">
      <div className="section-copy">
        <p className="panel-label">System state</p>
        <h2 className="section-title">Paper-first state is visible immediately.</h2>
      </div>

      <div className="state-strip" aria-label="System state">
        {variant.stateStrip.map((item) => (
          <article key={item.label} className="state-cell">
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}
