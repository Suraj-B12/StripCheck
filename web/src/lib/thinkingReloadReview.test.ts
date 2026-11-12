import { describe, expect, it } from "vitest";
import { blocksFromHistory, durationLabel, sourceLabel } from "./thinking";

// Reviewer (frontend UX lens): after a reload, an LLM decision is rebuilt from the
// history step, which (core/investigator.py _log) has no `model` and whose `ms` is the
// tool time or 0, not the decision time. FAILS on the current code.
describe("blocksFromHistory for an LLM ask_user step", () => {
  it("does not claim the model thought for under 0.1 s, and keeps the model name", () => {
    const [block] = blocksFromHistory([
      {
        step: 5,
        action: "ask_user",
        source: "llm",
        summary: "A printed detail needs your confirmation.",
        ms: 0,
        thought: "The closest listed batch differs only by look-alike characters.",
      },
    ]);
    expect(durationLabel(block.ms)).not.toBe("Thought for under 0.1 s");
    expect(sourceLabel(block)).not.toBe("Local model");
  });
});
