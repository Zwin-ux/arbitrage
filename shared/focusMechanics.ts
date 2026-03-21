export interface FocusWindow {
  opensAt: number;
  closesAt: number;
  idealCommitAt: number;
  holdMs: number;
}

export interface FocusBand {
  start: number;
  end: number;
  center: number;
  width: number;
}

export interface FocusAnalysis {
  band: FocusBand | null;
  score: number;
  hot: boolean;
  inside: boolean;
}

export type FocusGrade = "clear" | "early" | "late" | "off_target" | "miss" | "blocked";

export const FOCUS_DEFAULT_RATIO = 0.45;
export const FOCUS_HOT_THRESHOLD = 0.72;
export const FOCUS_PASS_THRESHOLD = 0.58;
export const FOCUS_NUDGE_STEP = 0.05;

const AXIS_START = 0.08;
const AXIS_SPAN = 0.84;
const AXIS_DRIFT = 0.44;
const MIN_FOCUS_RADIUS = 0.06;

export function clampRatio(value: number): number {
  return Math.max(0, Math.min(1, value));
}

export function getLaneProgress(currentTime: number, duration: number): number {
  if (duration <= 0) {
    return 0;
  }
  return clampRatio(currentTime / duration);
}

export function getEventScreenRatio(eventTime: number, duration: number, currentTime: number): number {
  const progress = getLaneProgress(currentTime, duration);
  const raw = AXIS_START + (eventTime / duration) * AXIS_SPAN - progress * AXIS_DRIFT;
  return clampRatio(raw);
}

export function getWindowBand(window: FocusWindow | null | undefined, duration: number, currentTime: number): FocusBand | null {
  if (!window || duration <= 0) {
    return null;
  }

  const start = getEventScreenRatio(window.opensAt, duration, currentTime);
  const end = getEventScreenRatio(window.closesAt, duration, currentTime);
  const left = Math.min(start, end);
  const right = Math.max(start, end);
  const width = Math.max(right - left, MIN_FOCUS_RADIUS * 2);

  return {
    start: left,
    end: right,
    center: clampRatio(left + width / 2),
    width,
  };
}

export function analyzeFocus(
  focusRatio: number,
  window: FocusWindow | null | undefined,
  duration: number,
  currentTime: number,
): FocusAnalysis {
  const band = getWindowBand(window, duration, currentTime);
  if (!band) {
    return {
      band: null,
      score: 0,
      hot: false,
      inside: false,
    };
  }

  const focus = clampRatio(focusRatio);
  const radius = Math.max(band.width / 2, MIN_FOCUS_RADIUS);
  const distance = Math.abs(focus - band.center);
  const score = clampRatio(1 - distance / radius);

  return {
    band,
    score,
    hot: score >= FOCUS_HOT_THRESHOLD,
    inside: focus >= band.start && focus <= band.end,
  };
}

export function resolveCommitGrade(
  window: FocusWindow | null | undefined,
  commitTimestamp: number | null,
  focusScore: number,
): FocusGrade {
  if (!window) {
    return "blocked";
  }
  if (commitTimestamp === null) {
    return "miss";
  }
  if (commitTimestamp < window.opensAt) {
    return "early";
  }
  if (commitTimestamp > window.closesAt) {
    return "late";
  }
  if (focusScore < FOCUS_PASS_THRESHOLD) {
    return "off_target";
  }
  return "clear";
}
