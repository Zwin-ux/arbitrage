import introRouteTape from "@tapes/tutorial/intro-route.json";
import steadyWindowTape from "@tapes/tutorial/steady-window.json";
import openingWindowTape from "@tapes/replay/opening-window.json";
import thinReversalTape from "@tapes/replay/thin-reversal.json";
import type { PackMode, Tape, TapeMode, TapePack } from "@domain/types";
import { getPackById, getPackForTape, listPackManifest } from "@services/packManifest";

const manifest: Tape[] = [
  introRouteTape as Tape,
  steadyWindowTape as Tape,
  openingWindowTape as Tape,
  thinReversalTape as Tape,
];

export interface TapeSummary {
  id: string;
  name: string;
  mode: TapeMode;
  symbol: string;
  packId: string | null;
}

export interface PackSummary {
  id: string;
  mode: PackMode;
  name: string;
  label: string;
  order: number;
  tapeCount: number;
}

export function listTapes(mode: TapeMode): Tape[] {
  return manifest.filter((item) => item.mode === mode);
}

export function getTapeById(id: string): Tape | undefined {
  return manifest.find((item) => item.id === id);
}

export function listTapeSummaries(mode: TapeMode): TapeSummary[] {
  return listTapes(mode).map((item) => ({
    id: item.id,
    name: item.name,
    mode: item.mode,
    symbol: item.market.symbol,
    packId: getPackForTape(item.id)?.id ?? null,
  }));
}

export function listPacks(mode: PackMode): PackSummary[] {
  return listPackManifest(mode).map((pack) => ({
    id: pack.id,
    mode: pack.mode,
    name: pack.name,
    label: pack.label,
    order: pack.order,
    tapeCount: pack.tapeIds.length,
  }));
}

export function getPack(packId: string): TapePack | undefined {
  return getPackById(packId);
}

export function listTapesForPack(packId: string): Tape[] {
  const pack = getPackById(packId);
  if (!pack) {
    return [];
  }

  return pack.tapeIds
    .map((tapeId) => getTapeById(tapeId))
    .filter((tape): tape is Tape => Boolean(tape));
}

export function listTapeSummariesForPack(packId: string): TapeSummary[] {
  return listTapesForPack(packId).map((item) => ({
    id: item.id,
    name: item.name,
    mode: item.mode,
    symbol: item.market.symbol,
    packId,
  }));
}
