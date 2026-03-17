import type { RunPhase } from "@domain/types";

export const RUN_PHASE_ORDER: RunPhase[] = [
  "standby",
  "arm",
  "run",
  "pressure",
  "commit_hold",
  "resolution",
  "afterimage",
  "reset",
];

const TRANSITIONS: Record<RunPhase, RunPhase[]> = {
  standby: ["arm", "reset"],
  arm: ["run", "reset"],
  run: ["pressure", "reset"],
  pressure: ["commit_hold", "resolution", "reset"],
  commit_hold: ["resolution", "reset"],
  resolution: ["afterimage", "reset"],
  afterimage: ["reset"],
  reset: ["standby"],
};

export function canTransition(from: RunPhase, to: RunPhase): boolean {
  return TRANSITIONS[from].includes(to);
}

export function nextPhase(current: RunPhase): RunPhase {
  const index = RUN_PHASE_ORDER.indexOf(current);
  const next = RUN_PHASE_ORDER[index + 1];
  return next ?? "reset";
}
