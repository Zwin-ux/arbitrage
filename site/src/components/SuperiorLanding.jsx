const starField = [
  { left: "8%", top: "10%", size: 4, color: "var(--white)", delay: "0s" },
  { left: "18%", top: "24%", size: 6, color: "var(--cyan)", delay: "1s" },
  { left: "29%", top: "14%", size: 4, color: "var(--purple)", delay: "2s" },
  { left: "41%", top: "20%", size: 4, color: "var(--white)", delay: "1.5s" },
  { left: "54%", top: "12%", size: 6, color: "var(--magenta)", delay: "0.6s" },
  { left: "68%", top: "18%", size: 4, color: "var(--cyan)", delay: "2.2s" },
  { left: "82%", top: "11%", size: 4, color: "var(--white)", delay: "0.2s" },
  { left: "90%", top: "26%", size: 6, color: "var(--purple)", delay: "1.1s" },
  { left: "13%", top: "58%", size: 4, color: "var(--cyan)", delay: "0.8s" },
  { left: "24%", top: "74%", size: 6, color: "var(--white)", delay: "1.7s" },
  { left: "36%", top: "66%", size: 4, color: "var(--magenta)", delay: "0.4s" },
  { left: "49%", top: "78%", size: 4, color: "var(--white)", delay: "2.3s" },
  { left: "63%", top: "64%", size: 6, color: "var(--cyan)", delay: "1.3s" },
  { left: "75%", top: "72%", size: 4, color: "var(--purple)", delay: "0.9s" },
  { left: "88%", top: "60%", size: 4, color: "var(--white)", delay: "2.1s" }
];

const palette = {
  c: "var(--cyan)",
  m: "var(--magenta)",
  p: "var(--purple)",
  w: "var(--white)",
  g: "var(--green)",
  y: "var(--gold)"
};

const sprites = {
  robot: [
    "..cccc..",
    ".cwwwwc.",
    "cwwppwwc",
    "cwppppwc",
    "cwccccwc",
    ".cwccwc.",
    ".p....p.",
    "p......p"
  ],
  scanner: [
    "....c...",
    "...ccc..",
    "..ccccc.",
    ".ccccccc",
    "cccccccc",
    ".ppyypp.",
    "..p..p..",
    ".p....p."
  ],
  docs: [
    "wwwwww..",
    "wccccw..",
    "wccccw..",
    "wppppw..",
    "wccccw..",
    "wccccw..",
    "wwwwww..",
    "........"
  ],
  chip: [
    "..yyyy..",
    ".yccccy.",
    "ycwwwwcy",
    "ycwggwcy",
    "ycwggwcy",
    "ycwwwwcy",
    ".yccccy.",
    "..yyyy.."
  ],
  coin: [
    "..yyyy..",
    ".ywwwwy.",
    "ywyyyywy",
    "ywyyyywy",
    "ywyyyywy",
    "ywyyyywy",
    ".ywwwwy.",
    "..yyyy.."
  ]
};

function PixelSprite({ name, label }) {
  const rows = sprites[name];
  return (
    <div
      aria-label={label}
      className="grid grid-cols-8 gap-px border-2 border-white bg-[#0A0F2E] p-2"
      role="img"
    >
      {rows.join("").split("").map((cell, index) => (
        <span
          key={`${name}-${index}`}
          className="block h-2 w-2"
          style={{ backgroundColor: palette[cell] ?? "transparent" }}
        />
      ))}
    </div>
  );
}

function PanelHeading({ sprite, title, label, accent = "var(--cyan)" }) {
  return (
    <div className="mb-4 flex items-center justify-between gap-4 border-b-2 border-white pb-4">
      <div className="flex items-center gap-4">
        <PixelSprite name={sprite} label={title} />
        <div>
          <p className="font-display text-[8px] uppercase leading-[16px] text-white">{label}</p>
          <p className="font-body text-[24px] uppercase leading-[24px]" style={{ color: accent }}>
            {title}
          </p>
        </div>
      </div>
      <span className="font-display text-[8px] uppercase leading-[16px] text-white">v1</span>
    </div>
  );
}

