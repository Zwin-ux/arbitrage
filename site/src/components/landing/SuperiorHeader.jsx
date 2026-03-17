function HeaderLink({ href, children }) {
  return (
    <a className="nav-link" href={href}>
      {children}
    </a>
  );
}

export default function SuperiorHeader({ variant }) {
  return (
    <header className="landing-header">
      <a className="landing-brand" href="/">
        <span className="landing-brand-mark">
          <img alt="Superior mark" className="h-full w-full object-cover" src="/assets/superior-head.png" />
        </span>
        <span className="landing-brand-copy">
          <small>{variant.brandEyebrow}</small>
          <strong>{variant.brandTitle}</strong>
          <em>{variant.brandSubtitle}</em>
        </span>
      </a>

      <div className="landing-header-actions">
        <nav aria-label="Primary" className="landing-nav">
          <HeaderLink href="#features">Features</HeaderLink>
          <HeaderLink href="#product">Product</HeaderLink>
          <HeaderLink href="/docs">Docs</HeaderLink>
        </nav>

        <a className="cta-primary" href={variant.windowsInstallerUrl}>
          Download
        </a>
      </div>
    </header>
  );
}
