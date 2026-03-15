export default function FooterStrip({ variant }) {
  return (
    <footer className="footer-strip">
      <div>
        <p className="section-label">Open source Windows build</p>
        <p className="footer-copy">Local-first. Paper-first. Score attack on real local books.</p>
      </div>

      <nav aria-label="Footer" className="footer-links">
        {variant.footerLinks.map((link) => (
          <a key={link.label} href={link.href} target={link.href.startsWith("http") ? "_blank" : undefined} rel={link.href.startsWith("http") ? "noreferrer" : undefined}>
            {link.label}
          </a>
        ))}
      </nav>
    </footer>
  );
}
