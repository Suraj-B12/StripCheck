import { useEffect, useId, useRef, useState } from "react";
import { ChevronDown, ShieldAlert } from "lucide-react";
import {
  TRANSPARENCY_NOTE,
  actionLabel,
  durationLabel,
  reducedMotion,
  sourceLabel,
} from "../lib/thinking";
import type { ThinkBlock } from "../lib/thinking";

/** Reveal streamed text a few characters per frame so deltas read as typing, not jumps. */
function useReveal(target: string, active: boolean) {
  const animate = active && !reducedMotion();
  const [shown, setShown] = useState(0);
  const targetRef = useRef(target);
  useEffect(() => {
    targetRef.current = target;
  }, [target]);
  useEffect(() => {
    if (!animate) return;
    let frame = 0;
    const tick = () => {
      setShown((n) => {
        const goal = targetRef.current.length;
        return n >= goal ? goal : n + Math.max(1, Math.ceil((goal - n) / 6));
      });
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [animate]);
  return animate ? target.slice(0, shown) : target;
}

function ThinkingOrb() {
  return <span className="think-orb" aria-hidden="true" />;
}

function ThoughtBlock({ block }: { block: ThinkBlock }) {
  // A streaming block is always open; once done it collapses until the user opens it.
  const [open, setOpen] = useState(false);
  const bodyId = useId();
  const text = useReveal(block.text, !block.done);
  const expanded = !block.done || open;
  return (
    <li
      className={`think-block ${block.done ? "is-done" : "is-streaming"} ${
        block.redacted ? "is-redacted" : ""
      }`}
    >
      {block.done ? (
        <button
          type="button"
          className="think-head"
          aria-expanded={expanded}
          aria-controls={bodyId}
          onClick={() => setOpen(!open)}
        >
          <span className="think-dot" aria-hidden="true" />
          <span className="think-duration">{durationLabel(block.ms)}</span>
          <span className="think-source">{sourceLabel(block)}</span>
          {block.action && (
            <span className="think-chip">{actionLabel(block.action)}</span>
          )}
          <ChevronDown size={15} className="think-chevron" aria-hidden="true" />
        </button>
      ) : (
        <div className="think-head is-live">
          <ThinkingOrb />
          <span className="think-shimmer">Thinking</span>
          <span className="think-source">{sourceLabel(block)}</span>
        </div>
      )}
      <div
        className={`think-body ${expanded ? "open" : ""}`}
        id={bodyId}
        aria-hidden={!expanded}
      >
        <div className="think-body-inner">
          {block.context && <p className="think-context">{block.context}</p>}
          {block.redacted && (
            <p className="think-withheld">
              <ShieldAlert size={14} aria-hidden="true" />
              Part of the model's wording was withheld by the safety wording
              rules.
            </p>
          )}
          {(text || !block.done) && (
            <p className={`think-text ${block.done ? "" : "streaming"}`}>
              {text}
            </p>
          )}
        </div>
      </div>
    </li>
  );
}

/** Live and recorded reasoning. `live` shows a working row when no block is streaming. */
export function ThinkingPanel({
  blocks,
  live = false,
  idleLabel = "Checking the available evidence",
  note = true,
}: {
  blocks: ThinkBlock[];
  live?: boolean;
  idleLabel?: string;
  note?: boolean;
}) {
  const last = [...blocks].reverse().find((b) => b.done);
  const streaming = blocks.some((b) => !b.done);
  if (!blocks.length && !live) return null;
  return (
    <section
      className={`thinking-panel ${live ? "is-live" : ""}`}
      aria-label="Agent reasoning"
    >
      {blocks.length > 0 && (
        <ol className="think-list">
          {blocks.map((block) => (
            <ThoughtBlock key={block.id} block={block} />
          ))}
        </ol>
      )}
      {live && !streaming && (
        <div className="think-head is-live think-idle">
          <ThinkingOrb />
          <span className="think-shimmer">{idleLabel}</span>
        </div>
      )}
      <p className="visually-hidden" aria-live="polite">
        {last
          ? `Finished thinking. ${durationLabel(last.ms)}. ${sourceLabel(last)}${
              last.action ? `. Next: ${actionLabel(last.action)}` : ""
            }.`
          : ""}
      </p>
      {note && blocks.length > 0 && (
        <p className="think-note">{TRANSPARENCY_NOTE}</p>
      )}
    </section>
  );
}
