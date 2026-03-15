const lineCount = 72;

function accentClass(accent) {
  if (accent === "green") {
    return "text-[var(--accent-green)]";
  }
  if (accent === "magenta") {
    return "text-[var(--accent-magenta)]";
  }
  if (accent === "yellow") {
    return "text-[var(--accent-yellow)]";
  }
  return "text-[var(--accent-cyan)]";
}

export default function ScannerVisual({
  compact = false,
  animated = true,
  className = "",
  stats = [],
}) {
  const sweepClass = animated ? "scanner-sweep motion-safe:animate-[scanner-rotate_14s_linear_infinite]" : "scanner-sweep";
  const dots = [
    "left-[21%] top-[26%]",
    "left-[65%] top-[22%]",
    "left-[77%] top-[57%]",
    "left-[29%] top-[70%]",
    "left-[54%] top-[72%]",
  ];

  return (
    <div className={`scanner-frame ${compact ? "scanner-frame-compact" : ""} ${className}`.trim()}>
      <div className="scanner-stage">
        <div className="crt-overlay" />
        <svg
          aria-hidden="true"
          className="scanner-burst"
          viewBox="0 0 100 100"
          xmlns="http://www.w3.org/2000/svg"
        >
          <g stroke="rgba(0,234,255,0.38)" strokeWidth="0.28">
            {Array.from({ length: lineCount }).map((_, index) => {
              const angle = (index / lineCount) * Math.PI * 2;
              const x = 50 + Math.cos(angle) * 42;
              const y = 50 + Math.sin(angle) * 42;
              return <line key={`line-${index}`} x1="50" y1="50" x2={x} y2={y} />;
            })}
          </g>
        </svg>

        <div className={sweepClass} />
        <div className="scanner-ring scanner-ring-inner" />
        <div className="scanner-ring scanner-ring-mid" />
        <div className="scanner-ring scanner-ring-outer" />
        <div className="scanner-core" />

        {dots.map((position, index) => (
          <span
            key={`dot-${index}`}
            className={`scanner-dot ${position} ${index % 2 === 0 ? "bg-[var(--accent-cyan)]" : "bg-[var(--accent-magenta)]"}`}
            style={{ animationDelay: `${index * 0.5}s` }}
          />
        ))}

        <img
          alt="Superior emblem"
          className="pointer-events-none absolute left-1/2 top-1/2 z-20 w-[15rem] -translate-x-1/2 -translate-y-1/2 select-none object-contain sm:w-[17rem]"
          src="/assets/superior-emblem.png"
        />

        <div className="scanner-hud">
          <div className="scanner-hud-header">
            <span>SESSION CABINET</span>
            <span>SCORE ATTACK</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {stats.map((stat) => (
              <div key={stat.label} className="scanner-stat">
                <p>{stat.label}</p>
                <strong className={accentClass(stat.accent)}>{stat.value}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
