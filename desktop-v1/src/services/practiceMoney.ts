import type { PracticeMoneyReceipt, RouteSnapshot, RunOutcome } from "@domain/types";
import {
  createPracticeMoneyOutcome,
  PRACTICE_STAKE,
  STARTING_BANKROLL,
} from "@shared/practiceMoneyProfiles";

export { PRACTICE_STAKE, STARTING_BANKROLL } from "@shared/practiceMoneyProfiles";

export function createPracticeMoneyReceipt(
  _snapshot: RouteSnapshot,
  outcome: RunOutcome,
  startingBankroll = STARTING_BANKROLL,
  stake = PRACTICE_STAKE,
): PracticeMoneyReceipt {
  const profileId = !outcome.committed || outcome.grade === "miss" || outcome.grade === "blocked"
    ? "no_trade"
    : outcome.grade;

  return createPracticeMoneyOutcome(profileId, startingBankroll, stake);
}
