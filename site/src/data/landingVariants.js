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
  brandSubtitle: "windows kalshi starter bot",
  brandEyebrow: "local-first / shadow before auto",
  stateStrip: [
    { label: "Mode", value: "Practice" },
    { label: "Feed", value: "Polymarket" },
    { label: "Storage", value: "Local" },
    { label: "Live", value: "Locked" },
  ],
  product: {
    eyebrow: "Starter bot",
    line: "Shadow the route. Arm the bot. Keep caps visible.",
    bullets: [
      "Kalshi only",
      "Shadow first",
      "Tight caps",
      "Auto after arm",
    ],
  },
  routePreview: {
    eyebrow: "World state",
    routeId: "09:41:18 LOCAL",
    path: "BUY 52C / SELL 71C",
    note: "Score carries",
    metrics: [
      { label: "Stake", value: "$25.00" },
      { label: "Gross", value: "+$9.13" },
      { label: "Costs", value: "-$1.39" },
      { label: "Net", value: "+$7.74" },
    ],
  },
  lockPanel: {
    eyebrow: "Live path",
    line: "Shadow first. Auto after arm.",
    rows: [
      { label: "Venue", value: "Kalshi" },
      { label: "Shadow", value: "Required" },
      { label: "Caps", value: "Visible" },
      { label: "State", value: "Auto locked" },
    ],
  },
  downloadPanel: {
    eyebrow: "Build",
    line: "Installer. Portable. Checksums. Source.",
    rows: [
      "SETUP.EXE",
      "PORTABLE.ZIP",
      "SHA256SUMS",
      "GITHUB",
    ],
  },
  footerLinks: [
    { href: githubUrl, label: "GitHub" },
    { href: "/download", label: "Download" },
    { href: "/docs", label: "Docs" },
  ],
};

export const landingVariants = {
  control: {
    key: "control",
    navLabel: "Control",
    pageTitle: "Superior | Kalshi starter bot",
    pageDescription:
      "Superior is a Windows desktop app for shadowing, arming, and tightly capping one explainable Kalshi starter bot.",
    eyebrow: "WINDOWS / KALSHI / SHADOW FIRST",
    heroLine: "Arm one starter bot.",
    heroSupport: "Shadow first. Auto after caps and a clear reason trail.",
    ...shared,
  },
  focus: {
    key: "focus",
    navLabel: "Focus",
    pageTitle: "Superior | Shadow, arm, auto",
    pageDescription:
      "Superior is a local Windows app for learning on Polymarket-style tapes, then running one tightly capped Kalshi starter bot.",
    eyebrow: "POLY LEARN / KALSHI LIVE / LOCAL",
    heroLine: "Shadow. Arm. Auto.",
    heroSupport: "Use replay to qualify the bot, then turn on one narrow live path.",
    ...shared,
  },
};

export const landingVariantOrder = ["control", "focus"];
