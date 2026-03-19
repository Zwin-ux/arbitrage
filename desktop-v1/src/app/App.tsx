import { useRehearsalMachine } from "@app/useRehearsalMachine";
import { LiveLockedScreen } from "@screens/LiveLockedScreen";
import { ModeSelectScreen } from "@screens/ModeSelectScreen";
import { RunScreen } from "@screens/RunScreen";
import { AppShell } from "@ui/AppShell";
import superiorWordmark from "../assets/superior-wordmark.png";

export function App() {
  const machine = useRehearsalMachine();
  const tapeTitle = machine.currentTape ? machine.currentTape.name.toUpperCase() : "NO TAPE";
  const marketLabel = machine.currentTape?.market.symbol ?? "LOCAL";
  const modeLabel = machine.mode === "tutorial" ? "TUTORIAL" : machine.mode === "replay" ? "REPLAY" : "LIVE";

  return (
    <AppShell label="SUP practice world">
      <div className="sup-shell">
        <header className="sup-marquee">
          <img alt="Superior" className="sup-wordmark" src={superiorWordmark} />
          <div className="sup-status">
            <span>BANK {formatMoney(machine.practiceBankroll)}</span>
            <span>BEST {formatMoney(machine.bestBankroll)}</span>
            <span>STREAK {machine.clearStreak}</span>
          </div>
          <div className="sup-substatus">
            <span>{modeLabel}</span>
            <span>{marketLabel}</span>
            <span>{tapeTitle}</span>
            <span>LIVE LOCKED</span>
          </div>
        </header>

        <ModeSelectScreen
          selected={machine.mode}
          availablePacks={machine.packStatuses}
          selectedPackId={machine.selectedPackId}
          onSelectMode={machine.selectMode}
          onSelectPack={machine.selectPack}
          replayUnlocked={machine.replayUnlocked}
          liveUnlocked={machine.progress.liveGate.unlocked}
        />

        {machine.mode === "live-preview" ? (
          <LiveLockedScreen gate={machine.progress.liveGate} />
        ) : machine.currentTape ? (
          <RunScreen
            phase={machine.phase}
            tape={machine.currentTape}
            currentEvent={machine.currentEvent}
            currentTime={machine.currentTime}
            holdProgress={machine.holdProgress}
            isRunning={machine.isRunning}
            selectedPreset={machine.selectedPreset}
            availableTapes={machine.availableTapes}
            selectedTapeId={machine.selectedTapeId}
            latestRun={machine.latestRun}
            comparisonResults={machine.comparisonResults}
            startingBankroll={machine.startingBankroll}
            currentBankroll={machine.practiceBankroll}
            clearStreak={machine.clearStreak}
            practiceStake={machine.practiceStake}
            selectedPack={machine.selectedPack}
            onSelectPreset={machine.selectPreset}
            onSelectTape={machine.selectTape}
            onStartRun={machine.startRun}
            onStep={machine.step}
            onHoldStart={machine.startHold}
            onHoldEnd={machine.cancelHold}
            onReset={machine.reset}
            onResetWorld={machine.resetWorld}
          />
        ) : null}
      </div>
    </AppShell>
  );
}

function formatMoney(value: number): string {
  return `$${value.toFixed(2)}`;
}
