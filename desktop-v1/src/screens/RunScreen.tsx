import type { PackStatus, RunPhase, RunRecord, Tape, TapeEvent } from "@domain/types";
import type { TapeSummary } from "@services/datasetLoader";
import { DecisionLane } from "@ui/DecisionLane";

interface RunScreenProps {
  phase: RunPhase;
  tape: Tape;
  currentEvent: TapeEvent | null;
  currentTime: number;
  focusPosition: number;
  focusHot: boolean;
  holdProgress: number;
  isRunning: boolean;
  availableTapes: TapeSummary[];
  selectedTapeId: string | null;
  latestRun: RunRecord | null;
  currentScore: number;
  clearStreak: number;
  practiceStake: number;
  selectedPack: PackStatus | null;
  starterBotLabel: string;
  onMoveFocus: (ratio: number) => void;
  onNudgeFocus: (delta: number) => void;
  onSelectTape: (tapeId: string) => void;
  onStartRun: () => void;
  onStep: () => void;
  onHoldStart: () => void;
  onHoldEnd: () => void;
  onReset: () => void;
  onResetWorld: () => void;
}

export function RunScreen({
  phase,
  tape,
  currentEvent,
  currentTime,
  focusPosition,
  focusHot,
  holdProgress,
  isRunning,
  availableTapes,
  selectedTapeId,
  latestRun,
  currentScore,
  clearStreak,
  practiceStake,
  selectedPack,
  starterBotLabel,
  onMoveFocus,
  onNudgeFocus,
  onSelectTape,
  onStartRun,
  onStep,
  onHoldStart,
  onHoldEnd,
  onReset,
  onResetWorld,
}: RunScreenProps) {
  const windowLabel = currentEvent?.window
    ? phase === "commit_hold"
      ? "Hold now"
      : "Window open"
    : phase === "afterimage"
      ? "Run complete"
      : "Wait";
  const scoreLabel = formatMoney(currentScore);
  const resultLabel = latestRun?.receipt.label ?? "Ready";
  const phaseLabel = phase === "commit_hold" ? "Hold" : formatPhaseLabel(phase);
  const focusLabel = latestRun
    ? latestRun.outcome.grade === "off_target"
      ? "Off target"
      : latestRun.outcome.grade === "clear"
        ? "Clean"
        : "Timed"
    : focusHot
      ? "Hot"
      : "Track";
  const packProgressLabel = selectedPack ? `${selectedPack.clearedCount}/${selectedPack.totalCount}` : "--";
  const guide = getGuide(phase, Boolean(currentEvent?.window), focusHot, tape.mode);

  return (
    <section aria-label={`${tape.name} rehearsal`} className="run-surface">
      <header className="run-header">
        <div className="surface-heading">
          <span className="surface-heading__eyebrow">{tape.mode === "tutorial" ? "Learn" : "Shadow"}</span>
          <strong>{tape.name}</strong>
        </div>
        <span>{phaseLabel}</span>
      </header>

      {selectedPack ? (
        <div className="run-packline">
          <span>{`${selectedPack.pack.label} / ${selectedPack.pack.name}`}</span>
          <span>{`${packProgressLabel} cleared`}</span>
          <span>{selectedPack.completed ? "Ready for auto" : "Still in progress"}</span>
        </div>
      ) : null}

      <div className="run-guide">
        <span className="run-guide__label">What to do</span>
        <strong className="run-guide__title">{guide.title}</strong>
        <p className="run-guide__body">{guide.body}</p>
      </div>

      <div className="run-menu">
        <div className="selection-strip selection-strip--readout" aria-label="Starter bot">
          <span className="selection-strip__label">Current bot</span>
          <div className="selection-strip__group">
            <span className="selection-strip__text">{starterBotLabel}</span>
          </div>
        </div>

        <div className="selection-strip" aria-label="Tape select">
          <span className="selection-strip__label">{tape.mode === "tutorial" ? "Pick a learn tape" : "Pick a shadow tape"}</span>
          <div className="selection-strip__group">
            {availableTapes.map((tapeOption) => (
              <button
                key={tapeOption.id}
                type="button"
                className="preset-button"
                aria-pressed={selectedTapeId === tapeOption.id}
                onClick={() => onSelectTape(tapeOption.id)}
              >
                {tapeOption.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      <DecisionLane
        tape={tape}
        currentTime={currentTime}
        currentEvent={currentEvent}
        phase={phase}
        focusPosition={focusPosition}
        focusHot={focusHot}
        onFocusChange={onMoveFocus}
        onFocusNudge={onNudgeFocus}
      />

      <div className="run-readout">
        <div className="run-readout__item">
          <span className="run-readout__label">Practice score</span>
          <strong>{scoreLabel}</strong>
        </div>
        <div className="run-readout__item">
          <span className="run-readout__label">Stake</span>
          <strong>{formatMoney(practiceStake)}</strong>
        </div>
        <div className="run-readout__item">
          <span className="run-readout__label">Focus</span>
          <strong>{focusLabel}</strong>
        </div>
        <div className="run-readout__item">
          <span className="run-readout__label">Window</span>
          <strong>{windowLabel}</strong>
        </div>
      </div>

      <footer className="command-row">
        <button
          type="button"
          className="command-button command-button--primary"
          onClick={onStartRun}
          disabled={isRunning || practiceStake <= 0}
        >
          {isRunning ? "Running" : practiceStake > 0 ? "Start run" : "Stake empty"}
        </button>
        <button type="button" className="command-button command-button--secondary" onClick={onStep} disabled={isRunning}>
          Step
        </button>
        <button
          type="button"
          className={`command-button command-button-commit ${focusHot ? "command-button-commit--hot" : ""}`}
          onMouseDown={onHoldStart}
          onMouseUp={onHoldEnd}
          onMouseLeave={onHoldEnd}
          onTouchStart={onHoldStart}
          onTouchEnd={onHoldEnd}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              onHoldStart();
            }
          }}
          onKeyUp={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              onHoldEnd();
            }
          }}
          disabled={!currentEvent?.window || phase === "afterimage"}
        >
          <span className="command-fill" style={{ transform: `scaleX(${holdProgress})` }} />
          <span className="command-text">{`Hold to buy ${formatMoney(practiceStake)}`}</span>
        </button>
        <button type="button" className="command-button" onClick={onReset}>
          Reset run
        </button>
        <button type="button" className="command-button command-button--secondary" onClick={onResetWorld}>
          Reset score
        </button>
      </footer>

      {latestRun ? (
        <div className={`afterimage afterimage--${latestRun.receipt.tone}`}>
          <div className="afterimage__main">
            <span className="afterimage__label">Result</span>
            <strong>{formatSignedMoney(latestRun.receipt.netPnl)}</strong>
            <span className="afterimage__bankroll">Score {formatMoney(latestRun.receipt.endingBankroll)}</span>
          </div>
          <div className="afterimage__receipt">
            <span>{resultLabel}</span>
            <span>
              {latestRun.receipt.entryPrice === null
                ? "No position opened"
                : `Entry ${formatPrice(latestRun.receipt.entryPrice)} -> Exit ${formatPrice(latestRun.receipt.exitPrice)}`}
            </span>
            <span>
              {`Gross ${formatSignedMoney(latestRun.receipt.grossPnl)} / Fees ${formatSignedMoney(-latestRun.receipt.fees)} / Slip ${formatSignedMoney(-latestRun.receipt.slippage)}`}
            </span>
            <span>{latestRun.outcome.grade === "off_target" ? "Focus Off Target" : `Focus ${latestRun.outcome.grade === "clear" ? "Clean" : "Timed"}`}</span>
            <span>{latestRun.debrief.recommendation}</span>
            {selectedPack ? <span>{selectedPack.completed ? "Ready for auto" : `${packProgressLabel} cleared`}</span> : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function formatMoney(value: number): string {
  return `$${value.toFixed(2)}`;
}

function formatSignedMoney(value: number): string {
  return `${value >= 0 ? "+" : "-"}$${Math.abs(value).toFixed(2)}`;
}

function formatPrice(value: number | null): string {
  if (value === null) {
    return "--";
  }
  return `${Math.round(value * 100)}c`;
}

function formatPhaseLabel(value: RunPhase): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function getGuide(phase: RunPhase, windowOpen: boolean, focusHot: boolean, mode: Tape["mode"]) {
  if (phase === "afterimage") {
    return {
      title: "Read the result before you run it again.",
      body: "Check the score, the buy line, and whether your focus stayed centered when the window was live.",
    };
  }

  if (windowOpen) {
    return {
      title: focusHot ? "The window is hot." : "Lead the reticle into the window.",
      body: focusHot
        ? "Hold once while the reticle stays centered. Let it go if the lane drifts away."
        : "Move the reticle until the line turns hot, then hold once. Timing and aim both matter now.",
    };
  }

  if (phase === "run" || phase === "pressure") {
    return {
      title: "Track the lane before you buy.",
      body: "Keep the reticle steady and let the lane come to you. Do not rush just because the motion started.",
    };
  }

  return {
    title: mode === "tutorial" ? "Start a learn run." : "Start a shadow run.",
    body: mode === "tutorial"
      ? "Start once, guide the reticle, and buy only when the window feels obvious."
      : "Shadow asks you to replay the move cleanly. Keep the reticle calm and buy only when it holds center.",
  };
}
