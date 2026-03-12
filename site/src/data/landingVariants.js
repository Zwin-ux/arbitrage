const windowsInstallerUrl =
  "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe";

const shared = {
  windowsInstallerUrl,
  secondaryCtaHref: "/download",
  badges: ["MIT licensed", "Local-first", "Windows first"],
  proofEyebrow: "Proof before download",
  proofTitle: "Everything important stays visible before you commit to the install.",
  proofBody:
    "Use the landing page to verify the release path, inspect the docs, and compare the draft front end before the public route changes.",
  proofCards: [
    {
      title: "Inspect the release path",
      body: "Choose the Windows installer or portable zip, then compare it against the documented source flow.",
      href: "/download",
      cta: "Review download options"
    },
    {
      title: "Read the build notes",
      body: "The docs keep local setup, release testing, and deployment details in one inspectable place.",
      href: "/docs",
      cta: "Read the docs"
    },
    {
      title: "Review the draft",
      body: "Compare the public homepage against the stronger draft variant before replacing the main route.",
      href: "/lab/draft",
      cta: "Open the draft route"
    }
  ],
  workflowEyebrow: "Operator flow",
  workflowTitle: "Three calm steps from scan to ship.",
  workflowBody:
    "Superior keeps the front end focused on signal, verification, and release discipline instead of decorative dashboard clutter.",
  workflowSteps: [
    {
      step: "01",
      title: "Scan",
      body: "See active markets and recorder context quickly without sacrificing readability."
    },
    {
      step: "02",
      title: "Verify",
      body: "Check docs, source, and packaging details before you trust the release path."
    },
    {
      step: "03",
      title: "Ship",
      body: "Use the lab routes to review challengers deliberately before changing the public homepage."
    }
  ]
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
  },
  draft: {
    key: "draft",
    label: "Draft",
    pageTitle: "Superior | Draft Front End For Review",
    pageDescription:
      "A draft landing page for Superior that prioritizes proof, hierarchy, and reviewable release paths for local-first arbitrage tooling.",
    eyebrow: "Draft landing page for review",
    headlineLead: "Review the build",
    headlineAccent: "before you trust the click.",
    subhead:
      "This draft sharpens hierarchy, surfaces proof earlier, and keeps the path from source to installer explicit for operators evaluating Superior.",
    navLabel: "Draft",
    heroTopLeft: "Draft review",
    heroTopRight: "Proof-first",
    heroPanels: [
      {
        title: "Trust",
        body: "Release links, docs, and source review stay one step away instead of being buried below the fold."
      },
      {
        title: "Calm",
        body: "The composition puts hierarchy before spectacle so the page reads quickly under pressure."
      }
    ],
    featureCards: [
      {
        title: "Clear hierarchy",
        body: "Hero, proof, workflow, and download sections now tell one coherent story from signal to install."
      },
      {
        title: "Draft ready",
        body: "The lab exposes this version separately so the public route can stay stable until the copy is approved."
      },
      {
        title: "Accessible motion",
        body: "Skip navigation, visible focus states, and reduced-motion support keep the experience usable for more operators."
      }
    ],
    productTitle: "A stronger front end draft designed for review, not just admiration.",
    productBody:
      "The layout keeps the logo and atmosphere, then earns trust with explicit proof, calmer section order, and shorter paths to real product information.",
    productNotes: [
      {
        title: "Reviewable",
        body: "The draft route makes composition changes inspectable before they touch the public homepage."
      },
      {
        title: "Transparent",
        body: "Docs, downloads, and source stay reachable from the first scroll instead of hiding behind marketing copy."
      },
      {
        title: "Deliberate",
        body: "The page now reads like a product release path rather than a static concept render."
      }
    ],
    downloadTitle: "Approve the draft, then download the build or inspect the source path.",
    downloadBody:
      "Start with the draft route if you want to evaluate copy and hierarchy. When you are ready, the installer and source path are both one click away.",
    ...shared
  }
};

export const landingVariantOrder = ["control", "focus", "draft"];
