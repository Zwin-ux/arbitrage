import { useEffect, useMemo, useRef, useState } from "react";

import type { BotPresetName, PackStatus, RunPhase, RunRecord, ShellView, Tape, TapeEvent, TapeMode } from "@domain/types";
import { STARTER_BOTS } from "@presets/starterBots";
import { evaluatePresetAgainstEvent } from "@services/botEngine";
import { buildBotComparisonResults } from "@services/botComparisonService";
import { getTapeById, listTapeSummariesForPack, listTapesForPack } from "@services/datasetLoader";
import { LocalProgressStore } from "@services/persistenceService";
import { PRACTICE_STAKE, STARTING_BANKROLL } from "@services/practiceMoney";
import {
  armStarterBot,
  canEnterMode,
  createInitialProgress,
  haltStarterBot,
  listPackStatuses,
  recordRun,
  setSelectedView,
  startStarterBot,
} from "@services/progressService";
import { RunEngine } from "@services/runEngine";
import { TapeEngine } from "@services/tapeEngine";

const HOLD_FALLBACK_MS = 500;
const toPackMode = (mode: TapeMode) => (mode === "replay" ? "replay" : "tutorial");

export function useRehearsalMachine() {
  const progressStoreRef = useRef(new LocalProgressStore());
  const tapeEngineRef = useRef(new TapeEngine());
  const runEngineRef = useRef(new RunEngine());
  const playbackFrameRef = useRef<number | null>(null);
  const holdFrameRef = useRef<number | null>(null);
  const holdStartRef = useRef<number | null>(null);
  const playbackStartRef = useRef<number | null>(null);

  const [progress, setProgress] = useState(() => progressStoreRef.current.load());
  const [mode, setMode] = useState<TapeMode>(progress.lastSelectedMode === "live-preview" ? "tutorial" : progress.lastSelectedMode);
  const [selectedPackId, setSelectedPackId] = useState<string | null>(progress.lastSelectedPackId);
  const [selectedView, setSelectedViewState] = useState<ShellView>(progress.selectedView);
  const [selectedTapeId, setSelectedTapeId] = useState<string | null>(null);
  const [phase, setPhase] = useState<RunPhase>("standby");
  const [currentTime, setCurrentTime] = useState(0);
  const [currentEvent, setCurrentEvent] = useState<TapeEvent | null>(null);
  const [latestRun, setLatestRun] = useState<RunRecord | null>(progress.recentRuns[0] ?? null);
  const [isRunning, setIsRunning] = useState(false);
  const [holdProgress, setHoldProgress] = useState(0);
  const [selectedPreset, setSelectedPreset] = useState<BotPresetName>("Balanced");

  const packStatuses = useMemo<PackStatus[]>(() => {
    return listPackStatuses(progress, toPackMode(mode));
  }, [mode, progress]);

  const selectedPack = useMemo(() => {
    return packStatuses.find((pack) => pack.pack.id === selectedPackId) ?? packStatuses[0] ?? null;
  }, [packStatuses, selectedPackId]);

  const availableTapes = useMemo(() => {
    return selectedPack ? listTapeSummariesForPack(selectedPack.pack.id) : [];
  }, [selectedPack]);

  const currentTape = useMemo<Tape | undefined>(() => {
    const fallbackTape = selectedPack ? listTapesForPack(selectedPack.pack.id)[0] : undefined;
    return selectedTapeId ? getTapeById(selectedTapeId) ?? fallbackTape : fallbackTape;
  }, [selectedPack, selectedTapeId]);

  const botDecision = useMemo(() => {
    if (!currentEvent) {
      return null;
    }
    return evaluatePresetAgainstEvent(STARTER_BOTS[selectedPreset], currentEvent);
  }, [currentEvent, selectedPreset]);

  const practiceBankroll = progress.practiceBankroll;
  const practiceStake = Math.min(PRACTICE_STAKE, Math.max(0, practiceBankroll));
  const replayUnlocked = useMemo(() => canEnterMode(progress, "replay"), [progress]);
  const comparisonResults = useMemo(() => {
    if (!latestRun || !currentTape) {
      return [];
    }
    return buildBotComparisonResults(currentTape, latestRun.receipt.startingBankroll, latestRun.receipt.stake);
  }, [currentTape, latestRun]);

  useEffect(() => {
    const nextPackId = selectedPack?.pack.id ?? null;
    if (nextPackId !== selectedPackId) {
      setSelectedPackId(nextPackId);
    }

    const nextTapeId = availableTapes[0]?.id ?? null;
    if (!selectedTapeId || !availableTapes.some((tape) => tape.id === selectedTapeId)) {
      setSelectedTapeId(nextTapeId);
    }
  }, [availableTapes, mode, selectedPack, selectedPackId, selectedTapeId]);

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

      while (true) {
        const peek = tapeEngineRef.current.peek();
        if (!peek || peek.t > elapsed) {
          break;
        }
        const next = tapeEngineRef.current.step();
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
    if (nextMode === "live-preview" || !canEnterMode(progress, nextMode)) {
      return;
    }

    const nextPack = listPackStatuses(progress, nextMode)[0]?.pack.id ?? null;
    const nextTape = nextPack ? listTapesForPack(nextPack)[0] : null;

    setMode(nextMode);
    setSelectedPackId(nextPack);
    setSelectedTapeId(nextTape?.id ?? null);
    reset(nextTape);
    setProgress((current) => ({
      ...current,
      lastSelectedMode: nextMode,
      lastSelectedPackId: nextPack,
    }));
  }

  function selectPreset(nextPreset: BotPresetName): void {
    setSelectedPreset(nextPreset);
  }

  function selectPack(packId: string): void {
    const pack = packStatuses.find((entry) => entry.pack.id === packId);
    if (!pack || !pack.unlocked) {
      return;
    }

    const nextTape = listTapesForPack(packId)[0] ?? null;
    setSelectedPackId(packId);
    setSelectedTapeId(nextTape?.id ?? null);
    reset(nextTape);
    setProgress((current) => ({
      ...current,
      lastSelectedPackId: packId,
    }));
  }

  function selectTape(tapeId: string): void {
    const nextTape = getTapeById(tapeId) ?? null;
    setSelectedTapeId(tapeId);
    reset(nextTape);
  }

  function startRun(): void {
    if (!currentTape || practiceStake <= 0) {
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

    const run = runEngineRef.current.finalize(currentTape, currentEvent, practiceBankroll, practiceStake);
    runEngineRef.current.transition("afterimage", currentTime, "resolved");
    setPhase("afterimage");
    setHoldProgress(0);
    setLatestRun(run);
    setProgress((current) => recordRun(current, run));
  }

  function reset(nextTape: Tape | null = currentTape ?? null): void {
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
    setCurrentEvent(nextTape?.events[0] ?? null);
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
    if (runEngineRef.current.getPhase() === "resolution" || runEngineRef.current.getPhase() === "afterimage") {
      return;
    }
    if (!currentTape) {
      setIsRunning(false);
      return;
    }

    runEngineRef.current.transition("resolution", event.t, "window closed");
    const run = !resolutionEvent?.routeSnapshot || !resolutionEvent.window
      ? runEngineRef.current.finalizeBlocked(currentTape, event.t, "invalid tape state", practiceBankroll, practiceStake)
      : runEngineRef.current.finalize(currentTape, resolutionEvent, practiceBankroll, practiceStake);
    runEngineRef.current.transition("afterimage", event.t, "debrief");
    setPhase("afterimage");
    setIsRunning(false);
    setLatestRun(run);
    setProgress((current) => recordRun(current, run));
  }

  function resetWorld(): void {
    const fresh = {
      ...createInitialProgress(),
    };
    setProgress(fresh);
    setMode(fresh.lastSelectedMode === "live-preview" ? "tutorial" : fresh.lastSelectedMode);
    setSelectedPackId(fresh.lastSelectedPackId);
    setSelectedViewState(fresh.selectedView);
    setSelectedTapeId(fresh.lastSelectedPackId ? listTapesForPack(fresh.lastSelectedPackId)[0]?.id ?? null : null);
    setLatestRun(null);
    setHoldProgress(0);
    setCurrentTime(0);
    setCurrentEvent(fresh.lastSelectedPackId ? listTapesForPack(fresh.lastSelectedPackId)[0]?.events[0] ?? null : null);
    setPhase("standby");
    setIsRunning(false);
  }

  function selectView(nextView: ShellView): void {
    setSelectedViewState(nextView);
    setProgress((current) => setSelectedView(current, nextView));
  }

  function armBot(): void {
    setSelectedViewState("bot");
    setProgress((current) => armStarterBot(current));
  }

  function startBot(): void {
    setSelectedViewState("live");
    setProgress((current) => startStarterBot(current));
  }

  function haltBot(): void {
    setSelectedViewState("live");
    setProgress((current) => haltStarterBot(current));
  }

  return {
    mode,
    selectedView,
    phase,
    currentTape,
    currentEvent,
    currentTime,
    isRunning,
    holdProgress,
    latestRun,
    progress,
    comparisonResults,
    selectedPreset,
    botDecision,
    startingBankroll: practiceBankroll || STARTING_BANKROLL,
    practiceBankroll,
    bestBankroll: progress.bestBankroll,
    clearStreak: progress.clearStreak,
    practiceStake,
    replayUnlocked,
    packStatuses,
    selectedPack,
    availableTapes,
    selectedPackId,
    selectedTapeId,
    starterBot: progress.starterBot,
    executionPolicy: progress.executionPolicy,
    botRuntime: progress.botRuntime,
    decisionAudit: progress.decisionAudit,
    selectMode,
    selectView,
    selectPack,
    selectPreset,
    selectTape,
    startRun,
    step,
    startHold,
    cancelHold,
    reset,
    resetWorld,
    armBot,
    startBot,
    haltBot,
  };
}
