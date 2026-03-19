import type { PackMode, TapeMode, TapePack } from "@domain/types";

const PACK_MANIFEST: TapePack[] = [
  {
    id: "pack-tutorial-open",
    mode: "tutorial",
    name: "Open",
    order: 1,
    label: "01",
    tapeIds: ["tutorial-intro-route"],
    unlock: { type: "free" },
  },
  {
    id: "pack-tutorial-timing",
    mode: "tutorial",
    name: "Timing",
    order: 2,
    label: "02",
    tapeIds: ["tutorial-steady-window"],
    unlock: { type: "requires_pack_clear", targetId: "pack-tutorial-open" },
  },
  {
    id: "pack-replay-volatile",
    mode: "replay",
    name: "Volatile",
    order: 3,
    label: "03",
    tapeIds: ["replay-opening-window"],
    unlock: { type: "requires_pack_clear", targetId: "pack-tutorial-timing" },
  },
  {
    id: "pack-replay-pressure",
    mode: "replay",
    name: "Pressure",
    order: 4,
    label: "04",
    tapeIds: ["replay-thin-reversal"],
    unlock: { type: "requires_pack_clear", targetId: "pack-replay-volatile" },
  },
];

export function listPackManifest(mode?: PackMode): TapePack[] {
  return PACK_MANIFEST
    .filter((pack) => !mode || pack.mode === mode)
    .sort((left, right) => left.order - right.order);
}

export function getPackById(packId: string): TapePack | undefined {
  return PACK_MANIFEST.find((pack) => pack.id === packId);
}

export function getPackForTape(tapeId: string): TapePack | undefined {
  return PACK_MANIFEST.find((pack) => pack.tapeIds.includes(tapeId));
}

export function getFirstPackId(mode: TapeMode): string | null {
  if (mode === "live-preview") {
    return null;
  }

  return listPackManifest(mode)[0]?.id ?? null;
}
