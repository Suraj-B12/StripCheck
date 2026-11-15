/** Agent names, self-check wording and decision labels (contract section 2a). */
export type AgentName =
  | "perception"
  | "investigator"
  | "verifier"
  | "supervisor";

export const AGENT_LABEL: Record<AgentName, string> = {
  perception: "Perception",
  investigator: "Investigator",
  verifier: "Verifier",
  supervisor: "Supervisor",
};

/** Same as agentOf, but undefined when the record names no known agent. */
export function knownAgent(value: unknown): AgentName | undefined {
  return typeof value === "string" && value in AGENT_LABEL
    ? (value as AgentName)
    : undefined;
}

/** Missing or unknown agent on an old record counts as the investigator. */
export function agentOf(value: unknown): AgentName {
  return knownAgent(value) ?? "investigator";
}

export const VIOLATION_TEXT: Record<string, string> = {
  R1: "the result label is not one of the four allowed",
  R2: "batch not confirmed by a person, QR or two photos",
  R3: "the alert type does not support this result",
  R4: "the search was not complete enough to say not listed",
  R5: "no traceable source, or wording outside the rules",
  R6: "the step or question limit was exceeded",
  R7: "a printed date conflict is unresolved",
  R8: "a detail used has no recorded source",
  R9: "list coverage and date were not stated",
  R10: "no reviewed translation for this language",
};

export function violationText(code: string): string {
  const key = String(code).trim().toUpperCase();
  return VIOLATION_TEXT[key] || `check ${key} was not met`;
}

export function decisionText(decision: unknown): string {
  if (decision === "ask_user") return "asked one more question";
  if (decision === "downgrade") return "gave can't verify";
  return "";
}

export const PLANNER_KEY = "stripcheck.planner";
