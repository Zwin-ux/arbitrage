const particles = [
  { left: "8%", top: "18%", size: 5, color: "rgba(80, 225, 255, 0.95)", duration: "10s" },
  { left: "18%", top: "72%", size: 4, color: "rgba(190, 104, 255, 0.85)", duration: "13s" },
  { left: "29%", top: "22%", size: 3, color: "rgba(255, 210, 104, 0.78)", duration: "11s" },
  { left: "40%", top: "68%", size: 6, color: "rgba(84, 246, 170, 0.82)", duration: "12s" },
  { left: "52%", top: "10%", size: 4, color: "rgba(110, 162, 255, 0.92)", duration: "9s" },
  { left: "58%", top: "78%", size: 5, color: "rgba(255, 112, 214, 0.84)", duration: "10.5s" },
  { left: "72%", top: "18%", size: 3, color: "rgba(118, 255, 241, 0.88)", duration: "14s" },
  { left: "86%", top: "60%", size: 5, color: "rgba(176, 130, 255, 0.92)", duration: "11.5s" },
  { left: "78%", top: "40%", size: 2, color: "rgba(255, 236, 147, 0.75)", duration: "8.5s" },
  { left: "12%", top: "48%", size: 3, color: "rgba(106, 155, 255, 0.8)", duration: "12.2s" },
  { left: "62%", top: "56%", size: 2, color: "rgba(84, 246, 170, 0.8)", duration: "9.6s" },
  { left: "92%", top: "24%", size: 4, color: "rgba(255, 122, 214, 0.72)", duration: "13.5s" }
];

const pixels = [
  { left: "6%", top: "16%" },
  { left: "12%", top: "24%" },
  { left: "14%", top: "58%" },
  { left: "26%", top: "12%" },
  { left: "34%", top: "74%" },
  { left: "41%", top: "18%" },
  { left: "49%", top: "82%" },
  { left: "58%", top: "16%" },
  { left: "63%", top: "68%" },
  { left: "74%", top: "24%" },
  { left: "82%", top: "14%" },
  { left: "88%", top: "70%" }
];

const featureCards = [
  {
    title: "Scan",
    body: "Superior watches fragmented venues and surfaces the few signals worth taking seriously."
  },
  {
    title: "Detect",
    body: "Edge is ranked by clarity, not noise. Precision beats spectacle."
  },
  {
    title: "Act",
    body: "Execution is framed as calm, deliberate, and exact when conditions align."
  }
];

const principles = [
  "Rare-summon energy without chaotic gamer clutter",
  "Pixel-soft fantasy tech instead of a generic finance dashboard",
  "Sacred logo treatment as the core identity beacon",
  "A premium product shell built around restraint and confidence"
];

const ritualStats = [
  { label: "scan", value: "multi-market" },
  { label: "edge", value: "ranked calm" },
  { label: "action", value: "precise only" }
];

