// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { StepTimeline } from "./Shared";
import { ThinkingPanel } from "./Thinking";
import { applyThinking, blocksFromHistory } from "../lib/thinking";
import type { Step } from "../lib/api";

afterEach(cleanup);
vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));

const step = (o: Record<string, unknown>) =>
  ({ step: 1, action: "search_exact", source: "rules", summary: "s", ms: 1, ...o }) as Step;

describe("agent badges", () => {
  it("renders a badge per agent on steps", () => {
    const names = ["perception", "investigator", "verifier", "supervisor"];
    const { container } = render(
      <StepTimeline steps={names.map((agent) => step({ agent }))} />,
    );
    for (const n of names)
      expect(container.querySelector(`[data-agent="${n}"]`)).toBeTruthy();
    expect(screen.getByText("Supervisor")).toBeTruthy();
  });
  it("shows the agent on thinking blocks from live events", () => {
    const blocks = applyThinking([], {
      id: "t1",
      phase: "end",
      agent: "investigator",
      source: "llm",
      text: "x",
      action: "search_exact",
      ms: 500,
    });
    const { container } = render(<ThinkingPanel blocks={blocks} />);
    expect(container.querySelector('[data-agent="investigator"]')).toBeTruthy();
  });
  it("keeps legacy steps and thoughts without badges", () => {
    const { container } = render(
      <StepTimeline steps={[step({ action: "search_exact" })]} />,
    );
    expect(container.querySelector(".agent-badge")).toBeNull();
    expect(screen.getByText("search exact")).toBeTruthy();
    const blocks = blocksFromHistory([step({ thought: "t" })]);
    expect(blocks[0].agent).toBeUndefined();
    const panel = render(<ThinkingPanel blocks={blocks} />);
    expect(panel.container.querySelector(".agent-badge")).toBeNull();
  });
});

describe("handoff and reflect rows", () => {
  it("renders a hand-off as a connector row, not a step card", () => {
    const { container } = render(
      <StepTimeline
        steps={[
          step({
            action: "handoff",
            from: "investigator",
            to: "verifier",
            kind: "draft",
            reason: "draft ready for review",
          }),
        ]}
      />,
    );
    const row = container.querySelector(".step-handoff");
    expect(row?.textContent).toContain("Investigator");
    expect(row?.textContent).toContain("Verifier: draft ready for review");
    expect(container.querySelector(".step-index")).toBeNull();
  });
  it("renders a self-check with plain-word violations and the decision", () => {
    const { container } = render(
      <StepTimeline
        steps={[
          step({
            action: "reflect",
            agent: "verifier",
            violations: ["R2"],
            decision: "ask_user",
          }),
        ]}
      />,
    );
    expect(screen.getByText("Self-check")).toBeTruthy();
    expect(
      screen.getByText(/batch not confirmed by a person, QR or two photos/),
    ).toBeTruthy();
    expect(screen.getByText(/asked one more question/)).toBeTruthy();
    expect(container.querySelector(".step-reflect")).toBeTruthy();
  });
  it("words a downgrade decision", () => {
    render(
      <StepTimeline
        steps={[step({ action: "reflect", violations: [], decision: "downgrade" })]}
      />,
    );
    expect(screen.getByText(/gave can't verify/)).toBeTruthy();
  });
});
