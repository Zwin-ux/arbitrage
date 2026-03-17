function HeaderLink({ href, children }) {
  return (
    <a className="header-nav-link" href={href}>
      {children}
    </a>
  );
}

export default function SuperiorHeader({ variant }) {
  return (
    <header className="header-frame">
      <a className="header-brand" href="/">
        <span className="header-brand-mark">
          <img alt="Superior mark" src="/assets/superior-head.png" />
        </span>
        <span className="header-brand-copy">
          <span className="header-kicker">{variant.brandEyebrow}</span>
          <strong>{variant.brandTitle}</strong>
          <span className="header-subtitle">{variant.brandSubtitle}</span>
        </span>
      </a>

      <div className="header-actions">
        <nav aria-label="Primary" className="header-nav">
          <HeaderLink href="#system-state">State</HeaderLink>
          <HeaderLink href="#signal-pipeline">Pipeline</HeaderLink>
          <HeaderLink href="#route-inspection">Inspection</HeaderLink>
          <HeaderLink href="/docs">Docs</HeaderLink>
        </nav>

        <a className="header-download" href={variant.windowsInstallerUrl}>
          Download Win
        </a>
      </div>
    </header>
  );
}
