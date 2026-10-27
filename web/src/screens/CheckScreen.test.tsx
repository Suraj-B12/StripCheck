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

describe("demo fields never leak into a real manual check", () => {
  it("clears all inherited synthetic fields once, then retains the newly typed batch and product", async () => {
    localStorage.setItem("stripcheck.current", "synthetic-old");
    const old = {
      ...restoredCheck(),
      thread_id: "synthetic-old",
      demo: true,
      fields: {
        ...emptyFields,
        batch: "LM2408B",
        product: "Lumera Tablets",
        brand: "Lumera",
        maker: "Example Laboratories",
        mfg: "2024-08",
        exp: "2027-07",
        source: "ocr",
        confirmed: false,
      },
    };
    let submitted: Record<string, unknown> | undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string, init?: RequestInit) => {
        if (url === "/api/checks/synthetic-old")
          return Promise.resolve(
            new Response(JSON.stringify(old), {
              headers: { "Content-Type": "application/json" },
            }),
          );
        submitted = JSON.parse(String(init?.body));
        return Promise.resolve(
          new Response(
            JSON.stringify({
              thread_id: "new-real-check",
              status: "done",
              fields: submitted,
              history: [],
            }),
            { headers: { "Content-Type": "application/json" } },
          ),
        );
      }),
    );
    render(<CheckScreen health={null} toast={() => {}} />);
    expect(
      (
        (await screen.findByDisplayValue(
          "Example Laboratories",
        )) as HTMLInputElement
      ).value,
    ).toBe("Example Laboratories");
    expect(screen.getByDisplayValue("2024-08")).toBeTruthy();
    fireEvent.change(screen.getByLabelText(/Batch number/), {
      target: { value: "TG261185" },
    });
    fireEvent.change(screen.getByLabelText(/Medicine or product name/), {
      target: { value: "New user product" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Check this batch" }));
    await waitFor(() => expect(submitted).toBeDefined());
    expect(submitted).toEqual({
      mode: "text",
      batch: "TG261185",
      product: "New user product",
      brand: "",
      maker: "",
      mfg: "",
      exp: "",
    });
    expect(JSON.stringify(submitted)).not.toMatch(
      /Example Laboratories|2024-08|2027-07|Lumera|ocr/,
    );
  });
});

it("keeps the manufacturer input open and focused while replacing demo details", async () => {
  localStorage.setItem("stripcheck.current", "manufacturer-demo");
  const old = {
    ...restoredCheck(),
    thread_id: "manufacturer-demo",
    demo: true,
    fields: {
      ...emptyFields,
      batch: "LM2408B",
      product: "Lumera Tablets",
      brand: "Lumera",
      maker: "Example Laboratories",
      mfg: "2024-08",
      exp: "2027-07",
    },
  };
  let submitted: Record<string, unknown> | undefined;
  vi.stubGlobal(
    "fetch",
    vi.fn((url: string, init?: RequestInit) => {
      if (url === "/api/checks/manufacturer-demo")
        return Promise.resolve(
          new Response(JSON.stringify(old), {
            headers: { "Content-Type": "application/json" },
          }),
        );
      submitted = JSON.parse(String(init?.body));
      return Promise.resolve(
        new Response(
          JSON.stringify({
            thread_id: "manual-maker-check",
            status: "done",
            fields: submitted,
            history: [],
          }),
          { headers: { "Content-Type": "application/json" } },
        ),
      );
    }),
  );
  render(<CheckScreen health={null} toast={() => {}} />);
  const maker = (await screen.findByLabelText(
    "Manufacturer",
  )) as HTMLInputElement;
  maker.focus();
  fireEvent.change(maker, { target: { value: "User" } });
  expect(screen.getByLabelText("Manufacturer")).toBe(maker);
  expect(document.activeElement).toBe(maker);
  expect((screen.getByLabelText("Brand") as HTMLInputElement).value).toBe("");
  expect(
    (screen.getByLabelText("Manufactured") as HTMLInputElement).value,
  ).toBe("");
  expect((screen.getByLabelText("Expires") as HTMLInputElement).value).toBe("");
  expect(
    (screen.getByLabelText(/Batch number/) as HTMLInputElement).value,
  ).toBe("");
  expect(
    (screen.getByLabelText(/Medicine or product name/) as HTMLInputElement)
      .value,
  ).toBe("");
  fireEvent.change(maker, { target: { value: "User Manufacturer" } });
  fireEvent.change(screen.getByLabelText(/Batch number/), {
    target: { value: "NEW456" },
  });
  fireEvent.change(screen.getByLabelText(/Medicine or product name/), {
    target: { value: "User product" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Check this batch" }));
  await waitFor(() => expect(submitted).toBeDefined());
  expect(submitted).toEqual({
    mode: "text",
    batch: "NEW456",
    product: "User product",
    maker: "User Manufacturer",
    brand: "",
    mfg: "",
    exp: "",
  });
});
