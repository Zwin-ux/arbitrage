const laneMarkers = [
  { id: "signal", label: "SIGNAL", position: "18%" },
  { id: "edge", label: "EDGE", position: "68%" },
  { id: "lock", label: "LOCK", position: "84%" },
];

export default function SuperiorLanding({ variant }) {
  const modeLabel = variant?.navLabel?.toUpperCase() ?? "CONTROL";
  const installerUrl = variant?.windowsInstallerUrl ?? "/download/";
  const docsUrl = "/docs/";
  const downloadUrl = "/download/";
  const resetUrl = variant?.githubUrl ?? "https://github.com/Zwin-ux/arbitrage";

  const controls = [
    { label: "START", href: downloadUrl, kind: "primary" },
    { label: "STEP", href: docsUrl, kind: "step" },
    { label: "HOLD TO COMMIT", href: installerUrl, kind: "commit", external: true },
    { label: "RESET", href: resetUrl, kind: "reset", external: true },
  ];

  return (
    <main className="superior-shell">
      <div className="superior-screen">
        <header className="superior-screen__header">
          <div className="superior-screen__brand">
            <img
              src="/assets/superior-head.png"
              alt=""
              width="30"
              height="30"
              loading="eager"
              decoding="async"
            />
            <span>SUPERIOR</span>
          </div>

          <div className="superior-screen__status" aria-label="Machine status">
            <span>{modeLabel}</span>
            <span>LOCAL / LIVE LOCKED</span>
          </div>
        </header>

        <section className="superior-screen__playfield" aria-label="Decision lane">
          <div className="decision-lane">
            <span className="decision-lane__track" aria-hidden="true" />
            <span className="decision-lane__runner" aria-hidden="true" />

            <span className="decision-lane__anchor" aria-hidden="true">
              <span className="decision-lane__anchor-line" />
              <span className="decision-lane__anchor-node" />
            </span>
            <span className="decision-lane__anchor-label">YOU</span>

            {laneMarkers.map((marker) => (
              <span
                key={marker.id}
                className="decision-lane__marker"
                style={{ "--marker-position": marker.position }}
              >
                <span className="decision-lane__marker-node" aria-hidden="true" />
                <span className="decision-lane__marker-label">{marker.label}</span>
              </span>
            ))}
          </div>
        </section>

        <nav className="superior-screen__controls" aria-label="Primary controls">
          {controls.map((control) => (
            <a
              key={control.label}
              className={`machine-control machine-control--${control.kind}`}
              href={control.href}
              {...(control.external ? { target: "_blank", rel: "noreferrer" } : {})}
            >
              <span>{control.label}</span>
            </a>
          ))}
        </nav>
      </div>
    </main>
  );
}
