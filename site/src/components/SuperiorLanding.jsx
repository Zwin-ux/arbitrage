const graphBars = [
  22, 28, 18, 34, 41, 36, 54, 46, 62, 58, 74, 69, 82, 76, 88, 80, 92
];

function ArcadeButton({ href, children, secondary = false, newTab = false }) {
  const className = secondary ? "arcade-button-secondary" : "arcade-button";
  const rel = newTab ? "noreferrer" : undefined;
  const target = newTab ? "_blank" : undefined;
  return (
    <a className={className} href={href} rel={rel} target={target}>
      {children}
    </a>
  );
}

function AccentValue({ accent, children }) {
  const map = {
    cyan: "text-[var(--cyan)]",
    magenta: "text-[var(--magenta)]",
    purple: "text-[var(--purple)]",
    green: "text-[var(--green)]",
    gold: "text-[var(--gold)]",
    white: "text-white"
  };
  return <span className={map[accent] ?? "text-white"}>{children}</span>;
}

function ScreenFrame({ title, children, className = "" }) {
  return (
    <section className={`arcade-panel ${className}`}>
      <div className="flex items-center justify-between border-b border-white/15 px-5 py-3 font-ui text-[11px] uppercase tracking-[0.35em] text-white/75">
        <span>{title}</span>
        <span>v1</span>
      </div>
      <div className="p-5 sm:p-6">{children}</div>
    </section>
  );
}

