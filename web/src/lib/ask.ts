export const batchKey = (value: string) =>
  String(value || "")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "");

/** Plain text of the user's answer, for the conversation thread. */
export function answerSummary(value: unknown): string {
  const answer = (value || {}) as Record<string, unknown>;
  if (answer.skip) return "I can’t confirm this detail.";
  if (answer.carton) return "I added a carton photo.";
  if (typeof answer.typed === "string") return answer.typed;
  if (typeof answer.choice === "string") return answer.choice;
  if (answer.chars && typeof answer.chars === "object")
    return Object.entries(answer.chars as Record<string, string>)
      .map(([pos, ch]) => `Position ${pos}: ${ch}`)
      .join(" · ");
  if (answer.fields) return "I added the printed details.";
  return "Answer sent.";
}

/** Raw indices (0-based) of `a` to highlight against `b`.
 * Both are compared as batch keys (separators removed), so a hyphen never shifts the mark;
 * when the keys differ in length, the server's 1-based key `positions` are used. Separators are never marked. */
export function differingIndices(
  a: string,
  b: string,
  positions: number[] = [],
) {
  const ka = batchKey(a);
  const kb = batchKey(b);
  const byChar = ka.length === kb.length && ka !== kb;
  const out = new Set<number>();
  let k = 0;
  [...a].forEach((ch, i) => {
    if (!/[A-Z0-9]/i.test(ch)) return;
    if (byChar ? ka[k] !== kb[k] : positions.includes(k + 1)) out.add(i);
    k += 1;
  });
  return out;
}

export function safeCrop(value: unknown): string {
  const url = typeof value === "string" ? value : "";
  return /^\/api\/crops\/[A-Za-z0-9_-]+\.png$/.test(url) ? url : "";
}
