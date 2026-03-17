export default function ScannerVisual({
  compact = false,
  animated = true,
  className = "",
}) {
  const rays = Array.from({ length: 24 }, (_, index) => index);
  const dots = [
    "scanner-spark-left",
    "scanner-spark-top",
    "scanner-spark-right",
    "scanner-spark-bottom",
  ];
  const commands = ["BOOT", "SCAN", "RUN", "BANK"];
  const readouts = [
    ["MODE", "PAPER"],
    ["FEED", "LOCAL"],
    ["GATE", "LOCKED"],
  ];

  return (
    <div className={`scanner-stage ${compact ? "scanner-stage-compact" : ""} ${className}`.trim()}>
      <div className="scanner-stage-header">
        <span>SIGNAL CORE</span>
        <span>SECTOR A1</span>
      </div>

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
        <div className="scanner-stage-target" aria-hidden="true" />
        <div className={`scanner-stage-screen ${animated ? "scanner-stage-screen-animated" : ""}`}>
          <img
            alt="Superior emblem"
            className={`scanner-emblem ${animated ? "scanner-emblem-flicker" : ""}`}
            src="/assets/superior-emblem.png"
          />
        </div>
      </div>

      <div className="scanner-readout-grid" aria-label="Machine state">
        {readouts.map(([label, value]) => (
          <div key={label} className="scanner-readout-card">
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
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