export default function SuperiorLanding({ variant }) {
  return (
    <div className="relative overflow-hidden bg-[var(--space)] text-white">
      <div className="pointer-events-none absolute inset-0">
        {starField.map((star, index) => (
          <span
            key={`star-${index}`}
            className="pixel-star absolute"
            style={{
              left: star.left,
              top: star.top,
              width: `${star.size}px`,
              height: `${star.size}px`,
              backgroundColor: star.color,
              animationDelay: star.delay
            }}
          />
        ))}
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 pb-24 pt-4 sm:px-8">
        <header className="pixel-panel px-4 py-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <a className="flex items-center gap-4" href="/">
              <PixelSprite name="chip" label="Superior cartridge icon" />
              <div>
                <p className="font-display text-[8px] uppercase leading-[16px] text-white">Superior</p>
                <p className="font-body text-[24px] uppercase leading-[24px] text-[var(--cyan)]">
                  paper-first bot cabinet
                </p>
              </div>
            </a>

            <nav className="flex flex-wrap gap-2">
              <a className="pixel-chip" href="#features">
                Features
              </a>
              <a className="pixel-chip" href="#product">
                Product
              </a>
              <a className="pixel-chip" href="/docs">
                Docs
              </a>
              <a className="pixel-button-secondary" href="/download">
                Download
              </a>
            </nav>
          </div>
        </header>

        <main className="flex flex-1 flex-col gap-16 pt-16">
          <section className="mx-auto flex w-full max-w-[960px] flex-col items-center gap-8 text-center">
            <div className="pixel-panel-alt pixel-frame pixel-scan w-full max-w-[480px] p-4">
              <div className="border-b-2 border-white pb-4">
                <p className="font-display text-[8px] uppercase leading-[16px] text-white">Superior cartridge art</p>
              </div>
              <div className="mt-4 border-2 border-white bg-[var(--panel-dark)] p-4">
                <img
                  alt="Superior cartridge art logo"
                  className="pixel-art mx-auto block w-full max-w-[320px]"
                  src="/assets/superior-logo.png"
                />
              </div>
            </div>

            <div className="flex flex-col items-center gap-6">
              <p className="font-display text-[8px] uppercase leading-[16px] text-[var(--gold)]">{variant.eyebrow}</p>
              <h1 className="font-display text-[32px] uppercase leading-[48px] text-white sm:text-[48px] sm:leading-[64px] lg:text-[64px] lg:leading-[80px]">
                {variant.headlineLead}
                <span className="mt-4 block text-[var(--cyan)]">{variant.headlineAccent}</span>
              </h1>
              <p className="max-w-[720px] font-body text-[24px] leading-[32px] text-white">
                {variant.subhead}
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <a className="pixel-button" href={variant.windowsInstallerUrl}>
                Download for Windows
              </a>
              <a className="pixel-button-secondary" href={variant.secondaryCtaHref}>
                Open setup menu
              </a>
            </div>

            <div className="flex flex-wrap justify-center gap-2">
              {variant.badges.map((item) => (
                <span key={item} className="pixel-chip">
                  {item}
                </span>
              ))}
            </div>

            <div className="pixel-screen w-full max-w-[720px] p-4">
              <p className="font-display text-[8px] uppercase leading-[16px] text-white">Score board</p>
              <div className="mt-4 grid gap-2 sm:grid-cols-3">
                <div className="border-2 border-white p-3">
                  <p className="font-display text-[8px] uppercase leading-[16px] text-white">paper score</p>
                  <p className="font-body text-[24px] uppercase leading-[24px] text-[var(--green)]">active</p>
                </div>
                <div className="border-2 border-white p-3">
                  <p className="font-display text-[8px] uppercase leading-[16px] text-white">live score</p>
                  <p className="font-body text-[24px] uppercase leading-[24px] text-[var(--cyan)]">reserved</p>
                </div>
                <div className="border-2 border-white p-3">
                  <p className="font-display text-[8px] uppercase leading-[16px] text-white">loadout</p>
                  <p className="font-body text-[24px] uppercase leading-[24px] text-[var(--magenta)]">equipped</p>
                </div>
              </div>
            </div>
          </section>

          <section id="features" className="grid gap-6 lg:grid-cols-3">
            {variant.featureCards.map((card, index) => {
              const sprite = ["robot", "scanner", "coin"][index] ?? "robot";
              const accent = ["var(--cyan)", "var(--magenta)", "var(--gold)"][index] ?? "var(--cyan)";
              return (
                <article key={card.title} className="pixel-panel p-6">
                  <PanelHeading accent={accent} label={`0${index + 1}`} sprite={sprite} title={card.title} />
                  <p className="font-body text-[24px] leading-[32px] text-white">{card.body}</p>
                </article>
              );
            })}
          </section>

          <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <article className="pixel-panel-alt p-6">
              <PanelHeading accent="var(--cyan)" label="setup flow" sprite="chip" title={variant.setupTitle} />
              <p className="font-body text-[24px] leading-[32px] text-white">{variant.setupBody}</p>
              <div className="mt-6 grid gap-4 md:grid-cols-3">
                {variant.setupSteps.map((step, index) => (
                  <article key={step.title} className="border-2 border-white bg-[var(--panel-dark)] p-4">
                    <p className="font-display text-[8px] uppercase leading-[16px] text-[var(--gold)]">
                      0{index + 1}
                    </p>
                    <p className="mt-2 font-display text-[8px] uppercase leading-[16px] text-white">{step.title}</p>
                    <p className="mt-4 font-body text-[24px] leading-[32px] text-white">{step.body}</p>
                  </article>
                ))}
              </div>
            </article>

            <aside className="pixel-screen p-6">
              <PanelHeading accent="var(--green)" label="field note" sprite="docs" title="first launch" />
              <p className="font-body text-[24px] leading-[32px] text-white">{variant.setupCaption}</p>
              <div className="mt-6 border-2 border-white p-4">
                <p className="font-display text-[8px] uppercase leading-[16px] text-white">menu</p>
                <div className="mt-4 flex flex-col gap-2">
                  <div className="border-2 border-[var(--cyan)] bg-[var(--cyan)] px-4 py-3 font-display text-[8px] uppercase leading-[16px] text-[var(--space)]">
                    &gt; guided setup
                  </div>
                  <div className="border-2 border-white px-4 py-3 font-display text-[8px] uppercase leading-[16px] text-white">
                    public data first
                  </div>
                  <div className="border-2 border-white px-4 py-3 font-display text-[8px] uppercase leading-[16px] text-white">
                    credentials later
                  </div>
                </div>
              </div>
            </aside>
          </section>

          <section id="product" className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
            <article className="pixel-panel p-6">
              <PanelHeading accent="var(--magenta)" label="bot interface" sprite="scanner" title={variant.productTitle} />
              <p className="font-body text-[24px] leading-[32px] text-white">{variant.productBody}</p>
            </article>

            <div className="grid gap-4">
              {variant.productNotes.map((note, index) => {
                const sprite = ["docs", "robot", "chip"][index] ?? "docs";
                const accent = ["var(--cyan)", "var(--green)", "var(--gold)"][index] ?? "var(--cyan)";
                return (
                  <article key={note.title} className="pixel-screen p-4">
                    <PanelHeading accent={accent} label={`note 0${index + 1}`} sprite={sprite} title={note.title} />
                    <p className="font-body text-[24px] leading-[32px] text-white">{note.body}</p>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="pixel-panel-alt p-6">
            <PanelHeading accent="var(--gold)" label="download menu" sprite="coin" title={variant.downloadTitle} />
            <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
              <div>
                <p className="font-body text-[24px] leading-[32px] text-white">{variant.downloadBody}</p>
                <div className="mt-6 flex flex-wrap gap-4">
                  <a className="pixel-button" href={variant.windowsInstallerUrl}>
                    Download windows build
                  </a>
                  <a className="pixel-button-secondary" href="/download">
                    Open full menu
                  </a>
                </div>
              </div>

              <div className="pixel-screen p-4">
                <p className="font-display text-[8px] uppercase leading-[16px] text-white">first mission</p>
                <div className="mt-4 space-y-2">
                  <div className="border-2 border-white px-4 py-3 font-body text-[24px] leading-[24px] text-[var(--green)]">
                    [OK] install windows build
                  </div>
                  <div className="border-2 border-white px-4 py-3 font-body text-[24px] leading-[24px] text-[var(--cyan)]">
                    [OK] equip polymarket
                  </div>
                  <div className="border-2 border-white px-4 py-3 font-body text-[24px] leading-[24px] text-[var(--magenta)]">
                    [RUN] record, scan, score
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
