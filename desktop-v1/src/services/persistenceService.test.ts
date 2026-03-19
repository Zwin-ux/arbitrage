import { describe, expect, it } from "vitest";

import type { Tape, TapeEvent } from "@domain/types";
import replayTapeJson from "@tapes/replay/opening-window.json";
import tutorialTapeJson from "@tapes/tutorial/intro-route.json";
import steadyWindowTapeJson from "@tapes/tutorial/steady-window.json";
import { LocalProgressStore } from "@services/persistenceService";
import { createInitialProgress, recordRun } from "@services/progressService";
import { RunEngine } from "@services/runEngine";

const tutorialTape = tutorialTapeJson as Tape;
const steadyWindowTape = steadyWindowTapeJson as Tape;
const replayTape = replayTapeJson as Tape;

describe("local progress store", () => {
  it("falls back cleanly when persisted JSON is corrupt", () => {
    const storage = createMemoryStorage({
      "sup-v1-progress": "{bad json",
    });
    const store = new LocalProgressStore("sup-v1-progress", storage);

    expect(store.load()).toEqual(createInitialProgress());
  });

  it("migrates legacy unversioned progress into the current live-gate shape", () => {
    const tutorialRun = createClearRun(tutorialTape, tutorialTape.events[3] as TapeEvent);
    const first = recordRun(createInitialProgress(), tutorialRun);
    const second = recordRun(first, createClearRun(steadyWindowTape, steadyWindowTape.events[3] as TapeEvent, first.practiceBankroll));
    const replayRun = createClearRun(replayTape, replayTape.events[2] as TapeEvent, second.practiceBankroll);
    const legacySnapshot = recordRun(second, replayRun);
    const storage = createMemoryStorage({
      "sup-v1-progress": JSON.stringify({
        lastSelectedMode: legacySnapshot.lastSelectedMode,
        recentRuns: legacySnapshot.recentRuns,
      }),
    });
    const store = new LocalProgressStore("sup-v1-progress", storage);
    const loaded = store.load();

    expect(loaded.liveGate.tutorialClears).toBe(2);
    expect(loaded.liveGate.replayClears).toBe(1);
    expect(loaded.liveGate.unlocked).toBe(true);
    expect(loaded.practiceBankroll).toBe(123.22);
    expect(loaded.bestBankroll).toBe(123.22);
    expect(loaded.clearStreak).toBe(3);
    expect(loaded.lastSelectedPackId).toBe("pack-tutorial-open");
    expect(loaded.packProgress).toHaveLength(4);
  });

  it("saves snapshots inside a versioned envelope", () => {
    const storage = createMemoryStorage();
    const store = new LocalProgressStore("sup-v1-progress", storage);
    const snapshot = createInitialProgress();

    store.save(snapshot);

    expect(JSON.parse(storage.getItem("sup-v1-progress") ?? "{}")).toEqual({
      version: 2,
      snapshot,
    });
  });
});

function createClearRun(tape: Tape, event: TapeEvent, startingBankroll = 100) {
  const engine = new RunEngine();
  engine.transition("arm", 0, "start");
  engine.transition("run", event.t, "motion");
  engine.transition("pressure", event.t, "window");
  engine.markCommit(event.window!.idealCommitAt);
  return engine.finalize(tape, event, startingBankroll);
}

function createMemoryStorage(seed: Record<string, string> = {}) {
  const map = new Map(Object.entries(seed));
  return {
    getItem(key: string) {
      return map.get(key) ?? null;
    },
    setItem(key: string, value: string) {
      map.set(key, value);
    },
  };
}
