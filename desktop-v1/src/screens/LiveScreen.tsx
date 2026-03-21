import type { BotRuntime, DecisionAuditEvent, StarterBotProfile } from "@domain/types";

interface LiveScreenProps {
  starterBot: StarterBotProfile;
  botRuntime: BotRuntime;
  decisionAudit: DecisionAuditEvent[];
  onStartBot: () => void;
  onHaltBot: () => void;
}

export function LiveScreen({ starterBot, botRuntime, decisionAudit, onStartBot, onHaltBot }: LiveScreenProps) {
  const lastEvent = decisionAudit[0] ?? null;
  const liveNote = getLiveNote(botRuntime.phase);

  return (
    <section className="control-surface" aria-label="Live status">
      <header className="control-surface__header">
        <div className="surface-heading">
          <span className="surface-heading__eyebrow">Live</span>
          <strong>{liveNote.title}</strong>
        </div>
        <span>{starterBot.venue} / {formatPhase(botRuntime.phase)}</span>
      </header>

      <div className="surface-intro">
        <article className="friendly-card friendly-card--primary">
          <span className="friendly-card__label">Live lane</span>
          <strong className="friendly-card__title">{liveNote.title}</strong>
          <p className="friendly-card__body">{liveNote.body}</p>
        </article>
        <article className="friendly-card">
          <span className="friendly-card__label">Instant stop</span>
          <strong className="friendly-card__title">Keep the halt button close</strong>
          <p className="friendly-card__body">A consumer bot should always be easy to stop before it is impressive.</p>
        </article>
      </div>

      <div className="control-surface__grid">
        <div className="metric-card">
          <span className="metric-card__label">Current mode</span>
          <strong>{formatPhase(botRuntime.phase)}</strong>
          <small>{botRuntime.haltReason ?? "No active halt."}</small>
        </div>
        <div className="metric-card">
          <span className="metric-card__label">Risk left</span>
          <strong>{`$${starterBot.dailyLossCap.toFixed(2)} left`}</strong>
          <small>{`$${starterBot.perTradeCap.toFixed(2)} max each / ${starterBot.maxOpenPositions} open`}</small>
        </div>
        <div className="metric-card">
          <span className="metric-card__label">Open positions</span>
          <strong>0</strong>
          <small>None right now. This lane should stay boring and easy to scan.</small>
        </div>
        <div className="metric-card">
          <span className="metric-card__label">Last action</span>
          <strong>{lastEvent?.title ?? "No live action yet"}</strong>
          <small>{lastEvent?.detail ?? "Arm the bot from Bot when you are ready."}</small>
        </div>
      </div>

      <footer className="control-surface__actions">
        <button type="button" className="command-button command-button--primary" onClick={onStartBot} disabled={botRuntime.phase !== "armed" && botRuntime.phase !== "halted"}>
          {botRuntime.phase === "auto_running" ? "Auto is on" : "Start auto"}
        </button>
        <button type="button" className="command-button command-button--secondary" onClick={onHaltBot} disabled={botRuntime.phase !== "auto_running"}>
          Stop now
        </button>
      </footer>
    </section>
  );
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

function getLiveNote(phase: BotRuntime["phase"]) {
  switch (phase) {
    case "armed":
      return {
        title: "Everything is ready, but auto is still off.",
        body: "This is the calm moment before you start. Read the caps, check the last shadow decision, then choose deliberately.",
      };
    case "auto_running":
      return {
        title: "Auto is running under tight caps.",
        body: "The goal here is clarity: current mode, risk left, open positions, and the last action in one glance.",
      };
    case "halted":
      return {
        title: "The bot is halted and waiting on you.",
        body: "Review the halt reason first. A good stop should always feel obvious and reversible.",
      };
    default:
      return {
        title: "Live stays small on purpose.",
        body: "One venue, one narrow lane, and a stop path that is always more important than raw speed.",
      };
  }
}
