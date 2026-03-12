const windowsInstallerUrl =
  "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe";

const particles = [
  { left: "9%", top: "18%", size: 4, color: "rgba(101, 225, 255, 0.88)", duration: "11s" },
  { left: "18%", top: "68%", size: 3, color: "rgba(192, 122, 255, 0.78)", duration: "13s" },
  { left: "31%", top: "14%", size: 3, color: "rgba(255, 222, 131, 0.7)", duration: "10s" },
  { left: "44%", top: "76%", size: 5, color: "rgba(86, 246, 181, 0.7)", duration: "12s" },
  { left: "59%", top: "10%", size: 4, color: "rgba(121, 168, 255, 0.88)", duration: "9s" },
  { left: "72%", top: "22%", size: 3, color: "rgba(102, 255, 241, 0.8)", duration: "14s" },
  { left: "84%", top: "58%", size: 4, color: "rgba(243, 122, 214, 0.72)", duration: "11s" },
  { left: "91%", top: "28%", size: 2, color: "rgba(255, 235, 150, 0.64)", duration: "8.5s" }
];

const featureCards = [
  {
    title: "Market scan",
    body: "Reads fragmented markets without turning the interface into noise."
  },
  {
    title: "Edge detection",
    body: "Highlights what matters and leaves the rest in the background."
  },
  {
    title: "Precise action",
    body: "Designed around deliberate execution, not constant motion."
  }
];

const productNotes = [
  {
    title: "Local-first",
    body: "Your data, logs, and credentials stay in your environment."
  },
  {
    title: "Open-source",
    body: "The code, packaging flow, and site are all inspectable."
  },
  {
    title: "Windows-ready",
    body: "Desktop app, installer flow, and release pipeline are already in place."
  }
];

