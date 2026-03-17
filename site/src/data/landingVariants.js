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
  brandSubtitle: "Paper-first market bot",
  brandEyebrow: "Friendly prediction-market app",
  trustItems: ["Open source", "Paper first", "Local first", "Use your own model"],
  statusTiles: [
    { label: "Mode", value: "Paper" },
    { label: "Feed", value: "Local" },
    { label: "Gate", value: "Locked" },
  ],
  featureCards: [
    {
      id: "01",
      title: "Start with Polymarket",
      tone: "cyan",
      body: "Connect public Polymarket books, keep your keys local, and get useful signal before you touch anything live.",
    },
    {
      id: "02",
      title: "Try paper bots",
      tone: "magenta",
      body: "Run a starter bot in paper mode, review clear route explanations, and learn what the bot is actually doing.",
    },
    {
      id: "03",
      title: "Unlock live later",
      tone: "yellow",
      body: "Build paper history first and keep live mode locked until the product and the user have both earned it.",
    },
    {
      id: "04",
      title: "Bring your own model",
      tone: "cyan",
      body: "Use OpenAI-compatible, Anthropic, Gemini, or Ollama if you want extra help explaining routes or drafting safer paper bots. Keys stay local.",
    },
  ],
  setupFlow: {
    eyebrow: "Getting started",
    title: "Set it up in a few minutes and start in paper mode.",
    body: "Install the Windows app, keep the guided path, and start with public market data before you think about credentials or live controls.",
    steps: [
      {
        id: "01",
        title: "Install the app",
        body: "Use the Windows installer for shortcuts, uninstall support, and the smoothest first run.",
      },
      {
        id: "02",
        title: "Pick the safe path",
        body: "Choose your goal, keep the default settings, and leave credentials blank if you only want paper mode to start.",
      },
      {
        id: "03",
        title: "Record, scan, test",
        body: "Turn recorder output into explainable routes and paper-test the best one before anything live wakes up.",
      },
    ],
  },
  firstLaunch: {
    eyebrow: "First launch",
    title: "A simple first run",
    body: "No exchange account is required to boot Superior into public-data mode and start the first paper session.",
    menu: ["Guided setup", "No credentials needed", "Paper first"],
  },
  productStory: {
    eyebrow: "What it is",
    title: "A simpler way to explore prediction-market bots.",
    body: "Superior helps you record local books, understand scanner results, and test bot ideas safely. If you want extra help, you can use your own model to explain routes or draft paper bots. It is careful software with clear guardrails, not a promise of profits.",
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
  footerTitle: "Download the Windows app and try it safely.",
  footerBody:
    "GitHub Releases hosts the installer. The docs explain paper mode, local storage, and live gating before you decide to go further.",
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
  secondaryCtaLabel: "See how setup works",
  secondaryCtaHref: "/download",
};

export const landingVariants = {
  control: {
    key: "control",
    navLabel: "Control",
    pageTitle: "Superior | Paper-First Prediction-Market Bot",
    pageDescription:
      "Superior is an open-source Windows desktop app for recording public prediction-market books, inspecting explainable routes, paper-testing bots locally, and optionally using your own model for help.",
    eyebrow: "Prediction-market bot for Windows",
    titleLines: ["Learn the market.", "Find price gaps.", "Test safely first."],
    subhead:
      "Superior helps you watch public prediction markets, understand why a route looks interesting, paper-test bot ideas, and optionally use your own model for safe drafting help before you risk real money.",
    systemNote: "Start in paper mode, see what the bot is doing, and add your own model only if you want extra help.",
    tertiaryCta: { label: "GitHub", href: githubUrl, external: true },
    ...shared,
  },
  focus: {
    key: "focus",
    navLabel: "Focus",
    pageTitle: "Superior | Local Arbitrage Bot Setup",
    pageDescription:
      "Superior is a local-first Windows app for watching public prediction-market books, reviewing explainable routes, testing paper bots, and optionally bringing your own model for guidance.",
    eyebrow: "A calmer way to test arbitrage bots",
    titleLines: ["Track the books.", "Spot the gap.", "Try it safely."],
    subhead:
      "Built for a tighter path. Superior records public books, explains scanner output in plain language, and lets you bring your own model for help while paper mode stays the safe default.",
    systemNote: "You can start small, learn the flow, and keep everything in paper mode until it feels right.",
    tertiaryCta: { label: "GitHub", href: githubUrl, external: true },
    ...shared,
  },
};

export const landingVariantOrder = ["control", "focus"];
