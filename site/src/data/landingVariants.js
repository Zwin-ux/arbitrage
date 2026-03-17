const windowsInstallerUrl =
  "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe";
const portableUrl =
  "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-app-portable.zip";
const checksumsUrl =
  "https://github.com/Zwin-ux/arbitrage/releases/latest/download/SHA256SUMS.txt";
const githubUrl = "https://github.com/Zwin-ux/arbitrage";

const shared = {
  windowsInstallerUrl,
  portableUrl,
  checksumsUrl,
  githubUrl,
  brandTitle: "Superior",
  brandSubtitle: "Paper arb firmware",
  brandEyebrow: "Cartridge signal OS",
  trustItems: ["Open source", "Paper first", "Local first"],
  statusTiles: [
    { label: "Mode", value: "Paper" },
    { label: "Feed", value: "Local" },
    { label: "Gate", value: "Locked" },
  ],
  featureCards: [
    {
      id: "01",
      title: "Boot Polymarket",
      tone: "cyan",
      body: "Load public Polymarket books first, keep keys local, and start the machine without touching live execution.",
    },
    {
      id: "02",
      title: "Stage bot runs",
      tone: "magenta",
      body: "Arm one starter bot, stage explainable routes, and keep the first run compact, readable, and deterministic.",
    },
    {
      id: "03",
      title: "Bank paper score",
      tone: "yellow",
      body: "Record honest paper score from real session output while the gate stays dark behind explicit checks.",
    },
  ],
  setupFlow: {
    eyebrow: "Boot phases",
    title: "Boot the cart, arm the feed, start the first run.",
    body: "Install the Windows build, keep the guided cart, and feed the machine with public books before you worry about keys or live controls.",
    steps: [
      {
        id: "01",
        title: "Install the cart",
        body: "Use the Windows installer for shortcuts, uninstall support, and the cleanest first boot.",
      },
      {
        id: "02",
        title: "Run boot phases",
        body: "Pick a mission, keep safe defaults, and leave key slots blank if you only want sample plus paper mode.",
      },
      {
        id: "03",
        title: "Sample, scan, run",
        body: "Turn recorder output into explainable routes and paper the top run before anything live wakes up.",
      },
    ],
  },
  firstLaunch: {
    eyebrow: "Field menu",
    title: "First ignition",
    body: "No exchange account is required to boot Superior into public-data mode and start the first paper session.",
    menu: ["Boot phases", "No key slots", "Paper first"],
  },
  productStory: {
    eyebrow: "Unit briefing",
    title: "A prediction-market bot machine with feed, scanner, and score in one shell.",
    body: "Superior is built around local books, scanner explanations, paper execution history, and explicit trust rules. It is stable software with guardrails, not a profit promise.",
  },
  infoCards: [
    {
      eyebrow: "Note 01",
      title: "Open source",
      body: "The app, site, packaging, and trust docs all live in the public repo.",
    },
    {
      eyebrow: "Note 02",
      title: "Local first",
      body: "Profiles, diagnostics, and paper history stay on your machine. Secrets stay in the OS keychain.",
    },
    {
      eyebrow: "Note 03",
      title: "Lab ready",
      body: "High-risk experiments live behind an explicit Lab toggle and stay paper-only in v1.",
    },
  ],
  footerTitle: "Download the Windows build or inspect the source before anything else.",
  footerBody:
    "GitHub Releases hosts the installer. The docs route explains how paper mode, local storage, and live gating work before you touch a trade button.",
  footerChecks: [
    "[OK] install Windows build",
    "[OK] run paper mode first",
    "[LOCK] live mode until checklist",
  ],
  footerLinks: [
    { href: githubUrl, label: "GitHub" },
    { href: "/docs", label: "Documentation" },
    { href: "/roadmap", label: "Roadmap" },
    { href: "/download", label: "Windows build" },
  ],
  primaryCtaLabel: "Download for Windows",
  secondaryCtaLabel: "Open setup menu",
  secondaryCtaHref: "/download",
};

export const landingVariants = {
  control: {
    key: "control",
    navLabel: "Control",
    pageTitle: "Superior | Paper-First Prediction-Market Bot",
    pageDescription:
      "Superior is an open-source Windows desktop app for recording public prediction-market books, inspecting explainable arbitrage routes, and paper-testing them locally before anything live unlocks.",
    eyebrow: "Windows prediction-market scanner",
    titleLines: ["Learn the market.", "Scan edge.", "Paper it first."],
    subhead:
      "Superior is a local-first desktop bot OS for recording public market books, staging explainable arbitrage routes, and banking paper score before anything live unlocks.",
    systemNote: "BOOT THE REC BUS. STAGE ONE CLEAN ROUTE. KEEP THE GATE LOCKED.",
    tertiaryCta: { label: "GitHub", href: githubUrl, external: true },
    ...shared,
  },
  focus: {
    key: "focus",
    navLabel: "Focus",
    pageTitle: "Superior | Local Arbitrage Bot Setup",
    pageDescription:
      "Superior is a local-first Windows app for watching public prediction-market books, reviewing explainable routes, and testing paper bots before any live path unlocks.",
    eyebrow: "Local arbitrage bot setup",
    titleLines: ["Track the books.", "Find the gap.", "Test it first."],
    subhead:
      "Built for a tighter path. Superior records public books, surfaces scanner output in plain language, and keeps the bot feed and paper score honest while live stays locked.",
    systemNote: "LOAD THE CART. WATCH THE FEED. BANK ONLY PAPER SCORE.",
    tertiaryCta: { label: "GitHub", href: githubUrl, external: true },
    ...shared,
  },
};

export const landingVariantOrder = ["control", "focus"];
