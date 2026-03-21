import type { BotRuntimePhase, ShellView } from "@domain/types";

interface ShellNavProps {
  selectedView: ShellView;
  botPhase: BotRuntimePhase;
  onSelectView: (view: ShellView) => void;
}

const VIEWS: Array<{ id: ShellView; label: string }> = [
  { id: "home", label: "Home" },
  { id: "practice", label: "Practice" },
  { id: "bot", label: "Bot" },
  { id: "live", label: "Live" },
];

export function ShellNav({ selectedView, botPhase, onSelectView }: ShellNavProps) {
  return (
    <nav className="shell-nav" aria-label="Primary navigation">
      <div className="shell-nav__tabs">
        {VIEWS.map((view) => (
          <button
            key={view.id}
            type="button"
            className={`shell-nav__button ${isMuted(view.id, botPhase, selectedView) ? "shell-nav__button--muted" : ""}`}
            aria-pressed={selectedView === view.id}
            onClick={() => onSelectView(view.id)}
          >
            {view.label}
          </button>
        ))}
      </div>
      <div className="shell-nav__status">
        <span className="shell-nav__status-label">Current step</span>
        <strong>{formatPhase(botPhase)}</strong>
      </div>
    </nav>
  );
}

function isMuted(view: ShellView, botPhase: BotRuntimePhase, selectedView: ShellView): boolean {
  if (selectedView === view) {
    return false;
  }

  const earlyPhase = botPhase === "setup" || botPhase === "learn";
  return earlyPhase && (view === "bot" || view === "live");
}

function formatPhase(value: BotRuntimePhase): string {
  switch (value) {
    case "auto_running":
      return "Auto on";
    case "halted":
      return "Halted";
    default:
      return value
        .split("_")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ");
  }
}
