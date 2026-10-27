import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fixtures from "./public-demo-fixtures.json";
import {
  createPublicDemo,
  MAX_DEMO_CHECKS,
  PUBLIC_DEMO_STORAGE_KEY,
} from "./publicDemo";
import { api, json, stream } from "./api";
import type { Snapshot } from "./api";

vi.mock("./environment", () => ({ PUBLIC_DEMO: true }));

function memoryStorage(initial: string | null = null) {
  const entries = new Map<string, string>();
  if (initial !== null) entries.set(PUBLIC_DEMO_STORAGE_KEY, initial);
  return {
    getItem: (key: string) => entries.get(key) ?? null,
    setItem: (key: string, value: string) => {
      entries.set(key, value);
    },
    removeItem: (key: string) => {
      entries.delete(key);
    },
  };
}

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => {
      throw new Error("Public replay must not use a network.");
    }),
  );
});
afterEach(() => {
  expect(fetch).not.toHaveBeenCalled();
  vi.unstubAllGlobals();
});

async function finish(
  demo: ReturnType<typeof createPublicDemo>,
  caseId = "01",
) {
  let saved = await demo.request<Snapshot>(
    "/api/demo/checks",
    json({ case_id: caseId }),
  );
  for (let step = 0; saved.status === "waiting" && step < 8; step++) {
    saved = await demo.request<Snapshot>(
      `/api/checks/${saved.thread_id}/resume`,
      json(saved.pending!.guided_answer),
    );
  }
  return saved;
}

