import type { BotPresetName, Debrief, RunPhase, Tape, TapeEvent } from "@domain/types";
import type { BotDecision } from "@services/botEngine";
import type { TapeSummary } from "@services/datasetLoader";
import { DecisionLane } from "@ui/DecisionLane";

interface RunScreenProps {
  phase: RunPhase;
  tape: Tape;
  currentEvent: TapeEvent | null;
  currentTime: number;
  holdProgress: number;
  isRunning: boolean;
  selectedPreset: BotPresetName;
  availableTapes: TapeSummary[];
  selectedTapeId: string | null;
  debrief: Debrief | null;
  botDecision: BotDecision | null;
  onSelectPreset: (preset: BotPresetName) => void;
  onSelectTape: (tapeId: string) => void;
  onStartRun: () => void;
  onStep: () => void;
  onHoldStart: () => void;
  onHoldEnd: () => void;
  onReset: () => void;
}

const PRESETS: BotPresetName[] = ["Safe", "Balanced", "Aggressive"];

export function RunScreen({
  phase,
  tape,
  currentEvent,
  currentTime,
  holdProgress,
  isRunning,
  selectedPreset,
  availableTapes,
  selectedTapeId,
  debrief,
  botDecision,
  onSelectPreset,
  onSelectTape,
  onStartRun,
  onStep,
  onHoldStart,
  onHoldEnd,
  onReset,
}: RunScreenProps) {
  const netEdgeLabel = currentEvent?.routeSnapshot
    ? `${(currentEvent.routeSnapshot.netEdgeBps / 100).toFixed(2)}% NET`
    : "NO EDGE";
  const windowLabel = currentEvent?.window
    ? phase === "commit_hold"
      ? "COMMIT HOLD"
      : "WINDOW OPEN"
    : phase === "afterimage"
      ? "AFTERIMAGE"
      : "WINDOW CLOSED";
  const decisionLabel = botDecision ? `${botDecision.preset.toUpperCase()} ${botDecision.shouldCommit ? "IN" : "OUT"}` : "NO CALL";

  return (
    <section aria-label={`${tape.name} run`} className="run-surface">
      <header className="run-header">
        <span>{tape.market.symbol}</span>
        <strong>{phase.toUpperCase()}</strong>
        <span>{currentEvent?.label?.toUpperCase() ?? "READY"}</span>
      </header>

      <div className="preset-strip" aria-label="Starter presets">
        {PRESETS.map((preset) => (
          <button
            key={preset}
            type="button"
            className="preset-button"
            aria-pressed={selectedPreset === preset}
            onClick={() => onSelectPreset(preset)}
          >
            {preset}
          </button>
        ))}
      </div>

      <div className="tape-strip" aria-label="Tape select">
        {availableTapes.map((tapeOption) => (
          <button
            key={tapeOption.id}
            type="button"
            className="preset-button"
            aria-pressed={selectedTapeId === tapeOption.id}
            onClick={() => onSelectTape(tapeOption.id)}
          >
            {tapeOption.symbol} {tapeOption.name}
          </button>
        ))}
      </div>

      <DecisionLane tape={tape} currentTime={currentTime} currentEvent={currentEvent} phase={phase} />

      <div className="run-readout">
        <span>{selectedPreset.toUpperCase()}</span>
        <span>{windowLabel}</span>
        <span>{netEdgeLabel}</span>
        <span>{decisionLabel}</span>
      </div>

      <footer className="command-row">
        <button type="button" className="command-button" onClick={onStartRun} disabled={isRunning}>
          {isRunning ? "RUNNING" : "START RUN"}
        </button>
        <button type="button" className="command-button" onClick={onStep} disabled={isRunning}>
          STEP
        </button>
        <button
          type="button"
          className="command-button command-button-commit"
          onMouseDown={onHoldStart}
          onMouseUp={onHoldEnd}
          onMouseLeave={onHoldEnd}
          onTouchStart={onHoldStart}
          onTouchEnd={onHoldEnd}
          disabled={!currentEvent?.window || phase === "afterimage"}
        >
          <span className="command-fill" style={{ transform: `scaleX(${holdProgress})` }} />
          <span className="command-text">HOLD TO COMMIT</span>
        </button>
        <button type="button" className="command-button" onClick={onReset}>
          RESET
        </button>
      </footer>

      {debrief ? (
        <div className="afterimage">
          <strong>{debrief.headline.toUpperCase()}</strong>
          {debrief.reasons.map((reason) => (
            <span key={reason}>{reason}</span>
          ))}
          <span>{debrief.recommendation}</span>
        </div>
      ) : null}
    </section>
  );
}
