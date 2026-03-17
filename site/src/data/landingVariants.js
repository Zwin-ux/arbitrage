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
  brandSubtitle: "windows practice money build",
  brandEyebrow: "local by default / live locked",
  stateStrip: [
    { label: "Mode", value: "Practice Money" },
    { label: "Feed", value: "Polymarket" },
    { label: "Storage", value: "Local" },
    { label: "Live", value: "Locked" },
  ],
  product: {
    eyebrow: "Practice loop",
    line: "Start with $100. Take one fake trade. Reset.",
    bullets: [
      "Start with $100",
      "Hold to buy",
      "Replay",
      "Live locked",
    ],
  },
  routePreview: {
    eyebrow: "Example run",
    routeId: "09:41:18 LOCAL",
    path: "BUY 52C / SELL 71C",
    note: "Practice money",
    metrics: [
      { label: "Stake", value: "$25.00" },
      { label: "Gross", value: "+$9.13" },
      { label: "Costs", value: "-$1.39" },
      { label: "Net", value: "+$7.74" },
    ],
  },
  lockPanel: {
    eyebrow: "Live",
    line: "Off by default.",
    rows: [
      { label: "Credentials", value: "Off" },
      { label: "Practice runs", value: "Required" },
      { label: "Checks", value: "Pending" },
      { label: "State", value: "Locked" },
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
    pageTitle: "Superior | Start with $100",
    pageDescription:
      "Superior is a Windows app for practicing fake trades on replay before real money is involved.",
    eyebrow: "WINDOWS / LOCAL / LIVE OFF",
    heroLine: "Start with $100.",
    heroSupport: "Practice before real money.",
    ...shared,
  },
  focus: {
    key: "focus",
    navLabel: "Focus",
    pageTitle: "Superior | Practice before real money",
    pageDescription:
      "Superior is a local Windows app for replaying trades with fake money before anything live is unlocked.",
    eyebrow: "POLYMARKET / LOCAL / PRACTICE",
    heroLine: "Practice before real money.",
    heroSupport: "Local replay. Fake bankroll. Live stays locked.",
    ...shared,
  },
};

export const landingVariantOrder = ["control", "focus"];
