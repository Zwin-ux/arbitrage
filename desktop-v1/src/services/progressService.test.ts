import { describe, expect, it } from "vitest";

import type { Tape, TapeEvent } from "@domain/types";
import replayTapeJson from "@tapes/replay/opening-window.json";
import tutorialTapeJson from "@tapes/tutorial/intro-route.json";
import steadyWindowTapeJson from "@tapes/tutorial/steady-window.json";
import { canEnterMode, createInitialProgress, listPackStatuses, recordRun } from "@services/progressService";
import { RunEngine } from "@services/runEngine";

const tutorialTape = tutorialTapeJson as Tape;
const steadyWindowTape = steadyWindowTapeJson as Tape;
const replayTape = replayTapeJson as Tape;

describe("progress service", () => {
  it("keeps replay packs locked until both tutorial packs are cleared", () => {
    const tutorialRun = createClearRun(tutorialTape, tutorialTape.events[3] as TapeEvent);
    const first = recordRun(createInitialProgress(), tutorialRun);
    const second = recordRun(first, createClearRun(tutorialTape, tutorialTape.events[3] as TapeEvent, first.practiceBankroll));
    const tutorialPacks = listPackStatuses(second, "tutorial");
    const replayPacks = listPackStatuses(second, "replay");

    expect(second.liveGate.successfulRuns).toBe(2);
    expect(second.liveGate.tutorialClears).toBe(1);
    expect(second.liveGate.replayClears).toBe(0);
    expect(second.practiceBankroll).toBe(115.48);
    expect(second.bestBankroll).toBe(115.48);
    expect(second.clearStreak).toBe(2);
    expect(tutorialPacks[0]?.completed).toBe(true);
    expect(tutorialPacks[1]?.unlocked).toBe(true);
    expect(replayPacks[0]?.unlocked).toBe(false);
    expect(canEnterMode(second, "replay")).toBe(false);
    expect(second.liveGate.unlocked).toBe(false);
  });

  it("unlocks replay after the tutorial packs are cleared and tracks pack progress", () => {
    const tutorialRun = createClearRun(tutorialTape, tutorialTape.events[3] as TapeEvent);
    const first = recordRun(createInitialProgress(), tutorialRun);
    const second = recordRun(first, createClearRun(steadyWindowTape, steadyWindowTape.events[3] as TapeEvent, first.practiceBankroll));
    const replayRun = createClearRun(replayTape, replayTape.events[2] as TapeEvent, second.practiceBankroll);

    const progressed = recordRun(second, replayRun);
    const replayPacks = listPackStatuses(progressed, "replay");

    expect(progressed.liveGate.tutorialClears).toBe(2);
    expect(progressed.liveGate.replayClears).toBe(1);
    expect(progressed.liveGate.consistencyScore).toBe(100);
    expect(progressed.practiceBankroll).toBe(123.22);
    expect(progressed.bestBankroll).toBe(123.22);
    expect(progressed.clearStreak).toBe(3);
    expect(replayPacks[0]?.completed).toBe(true);
    expect(replayPacks[1]?.unlocked).toBe(true);
    expect(canEnterMode(progressed, "replay")).toBe(true);
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
