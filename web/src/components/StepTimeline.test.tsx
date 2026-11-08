// @vitest-environment jsdom
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StepTimeline } from "./Shared";
import type { Step } from "../lib/api";

describe("StepTimeline", () => {
  it("renders steps that carry node instead of action", () => {
    const steps = [
      { node: "perception", summary: "Reading the printed pack details locally.", source: "ocr" },
      { action: "search_exact", summary: "Searched.", source: "rules" },
    ] as unknown as Step[];
    render(<StepTimeline steps={steps} />);
    expect(screen.getByText("perception")).toBeTruthy();
    expect(screen.getByText("search exact")).toBeTruthy();
  });
});
