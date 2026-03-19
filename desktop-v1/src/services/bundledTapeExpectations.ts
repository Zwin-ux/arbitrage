import type { BotComparisonResult, BotPresetName, OutcomeGrade } from "@domain/types";

export interface BundledTapeExpectation {
  tapeId: string;
  lesson: string;
  primaryOpportunityEventId: string;
  expectedUserOutcomes: {
    ideal: OutcomeGrade;
    early: OutcomeGrade;
    late: OutcomeGrade;
    noCommit: OutcomeGrade;
  };
  expectedBotVerdicts: Record<BotPresetName, BotComparisonResult["verdict"]>;
}

export const BUNDLED_TAPE_EXPECTATIONS: readonly BundledTapeExpectation[] = [
  {
    tapeId: "tutorial-intro-route",
    lesson: "Punish early aggression on the first clean route.",
    primaryOpportunityEventId: "e4",
    expectedUserOutcomes: {
      ideal: "clear",
      early: "early",
      late: "late",
      noCommit: "miss",
    },
    expectedBotVerdicts: {
      Safe: "clean",
      Balanced: "clean",
      Aggressive: "early",
    },
  },
  {
    tapeId: "tutorial-steady-window",
    lesson: "Teach a forgiving window where every preset can survive if it commits.",
    primaryOpportunityEventId: "s4",
    expectedUserOutcomes: {
      ideal: "clear",
      early: "early",
      late: "late",
      noCommit: "miss",
    },
    expectedBotVerdicts: {
      Safe: "clean",
      Balanced: "clean",
      Aggressive: "clean",
    },
  },
  {
    tapeId: "replay-opening-window",
    lesson: "Reward balanced timing while safer presets stay out and aggressive presets jump early.",
    primaryOpportunityEventId: "r3",
    expectedUserOutcomes: {
      ideal: "clear",
      early: "early",
      late: "late",
      noCommit: "miss",
    },
    expectedBotVerdicts: {
      Safe: "wait",
      Balanced: "clean",
      Aggressive: "early",
    },
  },
  {
    tapeId: "replay-thin-reversal",
    lesson: "Teach a no-trade replay where all presets should stay out.",
    primaryOpportunityEventId: "tr3",
    expectedUserOutcomes: {
      ideal: "clear",
      early: "early",
      late: "late",
      noCommit: "miss",
    },
    expectedBotVerdicts: {
      Safe: "wait",
      Balanced: "wait",
      Aggressive: "wait",
    },
  },
] as const;

export function getBundledTapeExpectation(tapeId: string): BundledTapeExpectation | undefined {
  return BUNDLED_TAPE_EXPECTATIONS.find((expectation) => expectation.tapeId === tapeId);
}
