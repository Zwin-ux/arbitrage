import ScannerVisual from "./ScannerVisual.jsx";

function SecondaryLink({ action }) {
  const props = action.external ? { target: "_blank", rel: "noreferrer" } : {};
  return (
    <a className="cta-secondary" href={action.href} {...props}>
      {action.label}
    </a>
  );
}

export default function HeroSection({ variant }) {
  return (
    <section className="hero-grid">
      <div className="space-y-6">
        <p className="section-label">{variant.eyebrow}</p>

        <h1 className="hero-title">
          {variant.titleLines.map((line) => (
            <span key={line}>{line}</span>
          ))}
        </h1>

        <p className="hero-copy">{variant.subhead}</p>

        <div className="hero-actions">
          <a className="cta-primary" href={variant.windowsInstallerUrl}>
            Download Superior
          </a>
          {variant.secondaryCtas.map((action) => (
            <SecondaryLink key={action.label} action={action} />
          ))}
        </div>

        <div className="trust-strip">
          {variant.trustItems.map((item) => (
            <span key={item} className="trust-chip">
              {item}
            </span>
          ))}
        </div>
      </div>

      <div id="scanner" className="hero-stage">
        <ScannerVisual animated className="w-full" stats={variant.scannerStats} />
      </div>
    </section>
  );
}
