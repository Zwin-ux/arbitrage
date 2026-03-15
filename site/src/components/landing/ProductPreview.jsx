function toneClass(tone) {
  if (tone === "green") {
    return "text-[var(--accent-green)]";
  }
  if (tone === "magenta") {
    return "text-[var(--accent-magenta)]";
  }
  return "text-[var(--accent-cyan)]";
}

export default function ProductPreview({ variant }) {
  return (
    <section className="preview-grid" id="preview">
      <div className="product-frame">
        <div className="product-frame-top">
          <span>SUPERIOR.EXE</span>
          <span>HANGAR / BOT BAY / SCORE</span>
        </div>

        <div className="product-frame-body">
          <div className="product-preview-left">
            <div className="product-preview-title">
              <p className="section-label">Session control</p>
              <h3>Record books. Stage routes. Start the run.</h3>
            </div>

            <div className="product-preview-checklist">
              <span>[x] Equip Polymarket</span>
              <span>[ ] Boot recorder</span>
              <span>[ ] Arm starter bot</span>
              <span>[ ] Land first paper score</span>
            </div>
          </div>

          <div className="product-preview-right">
            <div className="preview-status-grid">
              {variant.previewStatus.map((item) => (
                <div key={item.label} className="preview-status-card">
                  <p>{item.label}</p>
                  <strong className={toneClass(item.tone)}>{item.value}</strong>
                </div>
              ))}
            </div>

            <div className="preview-terminal">
              <p>[REC] Local sample ready</p>
              <p>[SCAN] One route staged for bot bay</p>
              <p>[SCORE] Portfolio will update after session bank</p>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-5">
        <p className="section-label">Product preview</p>
        <h2 className="section-title">{variant.previewHeading}</h2>
        <p className="hero-copy">{variant.previewBody}</p>

        <ul className="preview-bullets">
          {variant.previewBullets.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>

        <div className="hero-actions">
          <a className="cta-secondary" href={variant.previewCtaHref}>
            {variant.previewCtaLabel}
          </a>
          <a className="cta-secondary" href={variant.portableUrl}>
            Portable build
          </a>
        </div>
      </div>
    </section>
  );
}
