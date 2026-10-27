// @vitest-environment jsdom
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ActivityScreen, CabinetScreen } from "./LibraryScreens";
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
