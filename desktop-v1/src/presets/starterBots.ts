import type { BotPreset, BotPresetName, OpportunityWindow, RouteSnapshot } from "@domain/types";

export const STARTER_BOTS: Record<BotPresetName, BotPreset> = {
  Safe: {
    name: "Safe",
    commitThresholdBps: 220,
    patienceWindowMs: 380,
    sensitivity: 0.85,
    maxActionRate: 1,
    label: "waits for a cleaner window and commits late less often",
  },
  Balanced: {
    name: "Balanced",
    commitThresholdBps: 180,
    patienceWindowMs: 260,
    sensitivity: 1,
    maxActionRate: 2,
    label: "baseline preset with moderate confirmation and timing",
  },
  Aggressive: {
    name: "Aggressive",
    commitThresholdBps: 120,
    patienceWindowMs: 140,
    sensitivity: 1.2,
    maxActionRate: 3,
    label: "acts earlier and accepts more variance",
  },
};

export function shouldPresetCommit(
  preset: BotPreset,
  routeSnapshot: RouteSnapshot,
  window: OpportunityWindow,
  nowMs: number,
): boolean {
  const hasEdge = routeSnapshot.netEdgeBps >= preset.commitThresholdBps;
  const insideWindow = nowMs >= window.opensAt && nowMs <= window.closesAt;
  const withinPatience = Math.abs(window.idealCommitAt - nowMs) <= preset.patienceWindowMs;
  return hasEdge && insideWindow && withinPatience;
}