export default function SuperiorLanding({ variant }) {
  return (
    <div className="arcade-shell relative min-h-screen overflow-hidden text-white">
      <div className="arcade-grid absolute inset-0 opacity-50" />

      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 pb-20 pt-5 sm:px-8 lg:px-10">
        <header className="arcade-strip flex flex-wrap items-center justify-between gap-4 px-4 py-3">
          <a className="flex items-center gap-3" href="/">
            <div className="arcade-mark flex h-14 w-14 items-center justify-center overflow-hidden">
              <img
                alt="Superior mark"
                className="pixel-art h-full w-full object-cover"
                src="/assets/superior-head.png"
              />
            </div>
            <div>
              <p className="font-display text-[10px] uppercase tracking-[0.35em] text-white">Superior</p>
              <p className="mt-2 font-ui text-[12px] uppercase tracking-[0.28em] text-[var(--cyan)]">
                paper-first market scanner
              </p>
            </div>
          </a>

          <nav className="flex flex-wrap items-center gap-2 font-ui text-[11px] uppercase tracking-[0.28em]">
            <a className="arcade-nav-chip" href="#scanner">
              Scanner
            </a>
            <a className="arcade-nav-chip" href="#features">
              Features
            </a>
            <a className="arcade-nav-chip" href="#flow">
              How It Works
            </a>
            <ArcadeButton href={variant.windowsInstallerUrl}>Download Superior</ArcadeButton>
          </nav>
        </header>

        <main className="flex flex-1 flex-col gap-12 pt-6 sm:gap-16 sm:pt-8">
          <section className="space-y-6">
            <div className="arcade-marquee flex flex-col gap-2 px-4 py-2.5 font-ui text-[10px] uppercase tracking-[0.34em] text-white/80 sm:flex-row sm:items-center sm:justify-between">
              <span>{variant.heroMarqueeLeft}</span>
              <span>{variant.heroMarqueeRight}</span>
            </div>

            <div className="arcade-cabinet relative overflow-hidden px-4 py-5 sm:px-6 sm:py-6 lg:px-8">
              <div className="mx-auto max-w-3xl">
                <div className="arcade-logo-stage relative mx-auto flex max-w-xl justify-center border border-white/12 px-4 py-4 sm:px-6 sm:py-5">
                  <img
                    alt="Superior emblem"
                    className="pixel-art relative z-10 w-full max-w-[18rem] sm:max-w-[20rem] lg:max-w-[22rem]"
                    src="/assets/superior-emblem.png"
                  />
                </div>

                <div className="mt-6 text-center">
                  <p className="font-ui text-[11px] uppercase tracking-[0.42em] text-[var(--gold)]">{variant.eyebrow}</p>
                  <h1 className="mt-4 font-display text-[24px] uppercase leading-[1.65] text-white sm:text-[34px] lg:text-[42px]">
                    {variant.titleLines.map((line) => (
                      <span key={line} className="block">
                        {line}
                      </span>
                    ))}
                  </h1>
                  <p className="mx-auto mt-4 max-w-3xl text-balance font-body text-[1rem] leading-7 text-white/78 sm:text-[1.08rem]">
                    {variant.subhead}
                  </p>
                </div>

                <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
                  <ArcadeButton href={variant.windowsInstallerUrl}>Download Superior</ArcadeButton>
                  <ArcadeButton href={variant.portableUrl} secondary>
                    Portable Build
                  </ArcadeButton>
                </div>

                <div className="mt-8 grid gap-4 md:grid-cols-3">
                  {variant.scoreCards.map((card) => (
                    <div
                      key={card.label}
                      className="border border-white/10 bg-[rgba(9,14,40,0.78)] px-4 py-4"
                    >
                      <p className="font-ui text-[10px] uppercase tracking-[0.28em] text-white/60">{card.label}</p>
                      <p className="mt-3 font-display text-[14px] uppercase leading-[1.8]">
                        <AccentValue accent={card.accent}>{card.value}</AccentValue>
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <section id="scanner" className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
            <ScreenFrame title={variant.scannerFrameTitle} className="overflow-hidden">
              <div className="grid gap-6 lg:grid-cols-[1.08fr_0.92fr]">
                <div className="arcade-screen relative min-h-[23rem] overflow-hidden border border-white/10 p-5">
                  <img
                    alt=""
                    aria-hidden="true"
                    className="pointer-events-none absolute inset-0 h-full w-full object-cover opacity-40"
                    src="/assets/superior-scanner-frame.png"
                  />
                  <div className="absolute inset-0 opacity-70 [background-image:linear-gradient(rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.06)_1px,transparent_1px)] [background-size:2.2rem_2.2rem]" />
                  <div className="scanner-sweep absolute left-1/2 top-1/2 h-52 w-52 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[rgba(255,255,255,0.18)]" />
                  <div className="absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[rgba(255,255,255,0.08)]" />
                  <div className="absolute left-1/2 top-1/2 h-44 w-44 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[rgba(0,229,255,0.26)]" />
                  <span className="signal-dot left-[22%] top-[30%] bg-[var(--cyan)]" />
                  <span className="signal-dot left-[58%] top-[24%] bg-[var(--magenta)] [animation-delay:0.7s]" />
                  <span className="signal-dot left-[72%] top-[58%] bg-[var(--green)] [animation-delay:1.1s]" />
                  <span className="signal-dot left-[34%] top-[68%] bg-[var(--gold)] [animation-delay:0.3s]" />

                  <div className="relative z-10 flex h-full flex-col justify-between">
                    <div className="grid gap-3 sm:grid-cols-3">
                      {variant.scannerStats.map((stat) => (
                        <div key={stat.label} className="border border-white/12 bg-[rgba(4,6,18,0.82)] px-3 py-3">
                          <p className="font-ui text-[10px] uppercase tracking-[0.26em] text-white/62">{stat.label}</p>
                          <p className="mt-3 font-display text-[13px] uppercase leading-[1.9]">
                            <AccentValue accent={stat.accent}>{stat.value}</AccentValue>
                          </p>
                        </div>
                      ))}
                    </div>

                    <div className="border border-white/10 bg-[rgba(4,6,18,0.82)] px-4 py-4">
                      <div className="flex items-end gap-2">
                        {graphBars.map((bar, index) => (
                          <span
                            key={`bar-${index}`}
                            className="block w-3 bg-[var(--cyan)]"
                            style={{ height: `${bar}%` }}
                          />
                        ))}
                      </div>
                      <p className="mt-4 font-ui text-[10px] uppercase tracking-[0.22em] text-white/58">
                        Illustrative scan preview. Final route quality depends on local market data.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col gap-4">
                  <div className="border border-white/10 bg-[rgba(6,8,26,0.72)] px-4 py-4">
                    <p className="font-ui text-[10px] uppercase tracking-[0.3em] text-[var(--gold)]">Scanner summary</p>
                    <p className="mt-4 font-body text-[1rem] leading-7 text-white/78">{variant.scannerCopy}</p>
                  </div>

                  <div className="border border-white/10 bg-[rgba(6,8,26,0.72)] px-4 py-4">
                    <p className="font-ui text-[10px] uppercase tracking-[0.3em] text-[var(--cyan)]">Recent checks</p>
                    <div className="mt-4 space-y-3">
                      {variant.signalFeed.map((item) => (
                        <div
                          key={item}
                          className="border border-white/10 bg-[rgba(4,6,18,0.82)] px-3 py-3 font-ui text-[11px] uppercase tracking-[0.2em] text-white/78"
                        >
                          {item}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="border border-white/10 bg-[rgba(6,8,26,0.72)] px-4 py-4">
                    <p className="font-ui text-[10px] uppercase tracking-[0.3em] text-[var(--purple)]">System state</p>
                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      {variant.loadout.map((slot) => (
                        <div
                          key={slot.label}
                          className="border border-white/10 bg-[rgba(4,6,18,0.82)] px-3 py-3"
                        >
                          <p className="font-ui text-[10px] uppercase tracking-[0.24em] text-white/58">{slot.label}</p>
                          <p className="mt-3 font-display text-[12px] uppercase leading-[1.8]">
                            <AccentValue accent={slot.accent}>{slot.state}</AccentValue>
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </ScreenFrame>
          </section>

          <section id="features" className="space-y-6">
            <div className="max-w-3xl">
              <p className="font-ui text-[11px] uppercase tracking-[0.38em] text-[var(--gold)]">Product</p>
              <h2 className="mt-4 font-display text-[20px] uppercase leading-[1.9] text-white sm:text-[26px]">
                Purpose-built for readable market work.
                <span className="block text-[var(--cyan)]">Local recording, explainable routes, controlled unlocks.</span>
              </h2>
            </div>

            <div className="grid gap-5 lg:grid-cols-3">
              {variant.featureCards.map((card, index) => {
                const accents = ["cyan", "magenta", "green"];
                return (
                  <article
                    key={card.title}
                    className="arcade-panel min-h-[14rem] bg-[rgba(14,20,56,0.86)]"
                  >
                    <div className="p-5 sm:p-6">
                      <p className="font-ui text-[10px] uppercase tracking-[0.32em] text-white/58">0{index + 1}</p>
                      <h3 className="mt-4 font-display text-[14px] uppercase leading-[1.9]">
                        <AccentValue accent={accents[index]}>{card.title}</AccentValue>
                      </h3>
                      <p className="mt-5 font-body text-[1rem] leading-7 text-white/78">{card.body}</p>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>

          <section id="flow" className="arcade-panel bg-[rgba(13,17,48,0.86)]">
            <div className="p-6 sm:p-8">
              <div className="max-w-3xl">
                <p className="font-ui text-[11px] uppercase tracking-[0.38em] text-[var(--magenta)]">Setup flow</p>
                <h2 className="mt-4 font-display text-[20px] uppercase leading-[1.9] text-white sm:text-[28px]">
                  Start safely, then add complexity deliberately.
                  <span className="block text-[var(--cyan)]">Install, record, inspect, paper.</span>
                </h2>
              </div>

              <div className="mt-8 grid gap-4 lg:grid-cols-4">
                {variant.steps.map((step) => (
                  <article
                    key={step.step}
                    className="border border-white/10 bg-[rgba(9,14,40,0.78)] px-4 py-5"
                  >
                    <p className="font-display text-[12px] uppercase leading-[1.8] text-[var(--gold)]">{step.step}</p>
                    <p className="mt-3 font-ui text-[11px] uppercase tracking-[0.26em] text-white">{step.title}</p>
                    <p className="mt-4 font-body text-[0.98rem] leading-7 text-white/78">{step.body}</p>
                  </article>
                ))}
              </div>
            </div>
          </section>

          <section className="arcade-panel bg-[rgba(14,18,52,0.88)]">
            <div className="grid gap-6 p-6 sm:p-8 lg:grid-cols-[1.1fr_0.9fr]">
              <div>
                <p className="font-ui text-[11px] uppercase tracking-[0.38em] text-[var(--gold)]">Download</p>
                <h2 className="mt-4 font-display text-[20px] uppercase leading-[1.9] text-white sm:text-[28px]">
                  Download the Windows build.
                </h2>
                <p className="mt-5 max-w-2xl font-body text-[1rem] leading-7 text-white/78">{variant.downloadLead}</p>
                <div className="mt-8 flex flex-wrap gap-4">
                  <ArcadeButton href={variant.windowsInstallerUrl}>Download Superior</ArcadeButton>
                  <ArcadeButton href={variant.portableUrl} secondary>
                    Portable Build
                  </ArcadeButton>
                  <ArcadeButton href={variant.githubUrl} newTab secondary>
                    View GitHub
                  </ArcadeButton>
                </div>
              </div>

              <div className="border border-white/10 bg-[rgba(6,8,26,0.7)] px-5 py-5">
                <p className="font-ui text-[10px] uppercase tracking-[0.28em] text-[var(--cyan)]">Release files</p>
                <p className="mt-4 font-body text-[1rem] leading-7 text-white/78">{variant.downloadNote}</p>
                <div className="mt-6 space-y-3">
                  <div className="border border-white/10 bg-[rgba(4,6,18,0.82)] px-3 py-3 font-ui text-[11px] uppercase tracking-[0.18em] text-white/74">
                    [OK] Windows installer online
                  </div>
                  <div className="border border-white/10 bg-[rgba(4,6,18,0.82)] px-3 py-3 font-ui text-[11px] uppercase tracking-[0.18em] text-white/74">
                    [OK] Portable zip online
                  </div>
                  <div className="border border-white/10 bg-[rgba(4,6,18,0.82)] px-3 py-3 font-ui text-[11px] uppercase tracking-[0.18em] text-white/74">
                    [OK] GitHub source public
                  </div>
                  <div className="border border-white/10 bg-[rgba(4,6,18,0.82)] px-3 py-3 font-ui text-[11px] uppercase tracking-[0.18em] text-white/74">
                    [HASH] <a className="underline decoration-white/35 underline-offset-4" href={variant.checksumsUrl}>SHA256SUMS.txt</a>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
