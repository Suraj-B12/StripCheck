// @vitest-environment jsdom
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import CheckScreen from "./CheckScreen";
import { emptyFields } from "../lib/api";
import type { Health } from "../lib/api";

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

const health = (llm_ok: boolean): Health => ({
  db: { alerts: 10 },
  ollama: { up: llm_ok, llm_ok, model: "qwen2.5:3b" },
});
const sse = (events: [string, unknown][]) =>
  new Response(
    events
      .map(([e, d]) => `event: ${e}\ndata: ${JSON.stringify(d)}\n\n`)
      .join(""),
    { headers: { "Content-Type": "text/event-stream" } },
  );
const snapshot = {
  thread_id: "live-check",
  status: "done",
  fields: { ...emptyFields, batch: "AB12345" },
  history: [],
  final: {
    label: "NOT_LISTED",
    headline: "Synthetic completed result",
    explanation: "Test fixture only.",
    citations: [],
    evidence: {},
  },
};

function captureBody() {
  const bodies: unknown[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn((_url: string, init?: RequestInit) => {
      bodies.push(init?.body);
      return Promise.resolve(
        sse([
          [
            "thinking",
            {
              id: "think-1",
              phase: "start",
              source: "llm",
              model: "qwen2.5:3b",
              context: "Deciding.",
              text: "",
            },
          ],
          [
            "thinking",
            { id: "think-1", phase: "delta", text: "Look at variants" },
          ],
          [
            "thinking",
            {
              id: "think-1",
              phase: "end",
              source: "llm",
              text: "Look at variants.",
              action: "search_variants",
              ms: 1800,
            },
          ],
          ["snapshot", { snapshot }],
          ["done", {}],
        ]),
      );
    }),
  );
  return bodies;
}

describe("planner switch and live thinking", () => {
  it("sends hybrid when the local model is ready, rules when switched off, and remembers it", async () => {
    const bodies = captureBody();
    render(<CheckScreen health={health(true)} toast={() => {}} />);
    const toggle = screen.getByRole("switch", {
      name: /Local AI reasoning/,
    }) as HTMLInputElement;
    expect(toggle.disabled).toBe(false);
    expect(toggle.checked).toBe(true);
    fireEvent.change(screen.getByLabelText(/Batch number/), {
      target: { value: "AB12345" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Check this batch" }));
    await screen.findByRole("heading", { name: "Synthetic completed result" });
    expect(JSON.parse(String(bodies[0])).planner).toBe("hybrid");
    // Finished reasoning stays in "Behind this check".
    expect(
      screen.getByRole("button", { name: /Thought for 1.8 s/ }),
    ).toBeTruthy();
    expect(screen.getByText("search variants")).toBeTruthy();
    fireEvent.click(toggle);
    expect(localStorage.getItem("stripcheck.planner")).toBe("rules");
    fireEvent.click(screen.getByRole("button", { name: "Check this batch" }));
    await waitFor(() => expect(bodies).toHaveLength(2));
    expect(JSON.parse(String(bodies[1])).planner).toBe("rules");
  });
  it("disables the switch and sends rules when the model is not running", async () => {
    const bodies = captureBody();
    render(<CheckScreen health={health(false)} toast={() => {}} />);
    const toggle = screen.getByRole("switch", {
      name: /Local AI reasoning/,
    }) as HTMLInputElement;
    expect(toggle.disabled).toBe(true);
    expect(toggle.checked).toBe(false);
    expect(screen.getByText(/the local model is not running/)).toBeTruthy();
    fireEvent.change(screen.getByLabelText(/Batch number/), {
      target: { value: "AB12345" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Check this batch" }));
    await waitFor(() => expect(bodies).toHaveLength(1));
    expect(JSON.parse(String(bodies[0])).planner).toBe("rules");
  });
  it("adds the planner to a photo upload", async () => {
    const bodies = captureBody();
    render(<CheckScreen health={health(true)} toast={() => {}} />);
    vi.stubGlobal("URL", {
      ...URL,
      createObjectURL: () => "blob:x",
      revokeObjectURL: () => {},
    });
    fireEvent.change(screen.getByLabelText("Upload a pack photo"), {
      target: { files: [new File(["x"], "pack.png", { type: "image/png" })] },
    });
    fireEvent.click(
      await screen.findByRole("button", { name: "Check this photo" }),
    );
    await waitFor(() => expect(bodies).toHaveLength(1));
    expect((bodies[0] as FormData).get("planner")).toBe("hybrid");
  });
  it("answers a confirm_batch question with OTP characters", async () => {
    const waiting = {
      ...snapshot,
      status: "waiting",
      final: null,
      pending: {
        kind: "confirm_batch",
        question: "Type the characters at positions 3 and 6.",
        reason: "A person must confirm.",
        asks_used: 1,
        asks_max: 2,
        batch: "AB12345",
        positions: [3, 6],
      },
    };
    const calls: [string, unknown][] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string, init?: RequestInit) => {
        calls.push([url, init?.body]);
        return Promise.resolve(
          sse([
            ["snapshot", { snapshot: calls.length === 1 ? waiting : snapshot }],
            ["done", {}],
          ]),
        );
      }),
    );
    render(<CheckScreen health={null} toast={() => {}} />);
    fireEvent.change(screen.getByLabelText(/Batch number/), {
      target: { value: "AB12345" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Check this batch" }));
    const first = await screen.findByLabelText("Character 3 of 7");
    fireEvent.change(first, { target: { value: "8" } });
    fireEvent.change(screen.getByLabelText("Character 6 of 7"), {
      target: { value: "b" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: /Confirm these characters/ }),
    );
    await screen.findByRole("heading", { name: "Synthetic completed result" });
    expect(calls[1][0]).toBe("/api/checks/live-check/resume");
    expect(JSON.parse(String(calls[1][1]))).toEqual({
      chars: { "3": "8", "6": "B" },
    });
  });
});
