import type { TapeMode } from "@domain/types";
import { createInitialProgress } from "@services/progressService";

export interface AppState {
  mode: TapeMode;
  selectedTapeId: string | null;
  activeRunId: string | null;
  progress: ReturnType<typeof createInitialProgress>;
}

export function createInitialAppState(): AppState {
  return {
    mode: "tutorial",
    selectedTapeId: null,
    activeRunId: null,
    progress: createInitialProgress(),
  };
}
