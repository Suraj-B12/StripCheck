// @vitest-environment jsdom
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AnsweredThread, AskConversation, CharBoxes, ChoiceCards } from "./Ask";
import { answerSummary, differingIndices, safeCrop } from "../lib/ask";
import { emptyFields } from "../lib/api";

let reduced = true;
beforeEach(() => {
  reduced = true;
  vi.stubGlobal(
    "matchMedia",
    vi.fn(() => ({ matches: reduced })),
  );
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

const box = (pos: number) =>
  screen.getByLabelText(`Character ${pos} of 7`) as HTMLInputElement;

describe("CharBoxes (OTP input)", () => {
  it("auto-advances, uppercases and submits only the asked positions", () => {
    const onSubmit = vi.fn();
    render(
      <CharBoxes batch="AB12345" positions={[6, 3]} onSubmit={onSubmit} />,
    );
    expect(screen.queryByLabelText("Character 1 of 7")).toBeNull();
    const submit = screen.getByRole("button", {
      name: /Confirm these characters/,
    }) as HTMLButtonElement;
    expect(submit.disabled).toBe(true);
    box(3).focus();
    fireEvent.change(box(3), { target: { value: "8" } });
    expect(document.activeElement).toBe(box(6));
    fireEvent.change(box(6), { target: { value: "b" } });
    expect(box(6).value).toBe("B");
    expect(document.activeElement).toBe(submit);
    fireEvent.click(submit);
    expect(onSubmit).toHaveBeenCalledWith({ "3": "8", "6": "B" });
  });
  it("moves back and clears on backspace from an empty box", () => {
    render(<CharBoxes batch="AB12345" positions={[3, 6]} onSubmit={vi.fn()} />);
    fireEvent.change(box(3), { target: { value: "8" } });
    fireEvent.keyDown(box(6), { key: "Backspace" });
    expect(document.activeElement).toBe(box(3));
    expect(box(3).value).toBe("");
  });
  it("fills the boxes from a pasted whole batch", () => {
    const onSubmit = vi.fn();
    render(
      <CharBoxes batch="AB12345" positions={[3, 6]} onSubmit={onSubmit} />,
    );
    fireEvent.paste(box(3), {
      clipboardData: { getData: () => "ab8 23b5" },
    });
    expect(box(3).value).toBe("8");
    expect(box(6).value).toBe("B");
    fireEvent.submit(box(3).closest("form")!);
    expect(onSubmit).toHaveBeenCalledWith({ "3": "8", "6": "B" });
  });
});

describe("ChoiceCards", () => {
  it("highlights the differing characters and answers with the choice", () => {
    const onChoose = vi.fn();
    const onCantTell = vi.fn();
    render(
      <ChoiceCards
        options={["AB12345", "AB12845"]}
        onChoose={onChoose}
        onCantTell={onCantTell}
      />,
    );
    const marks = document.querySelectorAll("mark");
    expect([...marks].map((m) => m.textContent)).toEqual(["3", "8"]);
    fireEvent.click(screen.getByRole("button", { name: "AB12845" }));
    expect(onChoose).toHaveBeenCalledWith("AB12845");
    expect(differingIndices("2025-05", "2025-06")).toEqual(new Set([6]));
  });
  it("offers Can't tell", () => {
    const onCantTell = vi.fn();
    render(
      <ChoiceCards
        options={["2026-05", "2026-06"]}
        onChoose={vi.fn()}
        onCantTell={onCantTell}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Can’t tell" }));
    expect(onCantTell).toHaveBeenCalled();
  });
});

const confirmBatch = {
  kind: "confirm_batch",
  question: "Type the characters at positions 3 and 6.",
  reason: "A person must confirm the batch before a listed result.",
  asks_used: 1,
  asks_max: 2,
  batch: "AB12345",
  positions: [3, 6],
  options: ["Type the whole batch", "Can't tell"],
};

describe("AskConversation", () => {
  it("shows the question with reason, counter and focus on the first box", () => {
    const onAnswer = vi.fn();
    render(
      <AskConversation
        pending={confirmBatch}
        fields={{ ...emptyFields, batch: "AB12345" }}
        onAnswer={onAnswer}
        onCarton={vi.fn()}
      />,
    );
    expect(screen.getByText("Question 1 of 2")).toBeTruthy();
    expect(screen.getByText(confirmBatch.reason)).toBeTruthy();
    expect(document.activeElement).toBe(box(3));
    fireEvent.click(
      screen.getByRole("button", { name: /Type the whole batch instead/ }),
    );
    const input = screen.getByLabelText(
      /Type the full batch/,
    ) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "ab82 3b5" } });
    fireEvent.click(
      screen.getByRole("button", { name: /Confirm printed batch/ }),
    );
    expect(onAnswer).toHaveBeenCalledWith({ typed: "AB82 3B5" });
    fireEvent.click(
      screen.getByRole("button", { name: "I can’t confirm this detail" }),
    );
    expect(onAnswer).toHaveBeenCalledWith({ skip: true });
  });
  it("types for about 600 ms before the question appears", () => {
    reduced = false;
    vi.useFakeTimers();
    render(
      <AskConversation
        pending={confirmBatch}
        fields={{ ...emptyFields }}
        onAnswer={vi.fn()}
        onCarton={vi.fn()}
      />,
    );
    expect(
      screen.getByRole("status", { name: "StripCheck is writing" }),
    ).toBeTruthy();
    expect(screen.queryByText(confirmBatch.question)).toBeNull();
    act(() => {
      vi.advanceTimersByTime(650);
    });
    expect(screen.getByText(confirmBatch.question)).toBeTruthy();
  });
  it("shakes and shows the message for a rejected answer", () => {
    reduced = false;
    render(
      <AskConversation
        pending={{ ...confirmBatch, error: "Enter one letter or digit." }}
        fields={{ ...emptyFields }}
        onAnswer={vi.fn()}
        onCarton={vi.fn()}
      />,
    );
    const alert = screen.getByRole("alert");
    expect(alert.textContent).toBe("Enter one letter or digit.");
    expect(alert.closest(".ask-bubble")!.className).toContain("shake");
  });
  it("renders confirm_char as choice cards and a crop only from the crops API", () => {
    const onAnswer = vi.fn();
    render(
      <AskConversation
        pending={{
          kind: "confirm_char",
          question: "Which batch is printed?",
          options: ["AB12845", "AB12345", "Can't tell"],
          listed: "AB12845",
          pack: "AB12345",
          positions: [5],
          crop: "/api/crops/abc123.png",
        }}
        fields={{ ...emptyFields }}
        onAnswer={onAnswer}
        onCarton={vi.fn()}
      />,
    );
    expect(
      screen.getByAltText(/batch line from your photo/).getAttribute("src"),
    ).toBe("/api/crops/abc123.png");
    expect(screen.queryByRole("button", { name: "Can't tell" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "AB12845" }));
    expect(onAnswer).toHaveBeenCalledWith({ choice: "AB12845" });
    expect(safeCrop("https://example.com/x.png")).toBe("");
    expect(safeCrop("/api/crops/../x.png")).toBe("");
  });
});

