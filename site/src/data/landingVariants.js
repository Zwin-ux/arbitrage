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
  brandSubtitle: "Signal scanner / paper-first",
  brandEyebrow: "Signal OS / Windows build",
  primaryCtaLabel: "Download Windows Build",
  secondaryCtaLabel: "View Portable Build",
  secondaryCtaHref: portableUrl,
  tertiaryCta: { label: "Read the System", href: "/docs", external: false },
  trustStrip: ["POLYMARKET", "LOCAL BOOKS", "PAPER MODE", "LIVE LOCKED"],
  stateStrip: [
    { label: "Mode", value: "Paper" },
    { label: "Connector", value: "Polymarket" },
    { label: "Storage", value: "Local" },
    { label: "Live", value: "Locked" },
    { label: "Route Engine", value: "Ready" },
    { label: "Data Source", value: "Observed Books" },
  ],
  pipeline: {
    eyebrow: "Signal pipeline",
    title: "Observed books in. Readable route state out.",
    body: "The machine does not jump from raw market motion to action. It moves through explicit stages that can be inspected before anything reaches paper mode.",
    stages: [
      {
        id: "01",
        label: "Observe",
        body: "Record local books from market activity.",
      },
      {
        id: "02",
        label: "Normalize",
        body: "Turn snapshots into a readable internal structure.",
      },
      {
        id: "03",
        label: "Price Route",
        body: "Compute route shape, deductions, and net edge.",
      },
      {
        id: "04",
        label: "Inspect",
        body: "Show assumptions before anything reaches paper mode.",
      },
      {
        id: "05",
        label: "Paper",
        body: "Track candidate behavior without unlocking live actions.",
      },
      {
        id: "06",
        label: "Unlock Later",
        body: "Keep credentials and real execution behind explicit checks.",
      },
    ],
  },
  principles: {
    eyebrow: "Operating principles",
    title: "The system stays locked on purpose.",
    body: "Superior is built around readable market work. Every subsystem favors review, local evidence, and controlled state over remote abstraction or default exposure.",
    items: [
      {
        title: "Observed data over remote abstraction",
        body: "Routes are priced from local books, not a remote dashboard summary.",
      },
      {
        title: "Route clarity over black-box output",
        body: "Gross edge, fees, slippage, and deductions stay visible.",
      },
      {
        title: "Paper first before live risk",
        body: "The paper ledger is the primary path. Live stays separate.",
      },
      {
        title: "Explicit unlocks over default exposure",
        body: "Credentials, acknowledgements, and paper history all matter.",
      },
    ],
  },
  routeInspection: {
    eyebrow: "Route inspection preview",
    title: "Readable routes carry their own audit trail.",
    body: "A candidate is not just a number. Superior shows the route path, deductions, assumptions, and snapshot origin before the machine ever reaches paper entry.",
    routeId: "ROUTE / PM-IB-014",
    path: "BUY YES -> SELL NO",
    origin: "Local Polymarket book sample",
    quality: "Route quality / B1",
    snapshotAt: "Snapshot / 2026-03-17 01:58 UTC",
    metrics: [
      { label: "Gross edge", value: "+4.8%" },
      { label: "Fees", value: "-0.7%" },
      { label: "Slippage est.", value: "-0.9%" },
      { label: "Deductions", value: "-1.6%" },
      { label: "Net edge", value: "+2.3%" },
      { label: "State", value: "Paper-ready" },
    ],
    assumptions: [
      "Observed depth only",
      "No hidden fills assumed",
      "Route quality depends on local sample age",
    ],
  },
  unlockPanel: {
    eyebrow: "Controlled unlocks",
    title: "Live mode is not a default.",
    body: "Live remains locked until setup checks, acknowledgements, and paper activity are complete. The machine does not treat exposure like a welcome screen.",
    statusLabel: "Live mode",
    statusValue: "Locked",
    checks: [
      { label: "Credentials", value: "Not enabled", state: "warn" },
      { label: "Acknowledgements", value: "Required", state: "warn" },
      { label: "Paper history", value: "Required", state: "warn" },
      { label: "Setup checks", value: "Pending", state: "warn" },
      { label: "Route engine", value: "Ready", state: "active" },
    ],
  },
  setupSequence: {
    eyebrow: "Get started",
    title: "Deliberate sequencing. No friendly trap door into risk.",
    body: "The first run is short and direct. Install the build, connect public data, inspect one route, and keep paper mode active while the machine earns trust.",
    steps: [
      { id: "01", title: "Install the Windows build" },
      { id: "02", title: "Connect public data" },
      { id: "03", title: "Record and inspect a route" },
      { id: "04", title: "Keep paper mode active" },
      { id: "05", title: "Unlock only after checks pass" },
    ],
  },
  downloadPanel: {
    eyebrow: "Download",
    title: "Release distribution",
    body: "Use the Windows installer, the portable build, or inspect the source directly. The release manifest and checksums stay public.",
    releaseRows: [
      "WINDOWS INSTALLER / AVAILABLE",
      "PORTABLE BUILD / AVAILABLE",
      "SHA256 CHECKSUMS / PUBLIC",
      "SOURCE / GITHUB",
    ],
  },
  footerLinks: [
    { href: githubUrl, label: "GitHub" },
    { href: "/docs", label: "Read the system" },
    { href: "/roadmap", label: "Roadmap" },
    { href: "/download", label: "Download deck" },
  ],
};

export const landingVariants = {
  control: {
    key: "control",
    navLabel: "Console",
    pageTitle: "Superior | Paper-First Signal Scanner",
    pageDescription:
      "Superior is an open-source Windows signal scanner for recording local prediction-market books, pricing readable routes, and keeping live execution locked until review is complete.",
    eyebrow: "Open source / Windows / paper-first",
    titleLines: ["Read the market", "before you touch it."],
    subhead:
      "Superior records local market data, prices explainable routes, and keeps live execution locked until review and setup checks are complete.",
    systemNote: "Observed books. Readable routes. Live remains locked.",
    ...shared,
  },
  focus: {
    key: "focus",
    navLabel: "Focus",
    pageTitle: "Superior | Readable Market Workstation",
    pageDescription:
      "Superior is a local-first Windows workstation for recording prediction-market books, inspecting route deductions, and keeping paper mode in front of live risk.",
    eyebrow: "Open source / Local first / paper-first",
    titleLines: ["Record first.", "Inspect the route.", "Keep live locked."],
    subhead:
      "Built for readable market work. Superior records observed books, surfaces route deductions, and keeps paper mode in front while live remains a gated state.",
    systemNote: "Local evidence first. No remote dashboard voice. No live by default.",
    ...shared,
  },
};

export const landingVariantOrder = ["control", "focus"];
