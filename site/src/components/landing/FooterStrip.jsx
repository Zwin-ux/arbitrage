export default function FooterStrip({ variant }) {
  return (
    <footer className="footer-strip">
      <div className="footer-strip-copy">
        <span>SUPERIOR</span>
        <p>LOCAL / TEST / LOCKED</p>
      </div>

      <nav aria-label="Footer" className="footer-strip-links">
        {variant.footerLinks.map((link) => (
          <a key={link.label} href={link.href}>
            {link.label}
          </a>
        ))}
      </nav>
    </footer>
  );
}
