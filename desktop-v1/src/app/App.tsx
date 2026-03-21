import { useRehearsalMachine } from "@app/useRehearsalMachine";
import { BotControlScreen } from "@screens/BotControlScreen";
import { HomeScreen } from "@screens/HomeScreen";
import { LiveScreen } from "@screens/LiveScreen";
import { ModeSelectScreen } from "@screens/ModeSelectScreen";
import { RunScreen } from "@screens/RunScreen";
import { AppShell } from "@ui/AppShell";
import { ShellNav } from "@ui/ShellNav";
import superiorHead from "../assets/superior-head.png";
import superiorWordmark from "../assets/superior-wordmark.png";

export function App() {
  const machine = useRehearsalMachine();
  const riskLabel = `$${machine.starterBot.perTradeCap.toFixed(2)} / $${machine.starterBot.dailyLossCap.toFixed(2)}`;
  const heroCopy = getHeroCopy(machine.botRuntime.phase, machine.progress.liveGate.unlocked);

  return (
    <AppShell label="Superior consumer shell">
      <div className="sup-shell">
        <header className="sup-marquee">
          <div className="sup-marquee__copy">
            <span className="sup-marquee__eyebrow">Start in Practice. Shadow before auto.</span>
            <img alt="Superior" className="sup-wordmark" src={superiorWordmark} />
            <h1 className="sup-marquee__title">{heroCopy.title}</h1>
            <p className="sup-marquee__body">{heroCopy.body}</p>

            <div className="sup-status" aria-label="Current shell status">
              <div className="sup-status__chip">
                <small>Bot</small>
                <strong>{formatPhase(machine.botRuntime.phase)}</strong>
              </div>
              <div className="sup-status__chip">
                <small>Caps</small>
                <strong>{riskLabel}</strong>
              </div>
              <div className="sup-status__chip">
                <small>Shadow clears</small>
                <strong>{String(machine.botRuntime.shadowRuns).padStart(2, "0")}</strong>
              </div>
            </div>
          </div>

          <aside className="sup-head-panel" aria-label="Friendly first-run reminder">
            <img alt="Superior mascot" className="sup-head" src={superiorHead} />
            <span className="sup-head-panel__label">{heroCopy.panelLabel}</span>
            <strong className="sup-head-panel__title">{heroCopy.panelTitle}</strong>
            <p className="sup-head-panel__body">{heroCopy.panelBody}</p>
            <div className="sup-substatus">
              <span>Kalshi live</span>
              <span>Polymarket learn</span>
              <span>{machine.starterBot.strategyFamily.replace("-", " ")}</span>
            </div>
          </aside>
        </header>

        <ShellNav selectedView={machine.selectedView} botPhase={machine.botRuntime.phase} onSelectView={machine.selectView} />

        {machine.selectedView === "home" ? (
          <HomeScreen
            botRuntime={machine.botRuntime}
            starterBot={machine.starterBot}
            liveGate={machine.progress.liveGate}
            latestRun={machine.latestRun}
            onOpenPractice={() => machine.selectView("practice")}
            onOpenBot={() => machine.selectView("bot")}
            onStartBot={machine.startBot}
            onHaltBot={machine.haltBot}
          />
        ) : null}

        {machine.selectedView === "practice" ? (
          <>
            <ModeSelectScreen
              selected={machine.mode}
              availablePacks={machine.packStatuses}
              selectedPackId={machine.selectedPackId}
              replayUnlocked={machine.replayUnlocked}
              shadowReady={machine.progress.liveGate.unlocked}
              onSelectMode={machine.selectMode}
              onSelectPack={machine.selectPack}
            />

            {machine.currentTape ? (
              <RunScreen
                phase={machine.phase}
                tape={machine.currentTape}
                currentEvent={machine.currentEvent}
                currentTime={machine.currentTime}
                holdProgress={machine.holdProgress}
                isRunning={machine.isRunning}
                availableTapes={machine.availableTapes}
                selectedTapeId={machine.selectedTapeId}
                latestRun={machine.latestRun}
                currentScore={machine.practiceBankroll}
                clearStreak={machine.clearStreak}
                practiceStake={machine.practiceStake}
                selectedPack={machine.selectedPack}
                starterBotLabel={machine.starterBot.label}
                onSelectTape={machine.selectTape}
                onStartRun={machine.startRun}
                onStep={machine.step}
                onHoldStart={machine.startHold}
                onHoldEnd={machine.cancelHold}
                onReset={machine.reset}
                onResetWorld={machine.resetWorld}
              />
            ) : null}
          </>
        ) : null}

        {machine.selectedView === "bot" ? (
          <BotControlScreen
            starterBot={machine.starterBot}
            executionPolicy={machine.executionPolicy}
            botRuntime={machine.botRuntime}
            decisionAudit={machine.decisionAudit}
            onArmBot={machine.armBot}
            onStartBot={machine.startBot}
            onHaltBot={machine.haltBot}
          />
        ) : null}

        {machine.selectedView === "live" ? (
          <LiveScreen
            starterBot={machine.starterBot}
            botRuntime={machine.botRuntime}
            decisionAudit={machine.decisionAudit}
            onStartBot={machine.startBot}
            onHaltBot={machine.haltBot}
          />
        ) : null}
      </div>
    </AppShell>
  );
}

