export default function DownloadReleasePanel({ variant }) {
  return (
    <section className="section-frame download-frame" id="download">
      <div className="section-copy">
        <p className="panel-label">{variant.downloadPanel.eyebrow}</p>
        <h2 className="section-title">{variant.downloadPanel.title}</h2>
        <p className="section-body">{variant.downloadPanel.body}</p>
      </div>

      <div className="download-grid-panel">
        <div className="download-actions">
          <a className="button-primary" href={variant.windowsInstallerUrl}>
            {variant.primaryCtaLabel}
          </a>
          <a className="button-secondary" href={variant.portableUrl}>
            Portable Build
          </a>
          <a className="hero-link" href={variant.checksumsUrl}>
            SHA256 Checksums
          </a>
          <a className="hero-link" href={variant.githubUrl} target="_blank" rel="noreferrer">
            Source on GitHub
          </a>
        </div>

        <div className="release-status-panel" aria-label="Release distribution status">
          {variant.downloadPanel.releaseRows.map((row) => (
            <div key={row} className="release-status-row">
              {row}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
