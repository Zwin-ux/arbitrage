import type { Tape, TapeEvent } from "@domain/types";

export class TapeEngine {
  private tape: Tape | null = null;
  private cursor = 0;

  load(tape: Tape): void {
    this.tape = tape;
    this.cursor = 0;
  }

  reset(): void {
    this.cursor = 0;
  }

  step(): TapeEvent | null {
    if (!this.tape) {
      return null;
    }
    const event = this.tape.events[this.cursor] ?? null;
    if (event) {
      this.cursor += 1;
    }
    return event;
  }

  peek(): TapeEvent | null {
    if (!this.tape) {
      return null;
    }
    return this.tape.events[this.cursor] ?? null;
  }

  current(): TapeEvent | null {
    if (!this.tape) {
      return null;
    }
    return this.tape.events[Math.max(0, this.cursor - 1)] ?? this.tape.events[0] ?? null;
  }

  allEvents(): TapeEvent[] {
    return this.tape?.events ?? [];
  }
}
