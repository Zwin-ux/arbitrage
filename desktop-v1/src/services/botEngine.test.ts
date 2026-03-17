import { describe, expect, it } from "vitest";

import type { Tape, TapeEvent } from "@domain/types";
import { STARTER_BOTS } from "@presets/starterBots";
import introRouteTape from "@tapes/tutorial/intro-route.json";
import { evaluatePresetAgainstEvent } from "@services/botEngine";

const tutorialTape = introRouteTape as Tape;
const event = tutorialTape.events[3] as TapeEvent;

describe("bot engine", () => {
  it("lets the balanced preset commit on the clean tutorial tape", () => {
    const decision = evaluatePresetAgainstEvent(STARTER_BOTS.Balanced, event);

    expect(decision.shouldCommit).toBe(true);
    expect(decision.reason).toContain("commits");
  });

  it("keeps the safe preset waiting on a weaker replay tape", async () => {
    const replay = (await import("@tapes/replay/opening-window.json")).default as Tape;
    const decision = evaluatePresetAgainstEvent(STARTER_BOTS.Safe, replay.events[2] as TapeEvent);

    expect(decision.shouldCommit).toBe(false);
    expect(decision.reason).toContain("waits");
  });
});
