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
  brandSubtitle: "NES score-attack bot cabinet",
  trustItems: ["Open source", "Paper-first by default", "Local score ledger"],
  scannerStats: [
    { label: "Session", value: "Paper", accent: "green" },
    { label: "Source", value: "Local books", accent: "cyan" },
    { label: "Unlocks", value: "Live gated", accent: "yellow" },
  ],
  featureCards: [
    {
      eyebrow: "Build bots",
      title: "Arm the bot bay",
      body: "Equip a starter bot loadout, keep the rules explicit, and let the machine stage only the routes that clear the paper gate.",
    },
    {
      eyebrow: "Stage routes",
      title: "Feed it local books",
      body: "Superior records local Polymarket books first, then turns scanner output into staged routes for the active bot slots.",
    },
    {
      eyebrow: "Bank score",
      title: "Unlock deeper control",
      body: "Paper score, mastery, and bot-slot unlocks all come from deterministic paper evidence instead of fake credits or hype.",
    },
  ],
  previewHeading: "A score-attack machine, not a finance dashboard.",
  previewBody:
    "Superior turns real local market books into a playable paper loop: arm bots, stage routes, start a session, and watch portfolio score move inside one cabinet-like desktop shell.",
  previewBullets: [
    "Build and arm a starter bot loadout",
    "Stage explainable routes from local recorder output",
    "Bank paper score before any live path unlocks",
  ],
  previewCtaLabel: "See how it works",
  previewCtaHref: "/docs",
  footerLinks: [
    { href: githubUrl, label: "GitHub" },
    { href: "/docs", label: "Documentation" },
    { href: "/roadmap", label: "Roadmap" },
    { href: "/download", label: "Windows build" },
  ],
};

export const landingVariants = {
  control: {
    key: "control",
    navLabel: "Control",
    pageTitle: "Superior | NES Score-Attack Bot Cabinet",
    pageDescription:
      "Superior is an open-source Windows desktop app for building paper-first bot loadouts, staging explainable routes from local books, and chasing portfolio score before live execution exists.",
    eyebrow: "Windows prediction-market score cabinet",
    titleLines: ["Build bots.", "Stage routes.", "Bank score first."],
    subhead:
      "Local-first desktop machine for testing arbitrage bots on prediction markets. Record the books, arm the bot bay, run a paper session, and unlock deeper control deliberately.",
    secondaryCtas: [
      { label: "View cabinet", href: "#scanner" },
      { label: "GitHub", href: githubUrl, external: true },
    ],
    previewStatus: [
      { label: "Hangar", value: "Session ready", tone: "cyan" },
      { label: "Bot Bay", value: "Armed", tone: "magenta" },
      { label: "Score", value: "Paper only", tone: "green" },
    ],
    ...shared,
  },
  focus: {
    key: "focus",
    navLabel: "Focus",
    pageTitle: "Superior | Paper-First Bot Testing Machine",
    pageDescription:
      "Superior is a paper-first desktop machine for advanced testers who want to build bots, chase local score, and keep live execution locked behind real paper evidence.",
    eyebrow: "Controlled bot testing workflow",
    titleLines: ["Read the machine.", "Chase score.", "Keep live gated."],
    subhead:
      "Built for a tighter loop. Superior records locally, stages routes into a bot bay, and treats paper score plus unlock progression as the main game layer.",
    secondaryCtas: [
      { label: "View cabinet", href: "#scanner" },
      { label: "GitHub", href: githubUrl, external: true },
    ],
    previewStatus: [
      { label: "Hangar", value: "Mission control", tone: "cyan" },
      { label: "Bot Bay", value: "Score attack", tone: "magenta" },
      { label: "Score", value: "Honest history", tone: "green" },
    ],
    ...shared,
  },
};

export const landingVariantOrder = ["control", "focus"];
