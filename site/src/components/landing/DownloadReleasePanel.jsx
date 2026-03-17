export default function DownloadReleasePanel({ variant }) {
  return (
    <section className="download-frame" id="download">
      <div className="download-head">
        <span>{variant.downloadPanel.eyebrow}</span>
        <p>{variant.downloadPanel.line}</p>
      </div>

      <div className="download-grid">
        <div className="download-links">
          <a className="download-link" href={variant.windowsInstallerUrl}>
            Windows installer
          </a>
          <a className="download-link" href={variant.portableUrl}>
            Portable build
          </a>
          <a className="download-link" href={variant.checksumsUrl}>
            SHA256 checksums
          </a>
          <a className="download-link" href={variant.githubUrl} target="_blank" rel="noreferrer">
            Source on GitHub
          </a>
        </div>

        <div className="release-list">
          {variant.downloadPanel.rows.map((row) => (
            <div key={row} className="release-row">
              <span>{row}</span>
              <strong>READY</strong>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
