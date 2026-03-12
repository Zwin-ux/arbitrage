const windowsInstallerUrl =
  "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe";

const shared = {
  windowsInstallerUrl,
  secondaryCtaHref: "/download",
  badges: ["MIT licensed", "Local-first", "Windows first"]
};

export const landingVariants = {
  control: {
    key: "control",
    label: "Control",
    pageTitle: "Superior | Intelligent Arbitrage, Focused Cleanly",
    pageDescription:
      "Superior scans markets, detects edge, and acts with precision. An open-source, local-first arbitrage recorder with a calm interface.",
    eyebrow: "Open-source market recorder",
    headlineLead: "Scan markets.",
    headlineAccent: "Find edge. Act with precision.",
    subhead:
      "Superior is a local-first arbitrage recorder built to surface signal, preserve context, and stay readable under pressure.",
    navLabel: "Control",
    heroTopLeft: "Superior",
    heroTopRight: "Local-first",
    heroPanels: [
      {
        title: "Signal",
        body: "Live market context without forcing you through a wall of noisy widgets."
      },
      {
        title: "Execution",
        body: "Recorder, replay, and verification flows built for deliberate operation."
      }
    ],
    featureCards: [
      {
        title: "Market scan",
        body: "Tracks active markets and local orderbook state with a recorder-first flow."
      },
      {
        title: "Edge context",
        body: "Keeps the interface legible so the useful information is easier to act on."
      },
      {
        title: "Release discipline",
        body: "Open-source packaging, reproducible build steps, and explicit smoke checks."
      }
    ],
    productTitle: "Built to stay readable while the system does real work.",
    productBody:
      "The design keeps the atmosphere from the logo, then strips away everything that does not improve comprehension or trust.",
    productNotes: [
      {
        title: "Local-first",
        body: "Profiles, recorder data, diagnostics, and secrets stay under your control."
      },
      {
        title: "Open-source",
        body: "The code, packaging flow, site, and release scripts are all inspectable."
      },
      {
        title: "Release-ready",
        body: "Windows installer, portable build, and smoke-tested packaging are part of the repo."
      }
    ],
    downloadTitle: "Download the Windows build or inspect the source path first.",
    downloadBody:
      "GitHub Releases host the installer. If you want to verify the path yourself, the docs page covers local builds and release testing.",
    ...shared
  },
  focus: {
    key: "focus",
    label: "Focus",
    pageTitle: "Superior | See The Edge Before It Disappears",
    pageDescription:
      "Superior is an open-source arbitrage recorder designed to keep edge detection, recorder state, and execution context calm and clear.",
    eyebrow: "Local-first arbitrage recorder",
    headlineLead: "See the edge",
    headlineAccent: "before it disappears.",
    subhead:
      "Superior keeps market scanning, recorder state, and release tooling in one disciplined surface without drifting into dashboard clutter.",
    navLabel: "Focus",
    heroTopLeft: "Superior",
    heroTopRight: "Recorder core",
    heroPanels: [
      {
        title: "Recorder",
        body: "Gamma discovery, local books, replay, and verify behind a desktop flow that stays calm."
      },
      {
        title: "Operator",
        body: "A sharper landing message for people who care more about confidence than spectacle."
      }
    ],
    featureCards: [
      {
        title: "Fast setup",
        body: "Profiles, credential storage, and default presets are all configured from the desktop app."
      },
      {
        title: "Clear diagnostics",
        body: "Recorder state, latest warnings, and exported bundles live in one predictable place."
      },
      {
        title: "Stronger shipping loop",
        body: "The public installer is now gated by packaged-app and installer smoke checks."
      }
    ],
    productTitle: "A tighter front end for users who care about trust and speed.",
    productBody:
      "This variant reduces mood language and leans harder on clarity, release discipline, and operational confidence.",
    productNotes: [
      {
        title: "Deterministic",
        body: "The app stays local, explicit, and rules-based instead of depending on hidden services."
      },
      {
        title: "Inspectable",
        body: "GitHub holds the source, site, workflows, and release packaging in one public repo."
      },
      {
        title: "Testable",
        body: "Packaged app smoke mode, silent installer smoke tests, and browser-level site tests are built in."
      }
    ],
    downloadTitle: "Test the build, compare the page, then ship the stronger version.",
    downloadBody:
      "Use the lab routes to compare variants, then keep the public homepage on the winner once the copy and composition earn it.",
    ...shared
  }
};

export const landingVariantOrder = ["control", "focus"];
