/** Static, synthetic API replay. This module never checks a real medicine. */
import fixtures from "./public-demo-fixtures.json";
import type { Snapshot } from "./api";

type ObjectValue = Record<string, unknown>;
type Answer = Record<string, unknown>;
type DemoCase = {
  definition: { id: string; name: string; [key: string]: unknown };
  answers: Answer[];
  snapshots: Snapshot[];
};
type Cursor = {
  id: string;
  case_id: string;
  step: number;
  created_at: string;
  updated_at: string;
};
type State = {
  version: 1;
  next: number;
  checks: Cursor[];
  cabinet: string[];
  evaluation_at: string | null;
};
type DemoStorage = Pick<Storage, "getItem" | "setItem" | "removeItem">;
type EventCallback = (event: string, data: ObjectValue) => void;

export const PUBLIC_DEMO_STORAGE_KEY = "stripcheck.public-demo.v1";
export const MAX_DEMO_CHECKS = 30;
const MAX_STORAGE_BYTES = 32_768;
const cases = fixtures.cases as unknown as DemoCase[];
const notice = fixtures.notice;
const demoOnly =
  "This public website replays synthetic examples only. Use the local StripCheck app to check printed details or photos.";
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value));
const object = (value: unknown): value is ObjectValue =>
  !!value && typeof value === "object" && !Array.isArray(value);
const validDate = (value: unknown): value is string =>
  typeof value === "string" &&
  value.length <= 32 &&
  /^\d{4}-\d{2}-\d{2}T/.test(value) &&
  Number.isFinite(Date.parse(value));
const findCase = (id: unknown) =>
  cases.find((item) => item.definition.id === id);

function emptyState(): State {
  return { version: 1, next: 1, checks: [], cabinet: [], evaluation_at: null };
}

/** Persist only known fixture IDs and cursors; never trust stored result text. */
function restore(raw: string | null): State {
  if (!raw || raw.length > MAX_STORAGE_BYTES) return emptyState();
  try {
    const input: unknown = JSON.parse(raw);
    if (
      !object(input) ||
      input.version !== 1 ||
      !Array.isArray(input.checks) ||
      !Array.isArray(input.cabinet)
    )
      return emptyState();
    const state = emptyState();
    const ids = new Set<string>();
    for (const row of input.checks.slice(-MAX_DEMO_CHECKS)) {
      if (!object(row)) continue;
      const demo = findCase(row.case_id);
      if (
        !demo ||
        typeof row.id !== "string" ||
        !/^public-demo-\d{1,9}$/.test(row.id) ||
        ids.has(row.id) ||
        typeof row.step !== "number" ||
        !Number.isInteger(row.step) ||
        row.step < 0 ||
        row.step >= demo.snapshots.length ||
        !validDate(row.created_at) ||
        !validDate(row.updated_at)
      )
        continue;
      ids.add(row.id);
      state.checks.push({
        id: row.id,
        case_id: demo.definition.id,
        step: row.step,
        created_at: row.created_at,
        updated_at: row.updated_at,
      });
      state.next = Math.max(
        state.next,
        Number(row.id.slice("public-demo-".length)) + 1,
      );
    }
    state.cabinet = [
      ...new Set(
        input.cabinet.filter(
          (id): id is string => typeof id === "string" && ids.has(id),
        ),
      ),
    ].filter((id) => {
      const row = state.checks.find((item) => item.id === id)!;
      const snapshot = findCase(row.case_id)!.snapshots[row.step];
      return (
        snapshot.status === "done" &&
        !!snapshot.final &&
        !!snapshot.fields.batch
      );
    });
    if (validDate(input.evaluation_at))
      state.evaluation_at = input.evaluation_at;
    if (state.next > 999_999_999) return emptyState();
    return state;
  } catch {
    return emptyState();
  }
}

function body(init?: RequestInit): ObjectValue {
  if (init?.body === undefined || init.body === null || init.body === "")
    return {};
  if (typeof init.body !== "string") throw new Error(demoOnly);
  if (init.body.length > 16_384)
    throw new Error(
      "This example request is too large. Choose a built-in example.",
    );
  try {
    const value: unknown = JSON.parse(init.body);
    if (object(value)) return value;
  } catch {
    /* use the same readable message for malformed JSON */
  }
  throw new Error("Choose a built-in example and use its guided answer.");
}

