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
  brandSubtitle: "windows route machine",
  brandEyebrow: "local data / live off",
  stateStrip: [
    { label: "Mode", value: "Test" },
    { label: "Feed", value: "Polymarket" },
    { label: "Storage", value: "Local" },
    { label: "Live", value: "Locked" },
  ],
  product: {
    eyebrow: "Route readout",
    line: "One book. One route. Clear deductions.",
    bullets: [
      "Local books",
      "Gross to net",
      "Replay",
      "Live off",
    ],
  },
  routePreview: {
    eyebrow: "Example route",
    routeId: "09:41:18 LOCAL",
    path: "BUY YES / SELL NO",
    note: "Local snapshot",
    metrics: [
      { label: "Gross", value: "+4.8%" },
      { label: "Fees", value: "-0.7%" },
      { label: "Slip", value: "-0.9%" },
      { label: "Net", value: "+2.3%" },
    ],
  },
  lockPanel: {
    eyebrow: "Live",
    line: "Off by default.",
    rows: [
      { label: "Credentials", value: "Off" },
      { label: "Test history", value: "Required" },
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
    pageTitle: "Superior | Test routes before real money",
    pageDescription:
      "Superior is a Windows app for recording Polymarket books, reading route math, and testing an idea before real money is at risk.",
    eyebrow: "WINDOWS / LOCAL / LIVE OFF",
    heroLine: "Read the route first.",
    heroSupport: "Record the book. Check the math. Test before money.",
    ...shared,
  },
  focus: {
    key: "focus",
    navLabel: "Focus",
    pageTitle: "Superior | Watch the route math first",
    pageDescription:
      "Superior is a local Windows app for reading Polymarket routes and testing an idea before real money is involved.",
    eyebrow: "POLYMARKET / LOCAL / TEST",
    heroLine: "See the deductions first.",
    heroSupport: "Local data. Clear route math. Live stays off.",
    ...shared,
  },
};

export const landingVariantOrder = ["control", "focus"];
