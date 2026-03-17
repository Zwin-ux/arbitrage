import type { ProgressSnapshot } from "@domain/types";
import { createInitialProgress } from "@services/progressService";

export interface ProgressStore {
  load(): ProgressSnapshot;
  save(snapshot: ProgressSnapshot): void;
}

export class LocalProgressStore implements ProgressStore {
  constructor(private readonly key = "sup-v1-progress") {}

  load(): ProgressSnapshot {
    if (typeof localStorage === "undefined") {
      return createInitialProgress();
    }
    const raw = localStorage.getItem(this.key);
    return raw ? (JSON.parse(raw) as ProgressSnapshot) : createInitialProgress();
  }

  save(snapshot: ProgressSnapshot): void {
    if (typeof localStorage === "undefined") {
      return;
    }
    localStorage.setItem(this.key, JSON.stringify(snapshot));
  }
}