export default function SuperiorLanding() {
  return (
    <div className="relative overflow-hidden bg-[#03040b] text-white">
      <div className="pointer-events-none absolute inset-0 bg-pixel-grid opacity-40 [mask-image:radial-gradient(circle_at_center,black,transparent_85%)]" />
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
              boxShadow: `0 0 16px ${particle.color}`,
              "--drift-duration": particle.duration
            }}
          />
        ))}
        {pixels.map((pixel, index) => (
          <span
            key={`pixel-${index}`}
            className="pixel-star absolute h-2 w-2 rounded-[2px] bg-cyan-300/80 shadow-[0_0_16px_rgba(75,215,255,0.7)]"
            style={{
              left: pixel.left,
              top: pixel.top,
              "--twinkle-duration": `${3 + (index % 4)}s`
            }}
          />
        ))}
      </div>

      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-8%] top-[12%] h-[26rem] w-[26rem] rounded-full bg-cyan-400/10 blur-[120px]" />
        <div className="absolute right-[-10%] top-[6%] h-[30rem] w-[30rem] rounded-full bg-fuchsia-500/10 blur-[140px]" />
        <div className="absolute bottom-[-12%] left-[24%] h-[28rem] w-[28rem] rounded-full bg-indigo-500/10 blur-[130px]" />
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 pb-20 pt-6 sm:px-8 lg:px-10">
        <header className="glass-panel pixel-frame shine-border sticky top-4 z-20 flex flex-wrap items-center justify-between gap-4 rounded-[24px] px-5 py-4">
          <div className="flex items-center gap-4">
            <div className="grid h-12 w-12 place-items-center rounded-[16px] bg-[linear-gradient(135deg,rgba(66,233,255,0.22),rgba(181,76,255,0.34))] shadow-[0_0_24px_rgba(70,223,255,0.35)]">
              <div className="grid h-9 w-9 place-items-center rounded-[14px] border border-cyan-200/25 bg-slate-950/70 font-display text-sm font-bold tracking-[0.26em] text-cyan-200">
                S
              </div>
            </div>
            <div>
              <p className="font-display text-base font-semibold uppercase tracking-[0.24em] text-cyan-100/92">
                Superior
              </p>
              <p className="text-sm text-slate-300/72">intelligent arbitrage system</p>
            </div>
          </div>

          <nav className="flex flex-wrap items-center gap-2 text-sm text-slate-300/80">
            <a className="rounded-full px-4 py-2 transition hover:bg-white/5 hover:text-cyan-100" href="#features">
              Features
            </a>
            <a className="rounded-full px-4 py-2 transition hover:bg-white/5 hover:text-cyan-100" href="#precision">
              Precision
            </a>
            <a className="rounded-full px-4 py-2 transition hover:bg-white/5 hover:text-cyan-100" href="/docs">
              Docs
            </a>
            <a
              className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-4 py-2 font-medium text-cyan-100 transition hover:border-cyan-200/40 hover:bg-cyan-200/15"
              href="/download"
            >
              Summon the app
            </a>
          </nav>
        </header>

        <main className="relative z-10 flex flex-1 flex-col justify-center pt-12 lg:pt-20">
          <section className="grid items-center gap-14 lg:grid-cols-[1.02fr_0.98fr]">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-3 rounded-full border border-fuchsia-300/20 bg-fuchsia-300/8 px-4 py-2 text-xs font-semibold uppercase tracking-[0.32em] text-fuchsia-100/80">
                <span className="h-2 w-2 rounded-full bg-fuchsia-300 shadow-[0_0_14px_rgba(226,144,255,0.8)]" />
                Rare summon interface
              </div>

              <div className="space-y-5">
                <p className="font-display text-sm uppercase tracking-[0.34em] text-cyan-200/74">
                  calm / rare / smart
                </p>
                <h1 className="font-display text-5xl font-semibold leading-[0.92] tracking-[-0.06em] text-white sm:text-6xl lg:text-7xl">
                  Superior scans markets,
                  <span className="block bg-[linear-gradient(135deg,#f8fbff_0%,#81f1ff_38%,#d78bff_100%)] bg-clip-text text-transparent">
                    detects edge, and acts with precision.
                  </span>
                </h1>
                <p className="max-w-2xl text-lg leading-8 text-slate-300/78">
                  Designed like a sacred summon screen for an intelligent arbitrage bot: iconic, premium, and focused.
                  No dashboard clutter. Just signal, calm execution, and a visual identity that feels rare.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-4">
                <a
                  className="rounded-full bg-[linear-gradient(135deg,#55e1ff_0%,#7c5cff_55%,#f55ae7_100%)] px-6 py-3.5 font-semibold text-slate-950 shadow-[0_0_34px_rgba(99,201,255,0.42)] transition hover:translate-y-[-1px]"
                  href="/download"
                >
                  View Windows release
                </a>
                <a
                  className="rounded-full border border-white/12 bg-white/5 px-6 py-3.5 font-medium text-slate-100 transition hover:border-cyan-200/30 hover:bg-white/10"
                  href="https://github.com/Zwin-ux/arbitrage"
                  target="_blank"
                  rel="noreferrer"
                >
                  Inspect the source
                </a>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {featureCards.map((card) => (
                  <article key={card.title} className="glass-panel pixel-frame rounded-[26px] p-5">
                    <p className="font-display text-sm uppercase tracking-[0.28em] text-cyan-200/72">{card.title}</p>
                    <p className="mt-3 text-sm leading-7 text-slate-300/76">{card.body}</p>
                  </article>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="animate-ring-pulse h-[80%] w-[80%] rounded-full border border-cyan-300/20 bg-[radial-gradient(circle,rgba(76,202,255,0.14),transparent_72%)] blur-sm" />
                <div className="animate-ring-pulse-delayed absolute h-[92%] w-[92%] rounded-full border border-fuchsia-300/14 bg-[radial-gradient(circle,rgba(163,74,255,0.12),transparent_72%)]" />
              </div>

              <div className="relative mx-auto flex max-w-[620px] justify-center">
                <div className="absolute inset-x-6 bottom-14 top-14 rounded-[40px] bg-[radial-gradient(circle_at_center,rgba(76,202,255,0.12),transparent_66%)] blur-3xl" />
                <div className="absolute inset-x-16 bottom-10 top-10 rounded-[999px] border border-cyan-300/12" />
                <div className="absolute inset-x-24 bottom-16 top-16 rounded-[999px] border border-fuchsia-300/10" />
                <div className="glass-panel pixel-frame summon-ring shadow-aura relative rounded-[40px] px-6 py-10 sm:px-8 sm:py-12">
                  <div className="absolute left-6 top-6 rounded-full border border-white/10 bg-slate-950/48 px-3 py-1.5 text-[10px] uppercase tracking-[0.3em] text-slate-300/60">
                    summon protocol
                  </div>
                  <div className="absolute right-6 top-6 rounded-full border border-cyan-300/14 bg-cyan-300/8 px-3 py-1.5 text-[10px] uppercase tracking-[0.3em] text-cyan-100/70">
                    edge core
                  </div>
                  <div className="absolute -left-3 top-12 h-3 w-3 rounded-[2px] bg-cyan-300 shadow-[0_0_18px_rgba(103,232,249,0.8)]" />
                  <div className="absolute -right-3 top-28 h-3 w-3 rounded-[2px] bg-fuchsia-300 shadow-[0_0_18px_rgba(232,121,249,0.8)]" />
                  <div className="absolute bottom-16 left-8 h-2 w-2 rounded-[2px] bg-emerald-300 shadow-[0_0_14px_rgba(74,222,128,0.75)]" />
                  <div className="absolute bottom-20 right-10 h-2.5 w-2.5 rounded-[2px] bg-amber-300 shadow-[0_0_14px_rgba(253,224,71,0.7)]" />

                  <div className="flex items-center justify-center gap-3 text-xs uppercase tracking-[0.36em] text-slate-300/60">
                    <span className="h-px w-10 bg-cyan-200/30" />
                    core identity
                    <span className="h-px w-10 bg-fuchsia-200/30" />
                  </div>

                  <div className="relative mt-8 flex items-center justify-center">
                    <div className="absolute h-[72%] w-[72%] rounded-full bg-[radial-gradient(circle,rgba(66,233,255,0.28),transparent_65%)] blur-3xl" />
                    <div className="absolute h-[84%] w-[84%] rounded-full border border-cyan-300/16" />
                    <div className="absolute h-[96%] w-[96%] rounded-full border border-fuchsia-300/14" />
                    <img
                      src="/assets/superior-logo.png"
                      alt="Superior logo"
                      className="animate-float-slow relative z-10 w-full max-w-[480px] drop-shadow-[0_0_48px_rgba(80,225,255,0.34)]"
                    />
                  </div>

                  <div className="mt-7 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-[22px] border border-white/8 bg-slate-950/42 px-4 py-4">
                      <p className="font-display text-sm uppercase tracking-[0.26em] text-cyan-200/74">signal posture</p>
                      <p className="mt-2 text-sm leading-7 text-slate-300/72">Deliberate edge detection over noisy chart theatrics.</p>
                    </div>
                    <div className="rounded-[22px] border border-white/8 bg-slate-950/42 px-4 py-4">
                      <p className="font-display text-sm uppercase tracking-[0.26em] text-fuchsia-200/76">design posture</p>
                      <p className="mt-2 text-sm leading-7 text-slate-300/72">Cosmic arcade softness with premium product discipline.</p>
                    </div>
                  </div>

                  <div className="mt-4 rounded-[22px] border border-cyan-200/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] px-4 py-4">
                    <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.32em] text-slate-400/70">
                      <span>ritual seal</span>
                      <span>local-first</span>
                    </div>
                    <div className="mt-4 grid grid-cols-3 gap-3">
                      {ritualStats.map((item) => (
                        <div key={item.label} className="rounded-[18px] border border-white/8 bg-slate-950/44 px-3 py-3">
                          <p className="font-display text-[10px] uppercase tracking-[0.26em] text-slate-400/70">{item.label}</p>
                          <p className="mt-2 text-sm text-slate-100/88">{item.value}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section id="features" className="mt-20 grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
            <article className="glass-panel pixel-frame rounded-[34px] p-7 sm:p-8">
              <p className="font-display text-sm uppercase tracking-[0.28em] text-cyan-200/70">Iconic by design</p>
              <h2 className="mt-4 font-display text-3xl font-semibold tracking-[-0.05em] text-white sm:text-4xl">
                A summon-screen mood, translated into a serious product surface.
              </h2>
              <p className="mt-5 max-w-2xl text-base leading-8 text-slate-300/76">
                Superior is presented as a calm intelligence emerging from signal-rich darkness. The page treats the logo like
                a relic at the center of the system, then frames the platform around three simple promises: observe, recognize,
                and execute with confidence.
              </p>
              <div className="mt-8 grid gap-4 md:grid-cols-2">
                {principles.map((principle) => (
                  <div
                    key={principle}
                    className="rounded-[24px] border border-cyan-200/10 bg-white/[0.03] px-4 py-4 text-sm leading-7 text-slate-300/72"
                  >
                    {principle}
                  </div>
                ))}
              </div>
            </article>

            <article id="precision" className="glass-panel pixel-frame relative overflow-hidden rounded-[34px] p-7 sm:p-8">
              <div className="absolute inset-x-0 top-0 h-40 bg-[radial-gradient(circle_at_top,rgba(92,201,255,0.14),transparent_72%)]" />
              <p className="font-display relative text-sm uppercase tracking-[0.28em] text-fuchsia-200/74">Precision layer</p>
              <h2 className="relative mt-4 font-display text-3xl font-semibold tracking-[-0.05em] text-white">
                Sparse, exact, never loud.
              </h2>
              <p className="relative mt-5 text-base leading-8 text-slate-300/76">
                Decorative signal is used once, carefully, as atmosphere instead of dashboard spam. The result feels more premium
                and more trustworthy.
              </p>

              <div className="relative mt-8 rounded-[28px] border border-white/8 bg-slate-950/58 p-5">
                <div className="flex items-center justify-between text-xs uppercase tracking-[0.28em] text-slate-400/70">
                  <span>decorative signal trace</span>
                  <span>stable focus</span>
                </div>
                <div className="mt-6 flex h-28 items-end gap-2">
                  {[18, 26, 22, 38, 34, 50, 42, 60, 54, 74, 68, 82, 78, 96, 88].map((height, index) => (
                    <div
                      key={height + index}
                      className="w-full rounded-t-full bg-[linear-gradient(180deg,rgba(82,233,255,0.95),rgba(235,93,244,0.78))] shadow-[0_0_18px_rgba(82,233,255,0.22)]"
                      style={{ height: `${height}%` }}
                    />
                  ))}
                </div>
              </div>
            </article>
          </section>

          <section className="mt-20">
            <div className="glass-panel pixel-frame rounded-[34px] px-6 py-8 sm:px-10">
              <div className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
                <div className="max-w-3xl">
                  <p className="font-display text-sm uppercase tracking-[0.28em] text-cyan-200/72">Clean call to action</p>
                  <h2 className="mt-4 font-display text-3xl font-semibold tracking-[-0.05em] text-white sm:text-4xl">
                    Ready to make the first impression feel sacred.
                  </h2>
                  <p className="mt-4 text-base leading-8 text-slate-300/78">
                    This landing page is meant to feel like the moment an intelligent system materializes: composed, luminous,
                    and unmistakably Superior.
                  </p>
                </div>

                <div className="flex flex-wrap gap-4">
                  <a
                    className="rounded-full border border-cyan-200/24 bg-cyan-300/12 px-6 py-3.5 font-medium text-cyan-100 transition hover:border-cyan-200/42 hover:bg-cyan-200/18"
                    href="/download"
                  >
                    Download the app
                  </a>
                  <a
                    className="rounded-full border border-white/10 bg-white/5 px-6 py-3.5 font-medium text-slate-100 transition hover:bg-white/10"
                    href="/roadmap"
                  >
                    See the roadmap
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
