import { describe, expect, it } from "vitest";

import type { Tape, TapeEvent } from "@domain/types";
import replayTapeJson from "@tapes/replay/opening-window.json";
import tutorialTapeJson from "@tapes/tutorial/intro-route.json";
import { LocalProgressStore } from "@services/persistenceService";
import { createInitialProgress, recordRun } from "@services/progressService";
import { RunEngine } from "@services/runEngine";

const tutorialTape = tutorialTapeJson as Tape;
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
    const replayRun = createClearRun(replayTape, replayTape.events[2] as TapeEvent);
    const legacySnapshot = recordRun(recordRun(createInitialProgress(), tutorialRun), replayRun);
    const storage = createMemoryStorage({
      "sup-v1-progress": JSON.stringify({
        lastSelectedMode: legacySnapshot.lastSelectedMode,
        recentRuns: legacySnapshot.recentRuns,
      }),
    });
    const store = new LocalProgressStore("sup-v1-progress", storage);
    const loaded = store.load();

    expect(loaded.liveGate.tutorialClears).toBe(1);
    expect(loaded.liveGate.replayClears).toBe(1);
    expect(loaded.liveGate.unlocked).toBe(true);
  });

  it("saves snapshots inside a versioned envelope", () => {
    const storage = createMemoryStorage();
    const store = new LocalProgressStore("sup-v1-progress", storage);
    const snapshot = createInitialProgress();

    store.save(snapshot);

    expect(JSON.parse(storage.getItem("sup-v1-progress") ?? "{}")).toEqual({
      version: 1,
      snapshot,
    });
  });
});

function createClearRun(tape: Tape, event: TapeEvent) {
  const engine = new RunEngine();
  engine.transition("arm", 0, "start");
  engine.transition("run", event.t, "motion");
  engine.transition("pressure", event.t, "window");
  engine.markCommit(event.window!.idealCommitAt);
  return engine.finalize(tape, event);
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