export default function SuperiorLanding() {
  return (
    <div className="relative overflow-hidden bg-[#050612] text-white">
      <div className="pointer-events-none absolute inset-0 bg-pixel-grid opacity-25 [mask-image:radial-gradient(circle_at_center,black,transparent_80%)]" />
      <div className="pointer-events-none absolute inset-0">
        {particles.map((particle, index) => (
          <span
            key={`particle-${index}`}
            className="particle absolute rounded-full blur-[1px]"
            style={{
              left: particle.left,
              top: particle.top,
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              backgroundColor: particle.color,
              boxShadow: `0 0 18px ${particle.color}`,
              "--drift-duration": particle.duration
            }}
          />
        ))}
      </div>

      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-8%] top-[10%] h-[24rem] w-[24rem] rounded-full bg-cyan-400/10 blur-[120px]" />
        <div className="absolute right-[-10%] top-[4%] h-[28rem] w-[28rem] rounded-full bg-fuchsia-500/10 blur-[140px]" />
        <div className="absolute bottom-[-14%] left-[26%] h-[26rem] w-[26rem] rounded-full bg-indigo-500/10 blur-[130px]" />
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 pb-20 pt-6 sm:px-8 lg:px-10">
        <header className="glass-panel pixel-frame sticky top-4 z-20 flex flex-wrap items-center justify-between gap-4 rounded-[24px] px-5 py-4">
          <a className="flex items-center gap-4" href="/">
            <div className="grid h-12 w-12 place-items-center rounded-[16px] border border-cyan-200/18 bg-[linear-gradient(135deg,rgba(54,181,230,0.18),rgba(171,88,255,0.22))] shadow-[0_0_22px_rgba(70,223,255,0.2)]">
              <div className="grid h-9 w-9 place-items-center rounded-[14px] bg-slate-950/76 font-display text-sm font-bold tracking-[0.22em] text-cyan-100">
                S
              </div>
            </div>
            <div>
              <p className="font-display text-base font-semibold uppercase tracking-[0.24em] text-cyan-100/92">Superior</p>
              <p className="text-sm text-slate-300/68">open-source market recorder</p>
            </div>
          </a>

          <nav className="flex flex-wrap items-center gap-2 text-sm text-slate-300/80">
            <a className="rounded-full px-4 py-2 transition hover:bg-white/5 hover:text-cyan-100" href="#features">
              Features
            </a>
            <a className="rounded-full px-4 py-2 transition hover:bg-white/5 hover:text-cyan-100" href="#product">
              Product
            </a>
            <a className="rounded-full px-4 py-2 transition hover:bg-white/5 hover:text-cyan-100" href="/docs">
              Docs
            </a>
            <a
              className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-4 py-2 font-medium text-cyan-100 transition hover:border-cyan-200/40 hover:bg-cyan-200/15"
              href="/download"
            >
              Download
            </a>
          </nav>
        </header>

        <main className="relative z-10 flex flex-1 flex-col justify-center pt-12 lg:pt-20">
          <section className="grid items-center gap-12 lg:grid-cols-[0.92fr_1.08fr]">
            <div className="space-y-8">
              <p className="font-display text-xs uppercase tracking-[0.32em] text-cyan-200/66">
                Open-source market recorder
              </p>

              <div className="space-y-5">
                <h1 className="font-display text-5xl font-semibold leading-[0.92] tracking-[-0.06em] text-white sm:text-6xl lg:text-7xl">
                  Scan markets.
                  <span className="block bg-[linear-gradient(135deg,#f8fbff_0%,#88ebff_40%,#d79dff_100%)] bg-clip-text text-transparent">
                    Find edge. Act with precision.
                  </span>
                </h1>
                <p className="max-w-2xl text-lg leading-8 text-slate-300/76">
                  Superior is a calm interface for an intelligent arbitrage system. The logo does the heavy lifting. The page
                  stays clean.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-4">
                <a
                  className="rounded-full bg-[linear-gradient(135deg,#67e4ff_0%,#7e63ff_56%,#f273dc_100%)] px-6 py-3.5 font-semibold text-slate-950 shadow-[0_0_34px_rgba(99,201,255,0.32)] transition hover:translate-y-[-1px]"
                  href={windowsInstallerUrl}
                >
                  Download for Windows
                </a>
                <a
                  className="rounded-full border border-white/12 bg-white/5 px-6 py-3.5 font-medium text-slate-100 transition hover:border-cyan-200/30 hover:bg-white/10"
                  href="/download"
                >
                  All download options
                </a>
              </div>

              <div className="flex flex-wrap gap-3">
                {["MIT licensed", "Local-first", "Windows first"].map((item) => (
                  <span
                    key={item}
                    className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-slate-300/78"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <div className="relative mx-auto flex max-w-[640px] justify-center">
              <div className="absolute inset-x-6 bottom-14 top-14 rounded-[40px] bg-[radial-gradient(circle_at_center,rgba(76,202,255,0.12),transparent_66%)] blur-3xl" />
              <div className="absolute inset-x-18 bottom-10 top-10 rounded-[999px] border border-cyan-300/10" />
              <div className="absolute inset-x-26 bottom-16 top-16 rounded-[999px] border border-fuchsia-300/8" />

              <div className="glass-panel pixel-frame summon-ring shadow-aura relative w-full rounded-[40px] px-6 py-10 sm:px-8 sm:py-12">
                <div className="pointer-events-none absolute inset-0 rounded-[40px] bg-[radial-gradient(circle_at_top,rgba(96,226,255,0.08),transparent_40%)]" />
                <div className="flex items-center justify-between text-xs uppercase tracking-[0.28em] text-slate-400/58">
                  <span>Superior</span>
                  <span>quiet interface</span>
                </div>

                <div className="relative mt-8 flex items-center justify-center">
                  <div className="absolute h-[74%] w-[74%] rounded-full bg-[radial-gradient(circle,rgba(66,233,255,0.24),transparent_65%)] blur-3xl" />
                  <div className="absolute h-[86%] w-[86%] rounded-full border border-cyan-300/14" />
                  <div className="absolute h-[98%] w-[98%] rounded-full border border-fuchsia-300/10" />
                  <img
                    src="/assets/superior-logo.png"
                    alt="Superior logo"
                    className="animate-float-slow relative z-10 w-full max-w-[500px] drop-shadow-[0_0_48px_rgba(80,225,255,0.32)]"
                  />
                </div>

                <div className="mt-8 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-[20px] border border-white/8 bg-slate-950/42 px-4 py-4">
                    <p className="font-display text-xs uppercase tracking-[0.22em] text-cyan-200/70">Signal</p>
                    <p className="mt-2 text-sm leading-7 text-slate-300/72">Readable market context without dashboard clutter.</p>
                  </div>
                  <div className="rounded-[20px] border border-white/8 bg-slate-950/42 px-4 py-4">
                    <p className="font-display text-xs uppercase tracking-[0.22em] text-fuchsia-200/70">Execution</p>
                    <p className="mt-2 text-sm leading-7 text-slate-300/72">A product surface built around clarity and control.</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section id="features" className="mt-20 grid gap-4 md:grid-cols-3">
            {featureCards.map((card) => (
              <article key={card.title} className="glass-panel pixel-frame rounded-[28px] p-6">
                <p className="font-display text-sm uppercase tracking-[0.24em] text-cyan-200/72">{card.title}</p>
                <p className="mt-3 text-base leading-7 text-slate-300/74">{card.body}</p>
              </article>
            ))}
          </section>

          <section id="product" className="mt-20 grid gap-6 lg:grid-cols-[1.08fr_0.92fr]">
            <article className="glass-panel pixel-frame rounded-[34px] p-7 sm:p-8">
              <p className="font-display text-sm uppercase tracking-[0.26em] text-cyan-200/70">Product surface</p>
              <h2 className="mt-4 font-display text-3xl font-semibold tracking-[-0.05em] text-white sm:text-4xl">
                Built to stay readable under pressure.
              </h2>
              <p className="mt-5 max-w-2xl text-base leading-8 text-slate-300/76">
                The design keeps the atmosphere from the logo, then removes everything that does not help comprehension. It should
                feel rare, but still usable.
              </p>
            </article>

            <div className="grid gap-4">
              {productNotes.map((note) => (
                <article key={note.title} className="glass-panel pixel-frame rounded-[28px] p-6">
                  <p className="font-display text-sm uppercase tracking-[0.24em] text-fuchsia-200/72">{note.title}</p>
                  <p className="mt-3 text-base leading-7 text-slate-300/74">{note.body}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="mt-20">
            <div className="glass-panel pixel-frame rounded-[34px] px-6 py-8 sm:px-10">
              <div className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
                <div className="max-w-3xl">
                  <p className="font-display text-sm uppercase tracking-[0.26em] text-cyan-200/70">Download</p>
                  <h2 className="mt-4 font-display text-3xl font-semibold tracking-[-0.05em] text-white sm:text-4xl">
                    Windows build on GitHub Releases. Source build available today.
                  </h2>
                  <p className="mt-4 text-base leading-8 text-slate-300/78">
                    If the packaged release is not published yet, the docs page shows the local build path. No dead-end button.
                  </p>
                </div>

                <div className="flex flex-wrap gap-4">
                  <a
                    className="rounded-full border border-cyan-200/24 bg-cyan-300/12 px-6 py-3.5 font-medium text-cyan-100 transition hover:border-cyan-200/42 hover:bg-cyan-200/18"
                    href={windowsInstallerUrl}
                  >
                    Download for Windows
                  </a>
                  <a
                    className="rounded-full border border-white/10 bg-white/5 px-6 py-3.5 font-medium text-slate-100 transition hover:bg-white/10"
                    href="/download"
                  >
                    Other options
                  </a>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
