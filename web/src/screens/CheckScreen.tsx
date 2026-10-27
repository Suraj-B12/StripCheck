import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowRight,
  Camera,
  Upload,
  Keyboard,
  ChevronDown,
  ChevronRight,
  Play,
  ScanLine,
  ShieldCheck,
  Fingerprint,
  CircleHelp,
  X,
  RotateCcw,
  LoaderCircle,
  ImagePlus,
} from "lucide-react";
import { PUBLIC_DEMO, PROJECT_URL, appHref } from "../lib/environment";
import { createRequestGate, storage } from "../lib/runtime";
import { api, emptyFields, json, stream } from "../lib/api";
import type { Fields, Health, Snapshot } from "../lib/api";
import {
  BatchStrip,
  BlisterArt,
  Modal,
  StepTimeline,
  VerdictCard,
} from "../components/Shared";
type Demo = {
  id: string;
  name?: string;
  title?: string;
  description: string;
  fields: Fields;
  expected: string;
};
function guidedAnswerText(answer: Record<string, unknown>) {
  if (answer.skip) return "This example leaves the detail unconfirmed.";
  const batch = answer.typed || answer.choice;
  if (typeof batch === "string") return `Recorded answer: ${batch}`;
  if (answer.fields && typeof answer.fields === "object") {
    const labels: Record<string, string> = {
      product: "Product",
      brand: "Brand",
      maker: "Manufacturer",
      batch: "Batch",
      mfg: "Manufactured",
      exp: "Expires",
    };
    const details = Object.entries(answer.fields)
      .filter(
        ([key, value]) => labels[key] && typeof value === "string" && value,
      )
      .map(([key, value]) => `${labels[key]}: ${value}`);
    if (details.length) return details.join(" · ");
  }
  return "The next step uses the response recorded for this scenario.";
}
export default function CheckScreen({
  health,
  toast,
}: {
  health: Health | null;
  toast: (message: string) => void;
}) {
  const [fields, setFields] = useState<Fields>({ ...emptyFields });
  const [advanced, setAdvanced] = useState(false);
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const preview = useMemo(
    () => (photo ? URL.createObjectURL(photo) : ""),
    [photo],
  );
  const [drag, setDrag] = useState(false);
  const [demoOpen, setDemoOpen] = useState(false);
  const [demos, setDemos] = useState<Demo[]>([]);
  const [help, setHelp] = useState(false);
  const [answer, setAnswer] = useState("");
  const [details, setDetails] = useState<Fields>({ ...emptyFields });
  const uploadRef = useRef<HTMLInputElement>(null);
  const cameraRef = useRef<HTMLInputElement>(null);
  const cartonRef = useRef<HTMLInputElement>(null);
  const batchRef = useRef<HTMLInputElement>(null);
  const resultRef = useRef<HTMLDivElement>(null);
  const requests = useRef(createRequestGate());
  const demoFields = useRef(false);
  const acceptSnapshot = (value: Snapshot) => {
    demoFields.current = Boolean(value.demo);
    setSnapshot(value);
    setFields({ ...emptyFields, ...value.fields });
    setDetails({ ...emptyFields, ...value.fields });
    setAdvanced(
      Boolean(
        value.fields?.maker ||
        value.fields?.brand ||
        value.fields?.mfg ||
        value.fields?.exp,
      ),
    );
  };
  useEffect(() => {
    const gate = requests.current;
    const signal = gate.begin();
    const id = storage.get("stripcheck.current");
    if (id)
      api<Snapshot>(`/api/checks/${encodeURIComponent(id)}`, { signal })
        .then((s) => {
          if (!gate.isCurrent(signal)) return;
          acceptSnapshot(s);
        })
        .catch(() => {
          /* keep saved id for a reconnect after temporary failure */
        });
    return () => gate.cancel();
  }, []);
  useEffect(
    () => () => {
      if (preview) URL.revokeObjectURL(preview);
    },
    [preview],
  );
  useEffect(() => {
    if (demoOpen)
      api<{ items: Demo[] }>("/api/demo/cases")
        .then((d) => setDemos(d.items))
        .catch((e) => setError(e.message));
  }, [demoOpen]);
  const editFields = (patch: Partial<Fields>) => {
    if (busy) return;
    requests.current.cancel();
    storage.remove("stripcheck.current");
    setSnapshot(null);
    const clearDemo = demoFields.current;
    demoFields.current = false;
    if (clearDemo) {
      setDetails({ ...emptyFields });
      setAdvanced(["maker", "brand", "mfg", "exp"].some((key) => key in patch));
    }
    setFields((current) => ({
      ...(clearDemo ? emptyFields : current),
      ...patch,
    }));
  };
  const pick = (file?: File) => {
    if (PUBLIC_DEMO || !file || busy) return;
    if (!file.type.startsWith("image/")) {
      setError("Choose a photograph in JPG, PNG, WebP or HEIC format.");
      return;
    }
    if (file.size > 15 * 1024 * 1024) {
      setError("This photo is too large. Choose one under 15 MB.");
      return;
    }
    requests.current.cancel();
    storage.remove("stripcheck.current");
    setPhoto(file);
    demoFields.current = false;
    setAdvanced(false);
    setFields({ ...emptyFields });
    setError("");
    setSnapshot(null);
  };
  const execute = async (url: string, init: RequestInit) => {
    const gate = requests.current;
    const signal = gate.begin();
    setBusy(true);
    setError("");
    setAnswer("");
    let tid = "";
    let receivedSnapshot = false;
    try {
      await stream(url, { ...init, signal }, (event, data) => {
        if (!gate.isCurrent(signal)) return;
        if (data.thread_id) {
          tid = String(data.thread_id);
          storage.set("stripcheck.current", tid);
        }
        if (event === "snapshot" && data.snapshot) {
          const latest = data.snapshot as Snapshot;
          receivedSnapshot = true;
          tid = latest.thread_id || tid;
          if (tid) storage.set("stripcheck.current", tid);
          acceptSnapshot(latest);
        }
        if (event === "error" && !data.recoverable)
          throw new Error(String(data.message));
        if (event === "step")
          setSnapshot((s) =>
            s
              ? {
                  ...s,
                  history: [
                    ...(s.history || []),
                    data as unknown as Snapshot["history"][number],
                  ],
                }
              : s,
          );
        if (event === "fields")
          setSnapshot((s) =>
            s ? { ...s, fields: (data.fields || data) as Fields } : s,
          );
        if (event === "interrupt")
          setSnapshot((s) =>
            s ? { ...s, status: "waiting", pending: data } : s,
          );
        if (event === "final")
          setSnapshot((s) =>
            s
              ? {
                  ...s,
                  status: "done",
                  pending: null,
                  final: data as unknown as Snapshot["final"],
                }
              : s,
          );
      });
      if (!gate.isCurrent(signal)) return;
      if (tid && !receivedSnapshot) {
        const s = await api<Snapshot>(
          `/api/checks/${encodeURIComponent(tid)}`,
          { signal },
        );
        if (!gate.isCurrent(signal)) return;
        acceptSnapshot(s);
      }
      setTimeout(
        () =>
          gate.isCurrent(signal) &&
          resultRef.current?.scrollIntoView({
            behavior: window.matchMedia("(prefers-reduced-motion: reduce)")
              .matches
              ? "instant"
              : "smooth",
            block: "start",
          }),
        70,
      );
    } catch (e) {
      if (gate.isCurrent(signal)) setError((e as Error).message);
    } finally {
      if (gate.isCurrent(signal)) setBusy(false);
    }
  };
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (PUBLIC_DEMO || busy) return;
    if (!photo && !fields.batch.trim()) {
      batchRef.current?.focus();
      setError("Enter the batch number printed on your pack, or add a photo.");
      return;
    }
    setSnapshot({ thread_id: "", status: "running", fields, history: [] });
    if (photo) {
      const form = new FormData();
      form.append("images", photo);
      for (const [k, v] of Object.entries(fields))
        if (v) form.append(k, String(v));
      execute("/api/checks", { method: "POST", body: form });
    } else execute("/api/checks", json({ mode: "text", ...fields }));
  };
  const startDemo = (demo: Demo) => {
    setDemoOpen(false);
    setPhoto(null);
    demoFields.current = true;
    setAdvanced(
      Boolean(
        demo.fields.maker ||
        demo.fields.brand ||
        demo.fields.mfg ||
        demo.fields.exp,
      ),
    );
    setFields({ ...emptyFields, ...demo.fields });
    setSnapshot({
      thread_id: "",
      status: "running",
      fields: demo.fields,
      history: [],
      demo: true,
    });
    execute("/api/demo/checks", json({ case_id: demo.id }));
  };
  const reset = () => {
    requests.current.cancel();
    setBusy(false);
    setSnapshot(null);
    setFields({ ...emptyFields });
    demoFields.current = false;
    setAdvanced(false);
    setPhoto(null);
    setError("");
    setAnswer("");
    storage.remove("stripcheck.current");
    window.scrollTo({
      top: 0,
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "instant"
        : "smooth",
    });
  };
  const save = async () => {
    try {
      await api("/api/cabinet", json({ thread_id: snapshot?.thread_id }));
      toast(
        PUBLIC_DEMO
          ? "Example saved in this browser tab"
          : "Saved to your cabinet",
      );
    } catch (e) {
      toast((e as Error).message);
    }
  };
  const resume = (value: unknown) =>
    snapshot &&
    execute(
      `/api/checks/${encodeURIComponent(snapshot.thread_id)}/resume`,
      json(value),
    );
  const pending = snapshot?.pending;
  const kind = String(pending?.kind || "");
  return (
    <div className="check-page page-enter">
      <section className="hero">
        <div className="eyebrow">
          <span className="small-scan">
            <ScanLine size={15} />
          </span>
          A LITTLE CLARITY GOES A LONG WAY
        </div>
        <h1>
          Small details.
          <br />
          <span>Clearer answers.</span>
        </h1>
        <p>
          {PUBLIC_DEMO ? (
            <>
              See how a closer look changes the answer.
              <br className="desktop-break" /> Explore 11 guided examples with
              fictional medicine packs.
            </>
          ) : (
            <>
              A closer look at your medicine. Check the exact batch against
              <br className="desktop-break" /> official drug quality alerts, one
              pack at a time.
            </>
          )}
        </p>
      </section>
      {PUBLIC_DEMO ? (
        <section className="check-workspace glass-card public-demo-workspace">
          <div className="capture-panel">
            <div className="panel-topline">
              <span>
                <span className="number-dot">01</span>THE IDEA
              </span>
              <ScanLine size={20} />
            </div>
            <BlisterArt />
            <div className="capture-copy">
              <h2>A little detail. A different answer.</h2>
              <p>
                See why the exact batch, readable evidence and a human
                confirmation matter.
              </p>
            </div>
            <span className="demo-tag">FICTIONAL EXAMPLE PACKS</span>
          </div>
          <div className="details-panel demo-intro-panel">
            <div className="panel-topline">
              <span>
                <span className="number-dot">02</span>TAKE A LOOK
              </span>
              <Play size={20} />
            </div>
            <h2>
              Meet the checks.
              <br />
              Try the examples.
            </h2>
            <p>
              Follow a clear match, a hard-to-read character or missing
              evidence. Each guided story shows the questions and its recorded
              outcome.
            </p>
            <button
              className="button primary check-submit"
              onClick={() => setDemoOpen(true)}
              disabled={busy}
            >
              <Play size={19} />
              Try a demo pack
              <ArrowRight size={19} />
            </button>
            <p className="demo-boundary">
              This public website cannot check your medicine or accept photos.
              No real pack details are requested.
            </p>
            <a
              className="button secondary"
              href={PROJECT_URL}
              target="_blank"
              rel="noreferrer"
            >
              Get the full local app <ArrowRight size={18} />
            </a>
            <p className="private-note">
              <Fingerprint size={16} />
              Example activity stays in this browser tab.
            </p>
          </div>
        </section>
      ) : (
        <form className="check-workspace glass-card" onSubmit={submit}>
          <div
            className={`capture-panel ${drag ? "dragging" : ""}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDrag(true);
            }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDrag(false);
              pick(e.dataTransfer.files[0]);
            }}
          >
            <div className="panel-topline">
              <span>
                <span className="number-dot">01</span>THE PACK
              </span>
              <button
                className="icon-button"
                type="button"
                aria-label="Photo tips"
                onClick={() => setHelp(true)}
              >
                <CircleHelp size={20} />
              </button>
            </div>
            {preview ? (
              <div className="photo-preview">
                <img src={preview} alt="Your uploaded medicine pack" />
                <button
                  type="button"
                  className="icon-button"
                  aria-label="Remove photo"
                  onClick={() => {
                    if (!busy) setPhoto(null);
                  }}
                  disabled={busy}
                >
                  <X size={20} />
                </button>
                <span className="photo-filename">{photo?.name}</span>
              </div>
            ) : (
              <BlisterArt />
            )}
            <div className="capture-copy">
              <h2>
                {photo
                  ? "Ready for a closer look."
                  : "Your pack. The starting point."}
              </h2>
              <p>
                {photo
                  ? "We’ll read the printed details on your photo."
                  : "Photograph the batch number clearly, without glare."}
              </p>
            </div>
            <div className="capture-actions">
              <button
                className="button white"
                type="button"
                onClick={() => cameraRef.current?.click()}
                disabled={busy}
              >
                <Camera size={19} />
                Take a photo
              </button>
              <button
                className="button quiet"
                type="button"
                onClick={() => uploadRef.current?.click()}
                disabled={busy}
              >
                <Upload size={18} />
                Upload photo
              </button>
            </div>
            <p className="drop-hint">Or drop an image here · Up to 15 MB</p>
            <input
              type="file"
              className="visually-hidden"
              accept="image/*"
              capture="environment"
              ref={cameraRef}
              onChange={(e) => {
                pick(e.target.files?.[0]);
                e.target.value = "";
              }}
              aria-label="Take a photo of your pack"
            />
            <input
              type="file"
              className="visually-hidden"
              accept="image/*"
              ref={uploadRef}
              onChange={(e) => {
                pick(e.target.files?.[0]);
                e.target.value = "";
              }}
              aria-label="Upload a pack photo"
            />
          </div>
          <div className="details-panel">
            <div className="panel-topline">
              <span>
                <span className="number-dot">02</span>THE DETAILS
              </span>
              <Keyboard size={20} />
            </div>
            <div className="details-heading">
              <h2>
                Know the batch?
                <br />
                Start right here.
              </h2>
              <p>Type what’s printed on your strip or carton.</p>
            </div>
            <label className="field">
              <span>
                Batch number <span className="required">*</span>
              </span>
              <input
                ref={batchRef}
                className="batch-input"
                value={fields.batch}
                maxLength={50}
                onChange={(e) =>
                  editFields({ batch: e.target.value.toUpperCase() })
                }
                placeholder="e.g. AB12345"
                autoComplete="off"
                spellCheck={false}
                disabled={busy}
              />
            </label>
            <label className="field">
              <span>
                Medicine or product name{" "}
                <span className="optional">Optional</span>
              </span>
              <input
                value={fields.product}
                maxLength={200}
                onChange={(e) => editFields({ product: e.target.value })}
                placeholder="As printed on the pack"
                disabled={busy}
              />
            </label>
            <button
              className="details-toggle"
              type="button"
              aria-expanded={advanced}
              onClick={() => setAdvanced(!advanced)}
            >
              Add manufacturer, brand & dates{" "}
              <ChevronDown size={17} className={advanced ? "rotated" : ""} />
            </button>
            {advanced && (
              <div className="advanced-fields">
                <label className="field">
                  <span>Manufacturer</span>
                  <input
                    maxLength={500}
                    disabled={busy}
                    value={fields.maker}
                    onChange={(e) => editFields({ maker: e.target.value })}
                    placeholder="Manufacturer name"
                  />
                </label>
                <label className="field">
                  <span>Brand</span>
                  <input
                    maxLength={500}
                    disabled={busy}
                    value={fields.brand}
                    onChange={(e) => editFields({ brand: e.target.value })}
                    placeholder="Brand on the pack"
                  />
                </label>
                <div className="field-pair">
                  {(["mfg", "exp"] as const).map((k) => (
                    <label className="field" key={k}>
                      <span>{k === "mfg" ? "Manufactured" : "Expires"}</span>
                      <input
                        disabled={busy}
                        type="month"
                        value={fields[k]}
                        onChange={(e) => editFields({ [k]: e.target.value })}
                      />
                    </label>
                  ))}
                </div>
              </div>
            )}
            <button
              className="button primary check-submit"
              type="submit"
              disabled={busy}
            >
              {busy ? (
                <>
                  <LoaderCircle className="spin" size={20} />
                  Reading the details…
                </>
              ) : (
                <>
                  {photo ? "Check this photo" : "Check this batch"}
                  <ArrowRight size={20} />
                </>
              )}
            </button>
            <p className="private-note">
              <Fingerprint size={15} />
              Your photos stay on this computer.
            </p>
          </div>
          <div className="demo-bar">
            <span>
              <span className="demo-icon">
                <Play size={14} />
              </span>
              Curious how it works?
            </span>
            <button
              type="button"
              onClick={() => setDemoOpen(true)}
              disabled={busy}
            >
              Try a demo pack <ArrowRight size={17} />
            </button>
          </div>
        </form>
      )}
      {error && (
        <div role="alert" className="notice error-notice">
          <CircleHelp size={19} />
          <span>{error}</span>
          <button
            className="icon-button"
            aria-label="Dismiss error"
            onClick={() => setError("")}
          >
            <X size={18} />
          </button>
        </div>
      )}
      {snapshot && (
        <div ref={resultRef} className="check-results">
          <div className="section-heading">
            <div>
              <div className="eyebrow">
                {snapshot.demo
                  ? "SYNTHETIC DEMONSTRATION"
                  : "THE DETAILS, CHECKED"}
              </div>
              <h2>
                {busy
                  ? PUBLIC_DEMO
                    ? "Opening the next step…"
                    : "Taking a closer look…"
                  : snapshot.status === "waiting"
                    ? PUBLIC_DEMO
                      ? "A question in this example."
                      : "One detail needs your eye."
                    : PUBLIC_DEMO
                      ? "The example, explained."
                      : "Your check, explained."}
              </h2>
            </div>
            <button
              className="button secondary"
              onClick={reset}
              disabled={busy}
            >
              <RotateCcw size={17} />
              {PUBLIC_DEMO ? "Another example" : "New check"}
            </button>
          </div>
          {snapshot.demo && (
            <div className="notice demo-notice">
              {PUBLIC_DEMO
                ? "Recorded demonstration only. Every pack, alert and answer in this story is fictional. No real medicine is being checked."
                : "Demonstration only. These invented packs and alert records are kept separate from official data."}
            </div>
          )}
          <div className="result-grid">
            <div className="pack-summary glass-card">
              <div className="eyebrow">
                {PUBLIC_DEMO ? "EXAMPLE PACK DETAILS" : "READ FROM YOUR PACK"}
              </div>
              <BatchStrip
                batch={snapshot.fields?.batch || fields.batch}
                chars={snapshot.strip?.chars}
              />
              <dl>
                {Object.entries(snapshot.fields || {})
                  .filter(
                    ([k, v]) =>
                      ["product", "brand", "maker", "mfg", "exp"].includes(k) &&
                      v,
                  )
                  .map(([k, v]) => (
                    <div key={k}>
                      <dt>
                        {
                          (
                            {
                              product: "Product",
                              brand: "Brand",
                              maker: "Manufacturer",
                              mfg: "Manufactured",
                              exp: "Expires",
                            } as Record<string, string>
                          )[k]
                        }
                      </dt>
                      <dd>{String(v)}</dd>
                    </div>
                  ))}
              </dl>
              <p className="muted">
                {PUBLIC_DEMO
                  ? "Recorded details for this fictional example. No photo recognition or real batch search runs on this website."
                  : snapshot.fields?.source === "ocr"
                    ? "Read from your photo. Unclear details need your confirmation."
                    : "Details are checked against the records loaded on this computer."}
              </p>
            </div>
            <div className="result-content">
              {snapshot.final && (
                <VerdictCard
                  snapshot={snapshot}
                  onSave={save}
                  onToast={toast}
                />
              )}{" "}
              {pending &&
                !busy &&
                (PUBLIC_DEMO ? (
                  <section className="ask-card guided-example">
                    <div className="ask-icon">
                      <ScanLine size={25} />
                    </div>
                    <span className="demo-tag">GUIDED EXAMPLE</span>
                    <h3>
                      {String(
                        pending.question || "A detail needs confirmation",
                      )}
                    </h3>
                    <p>
                      Continue with the response written for this fictional
                      scenario. Real pack details cannot be entered here.
                    </p>
                    {pending.guided_answer &&
                    typeof pending.guided_answer === "object" ? (
                      <>
                        <p className="guided-answer">
                          {guidedAnswerText(
                            pending.guided_answer as Record<string, unknown>,
                          )}
                        </p>
                        <button
                          className="button primary"
                          onClick={() => resume(pending.guided_answer)}
                        >
                          Continue this example <ArrowRight size={18} />
                        </button>
                      </>
                    ) : (
                      <p>
                        This guided step is unavailable. Choose another example
                        to continue.
                      </p>
                    )}
                  </section>
                ) : (
                  <section className="ask-card">
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
                            if (!file || !snapshot) return;
                            if (file.size > 15 * 1024 * 1024) {
                              setError("Choose a photo under 15 MB.");
                              return;
                            }
                            const form = new FormData();
                            form.append("images", file);
                            execute(
                              `/api/checks/${snapshot.thread_id}/resume`,
                              {
                                method: "POST",
                                body: form,
                              },
                            );
                          }}
                        />
                      </div>
                    )}
                    <div className="ask-icon">
                      <ScanLine size={25} />
                    </div>
                    <h3>
                      {String(
                        pending.question || "Confirm the printed details",
                      )}
                    </h3>
                    {Boolean(pending.error) && (
                      <p role="alert" className="notice error-notice">
                        {String(pending.error)}
                      </p>
                    )}
                    {kind === "confirm_batch" &&
                      Array.isArray(pending.positions) && (
                        <p>
                          Look at positions{" "}
                          {(pending.positions as number[]).join(" and ")} on the
                          pack, or type the entire batch below.
                        </p>
                      )}
                    {(kind === "confirm_char" || kind === "confirm_field") &&
                      Array.isArray(pending.options) && (
                        <div className="button-row">
                          {(pending.options as unknown[]).map((option, i) => {
                            const value =
                              typeof option === "object" && option
                                ? String(
                                    (option as Record<string, unknown>).value ||
                                      (option as Record<string, unknown>).label,
                                  )
                                : String(option);
                            return (
                              <button
                                key={i}
                                className="button secondary"
                                onClick={() => resume({ choice: value })}
                              >
                                {value}
                              </button>
                            );
                          })}
                        </div>
                      )}
                    {(kind === "confirm_batch" ||
                      kind === "confirm_char" ||
                      kind === "type_batch") && (
                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          if (answer.trim()) resume({ typed: answer.trim() });
                        }}
                      >
                        <label className="field">
                          <span>Type the full batch exactly as printed</span>
                          <input
                            value={answer}
                            onChange={(e) =>
                              setAnswer(e.target.value.toUpperCase())
                            }
                            maxLength={50}
                            autoComplete="off"
                            className="batch-input"
                            autoFocus
                          />
                        </label>
                        <button
                          className="button primary"
                          disabled={!answer.trim()}
                        >
                          Confirm printed batch <ArrowRight size={17} />
                        </button>
                      </form>
                    )}
                    {(kind === "box_photo" ||
                      kind === "provide_fields" ||
                      kind === "confirm_product" ||
                      kind === "type_fields") && (
                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          resume({ fields: details });
                        }}
                      >
                        <p>Add the details you can read on the carton.</p>
                        {(["product", "maker", "mfg", "exp"] as const).map(
                          (k) => (
                            <label key={k} className="field">
                              <span>
                                {k === "mfg"
                                  ? "Manufactured"
                                  : k === "exp"
                                    ? "Expires"
                                    : k === "maker"
                                      ? "Manufacturer"
                                      : "Product"}
                              </span>
                              <input
                                value={details[k]}
                                onChange={(e) =>
                                  setDetails({
                                    ...details,
                                    [k]: e.target.value,
                                  })
                                }
                              />
                            </label>
                          ),
                        )}
                        <button className="button primary">
                          Check these details
                        </button>
                      </form>
                    )}
                    <button
                      className="text-button skip-button"
                      onClick={() => resume({ skip: true })}
                    >
                      I can’t confirm this detail
                    </button>
                  </section>
                ))}
              <details
                className="reasoning glass-card"
                open={busy || snapshot.status === "waiting"}
              >
                <summary>
                  <span>
                    <ScanLine size={19} />
                    {PUBLIC_DEMO ? "Recorded steps" : "Behind this check"}
                  </span>
                  <span>
                    {snapshot.history?.length || 0} steps{" "}
                    <ChevronDown size={17} />
                  </span>
                </summary>
                <StepTimeline steps={snapshot.history || []} />
                {busy && (
                  <div className="working">
                    <LoaderCircle size={18} className="spin" />
                    {PUBLIC_DEMO
                      ? "Opening the recorded example…"
                      : "Checking the available evidence…"}
                  </div>
                )}
              </details>
            </div>
          </div>
        </div>
      )}
      {!snapshot && (
        <>
          <div className="benefits">
            <div>
              <div className="benefit-icon">
                <ScanLine size={24} />
              </div>
              <h3>Every character counts.</h3>
              <p>
                A single digit can mean a different batch. We ask when a detail
                needs confirming.
              </p>
            </div>
            <div>
              <div className="benefit-icon">
                <ShieldCheck size={24} />
              </div>
              <h3>Evidence, in the open.</h3>
              <p>
                Results link back to the loaded alert records, with the
                reasoning there to explore.
              </p>
            </div>
            <div>
              <div className="benefit-icon">
                <Fingerprint size={24} />
              </div>
              <h3>Personal stays personal.</h3>
              <p>
                {PUBLIC_DEMO
                  ? "No photos or real medicine details are collected in this demo. Saved examples stay in your browser tab."
                  : "Photo reading and batch checks happen locally. No cloud AI account required."}
              </p>
            </div>
          </div>
          {!PUBLIC_DEMO && !health?.db?.alerts && (
            <div className="data-callout">
              <CircleHelp size={18} />
              <p>
                Official lists haven’t been loaded yet. Visit{" "}
                <a href={appHref("/lists")}>Alert lists</a> to sync with CDSCO.
                Demo packs are available now.
              </p>
            </div>
          )}
        </>
      )}
      {demoOpen && (
        <Modal
          title="Take a test drive."
          onClose={() => setDemoOpen(false)}
          wide
        >
          <p className="modal-intro">
            {PUBLIC_DEMO
              ? "Choose one of 11 authored stories. Each uses fictional pack details and recorded answers; these are not real medicine checks."
              : "Explore the checks with invented medicine packs. Demo data never mixes with official records."}
          </p>
          <div className="demo-grid">
            {demos.length ? (
              demos.map((d, i) => (
                <button
                  key={d.id}
                  className="demo-case"
                  onClick={() => startDemo(d)}
                >
                  <span className="demo-number">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <div>
                    <h3>{d.name || d.title || d.id.replaceAll("_", " ")}</h3>
                    <p>{d.description}</p>
                  </div>
                  <ChevronRight size={19} />
                </button>
              ))
            ) : (
              <p>Loading demo packs…</p>
            )}
          </div>
        </Modal>
      )}
      {!PUBLIC_DEMO && help && (
        <Modal
          title="A clearer photo. A better read."
          onClose={() => setHelp(false)}
        >
          <div className="tips">
            <div>
              <Camera />
              <h3>Find the printed batch</h3>
              <p>Look for “Batch”, “B. No.” or “Lot” on the foil or carton.</p>
            </div>
            <div>
              <ImagePlus />
              <h3>Keep it sharp</h3>
              <p>
                Fill the frame with the printed details. Tap to focus and tilt
                the foil away from glare.
              </p>
            </div>
            <div>
              <Keyboard />
              <h3>You’re in control</h3>
              <p>
                You can type the batch and product details instead, or confirm a
                character when asked.
              </p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