describe("AnsweredThread", () => {
  it("echoes the answer with a tick and a Checking again bubble", () => {
    render(
      <AnsweredThread
        question="Which batch is printed?"
        answer={answerSummary({ chars: { "3": "8" } })}
        busy
      />,
    );
    expect(screen.getByText("Position 3: 8")).toBeTruthy();
    expect(document.querySelector(".answer-tick")).toBeTruthy();
    expect(screen.getByText("Checking again")).toBeTruthy();
    expect(screen.getByText("Answer sent. Checking again.")).toBeTruthy();
    expect(answerSummary({ skip: true })).toBe("I can’t confirm this detail.");
  });
});

describe("AskConversation fixes from review", () => {
  it("moves a pasted batch of another length to the whole-batch form", () => {
    render(
      <AskConversation
        pending={confirmBatch}
        fields={{ ...emptyFields, batch: "AB12345" }}
        hints={{ 3: "1/I" }}
        onAnswer={vi.fn()}
        onCarton={vi.fn()}
      />,
    );
    expect(box(3).getAttribute("aria-describedby")).toBeTruthy();
    expect(screen.getByText("Could be 1 or I")).toBeTruthy();
    fireEvent.paste(box(3), {
      clipboardData: { getData: () => "AB1I2345" },
    });
    const input = screen.getByLabelText(
      /Type the full batch/,
    ) as HTMLInputElement;
    expect(input.value).toBe("AB1I2345");
  });

  it("announces the question after mount, even without the typing delay", async () => {
    vi.useFakeTimers();
    render(
      <AskConversation
        pending={confirmBatch}
        fields={{ ...emptyFields, batch: "AB12345" }}
        onAnswer={vi.fn()}
        onCarton={vi.fn()}
      />,
    );
    const region = document.querySelector("[aria-live='polite']")!;
    expect(region.textContent).toBe("");
    await act(async () => {
      vi.advanceTimersByTime(60);
    });
    expect(region.textContent).toContain("Question 1 of 2");
  });

  it("marks the differing character of a listed batch with a separator", () => {
    const diff = differingIndices("MZP-25O2", "MZP2502", [6]);
    expect([...diff]).toEqual([6]);
  });
});
