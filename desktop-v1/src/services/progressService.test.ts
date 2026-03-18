import { describe, expect, it } from "vitest";

import type { Tape, TapeEvent } from "@domain/types";
import replayTapeJson from "@tapes/replay/opening-window.json";
import tutorialTapeJson from "@tapes/tutorial/intro-route.json";
import { createInitialProgress, recordRun } from "@services/progressService";
import { RunEngine } from "@services/runEngine";

const tutorialTape = tutorialTapeJson as Tape;
const replayTape = replayTapeJson as Tape;

describe("progress service", () => {
  it("keeps live locked when only one tutorial tape is farmed", () => {
    const tutorialRun = createClearRun(tutorialTape, tutorialTape.events[3] as TapeEvent);
    const first = recordRun(createInitialProgress(), tutorialRun);
    const second = recordRun(first, createClearRun(tutorialTape, tutorialTape.events[3] as TapeEvent, first.practiceBankroll));

    expect(second.liveGate.successfulRuns).toBe(2);
    expect(second.liveGate.tutorialClears).toBe(1);
    expect(second.liveGate.replayClears).toBe(0);
    expect(second.practiceBankroll).toBe(115.48);
    expect(second.bestBankroll).toBe(115.48);
    expect(second.clearStreak).toBe(2);
    expect(second.liveGate.unlocked).toBe(false);
  });

  it("unlocks live only after one tutorial clear and one replay clear with consistent timing", () => {
    const tutorialRun = createClearRun(tutorialTape, tutorialTape.events[3] as TapeEvent);
    const first = recordRun(createInitialProgress(), tutorialRun);
    const replayRun = createClearRun(replayTape, replayTape.events[2] as TapeEvent, first.practiceBankroll);

    const progressed = recordRun(first, replayRun);

    expect(progressed.liveGate.tutorialClears).toBe(1);
    expect(progressed.liveGate.replayClears).toBe(1);
    expect(progressed.liveGate.consistencyScore).toBe(100);
    expect(progressed.practiceBankroll).toBe(115.48);
    expect(progressed.bestBankroll).toBe(115.48);
    expect(progressed.clearStreak).toBe(2);
    expect(progressed.liveGate.unlocked).toBe(true);
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
