export default function ScannerVisual({
  compact = false,
  animated = true,
  className = "",
}) {
  const rays = Array.from({ length: 20 }, (_, index) => index);
  const dots = [
    "scanner-spark-left",
    "scanner-spark-top",
    "scanner-spark-right",
    "scanner-spark-bottom",
  ];
  const commands = ["Load bot", "Scan edge", "Paper run", "Bank score"];

  return (
    <div className={`scanner-stage ${compact ? "scanner-stage-compact" : ""} ${className}`.trim()}>
      {dots.map((dot, index) => (
        <span
          key={dot}
          aria-hidden="true"
          className={`scanner-spark ${dot} ${animated ? "scanner-spark-animated" : ""}`}
          style={{ animationDelay: `${index * 0.35}s` }}
        />
      ))}

      <div className="scanner-stage-radial" aria-hidden="true">
        {rays.map((ray) => (
          <span
            key={ray}
            className="scanner-stage-ray"
            style={{ transform: `translate(-50%, -100%) rotate(${ray * 18}deg)` }}
          />
        ))}
      </div>

      <div className="scanner-stage-core">
        <div className="scanner-stage-label">Superior signal core</div>
        <div className={`scanner-stage-screen ${animated ? "scanner-stage-screen-animated" : ""}`}>
          <img
            alt="Superior emblem"
            className={`scanner-emblem ${animated ? "scanner-emblem-flicker" : ""}`}
            src="/assets/superior-emblem.png"
          />
        </div>
      </div>

      <div className="scanner-command-strip" aria-label="Session loop">
        {commands.map((command, index) => (
          <span key={command} className={index === 0 ? "scanner-command-active" : ""}>
            {command}
          </span>
        ))}
      </div>
    </div>
  );
}
