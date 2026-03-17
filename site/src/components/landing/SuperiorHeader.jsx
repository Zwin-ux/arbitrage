function HeaderLink({ href, children }) {
  return (
    <a className="header-link" href={href}>
      {children}
    </a>
  );
}

export default function SuperiorHeader({ variant }) {
  return (
    <header className="header-frame">
      <a className="header-brand" href="/">
        <span className="header-mark">
          <img alt="Superior mark" src="/assets/superior-head.png" />
        </span>
        <span className="header-copy">
          <span className="header-kicker">{variant.brandEyebrow}</span>
          <strong>{variant.brandTitle}</strong>
          <span className="header-subtitle">{variant.brandSubtitle}</span>
        </span>
      </a>

      <nav aria-label="Primary" className="header-nav">
        <HeaderLink href="#how">HOW</HeaderLink>
        <HeaderLink href="#download">DOWNLOAD</HeaderLink>
        <HeaderLink href="/docs">DOCS</HeaderLink>
      </nav>
    </header>
  );
}
