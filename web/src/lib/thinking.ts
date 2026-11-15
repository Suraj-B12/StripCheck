import type { ReactLabels, Step, ThinkingEvent } from "./api";
import { knownAgent } from "./agents";
import type { AgentName } from "./agents";

/** One branch-point decision, built from live `thinking` events or from a history step. */
export type ThinkBlock = {
  id: string;
  done: boolean;
  context: string;
  source: string;
  text: string;
  model?: string;
  action?: string;
  ms?: number;
  redacted?: boolean;
  agent?: AgentName;
  startedAt: number;
  /** ReAct rows (contract 2b): thought, tool call and a short observation of its result. */
  react?: { thought: string; tool: string; args: string; observation: string };
};

function argsText(args: unknown): string {
  if (!args || typeof args !== "object") return "";
  return Object.entries(args as Record<string, unknown>)
    .filter(
      ([k, v]) =>
        k !== "thought" && (typeof v === "string" || typeof v === "number"),
    )
    .map(([k, v]) => `${k}: ${String(v).replaceAll("_", " ")}`)
    .join(", ");
}

/** Normalise untrusted ReAct labels; undefined when there is no tool. */
export function reactRows(
  raw: unknown,
  fallback: { thought?: string; observation?: string } = {},
): ThinkBlock["react"] {
  const r = (raw && typeof raw === "object" ? raw : {}) as ReactLabels;
  const tool = typeof r.action?.tool === "string" ? r.action.tool : "";
  if (!tool) return undefined;
  return {
    thought: String(
      typeof r.thought === "string" ? r.thought : fallback.thought || "",
    ),
    tool,
    args: argsText(r.action?.args),
    observation: String(
      typeof r.observation === "string"
        ? r.observation
        : fallback.observation || "",
    ).slice(0, 240),
  };
}

/** Attach a step's observation to the thinking block that chose it (step.think_id === block id). */
export function applyObservation(
  blocks: ThinkBlock[],
  step: Record<string, unknown>,
): ThinkBlock[] {
  const id = typeof step.think_id === "string" ? step.think_id : "";
  const index = id ? blocks.findIndex((b) => b.id === id) : -1;
  if (index < 0) return blocks;
  const block = blocks[index];
  const rows =
    block.react || reactRows(step.react, { thought: block.text }) || undefined;
  if (!rows) return blocks;
  const observation =
    reactRows(step.react)?.observation || String(step.summary || "");
  const copy = blocks.slice();
  copy[index] = { ...block, react: { ...rows, observation } };
  return copy;
}

export const TRANSPARENCY_NOTE =
  "Shown for transparency. Results come only from the rules and the verifier.";

export function reducedMotion(): boolean {
  try {
    return (
      typeof window.matchMedia !== "function" ||
      Boolean(window.matchMedia("(prefers-reduced-motion: reduce)")?.matches)
    );
  } catch {
    return true;
  }
}

/** Fold one live event into the block list. Unknown ids create a block, so a dropped `start` is harmless. */
export function applyThinking(
  blocks: ThinkBlock[],
  raw: Record<string, unknown>,
): ThinkBlock[] {
  const ev = raw as unknown as ThinkingEvent;
  if (!ev || typeof ev.id !== "string" || !ev.id) return blocks;
  const index = blocks.findIndex((b) => b.id === ev.id);
  const old: ThinkBlock =
    index >= 0
      ? blocks[index]
      : {
          id: ev.id,
          done: false,
          context: "",
          source: "rules",
          text: "",
          startedAt: Date.now(),
        };
  if (old.done && ev.phase !== "end") return blocks;
  const next: ThinkBlock = {
    ...old,
    context:
      typeof ev.context === "string" && ev.context ? ev.context : old.context,
    source: typeof ev.source === "string" && ev.source ? ev.source : old.source,
    text: typeof ev.text === "string" ? ev.text : old.text,
    model: typeof ev.model === "string" && ev.model ? ev.model : old.model,
    redacted: Boolean(ev.redacted) || old.redacted,
    agent: knownAgent(ev.agent) ?? old.agent,
  };
  if (ev.phase === "start") {
    next.done = false;
    next.startedAt = Date.now();
  }
  if (ev.phase === "end") {
    next.done = true;
    next.action = typeof ev.action === "string" ? ev.action : old.action;
    next.ms =
      typeof ev.ms === "number" && Number.isFinite(ev.ms)
        ? ev.ms
        : Date.now() - old.startedAt;
    const rows = reactRows(ev.react, { thought: next.text });
    if (rows)
      next.react = { ...rows, observation: old.react?.observation || "" };
  }
  if (index < 0) return [...blocks, next];
  const copy = blocks.slice();
  copy[index] = next;
  return copy;
}

/** After a reload there are no live events: rebuild finished blocks from decision steps that carry a thought.
 * A step's `ms` is its tool time, not the decision time, so history blocks show no duration. */
export function blocksFromHistory(steps: Step[] | undefined): ThinkBlock[] {
  return (steps || [])
    .map((step, i) => ({ step, i }))
    .filter(
      ({ step }) =>
        typeof step.thought === "string" &&
        step.thought &&
        step.action !== "verify" &&
        !String(step.source || "").includes("verifier"),
    )
    .map(({ step, i }) => ({
      id: `hist-${i}`,
      done: true,
      context: String(step.summary || ""),
      source: String(step.source || "rules"),
      text: String(step.thought),
      model: typeof step.model === "string" ? step.model : undefined,
      action: typeof step.action === "string" ? step.action : undefined,
      ms: undefined,
      agent: knownAgent(step.agent),
      startedAt: 0,
      react: reactRows(step.react, {
        thought: String(step.thought),
        observation: String(step.summary || ""),
      }),
    }));
}

export function sourceLabel(block: Pick<ThinkBlock, "source" | "model">) {
  if (block.source.includes("fallback"))
    return "Local model unavailable, used the rules";
  if (block.source === "llm") return block.model || "Local AI reasoning";
  return "Rule-based";
}

export function durationLabel(ms?: number) {
  if (typeof ms !== "number" || !Number.isFinite(ms)) return "Recorded thought";
  if (ms < 100) return "Thought for under 0.1 s";
  return `Thought for ${(ms / 1000).toFixed(1)} s`;
}

export const actionLabel = (action?: string) =>
  action ? action.replaceAll("_", " ") : "";