function formatPhase(value: string): string {
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

function getHeroCopy(phase: string, liveUnlocked: boolean) {
  switch (phase) {
    case "setup":
      return {
        title: "Start with one clean learn run.",
        body: "Open Practice, watch the lane, then commit once when the gold window feels obvious.",
        panelLabel: "Friendly first run",
        panelTitle: "No pressure yet",
        panelBody: "The bot stays off until you clear the trust ladder and choose to arm it.",
      };
    case "learn":
      return {
        title: liveUnlocked ? "Learn cleared. Shadow comes next." : "Finish the learn ladder first.",
        body: liveUnlocked
          ? "Open a shadow run next. The shell only moves forward after one clean replay."
          : "The goal is rhythm, not speed. Learn the lane first so the bot never feels mysterious later.",
        panelLabel: "Practice first",
        panelTitle: "Shadow comes next",
        panelBody: "Practice is where the timing loop becomes obvious and low-stress.",
      };
    case "shadow":
      return {
        title: "Clear one shadow replay, then arm the bot.",
        body: "This is the final rehearsal step. Prove that the lane and the timing both make sense to you.",
        panelLabel: "Trust ladder",
        panelTitle: "Shadow is the gate",
        panelBody: "Nothing real should feel magical. Shadow makes the future live action legible first.",
      };
    case "armed":
      return {
        title: "The bot is ready, but the lane stays small.",
        body: "Auto can turn on now, but the caps stay small and the stop button stays visible the whole time.",
        panelLabel: "Ready state",
        panelTitle: "Small on purpose",
        panelBody: "One venue, one narrow lane, one very obvious halt path.",
      };
    case "auto_running":
      return {
        title: "Auto is on under tight caps.",
        body: "Watch the last action, keep the risk budget visible, and stop the bot immediately if trust breaks.",
        panelLabel: "Live lane",
        panelTitle: "Still human-readable",
        panelBody: "Every action should be explainable in one glance, not buried in a dashboard.",
      };
    case "halted":
      return {
        title: "The bot is halted. Read the reason before you resume.",
        body: "A good consumer tool stops cleanly and tells you why. Resume only if the lane still looks healthy.",
        panelLabel: "Safety first",
        panelTitle: "Stop means stop",
        panelBody: "The halt state should feel calm, obvious, and easy to trust.",
      };
    default:
      return {
        title: "Stay in the simple lane.",
        body: "Learn, shadow, then arm the bot only when the whole loop feels boring and clear.",
        panelLabel: "Superior",
        panelTitle: "One narrow lane",
        panelBody: "Friendly to start, strict once real money is involved.",
      };
  }
}
