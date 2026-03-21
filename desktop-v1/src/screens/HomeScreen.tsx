import type { BotRuntime, LiveGate, RunRecord, StarterBotProfile } from "@domain/types";

interface HomeScreenProps {
  botRuntime: BotRuntime;
  starterBot: StarterBotProfile;
  liveGate: LiveGate;
  latestRun: RunRecord | null;
  onOpenPractice: () => void;
  onOpenBot: () => void;
  onStartBot: () => void;
  onHaltBot: () => void;
}

const LADDER = [
  { id: "learn", label: "Learn" },
  { id: "shadow", label: "Shadow" },
  { id: "armed", label: "Armed" },
  { id: "auto_running", label: "Auto" },
] as const;

export function HomeScreen({
  botRuntime,
  starterBot,
  liveGate,
  latestRun,
  onOpenPractice,
  onOpenBot,
  onStartBot,
  onHaltBot,
}: HomeScreenProps) {
  const riskLeft = `$${starterBot.dailyLossCap.toFixed(2)}`;
  const lastRunLabel = latestRun ? `${formatGrade(latestRun.outcome.grade)} ${formatSignedMoney(latestRun.receipt.netPnl)}` : "No run yet";
  const canStartAuto = botRuntime.phase === "armed" || botRuntime.phase === "halted";
  const nextStep = getNextStep(botRuntime.phase);
  const shadowLabel = botRuntime.shadowRuns > 0 ? `${botRuntime.shadowRuns} clear${botRuntime.shadowRuns === 1 ? "" : "s"}` : "Not cleared yet";
  const homeCards = [
    {
      label: "Right now",
      value: formatPhase(botRuntime.phase),
      detail: botRuntime.lastAction,
    },
    {
      label: "Trust ladder",
      value: liveGate.unlocked ? "Unlocked" : "In progress",
      detail: liveGate.unlocked ? `Shadow clears: ${shadowLabel}` : "Nothing live can start until the learn ladder is clear.",
    },
    {
      label: "Today's max risk",
      value: riskLeft,
      detail: `$${starterBot.perTradeCap.toFixed(2)} per trade / ${starterBot.maxOpenPositions} open max`,
    },
    {
      label: "Last result",
      value: lastRunLabel,
      detail: latestRun ? latestRun.debrief.recommendation : "Start with Learn 01",
    },
  ];

  return (
    <section className="control-surface" aria-label="Starter bot home">
      <header className="control-surface__header">
        <div className="surface-heading">
          <span className="surface-heading__eyebrow">Home</span>
          <strong>{nextStep.title}</strong>
        </div>
        <span>{starterBot.venue} / {formatPhase(botRuntime.phase)}</span>
      </header>

      <div className="surface-intro surface-intro--home">
        <article className="friendly-card friendly-card--primary">
          <span className="friendly-card__label">Next step</span>
          <strong className="friendly-card__title">{nextStep.title}</strong>
          <p className="friendly-card__body">{nextStep.body}</p>
        </article>
        <article className="friendly-card">
          <span className="friendly-card__label">Guardrails</span>
          <strong className="friendly-card__title">{`${riskLeft} max today`}</strong>
          <p className="friendly-card__body">
            {`$${starterBot.perTradeCap.toFixed(2)} per trade, ${starterBot.maxOpenPositions} open positions max, and a stop button that stays visible.`}
          </p>
        </article>
      </div>

      <div className="control-surface__grid">
        {homeCards.map((card) => (
          <div key={card.label} className="metric-card">
            <span className="metric-card__label">{card.label}</span>
            <strong>{card.value}</strong>
            <small>{card.detail}</small>
          </div>
        ))}
      </div>

      <div className="ladder-strip" aria-label="Trust ladder">
        {LADDER.map((step) => (
          <div
            key={step.id}
            className={`ladder-step ${step.id === botRuntime.phase ? "ladder-step--current" : ""} ${isComplete(step.id, botRuntime) ? "ladder-step--complete" : ""}`}
          >
            <span>{step.label}</span>
          </div>
        ))}
      </div>

      <footer className="control-surface__actions">
        <button type="button" className="command-button command-button--primary" onClick={onOpenPractice}>
          {liveGate.unlocked ? "Open shadow run" : "Start learn run"}
        </button>
        <button type="button" className="command-button command-button--secondary" onClick={onOpenBot}>
          Bot rules
        </button>
        <button type="button" className="command-button" onClick={onStartBot} disabled={!canStartAuto}>
          {botRuntime.phase === "auto_running" ? "Auto is on" : "Start auto"}
        </button>
        <button type="button" className="command-button command-button--secondary" onClick={onHaltBot} disabled={botRuntime.phase !== "auto_running"}>
          Stop bot
        </button>
      </footer>
    </section>
  );
}

function isComplete(step: (typeof LADDER)[number]["id"], botRuntime: BotRuntime): boolean {
  const order = ["learn", "shadow", "armed", "auto_running"];
  const currentIndex = order.indexOf(botRuntime.phase === "halted" ? "armed" : botRuntime.phase);
  const targetIndex = order.indexOf(step);
  return currentIndex >= targetIndex && currentIndex !== -1;
}

function formatPhase(value: BotRuntime["phase"]): string {
  switch (value) {
    case "auto_running":
      return "Auto on";
    case "halted":
      return "Halted";
    default:
      return value
        .split("_")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ");
  }
}

function formatSignedMoney(value: number): string {
  return `${value >= 0 ? "+" : "-"}$${Math.abs(value).toFixed(2)}`;
}

function formatGrade(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function getNextStep(phase: BotRuntime["phase"]) {
  switch (phase) {
    case "setup":
      return {
        title: "Run the first learn tape",
        body: "Use Practice to learn the lane once without pressure. Watch the gold window and commit only when it feels obvious.",
      };
    case "learn":
      return {
        title: "Finish the learn ladder",
        body: "Keep the rhythm simple. Clear the learn tapes before you worry about auto or live states.",
      };
    case "shadow":
      return {
        title: "Clear one shadow replay",
        body: "Replay the move cleanly so the bot feels understandable before anything real is allowed to happen.",
      };
    case "armed":
      return {
        title: "The bot is ready to start",
        body: "Auto is available now, but the lane stays small and the caps stay visible the whole time.",
      };
    case "auto_running":
      return {
        title: "Auto is running under tight caps",
        body: "Watch the last action and stop the bot immediately if the lane stops making sense.",
      };
    case "halted":
      return {
        title: "Read the halt reason first",
        body: "A halt is good when something feels off. Review the reason, then re-arm only if the lane still looks healthy.",
      };
    default:
      return {
        title: "Stay in the simple lane",
        body: "Learn first, shadow second, auto last.",
      };
  }
}