describe("precomputed public demonstration", () => {
  for (const item of fixtures.cases) {
    it(`replays ${item.definition.id}: ${item.definition.name} using the exported engine result`, async () => {
      const demo = createPublicDemo();
      let current = await demo.request<Snapshot>(
        "/api/demo/checks",
        json({ case_id: item.definition.id }),
      );
      expect(current.demo).toBe(true);
      for (const answer of item.answers) {
        expect(current.pending?.guided_answer).toEqual(answer);
        const events: Record<string, unknown>[] = [];
        await demo.stream(
          `/api/checks/${current.thread_id}/resume`,
          json(answer),
          (name, data) => {
            expect(data.thread_id).toBe(current.thread_id);
            if (name === "snapshot") events.push(data);
          },
        );
        current = events[0].snapshot as Snapshot;
        expect(current.demo).toBe(true);
      }
      expect(current.status).toBe("done");
      expect(current.final).toEqual(item.snapshots.at(-1)!.final);
      expect(current.final?.label).toBe(item.definition.expected);
      expect(current.final?.headline.startsWith("Demo · ")).toBe(true);
      expect(
        current.final?.citations.every(
          (citation) => citation.synthetic && !citation.url,
        ),
      ).toBe(true);
      expect(await demo.request(`/api/checks/${current.thread_id}`)).toEqual(
        current,
      );
    });
  }

  it("rejects unrecognized answers without advancing or inventing a verdict", async () => {
    const demo = createPublicDemo();
    const first = await demo.request<Snapshot>(
      "/api/demo/checks",
      json({ case_id: "01" }),
    );
    for (const answer of [
      { typed: "REAL-BATCH" },
      { skip: true },
      { choice: "Yes" },
      { typed: "LM2408B", fields: { product: "Real pack" } },
      { typed: { deeply: { nested: true } } },
    ]) {
      const response = await demo.request<Snapshot>(
        `/api/checks/${first.thread_id}/resume`,
        json(answer),
      );
      expect(response.status).toBe("waiting");
      expect(response.final).toBeNull();
      expect(response.fields).toEqual(first.fields);
      expect(response.pending?.error).toContain("guided recording");
      expect(response.pending?.guided_answer).toEqual({ typed: "LM2408B" });
    }
    const result = await demo.request<Snapshot>(
      `/api/checks/${first.thread_id}/resume`,
      json({ typed: "  lm2408b  " }),
    );
    expect(result.final?.label).toBe("FLAGGED");
  });

  it("offers only synthetic searchable records and recorded diagnostic results", async () => {
    const demo = createPublicDemo();
    expect(fixtures.cases).toHaveLength(11);
    expect(fixtures.replay_only).toBe(true);
    const health = await demo.request<Record<string, unknown>>("/api/health");
    expect(health.mode).toBe("public_demo");
    expect(health.ocr).toEqual({ available: false });
    const stats = await demo.request<Record<string, unknown>>("/api/stats");
    expect(stats.official_alerts).toBe(0);
    const rows = await demo.request<{
      items: Record<string, unknown>[];
      total: number;
    }>("/api/alerts?q=Lumera&kind=spurious");
    expect(rows.total).toBe(1);
    expect(rows.items[0].synthetic).toBe(true);
    expect(await demo.request(`/api/alerts/${rows.items[0].id}`)).toEqual(
      rows.items[0],
    );
    expect(
      await demo.request("/api/alerts?q=unrecognized-real-product"),
    ).toMatchObject({ items: [], total: 0 });
    expect(await demo.request("/api/alerts?page=2&size=1")).toMatchObject({
      page: 2,
      pages: 2,
    });
    expect(await demo.request("/api/sources")).toMatchObject({
      synthetic: true,
      items: [{ synthetic: true, url: "" }],
    });
    expect(await demo.request("/api/quarantine")).toMatchObject({ items: [] });
    expect(await demo.request("/api/notifications")).toMatchObject({
      items: [],
    });
    expect(await demo.request("/api/eval/latest")).toMatchObject({
      available: false,
    });
    const events: string[] = [];
    await demo.stream("/api/eval/quick", json({}), (name, data) => {
      events.push(name);
      if (name === "report")
        expect(data).toMatchObject({
          precomputed: true,
          replay: true,
          passed: 11,
          failed: 0,
        });
    });
    expect(events).toEqual(["report", "done"]);
    expect(await demo.request("/api/eval/latest")).toMatchObject({
      cases: fixtures.evaluation.cases,
      precomputed: true,
    });
  });

  it("saves, deduplicates, restores and deletes only completed synthetic examples", async () => {
    const storage = memoryStorage();
    const demo = createPublicDemo(storage);
    const waiting = await demo.request<Snapshot>(
      "/api/demo/checks",
      json({ case_id: "01" }),
    );
    await expect(
      demo.request("/api/cabinet", json({ thread_id: waiting.thread_id })),
    ).rejects.toThrow("Finish this example");
    const done = await finish(demo);
    const saved = await demo.request<Record<string, unknown>>(
      "/api/cabinet",
      json({ thread_id: done.thread_id, label: "PRIVATE CUSTOM INPUT" }),
    );
    await demo.request("/api/cabinet", json({ thread_id: done.thread_id }));
    expect(await demo.request("/api/cabinet")).toMatchObject({
      items: [saved],
    });
    expect(saved).toMatchObject({
      demo: true,
      replay: true,
      label: "Lumera Tablets",
    });
    expect(storage.getItem(PUBLIC_DEMO_STORAGE_KEY)).not.toContain(
      "PRIVATE CUSTOM INPUT",
    );
    const reopened = createPublicDemo(storage);
    expect(await reopened.request("/api/cabinet")).toMatchObject({
      items: [saved],
    });
    await reopened.request(`/api/cabinet/${saved.id}`, { method: "DELETE" });
    expect(await reopened.request("/api/cabinet")).toMatchObject({ items: [] });
    expect(
      await reopened.request(`/api/checks/${done.thread_id}`),
    ).toMatchObject({ final: done.final });
    await expect(
      reopened.request("/api/cabinet/recheck", json({})),
    ).rejects.toThrow("recorded synthetic");
  });

  for (const corrupt of [
    "{invalid",
    "null",
    "[]",
    '{"version":2}',
    "x".repeat(32_769),
  ]) {
    it(`recovers from malformed or oversized browser state (${corrupt.length} characters)`, async () => {
      const storage = memoryStorage(corrupt);
      const demo = createPublicDemo(storage);
      expect(await demo.request("/api/checks")).toMatchObject({ items: [] });
      expect((await finish(demo)).final?.label).toBe("FLAGGED");
      expect(
        JSON.parse(storage.getItem(PUBLIC_DEMO_STORAGE_KEY)!),
      ).toMatchObject({ version: 1 });
    });
  }

  it("reconstructs trusted snapshots instead of restoring injected fields or verdicts", async () => {
    const date = "2026-01-01T00:00:00.000Z";
    const check = {
      id: "public-demo-1",
      case_id: "01",
      step: 1,
      created_at: date,
      updated_at: date,
      fields: { batch: "PRIVATE-PACK" },
      final: { label: "INJECTED" },
    };
    const storage = memoryStorage(
      JSON.stringify({
        version: 1,
        checks: [
          check,
          check,
          { ...check, id: "public-demo-2", case_id: "unknown" },
          { ...check, id: "public-demo-3", step: 9000 },
        ],
        cabinet: [check.id, check.id, "missing"],
      }),
    );
    const demo = createPublicDemo(storage);
    const history = await demo.request<{ items: Snapshot[] }>("/api/checks");
    expect(history.items).toHaveLength(1);
    expect(history.items[0].fields.batch).toBe("LM2408B");
    expect(history.items[0].final?.label).toBe("FLAGGED");
    const cabinet = await demo.request<{ items: unknown[] }>("/api/cabinet");
    expect(cabinet.items).toHaveLength(1);
  });

  it("bounds history and cabinet references, without storing request input or result text", async () => {
    const storage = memoryStorage();
    const demo = createPublicDemo(storage);
    const oldest = await finish(demo);
    await demo.request("/api/cabinet", json({ thread_id: oldest.thread_id }));
    for (let i = 0; i < MAX_DEMO_CHECKS + 2; i++)
      await demo.request("/api/demo/checks", json({ case_id: "02" }));
    const history = await demo.request<{ items: Snapshot[] }>(
      "/api/checks?limit=100",
    );
    expect(history.items).toHaveLength(MAX_DEMO_CHECKS);
    expect(await demo.request("/api/cabinet")).toMatchObject({ items: [] });
    const stored = storage.getItem(PUBLIC_DEMO_STORAGE_KEY)!;
    expect(stored.length).toBeLessThan(32_768);
    expect(stored).not.toMatch(/Lumera|LM2408B|headline|final|fields/);
    await expect(
      demo.request(`/api/checks/${oldest.thread_id}`),
    ).rejects.toThrow("no longer in this browser tab");
  });

  it("works in memory if session storage is blocked or full", async () => {
    const fail = () => {
      throw new Error("Storage unavailable");
    };
    const demo = createPublicDemo({
      getItem: fail,
      setItem: fail,
      removeItem: fail,
    });
    expect((await finish(demo)).final?.label).toBe("FLAGGED");
  });

  it("aborts before mutations and stops stream delivery after cancellation", async () => {
    const demo = createPublicDemo();
    const abort = new AbortController();
    abort.abort();
    await expect(
      demo.request("/api/demo/checks", {
        ...json({ case_id: "01" }),
        signal: abort.signal,
      }),
    ).rejects.toMatchObject({ name: "AbortError" });
    expect(await demo.request("/api/checks")).toMatchObject({ items: [] });
    const during = new AbortController();
    const events: string[] = [];
    await expect(
      demo.stream(
        "/api/demo/checks",
        { ...json({ case_id: "01" }), signal: during.signal },
        (name) => {
          events.push(name);
          during.abort();
        },
      ),
    ).rejects.toMatchObject({ name: "AbortError" });
    expect(events).toEqual(["snapshot"]);
  });

  it("never routes manual checks, photos, sync or unsupported paths to a backend", async () => {
    const demo = createPublicDemo();
    for (const path of [
      "/api/checks",
      "/api/sync",
      "/api/lan",
      "/api/private",
      "https://example.com/api/checks",
    ]) {
      await expect(
        demo.request(path, json({ batch: "PRIVATE-PACK" })),
      ).rejects.toThrow(/public|recorded synthetic/i);
    }
    await expect(
      demo.request("/api/checks", { method: "POST", body: new FormData() }),
    ).rejects.toThrow("public website");
    await expect(
      demo.request("/api/demo/checks", json({ case_id: "invented" })),
    ).rejects.toThrow("built-in");
    await expect(demo.request("/api/alerts?page=NaN")).rejects.toThrow(
      "valid page",
    );
    await expect(demo.request("/api/alerts/999999")).rejects.toThrow(
      "not found",
    );
  });

  it("integrates the existing api and stream entry points without calling fetch", async () => {
    expect(await api("/api/health")).toMatchObject({ mode: "public_demo" });
    const callback = vi.fn();
    await stream("/api/demo/checks", json({ case_id: "02" }), callback);
    expect(callback).toHaveBeenCalledWith(
      "snapshot",
      expect.objectContaining({
        snapshot: expect.objectContaining({ status: "done", demo: true }),
      }),
    );
    await expect(
      api("/api/checks", json({ batch: "NOT-A-DEMO" })),
    ).rejects.toThrow("public website");
    await expect(stream("/api/sync", json({}), callback)).rejects.toThrow(
      "recorded synthetic",
    );
  });
});
