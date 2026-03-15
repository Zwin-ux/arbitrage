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
  scannerFrameTitle: "SCAN PREVIEW",
  scoreCards: [
    { label: "Mode", value: "PAPER FIRST", accent: "green" },
    { label: "Live Trading", value: "LOCKED", accent: "gold" },
    { label: "Venue", value: "POLYMARKET", accent: "cyan" }
  ],
  featureCards: [
    {
      title: "LOCAL RECORDING",
      body: "Capture market books locally so the scanner works from observed data instead of a remote dashboard."
    },
    {
      title: "EXPLAINABLE ROUTES",
      body: "Show route structure, deductions, and net edge in a format people can review before taking action."
    },
    {
      title: "CONTROLLED UNLOCKS",
      body: "Keep credentials and live actions behind explicit setup checks instead of exposing them on day one."
    }
  ],
  steps: [
    {
      step: "01",
      title: "Install Superior",
      body: "Use the Windows build and start with the guided setup path."
    },
    {
      step: "02",
      title: "Connect data",
      body: "Start with public Polymarket data and leave credentials for later if paper mode is enough."
    },
    {
      step: "03",
      title: "Review a route",
      body: "Record local books, inspect the route, and understand the deductions before anything moves."
    },
    {
      step: "04",
      title: "Paper it first",
      body: "Keep live mode locked until the required checks, acknowledgements, and paper activity are complete."
    }
  ],
  loadout: [
    { label: "CONNECTOR", state: "POLYMARKET", accent: "cyan" },
    { label: "STORAGE", state: "LOCAL", accent: "green" },
    { label: "PAPER MODE", state: "READY", accent: "purple" },
    { label: "LIVE MODE", state: "LOCKED", accent: "magenta" }
  ]
};

export const landingVariants = {
  control: {
    key: "control",
    navLabel: "Control",
    pageTitle: "Superior | Paper-First Market Scanner",
    pageDescription:
      "Superior is an open-source Windows app for recording prediction-market data, reviewing explainable arbitrage routes, and paper-testing them before anything live is unlocked.",
    eyebrow: "Windows prediction-market scanner",
    titleLines: ["Learn the market.", "Scan edge.", "Paper it first."],
    subhead:
      "Superior is a Windows app for recording Polymarket data, surfacing explainable arbitrage candidates, and paper-testing them before anything live is unlocked.",
    heroMarqueeLeft: "OPEN SOURCE WINDOWS BUILD",
    heroMarqueeRight: "PAPER-FIRST BY DEFAULT",
    scannerStats: [
      { label: "Mode", value: "PAPER", accent: "green" },
      { label: "Data", value: "LOCAL BOOKS", accent: "cyan" },
      { label: "Live", value: "LOCKED", accent: "gold" }
    ],
    scannerCopy:
      "The scanner records local books, prices the route, and shows fees, deductions, and assumptions before a candidate reaches paper mode.",
    signalFeed: [
      "Local book snapshots retained for review",
      "Route costs shown before paper entry",
      "Live controls hidden until setup checks pass"
    ],
    downloadLead:
      "Download the Windows build, run guided setup, and keep the first session in paper mode.",
    downloadNote:
      "Installer, portable build, source, and checksums live on GitHub Releases.",
    ...shared
  },
  focus: {
    key: "focus",
    navLabel: "Focus",
    pageTitle: "Superior | Controlled Market Scanner",
    pageDescription:
      "Superior is a paper-first prediction-market scanner with guided setup, local recording, and a controlled path to reviewing opportunities before live mode is available.",
    eyebrow: "Controlled market workflow",
    titleLines: ["Record books.", "Read the edge.", "Keep live locked."],
    subhead:
      "Built for people who want a calmer workflow: record local data, inspect one candidate at a time, and keep live mode behind the checklist.",
    heroMarqueeLeft: "GUIDED SETUP INCLUDED",
    heroMarqueeRight: "LIVE MODE STAYS LOCKED",
    scannerStats: [
      { label: "Mode", value: "PAPER", accent: "green" },
      { label: "Review", value: "ONE AT A TIME", accent: "cyan" },
      { label: "Live", value: "LOCKED", accent: "gold" }
    ],
    scannerCopy:
      "This variant emphasizes clarity. The scanner shows route structure, deductions, and paper results before any live path is even visible.",
    signalFeed: [
      "One candidate reviewed at a time",
      "Paper results visible before live mode",
      "Advanced modules hidden until enabled"
    ],
    downloadLead:
      "Install the Windows build, complete the guided setup, and let paper results be the first thing that moves.",
    downloadNote:
      "Source, releases, and trust files stay public on GitHub.",
    ...shared
  }
};

export const landingVariantOrder = ["control", "focus"];
