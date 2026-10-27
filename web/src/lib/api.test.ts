import { afterEach, describe, expect, it, vi } from "vitest";
import { api, parseEvent, stream } from "./api";
import { readFileSync } from "node:fs";
afterEach(() => vi.unstubAllGlobals());
describe("reliable event streaming", () => {
  it("ignores heartbeats and preserves named events", () => {
    expect(parseEvent(": heartbeat")).toBeNull();
    expect(
      parseEvent('event: step\r\ndata: {"step":1,"summary":"Read a batch"}'),
    ).toEqual({ event: "step", data: { step: 1, summary: "Read a batch" } });
  });
  it("handles partial UTF-8 bytes, CRLF, and an unterminated final event", async () => {
    const payload =
      ': keepalive\r\n\r\nevent: step\r\ndata: {"summary":"Read → confirm"}\r\n\r\nevent: final\ndata: {"label":"CANT_VERIFY"}';
    const bytes = new TextEncoder().encode(payload);
    const body = new ReadableStream({
      start(c) {
        for (let i = 0; i < bytes.length; i += 3)
          c.enqueue(bytes.slice(i, i + 3));
        c.close();
      },
    });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(body, {
          headers: { "Content-Type": "text/event-stream" },
        }),
      ),
    );
    const events: unknown[] = [];
    await stream("/api/checks", { method: "POST" }, (event, data) =>
      events.push({ event, data }),
    );
    expect(events).toEqual([
      { event: "step", data: { summary: "Read → confirm" } },
      { event: "final", data: { label: "CANT_VERIFY" } },
    ]);
  });
  it("surfaces the server error message without pretending success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: { message: "Choose an image under 15 MB." },
          }),
          { status: 413, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );
    await expect(api("/api/checks")).rejects.toThrow(
      "Choose an image under 15 MB.",
    );
  });
  it("accepts the native-compatible JSON response shape", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ status: "done" }), {
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const callback = vi.fn();
    await stream("/api/checks", { method: "POST" }, callback);
    expect(callback).toHaveBeenCalledWith("snapshot", {
      snapshot: { status: "done" },
    });
  });
});
function luminance(hex: string) {
  const rgb = (
    hex.length === 4
      ? "#" +
        hex
          .slice(1)
          .split("")
          .map((x) => x + x)
          .join("")
      : hex
  )
    .replace("#", "")
    .match(/../g)!
    .map((v) => parseInt(v, 16) / 255)
    .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
}
function contrast(a: string, b: string) {
  const x = luminance(a),
    y = luminance(b);
  return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
}
describe("accessible theme contrast", () => {
  const css = readFileSync(
    new URL("../styles/tokens.css", import.meta.url),
    "utf8",
  );
  const themes = css.split(':root[data-theme="dark"]');
  for (const [i, theme] of themes.entries()) {
    const tokens = Object.fromEntries(
      [...theme.matchAll(/--([a-z0-9-]+):\s*(#[0-9a-f]{3,6})\s*;/gi)].map(
        (m) => [m[1], m[2]],
      ),
    );
    for (const [fg, bg] of [
      ["ink", "card"],
      ["ink-2", "card"],
      ["muted", "paper"],
      ["pen", "card"],
      ["on-pen", "pen"],
      ["nsq", "nsq-soft"],
      ["fake", "fake-soft"],
      ["nl", "nl-soft"],
      ["cv", "cv-soft"],
    ])
      it(`${i ? "dark" : "light"} ${fg} on ${bg} meets AA`, () =>
        expect(contrast(tokens[fg], tokens[bg])).toBeGreaterThanOrEqual(4.5));
  }
});
