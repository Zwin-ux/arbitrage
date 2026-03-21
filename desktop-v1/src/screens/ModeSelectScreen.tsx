import type { PackStatus, TapeMode } from "@domain/types";

interface ModeSelectScreenProps {
  selected: TapeMode;
  availablePacks: PackStatus[];
  selectedPackId: string | null;
  replayUnlocked: boolean;
  shadowReady: boolean;
  onSelectMode: (mode: TapeMode) => void;
  onSelectPack: (packId: string) => void;
}

export function ModeSelectScreen({
  selected,
  availablePacks,
  selectedPackId,
  replayUnlocked,
  shadowReady,
  onSelectMode,
  onSelectPack,
}: ModeSelectScreenProps) {
  return (
    <section aria-label="Practice lane select" className="mode-deck">
      <div className="mode-strip">
        <button type="button" className="mode-button" aria-pressed={selected === "tutorial"} onClick={() => onSelectMode("tutorial")}>
          <span className="mode-button__index">01</span>
          <strong className="mode-button__label">Learn</strong>
          <small className="mode-button__meta">Watch the lane once</small>
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
          <strong className="mode-button__label">Shadow</strong>
          <small className="mode-button__meta">Replay it cleanly</small>
        </button>
        <div className="mode-status">
          <span className="mode-status__index">03</span>
          <strong className="mode-status__label">{shadowReady ? "Auto ready" : "Auto locked"}</strong>
          <small className="mode-status__meta">{shadowReady ? "Arm it from Bot" : "Finish learn and shadow"}</small>
        </div>
      </div>

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
              {pack.completed ? "Clear" : `${pack.clearedCount} of ${pack.totalCount} cleared`}
            </small>
          </button>
        ))}
      </div>
    </section>
  );
}
