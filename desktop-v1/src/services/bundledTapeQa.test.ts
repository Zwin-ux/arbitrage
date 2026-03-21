import { describe, expect, it } from "vitest";

import type { OutcomeGrade, Tape, TapeEvent } from "@domain/types";
import { BUNDLED_TAPE_EXPECTATIONS } from "@services/bundledTapeExpectations";
import { computeNetEdgeBps } from "@services/routeEvaluator";
import { RunEngine } from "@services/runEngine";
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

describe("bundled tape qa", () => {
  it("keeps one primary route snapshot per shipped tape and consistent net-edge math", () => {
    for (const tape of bundledTapes) {
      const expectation = getExpectation(tape.id);
      const primaryEvents = tape.events.filter(
        (event) => event.eventType === "route_snapshot" && event.window && event.routeSnapshot,
      );

      expect(primaryEvents, `${tape.id} route snapshot count`).toHaveLength(1);
      expect(primaryEvents[0]?.id).toBe(expectation.primaryOpportunityEventId);

      const snapshot = primaryEvents[0]?.routeSnapshot;
      expect(snapshot).toBeDefined();
      expect(snapshot?.netEdgeBps).toBe(computeNetEdgeBps(snapshot!));
    }
  });

  it("resolves ideal, early, late, and no-commit outcomes exactly as expected", () => {
    for (const tape of bundledTapes) {
      const expectation = getExpectation(tape.id);
      const event = getPrimaryEvent(tape, expectation.primaryOpportunityEventId);

      expect(runGradeForCommit(tape, event, event.window!.idealCommitAt)).toBe(expectation.expectedUserOutcomes.ideal);
      expect(runGradeForCommit(tape, event, event.window!.opensAt - 1)).toBe(expectation.expectedUserOutcomes.early);
      expect(runGradeForCommit(tape, event, event.window!.closesAt + 1)).toBe(expectation.expectedUserOutcomes.late);
      expect(runGradeForCommit(tape, event, null)).toBe(expectation.expectedUserOutcomes.noCommit);
    }
  });
});

function getExpectation(tapeId: string) {
  const expectation = BUNDLED_TAPE_EXPECTATIONS.find((entry) => entry.tapeId === tapeId);
  expect(expectation, `missing expectation for ${tapeId}`).toBeDefined();
  return expectation!;
}

function getPrimaryEvent(tape: Tape, eventId: string): TapeEvent {
  const event = tape.events.find((entry) => entry.id === eventId);
  expect(event, `missing primary event ${eventId}`).toBeDefined();
  expect(event?.window).toBeDefined();
  expect(event?.routeSnapshot).toBeDefined();
  return event as TapeEvent;
}

function runGradeForCommit(tape: Tape, event: TapeEvent, commitAt: number | null): OutcomeGrade {
  const engine = new RunEngine();
  engine.transition("arm", 0, "start");
  engine.transition("run", event.t, "motion");
  engine.transition("pressure", event.t, "window");

  if (commitAt !== null) {
    engine.markCommit(commitAt);
  }

  return engine.finalize(tape, event).outcome.grade;
}
