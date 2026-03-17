export default function ScannerVisual({
  compact = false,
  animated = true,
  className = "",
}) {
  const rays = Array.from({ length: 18 }, (_, index) => index);
  const routeNodes = [
    { label: "OBS", className: "scanner-node-observe" },
    { label: "PRC", className: "scanner-node-price" },
    { label: "PPR", className: "scanner-node-paper" },
  ];

  return (
    <div className={`scanner-console ${compact ? "scanner-console-compact" : ""} ${className}`.trim()}>
      <div className="scanner-console-header">
        <span>SIGNAL CORE</span>
        <span>SECTOR A1</span>
      </div>

      <div className="scanner-console-stage">
        <div className="scanner-console-radial" aria-hidden="true">
          {rays.map((ray) => (
            <span
              key={ray}
              className="scanner-console-ray"
              style={{ transform: `translate(-50%, -100%) rotate(${ray * 20}deg)` }}
            />
          ))}
        </div>

        <div className="scanner-console-grid" aria-hidden="true" />
        <div className={`scanner-console-sweep ${animated ? "scanner-console-sweep-animated" : ""}`} aria-hidden="true" />

        <div className="scanner-console-target">
          <img
            alt="Superior emblem"
            className={`scanner-console-emblem ${animated ? "scanner-console-emblem-animated" : ""}`}
            src="/assets/superior-emblem.png"
          />
        </div>

        {routeNodes.map((node, index) => (
          <span
            key={node.label}
            className={`scanner-console-node ${node.className} ${animated ? "scanner-console-node-animated" : ""}`}
            style={{ animationDelay: `${index * 0.4}s` }}
          >
            {node.label}
          </span>
        ))}
      </div>

      <div className="scanner-console-footer">
        <span>MODE / PAPER</span>
        <span>LIVE / LOCKED</span>
        <span>DATA / LOCAL</span>
      </div>
    </div>
  );
}
