// @vitest-environment jsdom
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../lib/environment", () => ({
  PUBLIC_DEMO: true,
  PROJECT_URL: "https://github.com/Suraj-B12/StripCheck",
  appHref: (path: string) => `/StripCheck/#${path}`,
  currentPath: () =>
    window.location.hash.startsWith("#/") ? window.location.hash.slice(1) : "/",
}));
import App from "../App";
import fixtureData from "../lib/public-demo-fixtures.json";
const examples = fixtureData.cases as unknown as {
  definition: { id: string; name: string };
  answers: unknown[];
  snapshots: { final?: { headline: string } | null }[];
}[];

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  history.replaceState({}, "", "/StripCheck/#/");
  vi.stubGlobal(
    "fetch",
    vi.fn(() =>
      Promise.reject(new Error("A public example must not contact a backend")),
    ),
  );
  vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));
  vi.stubGlobal("scrollTo", vi.fn());
  Element.prototype.scrollIntoView = vi.fn();
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
  localStorage.clear();
  sessionStorage.clear();
});

async function chooseExample(id: string) {
  fireEvent.click(screen.getByRole("button", { name: "Try a demo pack" }));
  const dialog = await screen.findByRole("dialog");
  const example = examples.find((item) => item.definition.id === id)!;
  const heading = await within(dialog).findByRole("heading", {
    name: example.definition.name,
  });
  fireEvent.click(heading.closest("button")!);
  return example;
}

describe("public showcase boundaries and interactions", () => {
  it("walks all eleven authored examples without photo, text or backend requests", async () => {
    render(<App />);
    expect(
      screen.getByRole("complementary", {
        name: "Public demonstration notice",
      }),
    ).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Use your phone" })).toBeNull();
    expect(screen.queryByLabelText(/Batch number/)).toBeNull();
    expect(document.querySelector('input[type="file"]')).toBeNull();
    for (const example of examples) {
      await chooseExample(example.definition.id);
      for (let step = 0; step < example.answers.length; step++) {
        const next = await screen.findByRole("button", {
          name: "Continue this example",
        });
        expect(document.querySelector('input[type="file"]')).toBeNull();
        expect(
          screen.queryByRole("button", { name: "Add a carton photo" }),
        ).toBeNull();
        fireEvent.click(next);
      }
      const final = example.snapshots.at(-1)!.final!;
      expect(
        await screen.findByRole("heading", { name: final.headline }),
      ).toBeTruthy();
      expect(screen.getByText("RECORDED FICTIONAL EXAMPLE")).toBeTruthy();
    }
    expect(fetch).not.toHaveBeenCalled();
  });

  it("uses base-aware routes, browser navigation and skip focus without changing the route", async () => {
    history.replaceState({}, "", "/StripCheck/#/lists");
    render(<App />);
    expect(
      await screen.findByRole("heading", { name: "Evidence you can explore." }),
    ).toBeTruthy();
    expect(
      screen.queryByRole("button", { name: "Sync with CDSCO" }),
    ).toBeNull();
    const cabinet = screen.getAllByRole("link", { name: "Cabinet" })[0];
    expect(cabinet.getAttribute("href")).toBe("/StripCheck/#/cabinet");
    fireEvent.click(cabinet);
    expect(
      await screen.findByRole("heading", { name: "Your example cabinet." }),
    ).toBeTruthy();
    expect(window.location.hash).toBe("#/cabinet");
    fireEvent.click(screen.getByRole("link", { name: "Skip to content" }));
    expect(window.location.hash).toBe("#/cabinet");
    expect(document.activeElement?.id).toBe("main");
    expect(
      screen.queryByRole("button", { name: "Recheck all packs" }),
    ).toBeNull();
    await act(async () => {
      history.back();
    });
    await waitFor(() => expect(window.location.hash).toBe("#/lists"));
    expect(
      await screen.findByRole("heading", { name: "Evidence you can explore." }),
    ).toBeTruthy();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("labels scenario reports as recorded outcomes rather than live diagnostic runs", async () => {
    history.replaceState({}, "", "/StripCheck/#/eval");
    render(<App />);
    expect(
      await screen.findByRole("heading", {
        name: "Eleven stories. Clear outcomes.",
      }),
    ).toBeTruthy();
    fireEvent.click(
      screen.getByRole("button", { name: "Replay all examples" }),
    );
    expect(
      await screen.findByRole("heading", {
        name: "Recorded scenario outcomes.",
      }),
    ).toBeTruthy();
    expect(
      screen.getByRole("columnheader", { name: "Recorded outcome" }),
    ).toBeTruthy();
    expect(screen.queryByText("All diagnostic scenarios passed.")).toBeNull();
    expect(fetch).not.toHaveBeenCalled();
  });
});
