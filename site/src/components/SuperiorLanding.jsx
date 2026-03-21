export default function SuperiorLanding({ variant }) {
  const installerUrl = variant?.windowsInstallerUrl ?? "/download/";
  const portableUrl = variant?.portableUrl ?? "/download/";
  const statusText = variant?.statusText ?? "WINDOWS / LOCAL / AUTO";

  return (
    <main className="superior-shell">
      <div className="superior-screen">
        <header className="superior-screen__header">
          <div className="superior-screen__brand">
            <img
              className="superior-screen__brand-icon"
              src="/assets/superior-head.png"
              alt=""
              width="30"
              height="30"
              loading="eager"
              decoding="async"
            />
            <img
              className="superior-screen__wordmark"
              src="/assets/superior-wordmark.png"
              alt="Superior"
              width="168"
              height="52"
              loading="eager"
              decoding="async"
            />
            <span className="superior-screen__brand-label">{variant?.brandSubtitle ?? "engine prediction bot"}</span>
          </div>

          <div className="superior-screen__status" aria-label="Machine status">
            <span className="superior-screen__status-chip">WIN</span>
            <span className="superior-screen__status-chip">LOCAL</span>
            <span className="superior-screen__status-chip superior-screen__status-chip--accent">AUTO</span>
            <span className="superior-screen__status-text">{statusText}</span>
          </div>
        </header>

        <section className="superior-screen__playfield superior-screen__playfield--hero" aria-label="Superior hero">
          <div className="superior-promo superior-promo--logo-only">
            <img
              className="superior-promo__emblem"
              src="/assets/superior-emblem.png"
              alt="Superior emblem"
              width="640"
              height="640"
              loading="eager"
              decoding="async"
            />
          </div>
        </section>

        <nav className="superior-screen__controls superior-screen__controls--simple" aria-label="Primary controls">
          <a className="machine-control machine-control--primary" href={installerUrl}>
            <span>Download EXE</span>
          </a>
          <a className="machine-control machine-control--step" href={portableUrl}>
            <span>Portable ZIP</span>
          </a>
          <a className="machine-control machine-control--commit" href="/docs/">
            <span>Docs</span>
          </a>
        </nav>
      </div>
    </main>
  );
}
