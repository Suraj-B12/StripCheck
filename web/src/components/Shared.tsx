import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import {
  X,
  ArrowUpRight,
  ShieldCheck,
  ScanLine,
  Check,
  CircleHelp,
  Volume2,
  Bookmark,
  Download,
} from "lucide-react";
import { PUBLIC_DEMO } from "../lib/environment";
import { labelName, readableDate } from "../lib/api";
import type { Snapshot, Step, Verdict } from "../lib/api";
export function Modal({
  title,
  onClose,
  children,
  wide = false,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
  wide?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = ref.current;
    dialog?.showModal();
    const old = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      dialog?.close();
      document.body.style.overflow = old;
    };
  }, []);
  return (
    <dialog
      className={`modal ${wide ? "wide" : ""}`}
      ref={ref}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal-head">
        <h2>{title}</h2>
        <button
          className="icon-button"
          onClick={onClose}
          aria-label="Close dialog"
        >
          <X size={22} />
        </button>
      </div>
      <div className="modal-body">{children}</div>
    </dialog>
  );
}
export function BatchStrip({
  batch,
  compact = false,
  chars,
}: {
  batch: string;
  compact?: boolean;
  chars?: { ch: string; state: string; alts: string[] }[];
}) {
  return (
    <div
      className={`batch-strip ${compact ? "compact" : ""}`}
      aria-label={`Batch ${batch}`}
    >
      <span className="strip-tag">BATCH</span>
      {(chars?.length
        ? chars
        : [...(batch || "•••••••")].map((ch) => ({
            ch,
            state: "read",
            alts: [],
          }))
      ).map((cell, i) => (
        <span
          className={`batch-cell cell-${cell.state}`}
          aria-hidden="true"
          key={i}
        >
          {cell.ch}
          {cell.state === "uncertain" && (
            <span className="cell-alts">
              {cell.alts.length ? cell.alts.join(" / ") : "?"}
            </span>
          )}
        </span>
      ))}
    </div>
  );
}
export function BlisterArt() {
  return (
    <div className="blister-scene" aria-hidden="true">
      <div className="orb orb-one" />
      <div className="orb orb-two" />
      <div className="blister-back" />
      <div className="blister">
        <div className="blister-brand">
          <ScanLine size={18} />
          <span>STRIPCHECK</span>
          <span>01 / 06</span>
        </div>
        <div className="blister-pills">
          {Array.from({ length: 6 }, (_, i) => (
            <div className="pill-well" key={i}>
              <span className="pill" />
            </div>
          ))}
        </div>
        <div className="blister-code">A CLOSER LOOK, EVERY TIME</div>
      </div>
      <div className="floating-tag">
        <ScanLine size={17} />
        <span>Every character matters</span>
        <span className="tag-dot" />
      </div>
    </div>
  );
}
export function Empty({
  icon,
  title,
  description,
  action,
}: {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon || <ScanLine size={30} />}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}
export function StepTimeline({ steps }: { steps: Step[] }) {
  return (
    <ol className="timeline">
      {steps.map((step, i) => (
        <li key={`${i}-${step.action}`}>
          <span className="step-index">{String(i + 1).padStart(2, "0")}</span>
          <div>
            <strong>{step.action.replaceAll("_", " ")}</strong>
            <p>{step.summary}</p>
          </div>
          <span className="step-source">
            {step.source?.includes("fallback")
              ? "Rules fallback"
              : step.source || "rules"}
          </span>
        </li>
      ))}
    </ol>
  );
}
export function Evidence({ evidence }: { evidence: Verdict["evidence"] }) {
  return (
    <div className="evidence">
      {Object.entries(evidence || {})
        .filter(([, v]) => typeof v === "string")
        .map(([key, value]) => (
          <span key={key}>
            {["match", "exact", "confirmed", "accept"].includes(
              String(value),
            ) ? (
              <Check size={14} />
            ) : (
              <CircleHelp size={14} />
            )}
            <b>{key.replaceAll("_", " ")}</b>{" "}
            {String(value).replaceAll("_", " ")}
          </span>
        ))}
    </div>
  );
}
export function VerdictCard({
  snapshot,
  onSave,
  onToast,
}: {
  snapshot: Snapshot;
  onSave: () => void;
  onToast: (s: string) => void;
}) {
  const result = snapshot.final!;
  const download = () => {
    const blob = new Blob([JSON.stringify(snapshot, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `stripcheck-${snapshot.thread_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };
  const speak = () => {
    if (!("speechSynthesis" in window)) {
      onToast("Read aloud is unavailable in this browser.");
      return;
    }
    speechSynthesis.cancel();
    const text = new SpeechSynthesisUtterance(
      `${result.headline}. ${result.explanation}. ${result.advice || ""}`,
    );
    text.lang = "en-IN";
    speechSynthesis.speak(text);
  };
  return (
    <section className={`verdict verdict-${result.label}`}>
      <div className="verdict-overline">
        <ShieldCheck size={20} />
        {PUBLIC_DEMO
          ? "RECORDED FICTIONAL EXAMPLE"
          : snapshot.demo
            ? "DEMONSTRATION RESULT"
            : "YOUR BATCH CHECK"}
      </div>
      <h2>{result.headline}</h2>
      <p className="verdict-explanation">{result.explanation}</p>
      {result.advice && <p className="verdict-advice">{result.advice}</p>}
      <Evidence evidence={result.evidence} />
      {result.citations?.length > 0 && (
        <div className="citations">
          {result.citations.map((c, i) => (
            <div key={i}>
              <span>
                {String(
                  c.title || c.source_title || c.source || "Source record",
                )}{" "}
                {c.list_month ? `· ${readableDate(c.list_month)}` : ""}{" "}
                {c.row_no ? `· Row ${c.row_no}` : ""}
              </span>
              {!PUBLIC_DEMO &&
                typeof (c.url || c.source_url) === "string" &&
                /^https:\/\//.test(String(c.url || c.source_url)) && (
                  <a
                    href={String(c.url || c.source_url)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View source <ArrowUpRight size={15} />
                  </a>
                )}
            </div>
          ))}
        </div>
      )}
      <div className="button-row">
        <button className="button primary" onClick={onSave}>
          <Bookmark size={18} />
          {PUBLIC_DEMO ? "Save example" : "Save to cabinet"}
        </button>
        <button
          className="icon-button bordered"
          aria-label="Read result aloud"
          onClick={speak}
        >
          <Volume2 size={20} />
        </button>
        <button
          className="icon-button bordered"
          aria-label="Download check report"
          onClick={download}
        >
          <Download size={20} />
        </button>
      </div>
    </section>
  );
}
export function VerdictBadge({ label }: { label: string }) {
  return (
    <span className={`verdict-badge verdict-${label}`}>
      <span />
      {labelName(label)}
    </span>
  );
}
