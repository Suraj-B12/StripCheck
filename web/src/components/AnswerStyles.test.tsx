// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AskConversation } from "./Ask";
import { ThinkingPanel } from "./Thinking";
import { emptyFields } from "../lib/api";
import type { Pending } from "../lib/api";
import {
  applyObservation,
  applyThinking,
  blocksFromHistory,
} from "../lib/thinking";

beforeEach(() => {
  vi.stubGlobal(
    "matchMedia",
    vi.fn(() => ({ matches: true })),
  );
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const confirmReading: Pending = {
  kind: "confirm_reading",
  style: "yes_no",
  question: "Is this the batch printed on your pack?",
  reading: "LM2408B",
  options: ["Yes, that's the batch", "No, it's different"],
  crop: "/api/crops/abc.png",
  asks_used: 1,
  asks_max: 2,
};

function ask(pending: Pending, onAnswer = vi.fn(), onCarton = vi.fn()) {
  render(
    <AskConversation
      pending={pending}
      fields={{ ...emptyFields }}
      onAnswer={onAnswer}
      onCarton={onCarton}
    />,
  );
  return { onAnswer, onCarton };
}

describe("answer styles", () => {
  it("renders yes/no as a keyboard radiogroup of reply chips that sends on choose", () => {
    const { onAnswer } = ask(confirmReading);
    const group = screen.getByRole("radiogroup");
    const radios = screen.getAllByRole("radio");
    expect(group).toBeTruthy();
    expect(radios.map((r) => r.textContent)).toEqual([
      "Yes, that's the batch",
      "No, it's different",
    ]);
    expect(screen.getByText("LM2408B")).toBeTruthy();
    // No free-text batch input before a "No".
    expect(screen.queryByRole("textbox")).toBeNull();
    radios[0].focus();
    fireEvent.keyDown(radios[0], { key: "ArrowRight" });
    expect(document.activeElement).toBe(radios[1]);
    expect(radios[1].getAttribute("tabindex")).toBe("0");
    fireEvent.keyDown(radios[1], { key: "Enter" });
    expect(onAnswer).toHaveBeenCalledWith({ choice: "No, it's different" });
    expect(radios[1].getAttribute("aria-checked")).toBe("true");
    // A second choice is not sent.
    fireEvent.click(radios[0]);
    expect(onAnswer).toHaveBeenCalledTimes(1);
  });

  it("shows the typed batch input for type_batch (the question after a No)", () => {
    ask({
      kind: "type_batch",
      style: "text",
      question: "Read the batch number printed on your pack and type it here.",
    });
    expect(screen.getByRole("textbox")).toBeTruthy();
    expect(screen.queryByRole("radiogroup")).toBeNull();
  });

  it("renders two-option questions as two side-by-side choice boxes", () => {
    const { container } = render(
      <AskConversation
        pending={{
          kind: "confirm_char",
          style: "choice2",
          question: "Which batch is printed on your pack: LM24088 or LM2408B?",
          options: ["LM2408B", "LM24088", "Can't tell"],
          positions: [7],
          listed: "LM2408B",
          pack: "LM24088",
        }}
        fields={{ ...emptyFields }}
        onAnswer={vi.fn()}
        onCarton={vi.fn()}
      />,
    );
    const cards = container.querySelector(".choice-cards");
    expect(cards?.classList.contains("two-up")).toBe(true);
    expect(container.querySelectorAll(".choice-card")).toHaveLength(2);
    expect(screen.queryByRole("textbox")).toBeNull();
  });

  it("renders request_photo as a camera/upload button with a one-line hint and a decline", () => {
    const { onAnswer, onCarton } = ask({
      kind: "request_photo",
      style: "photo",
      photo_kind: "batch_zoom",
      photo_hint:
        "Take a close-up photo of the batch line (B.No.) so it fills the frame, without glare.",
      question: "Can you take one more photo?",
      options: ["I can't take another photo"],
    });
    expect(screen.getByText(/close-up photo of the batch line/)).toBeTruthy();
    expect(
      screen.getByRole("button", { name: /Take a close-up of the batch line/ }),
    ).toBeTruthy();
    const file = new File(["x"], "zoom.png", { type: "image/png" });
    fireEvent.change(screen.getByLabelText("Upload the requested photo"), {
      target: { files: [file] },
    });
    expect(onCarton).toHaveBeenCalledWith(file, "batch_zoom");
    fireEvent.click(
      screen.getByRole("button", { name: "I can't take another photo" }),
    );
    expect(onAnswer).toHaveBeenCalledWith({
      choice: "I can't take another photo",
    });
    expect(screen.queryByText(/I can’t confirm this detail/)).toBeNull();
  });
});

describe("ReAct rows in the thinking panel", () => {
  it("shows Thought / Action / Observation for a live block once its step arrives", () => {
    let blocks = applyThinking([], {
      id: "think-1",
      phase: "start",
      source: "llm",
      text: "",
    });
    blocks = applyThinking(blocks, {
      id: "think-1",
      phase: "end",
      source: "llm",
      text: "The text reader failed, so read the batch with vision.",
      action: "read_with_vision",
      ms: 900,
      react: {
        thought: "The text reader failed, so read the batch with vision.",
        action: { tool: "read_with_vision", args: {} },
      },
    });
    blocks = applyObservation(blocks, {
      think_id: "think-1",
      summary: "The local vision model read the batch as LM2408B.",
      react: {
        observation: "The local vision model read the batch as LM2408B.",
      },
    });
    render(<ThinkingPanel blocks={blocks} />);
    fireEvent.click(screen.getByRole("button", { expanded: false }));
    expect(screen.getByText("Thought")).toBeTruthy();
    expect(screen.getByText("Action")).toBeTruthy();
    expect(screen.getByText("Observation")).toBeTruthy();
    expect(
      screen.getByText("The local vision model read the batch as LM2408B."),
    ).toBeTruthy();
  });

  it("rebuilds the rows from history steps after a reload", () => {
    const blocks = blocksFromHistory([
      {
        step: 2,
        action: "ask_user",
        source: "llm",
        summary: "Asked whether the vision reading is the printed batch.",
        ms: 1,
        thought: "Confirm the reading.",
        react: {
          thought: "Confirm the reading.",
          action: { tool: "ask_user", args: { kind: "confirm_reading" } },
          observation: "Waiting for Yes or No.",
        },
      },
    ]);
    expect(blocks[0].react).toEqual({
      thought: "Confirm the reading.",
      tool: "ask_user",
      args: "kind: confirm reading",
      observation: "Waiting for Yes or No.",
    });
  });
});
