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
        <span>
          <strong>{variant.brandTitle}</strong>
          <small>{variant.brandSubtitle}</small>
        </span>
      </a>

      <div className="landing-header-actions">
        <nav aria-label="Primary" className="landing-nav">
          <HeaderLink href="#scanner">Cabinet</HeaderLink>
          <HeaderLink href="#features">Loop</HeaderLink>
          <HeaderLink href="#preview">Session</HeaderLink>
        </nav>

        <a className="cta-primary" href={variant.windowsInstallerUrl}>
          Download Superior
        </a>
      </div>
    </header>
  );
}
