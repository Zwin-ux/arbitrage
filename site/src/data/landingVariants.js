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
  brandSubtitle: "Arcade market scanner",
  brandEyebrow: "Paper-first desktop bot",
  trustItems: ["Open source", "Paper first", "Local profiles"],
  statusTiles: [
    { label: "Mode", value: "Paper" },
    { label: "Storage", value: "Local" },
    { label: "Unlock", value: "Locked" },
  ],
  featureCards: [
    {
      id: "01",
      title: "Polymarket first",
      tone: "cyan",
      body: "Connect public market data, keep your own keys local, and learn the venue before you risk capital.",
    },
    {
      id: "02",
      title: "Bot module bay",
      tone: "magenta",
      body: "Load a starter bot, stage explainable routes, and keep the first paper session tight and readable.",
    },
    {
      id: "03",
      title: "Score attack",
      tone: "yellow",
      body: "Bank honest paper score from completed sessions and keep live execution locked behind explicit rules.",
    },
  ],
  setupFlow: {
    eyebrow: "Setup flow",
    title: "Setup that feels like consumer software instead of exchange plumbing.",
    body: "Install the Windows app, keep the guided template, and start recording public books before you worry about credentials or live trading.",
    steps: [
      {
        id: "01",
        title: "Install the Windows build",
        body: "Use the installer for shortcuts, uninstall support, and the cleanest first-run path.",
      },
      {
        id: "02",
        title: "Launch guided setup",
        body: "Pick your goal, keep conservative defaults, and leave credentials blank if you only want recorder plus paper mode.",
      },
      {
        id: "03",
        title: "Record, scan, paper",
        body: "Turn recorder output into explainable scanner routes and paper the top candidate before anything live unlocks.",
      },
    ],
  },
  firstLaunch: {
    eyebrow: "Field menu",
    title: "First launch",
    body: "No exchange account is required to boot Superior into public-data mode and start the first paper session.",
    menu: ["Guided setup", "Bot garage", "Score lane"],
  },
  productStory: {
    eyebrow: "Unit briefing",
    title: "A prediction-market bot OS with scanner, feed, and score in one machine.",
    body: "Superior is built around guided onboarding, scanner explanations, paper execution history, and trust. It is stable software with transparent guardrails, not a promise of guaranteed profits.",
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
    eyebrow: "Open-source prediction-market bot",
    titleLines: ["Learn the market.", "Scan edge.", "Paper it first."],
    subhead:
      "Superior is a local-first desktop bot OS for recording public market books, staging explainable arbitrage routes, and banking paper score before anything live unlocks.",
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
    tertiaryCta: { label: "GitHub", href: githubUrl, external: true },
    ...shared,
  },
};

export const landingVariantOrder = ["control", "focus"];
