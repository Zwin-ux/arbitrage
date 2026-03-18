import type { BotComparisonResult, BotPresetName, RunPhase, RunRecord, Tape, TapeEvent } from "@domain/types";
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
  latestRun: RunRecord | null;
  comparisonResults: BotComparisonResult[];
  startingBankroll: number;
  currentBankroll: number;
  clearStreak: number;
  practiceStake: number;
  onSelectPreset: (preset: BotPresetName) => void;
  onSelectTape: (tapeId: string) => void;
  onStartRun: () => void;
  onStep: () => void;
  onHoldStart: () => void;
  onHoldEnd: () => void;
  onReset: () => void;
  onResetWorld: () => void;
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
  latestRun,
  comparisonResults,
  startingBankroll,
  currentBankroll,
  clearStreak,
  practiceStake,
  onSelectPreset,
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
      ? "HOLD TO BUY"
      : "BUY WINDOW OPEN"
    : phase === "afterimage"
      ? "RUN COMPLETE"
      : "WAIT";
  const bankrollLabel = formatMoney(currentBankroll);
  const resultLabel = latestRun?.receipt.label ?? "READY";
  const phaseLabel = phase === "commit_hold" ? "HOLD" : phase.toUpperCase();

  return (
    <section aria-label={`${tape.name} run`} className="run-surface">
      <header className="run-header">
        <span>{tape.market.symbol}</span>
        <strong>{tape.name.toUpperCase()}</strong>
        <span>{phaseLabel}</span>
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
        <div className="run-readout__item">
          <span className="run-readout__label">BANKROLL</span>
          <strong>{bankrollLabel}</strong>
        </div>
        <div className="run-readout__item">
          <span className="run-readout__label">STAKE</span>
          <strong>{formatMoney(practiceStake)}</strong>
        </div>
        <div className="run-readout__item">
          <span className="run-readout__label">BUY WINDOW</span>
          <strong>{windowLabel}</strong>
        </div>
        <div className="run-readout__item">
          <span className="run-readout__label">CLEAR STREAK</span>
          <strong>{String(clearStreak).padStart(2, "0")}</strong>
        </div>
      </div>

      <footer className="command-row">
        <button type="button" className="command-button" onClick={onStartRun} disabled={isRunning || practiceStake <= 0}>
          {isRunning ? "RUNNING" : practiceStake > 0 ? "START" : "BANK EMPTY"}
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
          <span className="command-text">{`HOLD TO BUY ${formatMoney(practiceStake)}`}</span>
        </button>
        <button type="button" className="command-button" onClick={onReset}>
          RESET
        </button>
        <button type="button" className="command-button" onClick={onResetWorld}>
          NEW $100
        </button>
      </footer>

      {latestRun ? (
        <div className={`afterimage afterimage--${latestRun.receipt.tone}`}>
          <div className="afterimage__main">
            <span className="afterimage__label">RESULT</span>
            <strong>{formatSignedMoney(latestRun.receipt.netPnl)}</strong>
            <span className="afterimage__bankroll">BANKROLL {formatMoney(latestRun.receipt.endingBankroll)}</span>
          </div>
          <div className="afterimage__receipt">
            <span>{resultLabel}</span>
            <span>
              {latestRun.receipt.entryPrice === null
                ? "NO POSITION OPENED"
                : `BUY ${formatPrice(latestRun.receipt.entryPrice)} -> SELL ${formatPrice(latestRun.receipt.exitPrice)}`}
            </span>
            <span>
              {`GROSS ${formatSignedMoney(latestRun.receipt.grossPnl)} / FEES ${formatSignedMoney(-latestRun.receipt.fees)} / SLIP ${formatSignedMoney(-latestRun.receipt.slippage)}`}
            </span>
            <span>{latestRun.debrief.recommendation.toUpperCase()}</span>
          </div>
          {comparisonResults.length > 0 ? (
            <div className="comparison-grid" aria-label="Bot comparison">
              <div className="comparison-grid__row">
                <span className="comparison-grid__header">YOU</span>
                <div className={`comparison-grid__cell comparison-grid__cell--${latestRun.receipt.tone}`}>
                  <strong>{formatSignedMoney(latestRun.receipt.netPnl)}</strong>
                  <span>{latestRun.receipt.label}</span>
                </div>
              </div>
              {comparisonResults.map((result) => (
                <div key={result.preset} className="comparison-grid__row">
                  <span className="comparison-grid__header">{result.preset.toUpperCase()}</span>
                  <div className={`comparison-grid__cell comparison-grid__cell--${result.receipt.tone}`}>
                    <strong>{formatSignedMoney(result.receipt.netPnl)}</strong>
                    <span>{result.verdict.toUpperCase()}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : null}
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
