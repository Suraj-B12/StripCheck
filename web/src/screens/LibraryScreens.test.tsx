// @vitest-environment jsdom
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ActivityScreen, CabinetScreen, ListsScreen } from "./LibraryScreens";
import { emptyFields } from "../lib/api";

beforeEach(() => {
  HTMLDialogElement.prototype.showModal = function () {
    this.open = true;
  };
  HTMLDialogElement.prototype.close = function () {
    this.open = false;
  };
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
const snapshot = (id: string) => ({
  thread_id: id,
  status: "done",
  fields: { ...emptyFields, batch: id, product: `Synthetic pack ${id}` },
  history: [],
  final: {
    label: "NOT_LISTED",
    headline: `Synthetic result ${id}`,
    explanation: "Fixture only.",
    citations: [],
    evidence: {},
  },
});
const response = (body: unknown) =>
  new Response(JSON.stringify(body), {
    headers: { "Content-Type": "application/json" },
  });

describe.each([
  ["cabinet", CabinetScreen],
  ["activity", ActivityScreen],
] as const)("%s detail request ordering", (_name, Screen) => {
  for (const closeBeforeOldResponse of [false, true]) {
    it(
      closeBeforeOldResponse
        ? "does not reopen a closed dialog for an old response"
        : "keeps the latest selected pack when old responses arrive late",
      async () => {
        const pending = new Map<string, (value: Response) => void>();
        const signals = new Map<string, AbortSignal>();
        vi.stubGlobal(
          "fetch",
          vi.fn((url: string, init: RequestInit) => {
            if (url === "/api/cabinet")
              return Promise.resolve(
                response({
                  items: ["A", "B"].map((id) => ({
                    id,
                    thread_id: id,
                    label: `Synthetic pack ${id}`,
                    fields: snapshot(id).fields,
                    last_verdict: "NOT_LISTED",
                  })),
                }),
              );
            if (url === "/api/notifications")
              return Promise.resolve(response({ items: [] }));
            if (url === "/api/checks?limit=100")
              return Promise.resolve(
                response({ items: ["A", "B"].map(snapshot) }),
              );
            const id = url.split("/").pop()!;
            signals.set(id, init.signal!);
            return new Promise<Response>((resolve) => pending.set(id, resolve));
          }),
        );
        render(<Screen toast={() => {}} refreshHealth={() => {}} />);
        fireEvent.click(
          await screen.findByRole("button", { name: /Synthetic pack A/ }),
        );
        fireEvent.click(
          screen.getByRole("button", { name: /Synthetic pack B/ }),
        );
        await act(async () => {
          pending.get("B")!(response(snapshot("B")));
        });
        expect(
          screen.getByRole("heading", { name: "Synthetic result B" }),
        ).toBeTruthy();
        expect(signals.get("A")!.aborted).toBe(true);
        if (closeBeforeOldResponse)
          fireEvent.click(screen.getByRole("button", { name: "Close dialog" }));
        await act(async () => {
          pending.get("A")!(response(snapshot("A")));
        });
        expect(
          screen.queryByRole("heading", { name: "Synthetic result A" }),
        ).toBeNull();
        if (closeBeforeOldResponse)
          expect(screen.queryByRole("dialog")).toBeNull();
        else
          expect(
            screen.getByRole("heading", { name: "Synthetic result B" }),
          ).toBeTruthy();
      },
    );
  }
});

describe("review records use readable source details", () => {
  function renderLists(items: Record<string, unknown>[]) {
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url === "/api/quarantine")
          return Promise.resolve(response({ items }));
        if (url === "/api/sources")
          return Promise.resolve(
            response({
              items: [
                {
                  id: 1,
                  title: "Synthetic stored source",
                  list_month: "2026-09",
                  rows_valid: 52,
                  sha256: "synthetic-source-fingerprint",
                },
              ],
            }),
          );
        if (url === "/api/stats")
          return Promise.resolve(response({ alerts: 0 }));
        return Promise.resolve(response({ items: [], total: 0, pages: 1 }));
      }),
    );
    render(<ListsScreen toast={() => {}} refreshHealth={() => {}} />);
  }
  it("reads serialized quarantine fields and explains the actual issue", async () => {
    renderLists([
      {
        id: 351,
        row_no: 17,
        raw_json: JSON.stringify({
          product_name_from_dtl: "Synthetic cough formula",
          dt_reporting_month_year: "SEP-2026",
        }),
        reasons: JSON.stringify(["batch_placeholder", "no_llm"]),
      },
    ]);
    fireEvent.click(screen.getByRole("button", { name: "Needs review" }));
    expect(
      await screen.findByRole("heading", { name: "Synthetic cough formula" }),
    ).toBeTruthy();
    expect(screen.getByText("SEP-2026 · Source row 17")).toBeTruthy();
    expect(
      screen.getByText("The source does not provide a clear batch number."),
    ).toBeTruthy();
    expect(screen.getByText(/excluded from batch checks/)).toBeTruthy();
    expect(
      screen.queryByText(/batch_placeholder|no_llm|Record 351/),
    ).toBeNull();
  });
  it("accepts parsed fields and explains multiple quality issues without internal codes", async () => {
    renderLists([
      {
        id: 2,
        row_no: 4,
        raw_json: { str_product_name: "Synthetic source tablet" },
        reasons: [
          "maker_missing",
          "batch_is_date",
          "no_llm",
          "future_internal_flag",
        ],
      },
    ]);
    fireEvent.click(screen.getByRole("button", { name: "Needs review" }));
    expect(
      await screen.findByRole("heading", { name: "Synthetic source tablet" }),
    ).toBeTruthy();
    expect(
      screen.getByText(/The manufacturer is missing from the source./),
    ).toBeTruthy();
    expect(
      screen.getByText(
        /The batch entry appears to be a date and needs checking./,
      ),
    ).toBeTruthy();
    expect(
      screen.queryByText(
        /maker_missing|batch_is_date|no_llm|future_internal_flag/,
      ),
    ).toBeNull();
  });
  it("uses a readable fallback for malformed stored records", async () => {
    renderLists([
      { id: 3, raw_json: "invalid JSON", reasons: "invalid reasons" },
    ]);
    fireEvent.click(screen.getByRole("button", { name: "Needs review" }));
    expect(
      await screen.findByRole("heading", { name: "Product name unavailable" }),
    ).toBeTruthy();
    expect(
      screen.getByText("The source details need a manual review."),
    ).toBeTruthy();
    expect(screen.queryByText(/invalid JSON|invalid reasons/)).toBeNull();
  });
  it("keeps source metadata separate from review explanations", async () => {
    renderLists([]);
    fireEvent.click(screen.getByRole("button", { name: "Sources" }));
    expect(
      await screen.findByRole("heading", { name: "Synthetic stored source" }),
    ).toBeTruthy();
    expect(screen.getByText("2026-09 · 52 records")).toBeTruthy();
    expect(screen.getByText("synthetic-source-fingerprint")).toBeTruthy();
    expect(screen.queryByText(/excluded from batch checks/)).toBeNull();
  });
});
