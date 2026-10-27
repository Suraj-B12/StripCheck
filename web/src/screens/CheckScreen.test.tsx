// @vitest-environment jsdom
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import CheckScreen from "./CheckScreen";
import { emptyFields } from "../lib/api";

beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));
  Element.prototype.scrollIntoView = vi.fn();
});
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});

function restoredCheck() {
  return {
    thread_id: "previous",
    status: "waiting",
    fields: { ...emptyFields, batch: "OLD123", product: "Old synthetic pack" },
    history: [],
    pending: { kind: "confirm_batch", question: "Old confirmation" },
  };
}
function delayedRestore() {
  localStorage.setItem("stripcheck.current", "previous");
  let resolve!: (value: unknown) => void;
  const fetcher = vi.fn().mockReturnValue(
    new Promise((r) => {
      resolve = r;
    }),
  );
  vi.stubGlobal("fetch", fetcher);
  return {
    fetcher,
    finish: () => resolve({ ok: true, json: async () => restoredCheck() }),
  };
}

describe("check screen races and complete stream consumption", () => {
  it("does not replace newly typed pack details with a late restored check", async () => {
    const pending = delayedRestore();
    render(<CheckScreen health={null} toast={() => {}} />);
    fireEvent.change(screen.getByLabelText(/Batch number/), {
      target: { value: "NEW456" },
    });
    fireEvent.change(screen.getByLabelText(/Medicine or product name/), {
      target: { value: "New synthetic pack" },
    });
    await act(async () => {
      pending.finish();
    });
    expect(
      (screen.getByLabelText(/Batch number/) as HTMLInputElement).value,
    ).toBe("NEW456");
    expect(
      (screen.getByLabelText(/Medicine or product name/) as HTMLInputElement)
        .value,
    ).toBe("New synthetic pack");
    expect(screen.queryByText("Old confirmation")).toBeNull();
    expect(pending.fetcher.mock.calls[0][1].signal.aborted).toBe(true);
  });
  it("cancels outstanding restoration when navigating away", async () => {
    const pending = delayedRestore();
    const { unmount } = render(<CheckScreen health={null} toast={() => {}} />);
    unmount();
    expect(pending.fetcher.mock.calls[0][1].signal.aborted).toBe(true);
    await act(async () => {
      pending.finish();
    });
  });
  it("uses a complete streamed snapshot without a redundant result fetch", async () => {
    const result = {
      thread_id: "synthetic-component-check",
      status: "done",
      demo: true,
      fields: {
        ...emptyFields,
        batch: "NEW456",
        product: "Synthetic test pack",
      },
      history: [],
      final: {
        label: "NOT_LISTED",
        headline: "Synthetic completed result",
        explanation: "Test fixture only.",
        citations: [],
        evidence: {},
      },
    };
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          new Response(
            `event: snapshot\ndata: ${JSON.stringify({ snapshot: result })}\n\nevent: done\ndata: {}\n\n`,
            { headers: { "Content-Type": "text/event-stream" } },
          ),
        ),
    );
    render(<CheckScreen health={null} toast={() => {}} />);
    fireEvent.change(screen.getByLabelText(/Batch number/), {
      target: { value: "NEW456" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Check this batch" }));
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Synthetic completed result" }),
      ).toBeTruthy(),
    );
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem("stripcheck.current")).toBe(result.thread_id);
  });
});
