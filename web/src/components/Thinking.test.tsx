// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ThinkingPanel } from "./Thinking";
import {
  TRANSPARENCY_NOTE,
  applyThinking,
  blocksFromHistory,
  durationLabel,
  sourceLabel,
} from "../lib/thinking";
import type { ThinkBlock } from "../lib/thinking";
import type { Step } from "../lib/api";

beforeEach(() => {
  vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const start = {
  id: "think-1",
  phase: "start",
  context: "Exact search found nothing. Deciding what to check next.",
  source: "llm",
  model: "qwen2.5:3b",
  text: "",
};

describe("applyThinking", () => {
  it("folds start, deltas and end into one block", () => {
    let blocks: ThinkBlock[] = [];
    blocks = applyThinking(blocks, start);
    blocks = applyThinking(blocks, {
      id: "think-1",
      phase: "delta",
      text: "The batch has",
    });
    blocks = applyThinking(blocks, {
      id: "think-1",
      phase: "delta",
      text: "The batch has a look-alike 8.",
    });
    expect(blocks).toHaveLength(1);
    expect(blocks[0].text).toBe("The batch has a look-alike 8.");
    expect(blocks[0].done).toBe(false);
    blocks = applyThinking(blocks, {
      id: "think-1",
      phase: "end",
      source: "llm",
      text: "Search look-alike variants.",
      action: "search_variants",
      ms: 1840,
    });
    expect(blocks[0]).toMatchObject({
      done: true,
      action: "search_variants",
      ms: 1840,
      model: "qwen2.5:3b",
      text: "Search look-alike variants.",
    });
    // A late delta never reopens a finished block.
    const after = applyThinking(blocks, {
      id: "think-1",
      phase: "delta",
      text: "late",
    });
    expect(after).toBe(blocks);
  });
  it("creates a block when the start frame was dropped and ignores junk", () => {
    const blocks = applyThinking([], {
      id: "think-4",
      phase: "end",
      source: "rules",
      text: "Rule thought.",
      action: "verify",
      ms: 0,
    });
    expect(blocks[0]).toMatchObject({ id: "think-4", done: true });
    expect(applyThinking(blocks, { phase: "delta" })).toBe(blocks);
  });
});

describe("labels", () => {
  it("names the source and formats the duration", () => {
    expect(sourceLabel({ source: "llm", model: "qwen2.5:3b" })).toBe(
      "qwen2.5:3b",
    );
    expect(sourceLabel({ source: "rules" })).toBe("Rule-based");
    expect(sourceLabel({ source: "rules(fallback)" })).toBe(
      "Local model unavailable, used the rules",
    );
    expect(durationLabel(1840)).toBe("Thought for 1.8 s");
    expect(durationLabel(20)).toBe("Thought for under 0.1 s");
  });
});

describe("ThinkingPanel", () => {
  it("streams text live, then collapses to a summary with the action chip", () => {
    let blocks = applyThinking([], start);
    const view = render(<ThinkingPanel blocks={blocks} live />);
    expect(screen.getByText("Thinking")).toBeTruthy();
    expect(screen.getByText(start.context)).toBeTruthy();
    blocks = applyThinking(blocks, {
      id: "think-1",
      phase: "delta",
      text: "Checking look-alike",
    });
    view.rerender(<ThinkingPanel blocks={blocks} live />);
    expect(screen.getByText("Checking look-alike").className).toContain(
      "streaming",
    );
    blocks = applyThinking(blocks, {
      id: "think-1",
      phase: "delta",
      text: "Checking look-alike characters in position 3",
    });
    view.rerender(<ThinkingPanel blocks={blocks} live />);
    expect(
      screen.getByText("Checking look-alike characters in position 3"),
    ).toBeTruthy();
    blocks = applyThinking(blocks, {
      id: "think-1",
      phase: "end",
      text: "Search look-alike variants.",
      action: "search_variants",
      ms: 1840,
    });
    view.rerender(<ThinkingPanel blocks={blocks} live />);
    const head = screen.getByRole("button", { name: /Thought for 1.8 s/ });
    expect(head.getAttribute("aria-expanded")).toBe("false");
    expect(head.textContent).toContain("qwen2.5:3b");
    expect(screen.getByText("search variants").className).toContain(
      "think-chip",
    );
    expect(screen.queryByText("Thinking")).toBeNull();
    fireEvent.click(head);
    expect(head.getAttribute("aria-expanded")).toBe("true");
    expect(screen.getByText("Search look-alike variants.")).toBeTruthy();
    expect(screen.getByText(TRANSPARENCY_NOTE)).toBeTruthy();
    expect(
      screen.getByText(/Finished thinking/).getAttribute("aria-live"),
    ).toBe("polite");
  });
  it("rebuilds finished blocks from history after a reload", () => {
    const steps: Step[] = [
      {
        step: 1,
        action: "read_pack",
        source: "rules",
        summary: "Read.",
        ms: 3,
      },
      {
        step: 2,
        action: "search_variants",
        source: "rules(fallback)",
        summary: "Exact search found nothing.",
        ms: 2100,
        thought: "Try look-alike variants of the batch.",
      },
    ];
    const blocks = blocksFromHistory(steps);
    expect(blocks).toHaveLength(1);
    render(<ThinkingPanel blocks={blocks} />);
    const head = screen.getByRole("button", { name: /Recorded thought/ });
    expect(head.textContent).toContain(
      "Local model unavailable, used the rules",
    );
    fireEvent.click(head);
    expect(
      screen.getByText("Try look-alike variants of the batch."),
    ).toBeTruthy();
  });
  it("shows the withheld note for a redacted block", () => {
    const blocks = applyThinking(applyThinking([], start), {
      id: "think-1",
      phase: "end",
      redacted: true,
      text: "The model's wording was withheld.",
      action: "ask_user",
      ms: 900,
    });
    render(<ThinkingPanel blocks={blocks} />);
    fireEvent.click(screen.getByRole("button", { name: /Thought for 0.9 s/ }));
    expect(
      screen.getByText(/withheld by the safety wording rules/),
    ).toBeTruthy();
  });
  it("shows a working row while live with no block streaming", () => {
    render(<ThinkingPanel blocks={[]} live idleLabel="Reading the pack" />);
    expect(screen.getByText("Reading the pack").className).toContain(
      "think-shimmer",
    );
  });
});
