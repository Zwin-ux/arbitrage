import type { BotRuntime, DecisionAuditEvent, ExecutionPolicy, StarterBotProfile } from "@domain/types";

interface BotControlScreenProps {
  starterBot: StarterBotProfile;
  executionPolicy: ExecutionPolicy;
  botRuntime: BotRuntime;
  decisionAudit: DecisionAuditEvent[];
  onArmBot: () => void;
  onStartBot: () => void;
  onHaltBot: () => void;
}

export function BotControlScreen({
  starterBot,
  executionPolicy,
  botRuntime,
  decisionAudit,
  onArmBot,
  onStartBot,
  onHaltBot,
}: BotControlScreenProps) {
  const canArm = botRuntime.phase === "shadow" && botRuntime.shadowRuns > 0;
  const canStart = botRuntime.phase === "armed" || botRuntime.phase === "halted";
  const readinessTitle = canArm ? "Ready to arm" : botRuntime.shadowRuns > 0 ? "Shadow passed" : "Shadow still needed";

  return (
    <section className="control-surface" aria-label="Starter bot controls">
      <header className="control-surface__header">
        <div className="surface-heading">
          <span className="surface-heading__eyebrow">Bot</span>
          <strong>{starterBot.label}</strong>
        </div>
        <span>{starterBot.venue} / {formatPhase(botRuntime.phase)}</span>
      </header>

      <div className="surface-intro">
        <article className="friendly-card friendly-card--primary">
          <span className="friendly-card__label">What this bot does</span>
          <strong className="friendly-card__title">One calm Kalshi lane</strong>
          <p className="friendly-card__body">
            It stays inside one narrow internal-binary ruleset so the live path feels readable instead of magical.
          </p>
        </article>
        <article className="friendly-card">
          <span className="friendly-card__label">Readiness</span>
          <strong className="friendly-card__title">{readinessTitle}</strong>
          <p className="friendly-card__body">{botRuntime.lastAction}</p>
        </article>
      </div>

      <div className="control-surface__grid">
        <div className="metric-card">
          <span className="metric-card__label">Strategy lane</span>
          <strong>Internal binary</strong>
          <small>{starterBot.cadence}</small>
        </div>
        <div className="metric-card">
          <span className="metric-card__label">Caps</span>
          <strong>{`$${starterBot.perTradeCap.toFixed(2)} / $${starterBot.dailyLossCap.toFixed(2)}`}</strong>
          <small>{`${starterBot.maxOpenPositions} open positions max`}</small>
        </div>
        <div className="metric-card">
          <span className="metric-card__label">Automatic halts</span>
          <strong>{`${executionPolicy.staleDataWindowSeconds}s stale halt`}</strong>
          <small>{`${executionPolicy.orderErrorLimit} order errors before halt`}</small>
        </div>
        <div className="metric-card">
          <span className="metric-card__label">Manual control</span>
          <strong>{executionPolicy.manualKillSwitch ? "Always visible" : "Missing"}</strong>
          <small>{executionPolicy.authFailureHalts ? "Auth failures also stop the bot." : "Auth halt still needs to be wired."}</small>
        </div>
      </div>

      <footer className="control-surface__actions">
        <button type="button" className="command-button command-button--primary" onClick={onArmBot} disabled={!canArm}>
          Arm bot
        </button>
        <button type="button" className="command-button" onClick={onStartBot} disabled={!canStart}>
          Start auto
        </button>
        <button type="button" className="command-button command-button--secondary" onClick={onHaltBot} disabled={botRuntime.phase !== "auto_running"}>
          Stop bot
        </button>
      </footer>

      <div className="audit-log" aria-label="Activity log">
        <div className="audit-log__header">
          <span className="audit-log__title">Why it acted</span>
          <small className="audit-log__subtitle">Every state change should be easy to read later.</small>
        </div>
        {decisionAudit.length > 0 ? (
          decisionAudit.map((event) => (
            <article key={event.id} className={`audit-log__row audit-log__row--${event.tone}`}>
              <span className="audit-log__meta">{formatTime(event.createdAt)}</span>
              <div>
                <strong>{event.title}</strong>
                <p>{event.detail}</p>
              </div>
            </article>
          ))
        ) : (
          <article className="audit-log__row audit-log__row--neutral">
            <span className="audit-log__meta">--</span>
            <div>
              <strong>No bot activity yet</strong>
              <p>Finish the trust ramp and the starter bot log begins here.</p>
            </div>
          </article>
        )}
      </div>
    </section>
  );
}

function formatTime(value: string): string {
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
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
