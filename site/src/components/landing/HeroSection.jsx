import ScannerVisual from "./ScannerVisual.jsx";

function TertiaryLink({ action }) {
  const props = action.external ? { target: "_blank", rel: "noreferrer" } : {};
  return (
    <a className="hero-link" href={action.href} {...props}>
      {action.label}
    </a>
  );
}

export default function HeroSection({ variant }) {
  return (
    <section className="hero-frame">
      <div className="hero-copy">
        <p className="panel-label">{variant.eyebrow}</p>

        <h1 className="hero-title">
          {variant.titleLines.map((line) => (
            <span key={line}>{line}</span>
          ))}
        </h1>

        <p className="hero-lead">{variant.subhead}</p>
        <p className="hero-note">{variant.systemNote}</p>

        <div className="hero-actions">
          <a className="button-primary" href={variant.windowsInstallerUrl}>
            {variant.primaryCtaLabel}
          </a>
          <a className="button-secondary" href={variant.secondaryCtaHref}>
            {variant.secondaryCtaLabel}
          </a>
          <TertiaryLink action={variant.tertiaryCta} />
        </div>

        <div className="trust-strip" aria-label="Core product identity">
          {variant.trustStrip.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </div>

      <div className="hero-visual">
        <ScannerVisual animated />
      </div>
    </section>
  );
}
