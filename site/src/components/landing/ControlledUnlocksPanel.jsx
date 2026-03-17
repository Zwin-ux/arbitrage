function rowClass(state) {
  if (state === "active") {
    return "unlock-row unlock-row-active";
  }
  return "unlock-row unlock-row-warn";
}

export default function ControlledUnlocksPanel({ variant }) {
  return (
    <section className="section-frame unlock-frame">
      <div className="section-copy">
        <p className="panel-label">{variant.unlockPanel.eyebrow}</p>
        <h2 className="section-title">{variant.unlockPanel.title}</h2>
        <p className="section-body">{variant.unlockPanel.body}</p>
      </div>

      <div className="unlock-grid">
        <article className="lock-display">
          <span className="lock-display-label">{variant.unlockPanel.statusLabel}</span>
          <strong>{variant.unlockPanel.statusValue}</strong>
          <p>Paper mode is the default state. Live requires evidence and checks.</p>
        </article>

        <div className="unlock-checks" aria-label="Live unlock checklist">
          {variant.unlockPanel.checks.map((item) => (
            <div key={item.label} className={rowClass(item.state)}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
