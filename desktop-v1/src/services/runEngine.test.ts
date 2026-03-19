import { describe, expect, it } from "vitest";

import type { Tape, TapeEvent } from "@domain/types";
import introRouteTape from "@tapes/tutorial/intro-route.json";
import { RunEngine } from "@services/runEngine";

const tape = introRouteTape as Tape;
const event = tape.events[3] as TapeEvent;

describe("run engine", () => {
  it("resolves a clear commit inside the window", () => {
    const engine = new RunEngine();
    engine.transition("arm", 0, "start");
    engine.transition("run", event.t, "motion");
    engine.transition("pressure", event.t, "window");
    engine.markCommit(event.window!.idealCommitAt);

    const result = engine.finalize(tape, event);

    expect(result.outcome.grade).toBe("clear");
    expect(result.outcome.success).toBe(true);
    expect(result.debrief.headline).toBe("CLEAN WIN");
    expect(result.receipt.startingBankroll).toBe(100);
    expect(result.receipt.stake).toBe(25);
    expect(result.receipt.netPnl).toBe(7.74);
    expect(result.receipt.endingBankroll).toBe(107.74);
  });

  it("resolves an early commit before the window", () => {
    const engine = new RunEngine();
    engine.transition("arm", 0, "start");
    engine.transition("run", event.t, "motion");
    engine.transition("pressure", event.t, "window");
    engine.markCommit(event.window!.opensAt - 40);

    const result = engine.finalize(tape, event);

    expect(result.outcome.grade).toBe("early");
    expect(result.outcome.success).toBe(false);
    expect(result.receipt.label).toBe("EARLY BUY");
    expect(result.receipt.netPnl).toBeLessThan(0);
    expect(result.receipt.endingBankroll).toBeLessThan(100);
  });

  it("resolves a late commit after the window closes", () => {
    const engine = new RunEngine();
    engine.transition("arm", 0, "start");
    engine.transition("run", event.t, "motion");
    engine.transition("pressure", event.t, "window");
    engine.markCommit(event.window!.closesAt + 40);

    const result = engine.finalize(tape, event);

    expect(result.outcome.grade).toBe("late");
    expect(result.outcome.success).toBe(false);
    expect(result.receipt.label).toBe("LATE BUY");
    expect(result.receipt.netPnl).toBeLessThan(0);
    expect(result.debrief.recommendation).toBe("Commit earlier");
  });

  it("resolves an explicit miss when no commit is registered", () => {
    const engine = new RunEngine();
    engine.transition("arm", 0, "start");
    engine.transition("run", event.t, "motion");
    engine.transition("pressure", event.t, "window");

    const result = engine.finalize(tape, event);

    expect(result.outcome.grade).toBe("miss");
    expect(result.outcome.success).toBe(false);
    expect(result.outcome.committed).toBe(false);
    expect(result.receipt.label).toBe("NO TRADE");
    expect(result.debrief.recommendation).toBe("No entry");
  });

  it("produces an explicit blocked run instead of dying on invalid tape state", () => {
    const engine = new RunEngine();
    engine.transition("arm", 0, "start");
    engine.transition("run", 1200, "motion");
    engine.transition("pressure", 1480, "window");
    engine.transition("resolution", 1980, "invalid tape");

    const result = engine.finalizeBlocked(tape, 1980, "invalid tape state");

    expect(result.outcome.grade).toBe("blocked");
    expect(result.receipt.label).toBe("NO TRADE");
    expect(result.receipt.netPnl).toBe(0);
    expect(result.debrief.reasons[0]).toContain("without a valid buy window");
  });
});
