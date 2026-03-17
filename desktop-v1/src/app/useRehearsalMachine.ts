import { useEffect, useMemo, useRef, useState } from "react";

import type { BotPresetName, RunPhase, RunRecord, Tape, TapeEvent, TapeMode } from "@domain/types";
import { STARTER_BOTS } from "@presets/starterBots";
import { evaluatePresetAgainstEvent } from "@services/botEngine";
import { getTapeById, listTapeSummaries, listTapes } from "@services/datasetLoader";
import { LocalProgressStore } from "@services/persistenceService";
import { PRACTICE_STAKE, STARTING_BANKROLL } from "@services/practiceMoney";
import { recordRun } from "@services/progressService";
import { RunEngine } from "@services/runEngine";
import { TapeEngine } from "@services/tapeEngine";

const HOLD_FALLBACK_MS = 500;

export function useRehearsalMachine() {
  const progressStoreRef = useRef(new LocalProgressStore());
  const tapeEngineRef = useRef(new TapeEngine());
  const runEngineRef = useRef(new RunEngine());
  const playbackFrameRef = useRef<number | null>(null);
  const holdFrameRef = useRef<number | null>(null);
  const holdStartRef = useRef<number | null>(null);
  const playbackStartRef = useRef<number | null>(null);

  const [progress, setProgress] = useState(() => progressStoreRef.current.load());
  const [mode, setMode] = useState<TapeMode>(progress.lastSelectedMode);
  const [selectedTapeId, setSelectedTapeId] = useState<string | null>(listTapes(progress.lastSelectedMode)[0]?.id ?? null);
  const [phase, setPhase] = useState<RunPhase>("standby");
  const [currentTime, setCurrentTime] = useState(0);
  const [currentEvent, setCurrentEvent] = useState<TapeEvent | null>(null);
  const [latestRun, setLatestRun] = useState<RunRecord | null>(progress.recentRuns[0] ?? null);
  const [isRunning, setIsRunning] = useState(false);
  const [holdProgress, setHoldProgress] = useState(0);
  const [selectedPreset, setSelectedPreset] = useState<BotPresetName>("Balanced");

  const availableTapes = useMemo(() => listTapeSummaries(mode), [mode]);

  const currentTape = useMemo<Tape | undefined>(() => {
    return selectedTapeId ? getTapeById(selectedTapeId) : listTapes(mode)[0];
  }, [mode, selectedTapeId]);

  const botDecision = useMemo(() => {
    if (!currentEvent) {
      return null;
    }
    return evaluatePresetAgainstEvent(STARTER_BOTS[selectedPreset], currentEvent);
  }, [currentEvent, selectedPreset]);

  useEffect(() => {
    if (!isRunning || !currentTape) {
      return;
    }

    const tick = (now: number) => {
      if (playbackStartRef.current === null) {
        playbackStartRef.current = now;
      }

      const elapsed = now - playbackStartRef.current;
      setCurrentTime(elapsed);

      let next = tapeEngineRef.current.current();
      while (true) {
        const peek = getNextEvent(currentTape, tapeEngineRef.current);
        if (!peek || peek.t > elapsed) {
          break;
        }
        next = tapeEngineRef.current.step();
        if (next) {
          applyEvent(next);
        }
      }

      if (phase !== "afterimage" && phase !== "reset") {
        playbackFrameRef.current = window.requestAnimationFrame(tick);
      }
    };

    playbackFrameRef.current = window.requestAnimationFrame(tick);
    return () => {
      if (playbackFrameRef.current !== null) {
        window.cancelAnimationFrame(playbackFrameRef.current);
      }
    };
  }, [currentTape, isRunning, phase]);

  useEffect(() => {
    progressStoreRef.current.save(progress);
  }, [progress]);

  function selectMode(nextMode: TapeMode): void {
    if (nextMode === "live-preview" && !progress.liveGate.unlocked) {
      return;
    }
    setMode(nextMode);
    const nextTape = listTapes(nextMode)[0] ?? null;
    setSelectedTapeId(nextTape?.id ?? null);
    reset();
    setProgress((current) => ({ ...current, lastSelectedMode: nextMode }));
  }

  function selectPreset(nextPreset: BotPresetName): void {
    setSelectedPreset(nextPreset);
  }

  function selectTape(tapeId: string): void {
    setSelectedTapeId(tapeId);
    reset();
  }

  function startRun(): void {
    if (!currentTape) {
      return;
    }
    tapeEngineRef.current.load(currentTape);
    runEngineRef.current.reset();
    runEngineRef.current.transition("arm", 0, "start run");
    runEngineRef.current.logAction({ type: "start_run", at: 0 });
    setPhase("arm");
    setCurrentTime(0);
    setCurrentEvent(currentTape.events[0] ?? null);
    setLatestRun(null);
    playbackStartRef.current = null;
    setIsRunning(true);
  }

  function step(): void {
    if (!currentTape) {
      return;
    }
    if (phase === "standby") {
      startRun();
      return;
    }
    const event = tapeEngineRef.current.step();
    if (!event) {
      return;
    }
    runEngineRef.current.logAction({ type: "step", at: event.t });
    setCurrentTime(event.t);
    applyEvent(event);
  }

  function startHold(): void {
    const enginePhase = runEngineRef.current.getPhase();
    if (!currentEvent?.window || (enginePhase !== "pressure" && enginePhase !== "run")) {
      return;
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
    }
    runEngineRef.current.transition("commit_hold", currentTime, "hold start");
    runEngineRef.current.logAction({ type: "hold_start", at: currentTime });
    setPhase("commit_hold");
    holdStartRef.current = window.performance.now();

    const tick = (now: number) => {
      if (holdStartRef.current === null) {
        return;
      }
      const elapsed = now - holdStartRef.current;
      const required = currentEvent.window?.holdMs ?? HOLD_FALLBACK_MS;
      const nextProgress = Math.min(1, elapsed / required);
      setHoldProgress(nextProgress);
      if (nextProgress >= 1) {
        finalizeCommit();
        return;
      }
      holdFrameRef.current = window.requestAnimationFrame(tick);
    };

    holdFrameRef.current = window.requestAnimationFrame(tick);
  }

  function cancelHold(): void {
    if (runEngineRef.current.getPhase() !== "commit_hold") {
      return;
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
    }
    holdStartRef.current = null;
    runEngineRef.current.logAction({ type: "hold_cancel", at: currentTime });
    runEngineRef.current.transition("pressure", currentTime, "hold cancel");
    setHoldProgress(0);
    setPhase("pressure");
  }

  function finalizeCommit(): void {
    if (!currentTape || !currentEvent) {
      return;
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
    }
    holdStartRef.current = null;
    runEngineRef.current.markCommit(currentTime);
    runEngineRef.current.transition("resolution", currentTime, "hold complete");
    setPhase("resolution");
    setIsRunning(false);

    const run = runEngineRef.current.finalize(currentTape, currentEvent);
    runEngineRef.current.transition("afterimage", currentTime, "resolved");
    setPhase("afterimage");
    setHoldProgress(0);
    setLatestRun(run);
    setProgress((current) => recordRun(current, run));
  }

  function reset(): void {
    if (playbackFrameRef.current !== null) {
      window.cancelAnimationFrame(playbackFrameRef.current);
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
    }
    holdStartRef.current = null;
    playbackStartRef.current = null;
    tapeEngineRef.current.reset();
    runEngineRef.current.reset();
    setIsRunning(false);
    setHoldProgress(0);
    setCurrentTime(0);
    setCurrentEvent(currentTape?.events[0] ?? null);
    setLatestRun(null);
    setPhase("standby");
  }

  function applyEvent(event: TapeEvent): void {
    setCurrentEvent(event);
    const enginePhase = runEngineRef.current.getPhase();

    if (enginePhase === "arm") {
      runEngineRef.current.transition("run", event.t, "first motion");
      setPhase("run");
    }

    if (event.window && enginePhase !== "commit_hold" && enginePhase !== "afterimage") {
      if (runEngineRef.current.getPhase() !== "pressure") {
        runEngineRef.current.transition("pressure", event.t, "window open");
      }
      setPhase("pressure");
      return;
    }

    if ((event.eventType === "window_close" || event.eventType === "hazard") && runEngineRef.current.getPhase() !== "afterimage") {
      resolveMiss(event);
    }
  }

  function resolveMiss(event: TapeEvent): void {
    const resolutionEvent = event.routeSnapshot && event.window ? event : currentEvent;
    if (!currentTape || !resolutionEvent?.routeSnapshot || !resolutionEvent.window) {
      setIsRunning(false);
      return;
    }
    if (runEngineRef.current.getPhase() === "resolution" || runEngineRef.current.getPhase() === "afterimage") {
      return;
    }
    runEngineRef.current.transition("resolution", event.t, "window closed");
    const run = runEngineRef.current.finalize(currentTape, resolutionEvent);
    runEngineRef.current.transition("afterimage", event.t, "debrief");
    setPhase("afterimage");
    setIsRunning(false);
    setLatestRun(run);
    setProgress((current) => recordRun(current, run));
  }

  return {
    mode,
    phase,
    currentTape,
    currentEvent,
    currentTime,
    isRunning,
    holdProgress,
    latestRun,
    progress,
    selectedPreset,
    botDecision,
    startingBankroll: STARTING_BANKROLL,
    practiceStake: PRACTICE_STAKE,
    availableTapes,
    selectedTapeId,
    selectMode,
    selectPreset,
    selectTape,
    startRun,
    step,
    startHold,
    cancelHold,
    reset,
  };
}

function getNextEvent(tape: Tape, engine: TapeEngine): TapeEvent | null {
  const events = engine.allEvents();
  const current = engine.current();
  if (!current) {
    return events[0] ?? null;
  }
  const index = events.findIndex((item) => item.id === current.id);
  return events[index + 1] ?? null;
}
