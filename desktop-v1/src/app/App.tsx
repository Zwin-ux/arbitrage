import { useRehearsalMachine } from "@app/useRehearsalMachine";
import { LiveLockedScreen } from "@screens/LiveLockedScreen";
import { ModeSelectScreen } from "@screens/ModeSelectScreen";
import { RunScreen } from "@screens/RunScreen";
import { AppShell } from "@ui/AppShell";
import superiorWordmark from "../assets/superior-wordmark.png";

export function App() {
  const machine = useRehearsalMachine();
  const tapeTitle = machine.currentTape
    ? `${machine.currentTape.name} / ${machine.currentTape.market.symbol}`
    : "NO TAPE";
  const modeLabel = machine.mode === "tutorial" ? "TUTORIAL" : machine.mode === "replay" ? "REPLAY" : "LIVE LOCKED";

  return (
    <AppShell label="SUP practice money">
      <div className="sup-shell">
        <header className="sup-marquee">
          <img alt="Superior" className="sup-wordmark" src={superiorWordmark} />
          <div className="sup-status">
            <span>PRACTICE MONEY</span>
            <span>{modeLabel}</span>
            <span>{tapeTitle}</span>
            <span>LIVE LOCKED</span>
          </div>
        </header>

        <ModeSelectScreen
          selected={machine.mode}
          onSelectMode={machine.selectMode}
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
            startingBankroll={machine.startingBankroll}
            practiceStake={machine.practiceStake}
            onSelectPreset={machine.selectPreset}
            onSelectTape={machine.selectTape}
            onStartRun={machine.startRun}
            onStep={machine.step}
            onHoldStart={machine.startHold}
            onHoldEnd={machine.cancelHold}
            onReset={machine.reset}
          />
        ) : null}
      </div>
    </AppShell>
  );
}
