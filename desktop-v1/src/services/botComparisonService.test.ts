import { describe, expect, it } from "vitest";

import type { Tape } from "@domain/types";
import { BUNDLED_TAPE_EXPECTATIONS } from "@services/bundledTapeExpectations";
import { buildBotComparisonResults, findPrimaryOpportunityEvent } from "@services/botComparisonService";
import openingWindowTapeJson from "@tapes/replay/opening-window.json";
import thinReversalTapeJson from "@tapes/replay/thin-reversal.json";
import introRouteTapeJson from "@tapes/tutorial/intro-route.json";
import steadyWindowTapeJson from "@tapes/tutorial/steady-window.json";

const bundledTapes: Tape[] = [
  introRouteTapeJson as Tape,
  steadyWindowTapeJson as Tape,
  openingWindowTapeJson as Tape,
  thinReversalTapeJson as Tape,
];

describe("bot comparison service", () => {
  it("locks primary opportunity selection to the bundled tape matrix", () => {
    for (const tape of bundledTapes) {
      const expectation = BUNDLED_TAPE_EXPECTATIONS.find((entry) => entry.tapeId === tape.id);
      expect(expectation, `missing expectation for ${tape.id}`).toBeDefined();

      const event = findPrimaryOpportunityEvent(tape);

      expect(event?.id).toBe(expectation?.primaryOpportunityEventId);
    }
  });

  it("matches the expected preset verdicts for every bundled tape", () => {
    for (const tape of bundledTapes) {
      const expectation = BUNDLED_TAPE_EXPECTATIONS.find((entry) => entry.tapeId === tape.id);
      expect(expectation, `missing expectation for ${tape.id}`).toBeDefined();

      const verdicts = Object.fromEntries(
        buildBotComparisonResults(tape, 100, 25).map((result) => [result.preset, result.verdict]),
      );

      expect(verdicts).toEqual(expectation?.expectedBotVerdicts);
    }
  });
});
