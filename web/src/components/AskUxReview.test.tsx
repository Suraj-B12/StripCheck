// @vitest-environment jsdom
// Reviewer (frontend UX lens): demonstrates OTP input edge cases. These tests FAIL on the current code.
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CharBoxes } from "./Ask";

afterEach(() => cleanup());

describe("CharBoxes paste of a batch whose length differs from the read batch", () => {
  it("does not put the first pasted character into a doubted position", () => {
    const onSubmit = vi.fn();
    render(<CharBoxes batch="LM0412" positions={[3]} onSubmit={onSubmit} />);
    const input = screen.getByLabelText("Character 3 of 6") as HTMLInputElement;
    // The printed batch has one extra character the reader missed.
    fireEvent.paste(input, { clipboardData: { getData: () => "LM0O412" } });
    // Current code fills position 3 with "L" (first pasted char) and enables submit.
    expect(input.value).not.toBe("L");
  });
});

describe("CharBoxes typing with the caret before an existing character", () => {
  it("keeps the newly typed character, not the old one", () => {
    render(<CharBoxes batch="LM0412" positions={[3, 4]} onSubmit={vi.fn()} />);
    const input = screen.getByLabelText("Character 3 of 6") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "O" } });
    // Caret placed before the O by a click, user types 0: the value becomes "0O".
    fireEvent.change(input, { target: { value: "0O" } });
    expect(input.value).toBe("0");
  });
});
