import { Eye, Search, ShieldQuestion, Workflow } from "lucide-react";
import { AGENT_LABEL } from "../lib/agents";
import type { AgentName } from "../lib/agents";

const ICON = {
  perception: Eye,
  investigator: Search,
  verifier: ShieldQuestion,
  supervisor: Workflow,
};

/** Small labelled badge naming the agent that acted. */
export function AgentBadge({ agent }: { agent: AgentName }) {
  const Icon = ICON[agent];
  return (
    <span className={`agent-badge agent-${agent}`} data-agent={agent}>
      <Icon size={11} aria-hidden="true" />
      {AGENT_LABEL[agent]}
    </span>
  );
}
