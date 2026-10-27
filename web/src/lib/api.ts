import { requestScope } from "./runtime";
export type Fields = {
  batch: string;
  product: string;
  brand: string;
  maker: string;
  mfg: string;
  exp: string;
  source?: string;
  confirmed?: boolean;
};
export type Step = {
  step: number;
  action: string;
  source: string;
  summary: string;
  ms: number;
};
export type Verdict = {
  label: string;
  headline: string;
  explanation: string;
  advice?: string;
  citations: Record<string, unknown>[];
  evidence: Record<string, unknown>;
  batch_evidence: string;
  lang: string;
  latest_month?: string;
};
export type Snapshot = {
  thread_id: string;
  status: string;
  fields: Fields;
  strip?: {
    chars: { ch: string; state: string; alts: string[] }[];
    source: string;
  };
  history: Step[];
  pending?: Record<string, unknown> | null;
  final?: Verdict | null;
  demo?: boolean;
  created_at?: string;
};
export type AlertRow = {
  id: number;
  product: string;
  brand: string;
  batch_raw: string;
  batch_key: string;
  maker_name: string;
  maker_raw: string;
  list_month: string;
  entry_type: string;
  result: string;
  reported_by: string;
  source_url?: string;
  row_no?: number;
  [key: string]: unknown;
};
export type Stats = {
  alerts?: number;
  sources?: number;
  months?: number | string[];
  month_count?: number;
  latest_month?: string;
  last_sync?: string;
  [key: string]: unknown;
};
export type Health = {
  db: Stats;
  ollama?: { up: boolean };
  lan_url?: string;
  ocr?: unknown;
  [key: string]: unknown;
};
export const emptyFields: Fields = {
  batch: "",
  product: "",
  brand: "",
  maker: "",
  mfg: "",
  exp: "",
};
async function responseError(res: Response): Promise<Error> {
  let message = `Request failed (${res.status}). Please try again.`;
  try {
    const data = await res.json();
    const detail = data?.detail || data?.error?.message || data?.message;
    if (typeof detail === "string") message = detail;
  } catch {
    /* retain the readable HTTP status */
  }
  return new Error(message);
}
export async function api<T>(url: string, init?: RequestInit): Promise<T> {
  const scope = requestScope(init?.signal);
  try {
    const res = await fetch(url, { ...init, signal: scope.signal });
    if (!res.ok) throw await responseError(res);
    return await res.json();
  } finally {
    scope.dispose();
  }
}
export const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});
export function parseEvent(
  block: string,
): { event: string; data: Record<string, unknown> } | null {
  let event = "message";
  const lines: string[] = [];
  for (const line of block.split(/\r?\n/)) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    if (line.startsWith("data:")) lines.push(line.slice(5).trimStart());
  }
  if (!lines.length) return null;
  return { event, data: JSON.parse(lines.join("\n")) };
}
export async function stream(
  url: string,
  init: RequestInit,
  onEvent: (event: string, data: Record<string, unknown>) => void,
) {
  const scope = requestScope(init.signal);
  let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
  let completed = false;
  const cancel = () => {
    void reader?.cancel().catch(() => {});
  };
  try {
    const res = await fetch(url, { ...init, signal: scope.signal });
    if (!res.ok) throw await responseError(res);
    if (res.headers.get("content-type")?.includes("application/json")) {
      onEvent("snapshot", { snapshot: await res.json() });
      return;
    }
    if (!res.body)
      throw new Error("The server did not return a response. Try again.");
    reader = res.body.getReader();
    scope.signal.addEventListener("abort", cancel, { once: true });
    const decoder = new TextDecoder();
    let buffer = "";
    let terminal = false;
    const emit = (block: string) => {
      const parsed = parseEvent(block);
      if (!parsed) return;
      if (
        ["done", "snapshot", "final", "interrupt", "report"].includes(
          parsed.event,
        )
      )
        terminal = true;
      onEvent(parsed.event, parsed.data);
    };
    const started = Date.now();
    for (;;) {
      scope.signal.throwIfAborted();
      scope.reset(
        Math.min(90_000, Math.max(1, 900_000 - (Date.now() - started))),
      );
      const { done, value } = await reader.read();
      scope.signal.throwIfAborted();
      buffer += decoder.decode(value, { stream: !done });
      if (buffer.length > 2 * 1024 * 1024)
        throw new Error(
          "The server response is too large. Reopen this check from Activity.",
        );
      let match;
      while ((match = /\r?\n\r?\n/.exec(buffer))) {
        const block = buffer.slice(0, match.index);
        buffer = buffer.slice(match.index + match[0].length);
        emit(block);
      }
      if (done) {
        if (buffer.trim()) emit(buffer);
        if (!terminal)
          throw new Error(
            "The connection ended before the check finished. Reopen it from Activity or retry.",
          );
        completed = true;
        break;
      }
    }
  } finally {
    scope.dispose();
    scope.signal.removeEventListener("abort", cancel);
    if (reader) {
      if (!completed) await reader.cancel().catch(() => {});
      reader.releaseLock();
    }
  }
}

export function readableDate(value: unknown) {
  if (!value) return "Not yet";
  const text = String(value);
  if (/^\d{4}-\d{2}$/.test(text))
    return new Date(`${text}-01T00:00:00`).toLocaleDateString("en-IN", {
      month: "short",
      year: "numeric",
    });
  const d = new Date(text);
  return Number.isNaN(d.getTime())
    ? text
    : d.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
}
export const labelName = (label: string) =>
  ({
    FLAGGED: "Listed batch",
    SUSPECTED_FAKE: "Spurious listing",
    NOT_LISTED: "No listing found",
    CANT_VERIFY: "Needs a closer look",
  })[label] || label;
