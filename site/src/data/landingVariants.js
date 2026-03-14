const windowsInstallerUrl =
  "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe";

const shared = {
  windowsInstallerUrl,
  secondaryCtaHref: "/download",
  badges: ["MIT licensed", "Paper first", "Windows first"]
};

export const landingVariants = {
  control: {
    key: "control",
    label: "Control",
    pageTitle: "Superior | Open-Source Prediction-Market Bot",
    pageDescription:
      "Superior is a guided, local-first prediction-market desktop app for equipping Polymarket, scanning edge, and building a paper score before any live gate clears.",
    eyebrow: "Open-source prediction-market desktop app",
    headlineLead: "Equip Polymarket.",
    headlineAccent: "Record books. Build a paper score.",
    subhead:
      "Superior gives everyday users a clean Windows path to learn Polymarket, record local books, inspect one explainable route at a time, and keep score without pretending paper and live results are the same thing.",
    navLabel: "Control",
    heroTopLeft: "Superior",
    heroTopRight: "Paper-first",
    heroPanels: [
      {
        title: "Guided",
        body: "Beginner-first onboarding, connector loadouts, and clear explanations instead of noisy dashboards."
      },
      {
        title: "Deterministic",
        body: "Scanner, paper execution, score updates, and live-gate rules stay explicit. The coach never places trades."
      }
    ],
    featureCards: [
      {
        title: "Equip Polymarket first",
        body: "Start with public data, add your own keys later, and learn the venue before you try to make the product do more."
      },
      {
        title: "Paper score",
        body: "Run deterministic paper routes against recorded books and watch the score board move from realized paper results only."
      },
      {
        title: "Live gated",
        body: "Credentials, risk acknowledgements, diagnostics, and paper history all have to clear before any live path appears."
      }
    ],
    setupTitle: "An arcade-style loadout that stays concrete about what the product is doing.",
    setupBody:
      "Install the Windows build, keep Guided mode on, equip Polymarket, and start recording public books before you worry about credentials, live mode, or experimental modules.",
    setupCaption: "No exchange account is required to equip Polymarket and finish the first recording run.",
    setupSteps: [
      {
        title: "Install the Windows build",
        body: "Use the installer for shortcuts, uninstall support, and the cleanest first-run path."
      },
      {
        title: "Equip your loadout",
        body: "Pick your goal, keep conservative defaults, equip Polymarket, and leave credentials blank if you only want recorder plus paper mode."
      },
      {
        title: "Record, scan, score",
        body: "Run the recorder, inspect explainable scanner output, and paper the top candidate before anything live unlocks."
      }
    ],
    productTitle: "A consumer desktop app for prediction-market learning, explainable routes, and honest scorekeeping.",
    productBody:
      "The product is built around guided onboarding, connector loadouts, scanner explanations, paper execution history, and trust. Superior is stable software with explicit guardrails, not a promise of guaranteed profits.",
    productNotes: [
      {
        title: "Open source",
        body: "The app, site, packaging, and trust docs all live in one public repo."
      },
      {
        title: "Local first",
        body: "Profiles, diagnostics, and paper history stay on your machine. Secrets stay in the OS keychain."
      },
      {
        title: "Lab ready",
        body: "High-risk experiments live behind an explicit Lab toggle and stay paper-only in v1."
      }
    ],
    downloadTitle: "Download the Windows build, then inspect the source if you want the full trust story.",
    downloadBody:
      "GitHub Releases hosts the installer. The docs explain loadouts, paper score, local storage, and live gating before you ever click a trade button.",
    ...shared
  },
  focus: {
    key: "focus",
    label: "Focus",
    pageTitle: "Superior | Scan Markets With Guardrails",
    pageDescription:
      "Superior helps users equip Polymarket, record local market data, understand edge, and keep live trading behind explicit checklists and risk controls.",
    eyebrow: "Guided Polymarket onboarding",
    headlineLead: "Equip the loadout.",
    headlineAccent: "Explain edge. Keep live gated.",
    subhead:
      "This variant leans harder on trust: local-first storage, deterministic paper bots, and a score board that moves only from realized paper results.",
    navLabel: "Focus",
    heroTopLeft: "Superior",
    heroTopRight: "Guided mode",
    heroPanels: [
      {
        title: "Trust",
        body: "Stable recorder, transparent risk policies, and no hidden hosted control plane."
      },
      {
        title: "Clarity",
        body: "Every candidate shows the match, the assumptions, and the cost adjustments that cut gross edge down to net."
      }
    ],
    featureCards: [
      {
        title: "Consumer setup",
        body: "Profiles, connector loadouts, risk presets, and coach settings all live inside one Windows desktop flow."
      },
      {
        title: "Explainable scanner",
        body: "The UI explains why a route qualifies, why it fails, and what still blocks the live gate."
      },
      {
        title: "Public trust docs",
        body: "Risk model, live limits, local storage, and contributor architecture are documented in the repo."
      }
    ],
    setupTitle: "A disciplined path from curiosity to one clean recording and one honest score update.",
    setupBody:
      "Superior is designed so the first launch feels understandable: guided defaults, optional credentials, connector loadouts, and a paper-first workflow that does not demand trust up front.",
    setupCaption: "Guided setup, local storage, and paper score all work before live credentials enter the conversation.",
    setupSteps: [
      {
        title: "Download and launch",
        body: "The Windows installer gets the product onto the machine with the fewest manual decisions."
      },
      {
        title: "Equip the safe defaults",
        body: "Start with Polymarket, a conservative risk policy, and Guided mode on unless you already know the workflow."
      },
      {
        title: "Use evidence before intent",
        body: "Record local books, read the scanner explanation, and paper the candidate before you even think about live readiness."
      }
    ],
    productTitle: "Built for users who want a clean path from curiosity to disciplined experimentation and honest scorekeeping.",
    productBody:
      "Superior is not a black-box money machine. It is an open-source desktop app for studying prediction markets, running paper bots, and deciding when a live path is earned.",
    productNotes: [
      {
        title: "Paper first",
        body: "No live mode until credentials, risk acknowledgements, diagnostics, and paper history all pass."
      },
      {
        title: "Coach only",
        body: "The assistant explains venues, logs, and scanner results without gaining control over execution."
      },
      {
        title: "Score split",
        body: "Paper score is the default. Live score stays separate and empty until a real live surface exists."
      }
    ],
    downloadTitle: "Use the Windows installer, then verify the trust story in the docs.",
    downloadBody:
      "The public build is for onboarding, paper bots, and education first. Releases, docs, and the full repo stay linked from one place.",
    ...shared
  }
};

export const landingVariantOrder = ["control", "focus"];
