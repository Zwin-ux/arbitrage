import type { PackStatus, TapeMode } from "@domain/types";

interface ModeSelectScreenProps {
  selected: TapeMode;
  availablePacks: PackStatus[];
  selectedPackId: string | null;
  replayUnlocked: boolean;
  liveUnlocked: boolean;
  onSelectMode: (mode: TapeMode) => void;
  onSelectPack: (packId: string) => void;
}

export function ModeSelectScreen({
  selected,
  availablePacks,
  selectedPackId,
  replayUnlocked,
  liveUnlocked,
  onSelectMode,
  onSelectPack,
}: ModeSelectScreenProps) {
  return (
    <section aria-label="Mode select" className="mode-deck">
      <div className="mode-strip">
        <button type="button" className="mode-button" aria-pressed={selected === "tutorial"} onClick={() => onSelectMode("tutorial")}>
          <span className="mode-button__index">01</span>
          <strong className="mode-button__label">Tutorial</strong>
        </button>
        <button
          type="button"
          className="mode-button"
          aria-pressed={selected === "replay"}
          aria-disabled={!replayUnlocked}
          disabled={!replayUnlocked}
          onClick={() => onSelectMode("replay")}
        >
          <span className="mode-button__index">02</span>
          <strong className="mode-button__label">Replay</strong>
        </button>
        <button
          type="button"
          className="mode-button"
          aria-pressed={selected === "live-preview"}
          aria-disabled={!liveUnlocked}
          disabled={!liveUnlocked}
          onClick={() => onSelectMode("live-preview")}
        >
          <span className="mode-button__index">03</span>
          <strong className="mode-button__label">{liveUnlocked ? "Live Books" : "Live Locked"}</strong>
        </button>
      </div>

      {selected !== "live-preview" ? (
        <div className="pack-strip" aria-label="Pack select">
          {availablePacks.map((pack) => (
            <button
              key={pack.pack.id}
              type="button"
              className="pack-button"
              aria-pressed={selectedPackId === pack.pack.id}
              aria-disabled={!pack.unlocked}
              disabled={!pack.unlocked}
              onClick={() => onSelectPack(pack.pack.id)}
            >
              <span className="pack-button__index">{pack.pack.label}</span>
              <strong className="pack-button__label">{pack.pack.name}</strong>
              <small className="pack-button__meta">
                {pack.completed ? "Clear" : `${pack.clearedCount}/${pack.totalCount}`}
              </small>
            </button>
          ))}
        </div>
      ) : null}
    </section>
  );
}
