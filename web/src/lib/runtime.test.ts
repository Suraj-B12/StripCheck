import { afterEach, describe, expect, it, vi } from "vitest";
import { createRequestGate, requestScope, storage } from "./runtime";
import { api, stream } from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("recovery under failed browser storage", () => {
  it("keeps preferences optional when privacy settings deny storage", () => {
    vi.stubGlobal("localStorage", {
      getItem() {
        throw new DOMException("Denied", "SecurityError");
      },
      setItem() {
        throw new DOMException("Full", "QuotaExceededError");
      },
      removeItem() {
        throw new Error("Denied");
      },
    });
    expect(storage.get("stripcheck.current")).toBeNull();
    expect(() => storage.set("stripcheck.current", "demo-123")).not.toThrow();
    expect(() => storage.remove("stripcheck.current")).not.toThrow();
  });
  it("forwards available storage without changing values", () => {
    const values = new Map<string, string>();
    vi.stubGlobal("localStorage", {
      getItem: (k: string) => values.get(k) ?? null,
      setItem: (k: string, v: string) => values.set(k, v),
      removeItem: (k: string) => values.delete(k),
    });
    storage.set("theme", "dark");
    expect(storage.get("theme")).toBe("dark");
    storage.remove("theme");
    expect(storage.get("theme")).toBeNull();
  });
});

describe("request lifecycle and stale-response protection", () => {
  it("invalidates a delayed restore when the user starts a new check", () => {
    const gate = createRequestGate();
    const restore = gate.begin();
    const fresh = gate.begin();
    expect(restore.aborted).toBe(true);
    expect(gate.isCurrent(restore)).toBe(false);
    expect(gate.isCurrent(fresh)).toBe(true);
    gate.cancel();
    expect(fresh.aborted).toBe(true);
    expect(gate.isCurrent(fresh)).toBe(false);
  });
  it("bounds a stalled request and clears timers on disposal", () => {
    vi.useFakeTimers();
    const scope = requestScope(undefined, 50);
    vi.advanceTimersByTime(49);
    expect(scope.signal.aborted).toBe(false);
    vi.advanceTimersByTime(1);
    expect(scope.signal.reason.name).toBe("TimeoutError");
    scope.dispose();
    expect(vi.getTimerCount()).toBe(0);
  });
  it("preserves caller cancellation including pre-aborted requests", () => {
    const parent = new AbortController();
    parent.abort();
    const scope = requestScope(parent.signal);
    expect(scope.signal.aborted).toBe(true);
    expect(scope.signal.reason.name).toBe("AbortError");
    scope.dispose();
  });
  it("aborts an API request that never responds after 30 seconds", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn(
        (_url, init: RequestInit) =>
          new Promise((_resolve, reject) => {
            init.signal!.addEventListener(
              "abort",
              () => reject(init.signal!.reason),
              { once: true },
            );
          }),
      ),
    );
    const request = api("/api/health");
    const assertion = expect(request).rejects.toThrow("took too long");
    await vi.advanceTimersByTimeAsync(30_000);
    await assertion;
    expect(vi.getTimerCount()).toBe(0);
  });
});

function mockStream(body: ReadableStream<Uint8Array>) {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue(
        new Response(body, {
          headers: { "Content-Type": "text/event-stream" },
        }),
      ),
  );
}
function payload(text: string) {
  return new ReadableStream<Uint8Array>({
    start(c) {
      c.enqueue(new TextEncoder().encode(text));
      c.close();
    },
  });
}
describe("stream interruption and resource cleanup", () => {
  it("reports a truncated connection instead of claiming completion", async () => {
    mockStream(payload('event: step\ndata: {"step":1}\n\n'));
    await expect(stream("/api/checks", {}, () => {})).rejects.toThrow(
      "before the check finished",
    );
  });
  it("cancels and releases the body after an event handler rejects evidence", async () => {
    const cancel = vi.fn();
    const body = new ReadableStream<Uint8Array>({
      start(c) {
        c.enqueue(
          new TextEncoder().encode(
            'event: error\ndata: {"message":"failed"}\n\n',
          ),
        );
      },
      cancel,
    });
    mockStream(body);
    await expect(
      stream("/api/checks", {}, () => {
        throw new Error("failed");
      }),
    ).rejects.toThrow("failed");
    expect(cancel).toHaveBeenCalledTimes(1);
    expect(body.locked).toBe(false);
  });
  it("cancels an idle stream and releases its lock at the deadline", async () => {
    vi.useFakeTimers();
    const cancel = vi.fn();
    const body = new ReadableStream<Uint8Array>({ cancel });
    mockStream(body);
    const request = stream("/api/checks", {}, () => {});
    const assertion = expect(request).rejects.toThrow("took too long");
    await vi.advanceTimersByTimeAsync(90_000);
    await assertion;
    expect(cancel).toHaveBeenCalledTimes(1);
    expect(body.locked).toBe(false);
    expect(vi.getTimerCount()).toBe(0);
  });
  it("bounds an unframed response before it can grow without limit", async () => {
    mockStream(payload("x".repeat(2 * 1024 * 1024 + 1)));
    await expect(stream("/api/checks", {}, () => {})).rejects.toThrow(
      "too large",
    );
  });
});
