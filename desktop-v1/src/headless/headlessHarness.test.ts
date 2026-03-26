import { describe, expect, it } from "vitest";

import type { OutcomeGrade, Tape } from "@domain/types";
import { BUNDLED_TAPE_EXPECTATIONS } from "@services/bundledTapeExpectations";
import { listPackManifest } from "@services/packManifest";
import { STARTING_BANKROLL } from "@services/practiceMoney";
import { listTapes } from "@services/datasetLoader";

import { buildHeadlessBotMatrix, runPackSweep, runUnlockCampaign, simulateTapeScenario } from "./headlessHarness";

const bundledTapes: Tape[] = [...listTapes("tutorial"), ...listTapes("replay")];

describe("headless harness", () => {
  it("resolves every bundled tape through ideal, early, late, miss, and off-target paths", () => {
    for (const tape of bundledTapes) {
      const expectation = getExpectation(tape.id);

      expect(gradeFor(tape, "ideal")).toBe(expectation.expectedUserOutcomes.ideal);
      expect(gradeFor(tape, "early")).toBe(expectation.expectedUserOutcomes.early);
      expect(gradeFor(tape, "late")).toBe(expectation.expectedUserOutcomes.late);
      expect(gradeFor(tape, "miss")).toBe(expectation.expectedUserOutcomes.noCommit);
      expect(gradeFor(tape, "off_target")).toBe("off_target");
    }
  });

  it("keeps starter-bot verdicts stable across the bundled tape matrix", () => {
    const matrix = buildHeadlessBotMatrix();

    for (const item of matrix) {
      const expectation = getExpectation(item.tapeId);
      const verdictByPreset = Object.fromEntries(item.verdicts.map((entry) => [entry.preset, entry.verdict]));
      expect(verdictByPreset).toEqual(expectation.expectedBotVerdicts);
    }
  });

  it("completes tutorial and replay pack sweeps without blocked runs", () => {
    for (const mode of ["tutorial", "replay"] as const) {
      const sweep = runPackSweep(mode);
      expect(sweep.runs.length).toBe(listTapes(mode).length);
      expect(sweep.runs.every((run) => run.outcome.grade !== "blocked")).toBe(true);

      const relevantPackIds = new Set(listPackManifest(mode).map((pack) => pack.id));
      const completedRelevantPacks = sweep.progress.packProgress.filter(
        (entry) => relevantPackIds.has(entry.packId) && entry.completed,
      );
      expect(completedRelevantPacks).toHaveLength(listPackManifest(mode).length);
    }
  });

  it("can unlock the live gate headlessly with the shipped content", () => {
    const campaign = runUnlockCampaign();

    expect(campaign.runs).toHaveLength(bundledTapes.length);
    expect(campaign.progress.liveGate.unlocked).toBe(true);
    expect(campaign.progress.tutorialClearedTapeIds).toHaveLength(listTapes("tutorial").length);
    expect(campaign.progress.replayClearedTapeIds).toHaveLength(listTapes("replay").length);
    expect(campaign.progress.practiceBankroll).toBeGreaterThan(STARTING_BANKROLL);
    expect(campaign.progress.clearStreak).toBe(bundledTapes.length);
  });
});

function getExpectation(tapeId: string) {
  const expectation = BUNDLED_TAPE_EXPECTATIONS.find((entry) => entry.tapeId === tapeId);
  expect(expectation, `missing expectation for ${tapeId}`).toBeDefined();
  return expectation!;
}

function gradeFor(tape: Tape, scenario: Parameters<typeof simulateTapeScenario>[1]): OutcomeGrade {
  return simulateTapeScenario(tape, scenario).run.outcome.grade;
}
