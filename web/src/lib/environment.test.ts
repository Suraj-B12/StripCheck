// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
  history.replaceState({}, "", "/");
});

describe("public and local route boundaries", () => {
  it("uses the repository base and hash route on Pages, including refresh", async () => {
    vi.stubEnv("MODE", "pages");
    vi.stubEnv("BASE_URL", "/StripCheck/");
    const env = await import("./environment");
    expect(env.PUBLIC_DEMO).toBe(true);
    expect(env.appHref("/cabinet")).toBe("/StripCheck/#/cabinet");
    expect(env.appHref("/")).toBe("/StripCheck/#/");
    history.replaceState({}, "", "/StripCheck/#/traces");
    expect(env.currentPath()).toBe("/traces");
    history.replaceState({}, "", "/StripCheck/");
    expect(env.currentPath()).toBe("/");
  });
  it("preserves existing local path navigation", async () => {
    vi.stubEnv("MODE", "production");
    const env = await import("./environment");
    expect(env.PUBLIC_DEMO).toBe(false);
    expect(env.appHref("/cabinet")).toBe("/cabinet");
    history.replaceState({}, "", "/lists");
    expect(env.currentPath()).toBe("/lists");
  });
});
