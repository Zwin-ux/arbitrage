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
  brandSubtitle: "engine prediction bot",
  heroLine: "ENGINE PREDICTION BOT",
  heroSupport: "Windows bot for Kalshi.",
  heroNote: "Local setup. Auto after checks.",
  statusText: "WINDOWS / LOCAL / AUTO",
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
    pageTitle: "Superior | Engine Prediction Bot",
    pageDescription: "Superior is a Windows bot for Kalshi. Local setup. Automatic after checks.",
    ...shared,
  },
  focus: {
    key: "focus",
    navLabel: "Focus",
    pageTitle: "Superior | Windows Bot for Kalshi",
    pageDescription: "Local Windows build for Kalshi. Install it, set caps, and arm auto after checks.",
    ...shared,
    heroSupport: "Local build for Kalshi.",
    heroNote: "Install it. Set caps. Arm auto.",
  },
};

export const landingVariantOrder = ["control", "focus"];
