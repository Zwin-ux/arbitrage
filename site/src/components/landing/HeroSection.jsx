import ScannerVisual from "./ScannerVisual.jsx";

function TertiaryLink({ action }) {
  const props = action.external ? { target: "_blank", rel: "noreferrer" } : {};
  return (
    <a className="cta-tertiary" href={action.href} {...props}>
      {action.label}
    </a>
  );
}

export default function HeroSection({ variant }) {
  return (
    <section className="hero-section">
      <div className="hero-visual">
        <ScannerVisual animated className="w-full" />
      </div>

      <div className="hero-copy-block">
        <p className="section-label">{variant.eyebrow}</p>

        <h1 className="hero-title">
          {variant.titleLines.map((line, index) => (
            <span key={line} className={index === 0 ? "" : "hero-title-accent"}>
              {line}
            </span>
          ))}
        </h1>

        <p className="hero-copy">{variant.subhead}</p>

        <div className="hero-actions hero-actions-centered">
          <a className="cta-primary" href={variant.windowsInstallerUrl}>
            {variant.primaryCtaLabel}
          </a>
          <a className="cta-secondary" href={variant.secondaryCtaHref}>
            {variant.secondaryCtaLabel}
          </a>
        </div>

        <div className="hero-actions hero-actions-centered hero-actions-tertiary">
          <TertiaryLink action={variant.tertiaryCta} />
          {variant.trustItems.map((item) => (
            <span key={item} className="trust-chip">
              {item}
            </span>
          ))}
        </div>

        <div className="hero-status-grid" aria-label="Current product status">
          {variant.statusTiles.map((item) => (
            <article key={item.label} className="status-tile">
              <p>{item.label}</p>
              <strong>{item.value}</strong>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
