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

  return (
    <AppShell label="SUP rehearsal machine">
      <div className="sup-shell">
        <header className="sup-marquee">
          <img alt="Superior" className="sup-wordmark" src={superiorWordmark} />
          <div className="sup-status">
            <span>{machine.mode === "tutorial" ? "TUTORIAL" : machine.mode === "replay" ? "REPLAY" : "LIVE BOOKS"}</span>
            <span>{tapeTitle}</span>
            <span>{machine.phase.toUpperCase()}</span>
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
            onSelectPreset={machine.selectPreset}
            onSelectTape={machine.selectTape}
            onStartRun={machine.startRun}
            onStep={machine.step}
            onHoldStart={machine.startHold}
            onHoldEnd={machine.cancelHold}
            onReset={machine.reset}
            debrief={machine.latestRun?.debrief ?? null}
            botDecision={machine.botDecision}
          />
        ) : null}
      </div>
    </AppShell>
  );
}
