import { useEffect, useId, useRef, useState } from "react";
import type { ClipboardEvent, KeyboardEvent } from "react";
import { ArrowRight, Camera, Info, Keyboard, ScanLine } from "lucide-react";
import { reducedMotion } from "../lib/thinking";
import { batchKey, differingIndices, safeCrop } from "../lib/ask";
import type { Fields, Pending } from "../lib/api";

const TYPING_MS = 600;
const CANT_TELL = /^(can'?t|cannot|can’t) tell$/i;
const OPTION_ACTIONS = /^(type the whole batch|add printed details)$/i;

export function AgentAvatar({ typing = false }: { typing?: boolean }) {
  return (
    <span
      className={`agent-avatar ${typing ? "typing" : ""}`}
      aria-hidden="true"
    >
      <ScanLine size={17} />
    </span>
  );
}

export function TypingDots({ label = "StripCheck is writing" }) {
  return (
    <span className="typing-dots" role="status" aria-label={label}>
      <span />
      <span />
      <span />
    </span>
  );
}

function Tick() {
  return (
    <svg className="answer-tick" viewBox="0 0 20 20" aria-hidden="true">
      <circle cx="10" cy="10" r="8.5" />
      <path d="M6 10.4 8.7 13 14 7.4" />
    </svg>
  );
}

/** OTP-style boxes for the look-alike positions; other characters stay as fixed tiles. */
export function CharBoxes({
  batch,
  positions,
  hints = {},
  onSubmit,
  onWhole,
}: {
  batch: string;
  positions: number[];
  hints?: Record<number, string>;
  onSubmit: (chars: Record<string, string>) => void;
  /** A paste that does not fit the boxes: hand it to the whole-batch form. */
  onWhole?: (text: string) => void;
}) {
  const hintId = useId();
  const key = batchKey(batch);
  const open = [...new Set(positions)]
    .filter((p) => Number.isInteger(p) && p >= 1 && p <= key.length)
    .sort((a, b) => a - b);
  const [values, setValues] = useState<Record<number, string>>({});
  const [misfit, setMisfit] = useState(false);
  const refs = useRef(new Map<number, HTMLInputElement>());
  const submitRef = useRef<HTMLButtonElement>(null);
  const toSubmit = useRef(false);
  const focusAt = (index: number) => {
    const pos = open[index];
    // The submit button enables on the next render, so focus it from an effect.
    if (pos === undefined) toSubmit.current = true;
    else refs.current.get(pos)?.focus();
  };
  useEffect(() => {
    if (!toSubmit.current) return;
    toSubmit.current = false;
    submitRef.current?.focus();
  }, [values]);
  const complete = open.every((p) => values[p]);
  const fill = (start: number, text: string) => {
    const chars = batchKey(text);
    if (!chars) return;
    const next = { ...values };
    if (chars.length === key.length) {
      for (const p of open) next[p] = chars[p - 1];
      setValues(next);
      setMisfit(false);
      focusAt(open.length);
      return;
    }
    if (chars.length > open.length - start) {
      // A whole batch of another length: never spread it over the doubted boxes.
      if (onWhole) onWhole(text);
      else setMisfit(true);
      return;
    }
    setMisfit(false);
    let i = start;
    for (const ch of chars) {
      if (i >= open.length) break;
      next[open[i]] = ch;
      i += 1;
    }
    setValues(next);
    focusAt(i);
  };
  const onKey = (e: KeyboardEvent<HTMLInputElement>, index: number) => {
    const pos = open[index];
    if (e.key === "Backspace" && !values[pos] && index > 0) {
      e.preventDefault();
      setValues({ ...values, [open[index - 1]]: "" });
      focusAt(index - 1);
    } else if (e.key === "ArrowLeft" && index > 0) {
      e.preventDefault();
      focusAt(index - 1);
    } else if (e.key === "ArrowRight" && index < open.length - 1) {
      e.preventDefault();
      focusAt(index + 1);
    }
  };
  return (
    <form
      className="otp-form"
      onSubmit={(e) => {
        e.preventDefault();
        if (complete)
          onSubmit(Object.fromEntries(open.map((p) => [String(p), values[p]])));
      }}
    >
      <div
        className="otp-row"
        role="group"
        aria-label={`Batch characters, read as ${[...key]
          .map((ch, i) => (open.includes(i + 1) ? "unclear" : ch))
          .join(" ")}. Type the ${open.length} unclear ${
          open.length === 1 ? "character" : "characters"
        } exactly as printed.`}
      >
        {[...key].map((ch, i) => {
          const pos = i + 1;
          const index = open.indexOf(pos);
          if (index < 0)
            return (
              <span className="otp-fixed" aria-hidden="true" key={pos}>
                {ch}
              </span>
            );
          return (
            <span className="otp-slot" key={pos}>
              <input
                ref={(el) => {
                  if (el) refs.current.set(pos, el);
                  else refs.current.delete(pos);
                }}
                className={`otp-box ${values[pos] ? "filled" : ""}`}
                value={values[pos] || ""}
                inputMode="text"
                autoComplete="off"
                autoCapitalize="characters"
                spellCheck={false}
                aria-label={`Character ${pos} of ${key.length}`}
                aria-describedby={hints[pos] ? `${hintId}-${pos}` : undefined}
                data-autofocus={index === 0 ? "" : undefined}
                onFocus={(e) => e.target.select()}
                onKeyDown={(e) => onKey(e, index)}
                onPaste={(e: ClipboardEvent<HTMLInputElement>) => {
                  e.preventDefault();
                  fill(index, e.clipboardData.getData("text"));
                }}
                onChange={(e) => {
                  const typed = batchKey(e.target.value);
                  if (!typed) {
                    setValues({ ...values, [pos]: "" });
                    return;
                  }
                  const prev = values[pos] || "";
                  if (typed.length > 2 || (typed.length === 2 && !prev)) {
                    fill(index, typed);
                    return;
                  }
                  // Keep the newly typed character, wherever the caret was.
                  const ch =
                    typed.length === 2 && typed.startsWith(prev)
                      ? typed[1]
                      : typed.length === 2 && typed.endsWith(prev)
                        ? typed[0]
                        : typed[typed.length - 1];
                  setMisfit(false);
                  setValues({ ...values, [pos]: ch });
                  focusAt(index + 1);
                }}
              />
              <span className="otp-pos" aria-hidden="true">
                {hints[pos] || pos}
              </span>
              {hints[pos] && (
                <span className="visually-hidden" id={`${hintId}-${pos}`}>
                  Could be {hints[pos].split("/").join(" or ")}
                </span>
              )}
            </span>
          );
        })}
      </div>
      {misfit && (
        <p role="alert" className="ask-error">
          This batch has a different length. Type the whole batch instead.
        </p>
      )}
      <button
        ref={submitRef}
        className="button primary"
        disabled={!complete}
        type="submit"
      >
        Confirm these characters <ArrowRight size={17} />
      </button>
    </form>
  );
}

/** Large choice cards with the differing characters highlighted, plus "Can't tell". */
export function ChoiceCards({
  options,
  positions = [],
  onChoose,
  onCantTell,
}: {
  options: string[];
  positions?: number[];
  onChoose: (value: string) => void;
  onCantTell: () => void;
}) {
  const [chosen, setChosen] = useState("");
  const [a = "", b = ""] = options;
  return (
    <div
      className="choice-group"
      role="group"
      aria-label="Which is printed on your pack?"
    >
      <div className="choice-cards">
        {options.map((value, n) => {
          const diff = differingIndices(value, n === 0 ? b : a, positions);
          return (
            <button
              key={value}
              type="button"
              className={`choice-card ${chosen === value ? "chosen" : ""}`}
              aria-label={value}
              data-autofocus={n === 0 ? "" : undefined}
              disabled={Boolean(chosen)}
              onClick={() => {
                setChosen(value);
                onChoose(value);
              }}
            >
              <span className="choice-letter" aria-hidden="true">
                {String.fromCharCode(65 + n)}
              </span>
              <span className="choice-value" aria-hidden="true">
                {[...value].map((ch, i) =>
                  diff.has(i) ? (
                    <mark key={i}>{ch}</mark>
                  ) : (
                    <span key={i}>{ch}</span>
                  ),
                )}
              </span>
            </button>
          );
        })}
      </div>
      <button
        type="button"
        className="button secondary cant-tell"
        disabled={Boolean(chosen)}
        onClick={onCantTell}
      >
        Can’t tell
      </button>
    </div>
  );
}

function TypedBatch({
  onSubmit,
  label = "Type the full batch exactly as printed",
  initial = "",
}: {
  onSubmit: (typed: string) => void;
  label?: string;
  initial?: string;
}) {
  const [value, setValue] = useState(initial.toUpperCase().slice(0, 50));
  return (
    <form
      className="typed-batch"
      onSubmit={(e) => {
        e.preventDefault();
        if (value.trim()) onSubmit(value.trim());
      }}
    >
      <label className="field">
        <span>{label}</span>
        <input
          value={value}
          onChange={(e) => setValue(e.target.value.toUpperCase())}
          maxLength={50}
          autoComplete="off"
          spellCheck={false}
          className="batch-input"
          data-autofocus=""
        />
      </label>
      <button className="button primary" disabled={!value.trim()}>
        Confirm printed batch <ArrowRight size={17} />
      </button>
    </form>
  );
}

function Magnifier({ src }: { src: string }) {
  const [failed, setFailed] = useState(false);
  if (failed) return null;
  return (
    <figure className="ask-crop">
      <div className="crop-frame">
        <img
          src={src}
          alt="The batch line from your photo, enlarged"
          onError={() => setFailed(true)}
        />
        <span className="crop-scan" aria-hidden="true" />
      </div>
      <figcaption>From your photo</figcaption>
    </figure>
  );
}

const FIELD_LABELS = {
  product: "Product",
  maker: "Manufacturer",
  mfg: "Manufactured",
  exp: "Expires",
} as const;

/** The agent's question, as a short conversation. Remount (key) per question. */
export function AskConversation({
  pending,
  fields,
  hints,
  onAnswer,
  onCarton,
}: {
  pending: Pending;
  fields: Fields;
  hints?: Record<number, string>;
  onAnswer: (value: Record<string, unknown>) => void;
  onCarton: (file: File) => void;
}) {
  const kind = String(pending.kind || "");
  const error = typeof pending.error === "string" ? pending.error : "";
  const [typing, setTyping] = useState(() => !error && !reducedMotion());
  const [whole, setWhole] = useState(false);
  const [prefill, setPrefill] = useState("");
  // Fill the live region after mount: a region that mounts with text is often not announced.
  const [announce, setAnnounce] = useState("");
  const [details, setDetails] = useState<Fields>({ ...fields });
  const bubble = useRef<HTMLDivElement>(null);
  const cartonRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (!typing) return;
    const timer = setTimeout(() => setTyping(false), TYPING_MS);
    return () => clearTimeout(timer);
  }, [typing]);
  useEffect(() => {
    if (typing) return;
    bubble.current
      ?.querySelector<HTMLElement>("[data-autofocus]")
      ?.focus({ preventScroll: true });
  }, [typing, whole]);
  const question = String(pending.question || "Confirm the printed details");
  const used = Number(pending.asks_used);
  const max = Number(pending.asks_max);
  const counter =
    Number.isFinite(used) && Number.isFinite(max) && used > 0 && max > 0
      ? `Question ${Math.min(used, max)} of ${max}`
      : "";
  const crop = safeCrop(pending.crop);
  const positions = Array.isArray(pending.positions)
    ? (pending.positions as unknown[]).map(Number).filter(Number.isInteger)
    : [];
  const options = (Array.isArray(pending.options) ? pending.options : [])
    .map((o) =>
      typeof o === "object" && o
        ? String(
            (o as Record<string, unknown>).value ??
              (o as Record<string, unknown>).label ??
              "",
          )
        : String(o),
    )
    .filter((o) => o && !CANT_TELL.test(o) && !OPTION_ACTIONS.test(o));
  const batch = batchKey(String(pending.batch ?? fields.batch ?? ""));
  const otp =
    kind === "confirm_batch" &&
    positions.length > 0 &&
    positions.every((p) => p >= 1 && p <= batch.length);
  const choices =
    (kind === "confirm_char" || kind === "confirm_field") &&
    options.length >= 2;
  const skip = () => onAnswer({ skip: true });
  const spoken = `${counter ? `${counter}. ` : ""}${question}`;
  useEffect(() => {
    if (typing) return;
    const timer = setTimeout(() => setAnnounce(spoken), 50);
    return () => clearTimeout(timer);
  }, [typing, spoken]);
  return (
    <section className="ask-convo" aria-label="Question from StripCheck">
      <p className="visually-hidden" aria-live="polite">
        {typing ? "" : announce}
      </p>
      <div className="convo-row agent">
        <AgentAvatar typing={typing} />
        {typing ? (
          <div className="bubble agent-bubble typing-bubble">
            <TypingDots />
          </div>
        ) : (
          <div
            ref={bubble}
            className={`bubble agent-bubble ask-bubble ${error ? "shake" : ""}`}
          >
            <div className="bubble-meta">
              <span>StripCheck asks</span>
              {counter && <span className="ask-counter">{counter}</span>}
            </div>
            <h3>{question}</h3>
            {pending.reason && (
              <p className="ask-why">
                <Info size={14} aria-hidden="true" />
                <span>
                  <b>Why I’m asking.</b> {String(pending.reason)}
                </span>
              </p>
            )}
            {error && (
              <p role="alert" className="ask-error">
                {error}
              </p>
            )}
            {crop && <Magnifier src={crop} />}
            {otp && !whole && (
              <CharBoxes
                batch={batch}
                positions={positions}
                hints={hints}
                onSubmit={(chars) => onAnswer({ chars })}
                onWhole={(text) => {
                  setPrefill(text);
                  setWhole(true);
                }}
              />
            )}
            {choices && !whole && (
              <ChoiceCards
                options={options.slice(0, 2)}
                positions={positions}
                onChoose={(choice) => onAnswer({ choice })}
                onCantTell={skip}
              />
            )}
            {(kind === "type_batch" ||
              (kind === "confirm_batch" && (!otp || whole)) ||
              (kind === "confirm_char" && (!choices || whole))) && (
              <TypedBatch
                initial={prefill}
                onSubmit={(typed) => onAnswer({ typed })}
              />
            )}
            {(otp || (kind === "confirm_char" && choices)) && (
              <button
                type="button"
                className="text-button whole-toggle"
                onClick={() => setWhole(!whole)}
              >
                <Keyboard size={15} aria-hidden="true" />
                {whole
                  ? otp
                    ? "Confirm single characters instead"
                    : "Choose from the two options instead"
                  : "Type the whole batch instead"}
              </button>
            )}
            {kind === "box_photo" && (
              <div className="carton-upload">
                <button
                  className="button secondary"
                  type="button"
                  onClick={() => cartonRef.current?.click()}
                >
                  <Camera size={18} />
                  Add a carton photo
                </button>
                <input
                  ref={cartonRef}
                  className="visually-hidden"
                  aria-label="Upload carton photo"
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    e.target.value = "";
                    if (file) onCarton(file);
                  }}
                />
              </div>
            )}
            {(kind === "box_photo" ||
              kind === "provide_fields" ||
              kind === "confirm_product" ||
              kind === "type_fields") && (
              <form
                className="fields-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  onAnswer({ fields: details });
                }}
              >
                <p>Add the details you can read on the carton.</p>
                {(
                  Object.keys(FIELD_LABELS) as (keyof typeof FIELD_LABELS)[]
                ).map((k, i) => (
                  <label key={k} className="field">
                    <span>{FIELD_LABELS[k]}</span>
                    <input
                      value={details[k] || ""}
                      data-autofocus={
                        i === 0 && kind !== "box_photo" ? "" : undefined
                      }
                      onChange={(e) =>
                        setDetails({ ...details, [k]: e.target.value })
                      }
                    />
                  </label>
                ))}
                <button className="button primary">Check these details</button>
              </form>
            )}
            <button
              className="text-button skip-button"
              type="button"
              onClick={skip}
            >
              I can’t confirm this detail
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

/** What was asked, the user's answer with a tick, then "Checking again" while the agent works. */
export function AnsweredThread({
  question,
  answer,
  busy,
}: {
  question: string;
  answer: string;
  busy: boolean;
}) {
  return (
    <section className="ask-convo answered" aria-label="Your answer">
      <p className="visually-hidden" aria-live="polite">
        {busy ? "Answer sent. Checking again." : ""}
      </p>
      {question && (
        <div className="convo-row agent">
          <AgentAvatar />
          <div className="bubble agent-bubble past">{question}</div>
        </div>
      )}
      <div className="convo-row user">
        <div className="bubble user-bubble">
          <Tick />
          <span>{answer}</span>
        </div>
      </div>
      {busy && (
        <div className="convo-row agent">
          <AgentAvatar typing />
          <div className="bubble agent-bubble checking">
            <TypingDots label="Checking again" />
            <span className="think-shimmer">Checking again</span>
          </div>
        </div>
      )}
    </section>
  );
}
