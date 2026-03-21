export default function SuperiorLanding({ variant }) {
  const installerUrl = variant?.windowsInstallerUrl ?? "/download/";

  return (
    <main className="superior-shell">
      <div className="superior-screen">
        <header className="superior-screen__header">
          <div className="superior-screen__brand">
            <img
              className="superior-screen__wordmark"
              src="/assets/superior-wordmark.png"
              alt="Superior"
              width="168"
              height="52"
              loading="eager"
              decoding="async"
            />
            <span className="superior-screen__brand-label">Windows Kalshi starter bot</span>
          </div>

          <div className="superior-screen__status" aria-label="Machine status">
            <span className="superior-screen__status-dot superior-screen__status-dot--active" aria-hidden="true" />
            <span className="superior-screen__status-text">Shadow first / auto after arm</span>
          </div>
        </header>

        <section className="superior-screen__playfield superior-screen__playfield--hero" aria-label="Superior hero">
          <div className="superior-hero">
            <img
              className="superior-hero__sprite"
              src="/assets/superior-emblem.png"
              alt="Superior emblem"
              width="520"
              height="520"
              loading="eager"
              decoding="async"
            />

            <div className="superior-hero__copy">
              <strong>One tight Kalshi starter bot.</strong>
              <p>Set it up once, clear shadow, keep caps visible, and know why it acted.</p>
            </div>
          </div>
        </section>

        <nav className="superior-screen__controls superior-screen__controls--simple" aria-label="Primary controls">
          <a className="machine-control machine-control--primary" href={installerUrl}>
            <span>Download EXE</span>
          </a>
          <a className="machine-control machine-control--step" href="/download/">
            <span>Install notes</span>
          </a>
          <a className="machine-control machine-control--commit" href="/docs/">
            <span>Docs</span>
          </a>
        </nav>
      </div>
    </main>
  );
}