function sameAnswer(actual: unknown, expected: unknown): boolean {
  // Extra fields, free-form substitutions and skip commands cannot select a result.
  // Recursion follows the small trusted answer, never an arbitrary request tree.
  if (typeof expected === "string") {
    const normalize = (value: string) =>
      value.trim().replace(/\s+/g, " ").toUpperCase();
    return (
      typeof actual === "string" && normalize(actual) === normalize(expected)
    );
  }
  if (object(expected))
    return (
      object(actual) &&
      Object.keys(actual).length === Object.keys(expected).length &&
      Object.keys(expected).every(
        (key) =>
          Object.hasOwn(actual, key) && sameAnswer(actual[key], expected[key]),
      )
    );
  return actual === expected;
}

function pageNumber(value: string | null, fallback: number, maximum: number) {
  if (value === null) return fallback;
  const number = Number(value);
  if (!Number.isInteger(number) || number < 1 || number > maximum)
    throw new Error("Choose a valid page and page size.");
  return number;
}

/** Factory enables isolated tests and handles unavailable browser storage. */
export function createPublicDemo(storage?: DemoStorage) {
  let state = emptyState();
  try {
    state = restore(storage?.getItem(PUBLIC_DEMO_STORAGE_KEY) ?? null);
  } catch {
    /* in-memory fallback */
  }
  const persist = () => {
    try {
      storage?.setItem(PUBLIC_DEMO_STORAGE_KEY, JSON.stringify(state));
    } catch {
      /* optional session storage */
    }
  };
  const cursor = (id: string): Cursor => {
    const item = state.checks.find((check) => check.id === id);
    if (!item)
      throw new Error(
        "This example is no longer in this browser tab. Choose a built-in example to start again.",
      );
    return item;
  };
  const snapshot = (item: Cursor, error?: string): Snapshot => {
    const demo = findCase(item.case_id)!;
    const value = clone(demo.snapshots[item.step]);
    if (value.pending) {
      value.pending.guided_answer = clone(demo.answers[item.step]);
      if (error) value.pending.error = error;
    }
    return {
      ...value,
      thread_id: item.id,
      demo: true,
      created_at: item.created_at,
      ...{
        updated_at: item.updated_at,
        public_demo: true,
        replay: true,
        notice,
      },
    };
  };
  const cabinetItem = (id: string) => {
    const saved = snapshot(cursor(id));
    return {
      id,
      thread_id: id,
      check_thread_id: id,
      demo: true,
      public_demo: true,
      replay: true,
      label: saved.fields.brand || saved.fields.product || "Synthetic example",
      fields: saved.fields,
      final: saved.final,
      batch_evidence: saved.final?.batch_evidence,
      batch_display: saved.fields.batch,
      last_verdict: saved.final?.label,
      created_at: saved.created_at,
      added_at: saved.created_at,
      last_checked_at: saved.created_at,
      notice,
    };
  };
  const stats = () => ({
    alerts: fixtures.alerts.length,
    total: fixtures.alerts.length,
    total_alerts: fixtures.alerts.length,
    sources: 1,
    nsq: fixtures.alerts.filter((row) => row.entry_type === "NSQ").length,
    spurious: fixtures.alerts.filter((row) => row.entry_type === "SPURIOUS")
      .length,
    months: ["2026-09"],
    month_count: 1,
    latest_month: "2026-09",
    earliest_month: "2026-09",
    checks: state.checks.length,
    has_data: true,
    synthetic: true,
    public_demo: true,
    official_alerts: 0,
    last_sync: null,
    coverage: { scope: "synthetic_examples_only", limited: true, notice },
    coverage_warning: notice,
  });
  const evaluation = () => ({
    ...clone(fixtures.evaluation),
    created_at: state.evaluation_at,
    public_demo: true,
    replay: true,
    precomputed: true,
    title: "Recorded synthetic diagnostics",
    notice:
      "These results were recorded from the Python engine when this demo was built. The browser replays them; no new medicine check or accuracy evaluation runs here.",
  });

  async function request<T = unknown>(
    url: string,
    init?: RequestInit,
  ): Promise<T> {
    await Promise.resolve();
    init?.signal?.throwIfAborted();
    if (!url.startsWith("/api/")) throw new Error(demoOnly);
    const parsed = new URL(url, "https://stripcheck.invalid");
    const path = parsed.pathname;
    const method = (init?.method || "GET").toUpperCase();
    const params = parsed.searchParams;
    let result: unknown;
    if (path === "/api/checks" && method !== "GET") throw new Error(demoOnly);
    if (
      path === "/api/sync" ||
      path.startsWith("/api/lan") ||
      path === "/api/cabinet/recheck"
    )
      throw new Error(
        "Live sync, phone pairing and medicine monitoring are available in the local app. This public site contains recorded synthetic examples only.",
      );

    if (path === "/api/health" && method === "GET") {
      result = {
        status: "ok",
        mode: "public_demo",
        synthetic: true,
        public_demo: true,
        replay: true,
        db: stats(),
        offline_ready: false,
        ocr: { available: false },
        ollama: { up: false },
        lan: { enabled: false },
        coverage: stats().coverage,
        coverage_warning: notice,
        notice,
      };
    } else if (path === "/api/stats" && method === "GET") result = stats();
    else if (path === "/api/demo/cases" && method === "GET")
      result = {
        items: cases.map((item) => item.definition),
        synthetic: true,
        replay: true,
      };
    else if (path === "/api/demo/checks" && method === "POST") {
      const demo = findCase(body(init).case_id);
      if (!demo)
        throw new Error(
          "Choose one of the eleven built-in synthetic examples.",
        );
      const date = new Date().toISOString();
      const item: Cursor = {
        id: `public-demo-${state.next++}`,
        case_id: demo.definition.id,
        step: 0,
        created_at: date,
        updated_at: date,
      };
      state.checks.push(item);
      state.checks = state.checks.slice(-MAX_DEMO_CHECKS);
      state.cabinet = state.cabinet.filter((id) =>
        state.checks.some((check) => check.id === id),
      );
      result = snapshot(item);
      persist();
    } else if (path === "/api/checks" && method === "GET") {
      const limit = pageNumber(params.get("limit"), MAX_DEMO_CHECKS, 200);
      result = {
        items: state.checks
          .slice()
          .reverse()
          .slice(0, limit)
          .map((item) => snapshot(item)),
        synthetic: true,
      };
    } else if (/^\/api\/checks\/[^/]+(?:\/resume)?$/.test(path)) {
      const item = cursor(decodeURIComponent(path.split("/")[3]));
      if (path.endsWith("/resume") && method === "POST") {
        const demo = findCase(item.case_id)!;
        if (demo.snapshots[item.step].status !== "waiting")
          throw new Error(
            "This recorded example is complete. Choose another example to explore.",
          );
        const expected = demo.answers[item.step];
        if (!expected || !sameAnswer(body(init), expected)) {
          result = snapshot(
            item,
            "This is a guided recording. Use ‘Continue this example’ to replay the authored answer. Other details cannot be checked on the public site.",
          );
        } else {
          item.step += 1;
          item.updated_at = new Date().toISOString();
          result = snapshot(item);
          persist();
        }
      } else if (!path.endsWith("/resume") && method === "GET")
        result = snapshot(item);
      else
        throw new Error(
          "This action is unavailable in the public demonstration.",
        );
    } else if (path === "/api/cabinet" && method === "GET") {
      result = {
        items: state.cabinet.map(cabinetItem),
        synthetic: true,
        replay: true,
      };
    } else if (path === "/api/cabinet" && method === "POST") {
      const id = body(init).thread_id;
      if (typeof id !== "string")
        throw new Error("Finish an example before saving it.");
      const saved = snapshot(cursor(id));
      if (saved.status !== "done" || !saved.final)
        throw new Error("Finish this example before saving it.");
      if (!saved.fields.batch)
        throw new Error("This example has no printed batch to save.");
      if (!state.cabinet.includes(id)) state.cabinet.push(id);
      result = cabinetItem(id);
      persist();
    } else if (/^\/api\/cabinet\/[^/]+$/.test(path) && method === "DELETE") {
      const id = decodeURIComponent(path.split("/")[3]);
      if (!state.cabinet.includes(id))
        throw new Error("This saved example was not found.");
      state.cabinet = state.cabinet.filter((saved) => saved !== id);
      persist();
      result = { deleted: true, id };
    } else if (path === "/api/notifications" && method === "GET")
      result = { items: [], synthetic: true };
    else if (path === "/api/alerts" && method === "GET") {
      const page = pageNumber(params.get("page"), 1, 1000);
      const size = pageNumber(params.get("size"), 30, 100);
      const q = (params.get("q") || "").trim().toLowerCase();
      if (q.length > 500)
        throw new Error("Use a shorter search of the synthetic records.");
      const month = params.get("month") || "";
      const kind = (params.get("kind") || "").toLowerCase();
      const batch = (params.get("batch") || "").trim().toUpperCase();
      const rows = fixtures.alerts.filter(
        (row) =>
          (!month || row.list_month === month) &&
          (!kind ||
            row.list_kind === kind ||
            row.entry_type.toLowerCase() === kind) &&
          (!batch || row.batch_key === batch) &&
          (!q ||
            [row.product, row.batch_raw, row.maker_raw, row.result].some(
              (text) => text.toLowerCase().includes(q),
            )),
      );
      result = {
        items: rows.slice((page - 1) * size, page * size),
        total: rows.length,
        page,
        pages: Math.max(1, Math.ceil(rows.length / size)),
        synthetic: true,
      };
    } else if (/^\/api\/alerts\/[^/]+$/.test(path) && method === "GET") {
      result = fixtures.alerts.find(
        (row) => String(row.id) === path.split("/")[3],
      );
      if (!result) throw new Error("This synthetic record was not found.");
    } else if (path === "/api/sources" && method === "GET") {
      result = {
        items: [
          {
            id: "authored-synthetic-fixtures",
            title: "Authored synthetic demonstration records",
            list_month: "2026-09",
            rows_valid: fixtures.alerts.length,
            synthetic: true,
            source_type: "synthetic",
            url: "",
          },
        ],
        synthetic: true,
      };
    } else if (path === "/api/quarantine" && method === "GET")
      result = { items: [], synthetic: true };
    else if (path === "/api/eval/latest" && method === "GET")
      result = state.evaluation_at
        ? evaluation()
        : { available: false, replay: true, synthetic: true };
    else if (path === "/api/eval/quick" && method === "POST") {
      state.evaluation_at = new Date().toISOString();
      persist();
      result = evaluation();
    } else
      throw new Error(
        "This action is unavailable in the public demonstration. Explore a built-in example or use the local app.",
      );
    return clone(result) as T;
  }

  async function stream(
    url: string,
    init: RequestInit,
    onEvent: EventCallback,
  ) {
    const result = await request<ObjectValue>(url, init);
    init.signal?.throwIfAborted();
    if (url.split("?")[0] === "/api/eval/quick") {
      onEvent("report", { ...result, thread_id: "public-demo-evaluation" });
      await Promise.resolve();
      init.signal?.throwIfAborted();
      onEvent("done", {
        thread_id: "public-demo-evaluation",
        status: "done",
        replay: true,
      });
    } else if (typeof result.thread_id === "string") {
      onEvent("snapshot", {
        thread_id: result.thread_id,
        snapshot: result,
        replay: true,
      });
      await Promise.resolve();
      init.signal?.throwIfAborted();
      onEvent("done", {
        thread_id: result.thread_id,
        status: result.status,
        replay: true,
      });
    } else
      throw new Error(
        "This public demonstration action does not stream a check.",
      );
  }
  return { request, stream };
}

const browserDemo = createPublicDemo({
  getItem: (key) => sessionStorage.getItem(key),
  setItem: (key, value) => sessionStorage.setItem(key, value),
  removeItem: (key) => sessionStorage.removeItem(key),
});
export const publicDemoApi = browserDemo.request;
export const publicDemoStream = browserDemo.stream;
