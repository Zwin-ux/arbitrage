export default function FooterStrip({ variant }) {
  return (
    <footer className="download-strip">
      <div className="download-strip-main">
        <div className="panel-card-head">
          <p className="section-label">Download menu</p>
          <span className="panel-version">v1</span>
        </div>
        <h2 className="panel-card-title">{variant.footerTitle}</h2>
        <p className="panel-card-copy">{variant.footerBody}</p>

        <div className="hero-actions">
          <a className="cta-primary" href={variant.windowsInstallerUrl}>
            {variant.primaryCtaLabel}
          </a>
          <a className="cta-secondary" href={variant.secondaryCtaHref}>
            Open full menu
          </a>
        </div>
      </div>

      <div className="download-strip-side">
        <p className="section-label">Source + checklist</p>
        <div className="download-checks">
          {variant.footerChecks.map((item) => (
            <div key={item} className="download-check-row">
              {item}
            </div>
          ))}
        </div>
      </div>
    </footer>
  );
}
