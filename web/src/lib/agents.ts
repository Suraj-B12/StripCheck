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
  R1: "the draft named a result the evidence does not support",
  R2: "batch not confirmed by a person, QR or two photos",
  R3: "the maker on the pack was not checked against the listing",
  R4: "a look-alike character in the batch was not resolved",
  R5: "a needed pack detail was missing",
  R6: "a cited listing could not be traced to a stored record",
  R7: "the draft wording was outside the approved wording",
  R8: "the draft claimed more than the evidence shows",
  R9: "the list data was out of date",
  R10: "the checks did not agree with each other",
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
