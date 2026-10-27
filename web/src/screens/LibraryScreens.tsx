import { useEffect, useRef, useState } from "react";
import {
  Search,
  RefreshCw,
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  ListFilter,
  Database,
  BookOpen,
  Bookmark,
  Trash2,
  Play,
  FlaskConical,
  Activity,
  ArrowRight,
  LoaderCircle,
  Bell,
  FileText,
  Download,
  CircleHelp,
} from "lucide-react";
import { createRequestGate, storage } from "../lib/runtime";
import { api, json, readableDate, stream } from "../lib/api";
import type { AlertRow, Snapshot, Stats } from "../lib/api";
import {
  BatchStrip,
  Empty,
  Modal,
  StepTimeline,
  VerdictBadge,
  VerdictCard,
} from "../components/Shared";
type Props = { toast: (message: string) => void; refreshHealth: () => void };
function storedValue(value: unknown): unknown {
  if (typeof value !== "string") return value;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}
function reviewRecord(row: Record<string, unknown>) {
  const value = storedValue(row.raw_json);
  const raw =
    value && typeof value === "object" && !Array.isArray(value)
      ? (value as Record<string, unknown>)
      : {};
  const text = (value: unknown) =>
    typeof value === "string" || typeof value === "number"
      ? String(value).trim()
      : "";
  const labels: Record<string, string> = {
    batch_placeholder: "The source does not provide a clear batch number.",
    batch_is_date: "The batch entry appears to be a date and needs checking.",
    ambiguous_multi_batch:
      "Several batch numbers are written together and need clarification.",
    maker_missing: "The manufacturer is missing from the source.",
    product_missing: "The product name is missing from the source.",
    unsupported_field_shape: "Some source details could not be read reliably.",
    unknown_row_format: "The source record could not be read reliably.",
  };
  const reasons = storedValue(row.reasons);
  const explanations = Array.isArray(reasons)
    ? reasons
        .filter((reason): reason is string => typeof reason === "string")
        .filter((reason) => reason !== "no_llm")
        .map(
          (reason) =>
            labels[reason] || "The source details need a manual review.",
        )
    : [];
  return {
    title:
      text(raw.str_product_name) ||
      text(raw.product_name_from_dtl) ||
      text(raw.product) ||
      "Product name unavailable",
    context: [
      text(row.list_month) || text(raw.dt_reporting_month_year),
      row.row_no ? `Source row ${text(row.row_no)}` : "",
    ]
      .filter(Boolean)
      .join(" · "),
    explanation:
      [...new Set(explanations)].join(" ") ||
      "The source details need a manual review.",
  };
}
function PageTitle({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="page-title">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </header>
  );
}
export function ListsScreen({ toast, refreshHealth }: Props) {
  const [q, setQ] = useState("");
  const [kind, setKind] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<{
    items: AlertRow[];
    total: number;
    pages: number;
  }>({ items: [], total: 0, pages: 0 });
  const [stats, setStats] = useState<Stats>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [syncing, setSyncing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [selected, setSelected] = useState<AlertRow | null>(null);
  const [tab, setTab] = useState("entries");
  const [aux, setAux] = useState<Record<string, unknown>[]>([]);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const abort = new AbortController();
    const timer = setTimeout(() => {
      setLoading(true);
      api<typeof data>(
        `/api/alerts?q=${encodeURIComponent(q)}&kind=${kind}&page=${page}&size=15`,
        { signal: abort.signal },
      )
        .then((d) => {
          if (abort.signal.aborted) return;
          setData(d);
          setError("");
        })
        .catch((e) => {
          if (e.name !== "AbortError") setError(e.message);
        })
        .finally(() => {
          if (!abort.signal.aborted) setLoading(false);
        });
    }, 220);
    return () => {
      clearTimeout(timer);
      abort.abort();
    };
  }, [q, kind, page, revision]);
  useEffect(() => {
    const abort = new AbortController();
    api<Stats>("/api/stats", { signal: abort.signal })
      .then((s) => {
        if (!abort.signal.aborted) setStats(s);
      })
      .catch((e) => {
        if (!abort.signal.aborted) setError(e.message);
      });
    return () => abort.abort();
  }, [revision]);
  const [auxLoading, setAuxLoading] = useState(false);
  useEffect(() => {
    if (tab === "entries") return;
    const abort = new AbortController();
    api<{ items: Record<string, unknown>[] }>(
      tab === "sources" ? "/api/sources" : "/api/quarantine",
      { signal: abort.signal },
    )
      .then((d) => {
        if (!abort.signal.aborted) {
          setAux(d.items);
          setError("");
        }
      })
      .catch((e) => {
        if (!abort.signal.aborted) setError(e.message);
      })
      .finally(() => {
        if (!abort.signal.aborted) setAuxLoading(false);
      });
    return () => abort.abort();
  }, [tab, revision]);
  const detailRequests = useRef(createRequestGate());
  useEffect(() => {
    const gate = detailRequests.current;
    return () => gate.cancel();
  }, []);
  const sync = async () => {
    setSyncing(true);
    setLogs([]);
    setError("");
    try {
      await stream("/api/sync", json({}), (_event, d) => {
        const message = d.message || d.summary || d.status;
        if (message) setLogs((l) => [...l.slice(-7), String(message)]);
        if (_event === "error")
          setError(
            String(
              d.message || "The source could not be reached. Try again later.",
            ),
          );
      });
      if (tab !== "entries") {
        setAuxLoading(true);
        setAux([]);
      }
      setRevision((n) => n + 1);
      refreshHealth();
      toast("List sync finished. Review the source status below.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSyncing(false);
    }
  };
  const detail = async (row: AlertRow) => {
    const gate = detailRequests.current;
    const signal = gate.begin();
    try {
      const rowDetail = await api<AlertRow>(`/api/alerts/${row.id}`, {
        signal,
      });
      if (gate.isCurrent(signal)) setSelected(rowDetail);
    } catch (e) {
      if (gate.isCurrent(signal)) toast((e as Error).message);
    }
  };
  return (
    <div className="inner-page page-enter">
      <PageTitle
        eyebrow="THE SOURCE OF EVERY CHECK"
        title="Evidence you can explore."
        description="Official records. Exact batches. The details behind the result."
        action={
          <button className="button primary" onClick={sync} disabled={syncing}>
            <RefreshCw size={18} className={syncing ? "spin" : ""} />
            {syncing ? "Updating lists…" : "Sync with CDSCO"}
          </button>
        }
      />
      <div className="stats-row">
        <div>
          <span>Loaded records</span>
          <strong>
            {Number(stats.alerts || data.total).toLocaleString("en-IN")}
          </strong>
        </div>
        <div>
          <span>Months covered</span>
          <strong>
            {Number(
              stats.month_count ||
                (Array.isArray(stats.months)
                  ? stats.months.length
                  : stats.months) ||
                0,
            )}
          </strong>
        </div>
        <div>
          <span>Latest list</span>
          <strong>{readableDate(stats.latest_month)}</strong>
        </div>
        <div>
          <span>Last updated</span>
          <strong>{readableDate(stats.last_sync)}</strong>
        </div>
      </div>
      {typeof stats.coverage_warning === "string" && (
        <p className="page-footnote">{stats.coverage_warning}</p>
      )}
      {error && (
        <div className="notice error-notice" role="alert">
          <CircleHelp size={19} />
          {error}
        </div>
      )}
      {logs.length > 0 && (
        <div className="sync-log glass-card" aria-live="polite">
          {logs.map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
      )}
      <section className="table-card glass-card">
        <div className="table-toolbar">
          <div className="segmented">
            {[
              ["entries", "Alert records"],
              ["sources", "Sources"],
              ["quarantine", "Needs review"],
            ].map(([id, label]) => (
              <button
                key={id}
                onClick={() => {
                  if (id === tab) return;
                  setAux([]);
                  setAuxLoading(id !== "entries");
                  setTab(id);
                }}
                aria-pressed={tab === id}
              >
                {label}
              </button>
            ))}
          </div>
          <a
            className="text-link"
            href="https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug"
            target="_blank"
            rel="noreferrer"
          >
            Official portal <ArrowUpRight size={16} />
          </a>
        </div>
        {tab === "entries" ? (
          <>
            <div className="search-row">
              <div className="search-field">
                <Search size={20} />
                <input
                  aria-label="Search alert records"
                  placeholder="Search a batch, medicine or manufacturer"
                  value={q}
                  onChange={(e) => {
                    setQ(e.target.value);
                    setPage(1);
                  }}
                />
              </div>
              <label className="select-filter">
                <ListFilter size={17} />
                <select
                  aria-label="Filter alert type"
                  value={kind}
                  onChange={(e) => {
                    setKind(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="">All alert types</option>
                  <option value="nsq">Quality alerts</option>
                  <option value="spurious">Spurious alerts</option>
                </select>
              </label>
            </div>
            {loading ? (
              <div className="loading-state">
                <LoaderCircle className="spin" />
                Loading records…
              </div>
            ) : data.items.length ? (
              <>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Medicine / product</th>
                        <th>Batch</th>
                        <th>Manufacturer</th>
                        <th>List month</th>
                        <th>Finding</th>
                        <th>
                          <span className="visually-hidden">Details</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.items.map((row) => (
                        <tr key={row.id}>
                          <td>
                            <button
                              className="table-product"
                              onClick={() => detail(row)}
                            >
                              {row.product}
                            </button>
                            {row.brand && (
                              <span className="table-sub">{row.brand}</span>
                            )}
                          </td>
                          <td>
                            <code className="batch-code">
                              {row.batch_raw || row.batch_key}
                            </code>
                            {Boolean(row.distance) && (
                              <span className="table-sub">
                                {String(row.distance)} character differs
                              </span>
                            )}
                          </td>
                          <td>
                            {row.maker_name || row.maker_raw || "Not reported"}
                          </td>
                          <td className="nowrap">
                            {readableDate(row.list_month)}
                          </td>
                          <td>
                            <span
                              className={`record-kind ${row.entry_type === "SPURIOUS" ? "spurious" : ""}`}
                            >
                              {row.entry_type === "SPURIOUS"
                                ? "Spurious"
                                : "Quality alert"}
                            </span>
                          </td>
                          <td>
                            <button
                              className="icon-button"
                              aria-label={`View ${row.batch_raw} record`}
                              onClick={() => detail(row)}
                            >
                              <ArrowUpRight size={19} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="pagination">
                  <span>
                    {data.total.toLocaleString("en-IN")} records · Page {page}{" "}
                    of {data.pages || 1}
                  </span>
                  <div>
                    <button
                      className="icon-button bordered"
                      disabled={page <= 1}
                      onClick={() => setPage((p) => p - 1)}
                      aria-label="Previous page"
                    >
                      <ChevronLeft size={18} />
                    </button>
                    <button
                      className="icon-button bordered"
                      disabled={page >= (data.pages || 1)}
                      onClick={() => setPage((p) => p + 1)}
                      aria-label="Next page"
                    >
                      <ChevronRight size={18} />
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <Empty
                icon={<Database size={32} />}
                title={
                  q
                    ? "No records match this search."
                    : "Start with the official lists."
                }
                description={
                  q
                    ? "Try a different batch number, product name or manufacturer."
                    : "Sync with CDSCO to load the available records. Once stored, batch checks work offline."
                }
                action={
                  !q ? (
                    <button
                      className="button primary"
                      onClick={sync}
                      disabled={syncing}
                    >
                      <RefreshCw size={17} />
                      Load official records
                    </button>
                  ) : undefined
                }
              />
            )}
          </>
        ) : auxLoading ? (
          <div className="loading-state" role="status">
            <LoaderCircle className="spin" />
            Loading source records…
          </div>
        ) : aux.length ? (
          <div className="source-list">
            {tab === "quarantine" && (
              <p className="page-footnote">
                These records are excluded from batch checks until their source
                details can be verified.
              </p>
            )}
            {aux.map((row, i) => {
              const review = tab === "quarantine" ? reviewRecord(row) : null;
              return (
                <article key={String(row.id ?? i)}>
                  <FileText size={25} />
                  <div>
                    <h3>
                      {review?.title ||
                        String(
                          row.title ||
                            row.file_name ||
                            `Source ${row.id || i + 1}`,
                        )}
                    </h3>
                    {review ? (
                      <>
                        {review.context && <p>{review.context}</p>}
                        <p>{review.explanation}</p>
                      </>
                    ) : (
                      <>
                        <p>
                          {String(row.list_month || "")} ·{" "}
                          {Number(row.rows_valid || 0).toLocaleString("en-IN")}{" "}
                          records
                        </p>
                        <code>{String(row.sha256 || "")}</code>
                      </>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        ) : (
          <Empty
            icon={<BookOpen size={30} />}
            title={
              tab === "quarantine"
                ? "No records need review."
                : "No source files loaded yet."
            }
            description={
              tab === "quarantine"
                ? "Records with missing or inconsistent details appear here instead of entering the checking index."
                : "Each downloaded source will appear here with its date and integrity fingerprint."
            }
          />
        )}
      </section>
      <p className="page-footnote">
        Source: Central Drugs Standard Control Organisation, Government of
        India. A listing applies to the named batch, not every product from a
        brand.
      </p>
      {selected && (
        <Modal
          title="The original record."
          onClose={() => setSelected(null)}
          wide
        >
          <div className="record-detail">
            <span className="record-kind">
              {selected.entry_type === "SPURIOUS"
                ? "Spurious listing"
                : "Quality alert"}
            </span>
            <h3>{selected.product}</h3>
            <BatchStrip batch={selected.batch_raw || selected.batch_key} />
            <dl>
              {Object.entries({
                Brand: selected.brand,
                Manufacturer: selected.maker_name || selected.maker_raw,
                "List month": readableDate(selected.list_month),
                Finding: selected.result,
                "Reported by": selected.reported_by,
                "Source row": selected.row_no,
                Manufactured: selected.mfg,
                Expires: selected.exp,
              })
                .filter(([, v]) => v)
                .map(([key, v]) => (
                  <div key={key}>
                    <dt>{key}</dt>
                    <dd>{String(v)}</dd>
                  </div>
                ))}
            </dl>
            <a
              className="button primary"
              href={String(
                selected.source_url ||
                  "https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug",
              )}
              target="_blank"
              rel="noreferrer"
            >
              Open official source <ArrowUpRight size={18} />
            </a>
          </div>
        </Modal>
      )}
    </div>
  );
}
export function CabinetScreen({ toast }: Props) {
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [notifications, setNotifications] = useState<Record<string, unknown>[]>(
    [],
  );
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [remove, setRemove] = useState<Record<string, unknown> | null>(null);
  const [selected, setSelected] = useState<Snapshot | null>(null);
  const [error, setError] = useState("");
  const detailRequests = useRef(createRequestGate());
  useEffect(() => {
    const gate = detailRequests.current;
    return () => gate.cancel();
  }, []);
  const closeSelected = () => {
    detailRequests.current.cancel();
    setSelected(null);
  };
  const load = () =>
    Promise.all([
      api<{ items: Record<string, unknown>[] }>("/api/cabinet"),
      api<{ items: Record<string, unknown>[] }>("/api/notifications"),
    ])
      .then(([c, n]) => {
        setError("");
        setItems(c.items);
        setNotifications(n.items.filter((x) => !x.seen));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  useEffect(() => {
    load();
  }, []);
  const recheck = async () => {
    setBusy(true);
    try {
      await api("/api/cabinet/recheck", json({}));
      await load();
      toast("Cabinet rechecked against the loaded lists");
    } catch (e) {
      toast((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  const deleteItem = async () => {
    try {
      await api(`/api/cabinet/${remove?.id}`, { method: "DELETE" });
      setRemove(null);
      await load();
      toast("Removed from cabinet");
    } catch (e) {
      toast((e as Error).message);
    }
  };
  const open = async (item: Record<string, unknown>) => {
    const id = item.check_thread_id || item.thread_id;
    const gate = detailRequests.current;
    const signal = gate.begin();
    try {
      const snapshot = await api<Snapshot>(
        `/api/checks/${encodeURIComponent(String(id))}`,
        { signal },
      );
      if (gate.isCurrent(signal)) setSelected(snapshot);
    } catch (e) {
      if (gate.isCurrent(signal)) toast((e as Error).message);
    }
  };
  return (
    <div className="inner-page page-enter">
      <PageTitle
        eyebrow="A LITTLE LESS TO KEEP TRACK OF"
        title="Your personal cabinet."
        description="Saved packs, their latest checks, and a little peace of organisation."
        action={
          <button
            className="button primary"
            disabled={!items.length || busy}
            onClick={recheck}
          >
            <RefreshCw size={18} className={busy ? "spin" : ""} />
            {busy ? "Rechecking…" : "Recheck all packs"}
          </button>
        }
      />
      {error && <div className="notice error-notice">{error}</div>}
      {notifications.map((n) => (
        <div className="notice notification" key={String(n.id)}>
          <Bell size={20} />
          <p>{String(n.message)}</p>
          <button
            className="text-button"
            onClick={async () => {
              try {
                await api(`/api/notifications/${n.id}/seen`, json({}));
                await load();
              } catch (e) {
                toast((e as Error).message);
              }
            }}
          >
            Dismiss
          </button>
        </div>
      ))}
      <section className="glass-card cabinet-card">
        <div className="table-toolbar">
          <h2>
            Saved packs <span className="count-chip">{items.length}</span>
          </h2>
          <span className="muted">Stored on this computer</span>
        </div>
        {loading ? (
          <div className="loading-state">
            <LoaderCircle className="spin" />
            Opening your cabinet…
          </div>
        ) : items.length ? (
          <div className="cabinet-list">
            {items.map((item) => {
              const fields = (item.fields || {}) as Record<string, string>;
              const batch = String(
                item.batch_display || item.batch_key || fields.batch || "",
              );
              return (
                <article className="cabinet-item" key={String(item.id)}>
                  <div className="cabinet-product-icon">
                    <Bookmark size={26} />
                  </div>
                  <div className="cabinet-item-main">
                    <button
                      className="table-product"
                      onClick={() => open(item)}
                    >
                      {String(
                        item.label ||
                          item.product_text ||
                          fields.product ||
                          "Medicine pack",
                      )}
                    </button>
                    <div className="cabinet-meta">
                      <code>{batch}</code>
                      {Boolean(item.demo) && (
                        <span className="demo-tag">Demo</span>
                      )}
                    </div>
                    <span className="muted">
                      Checked{" "}
                      {readableDate(item.last_checked_at || item.added_at)}
                      {item.exp || fields.exp
                        ? ` · Expires ${readableDate(item.exp || fields.exp)}`
                        : ""}
                    </span>
                  </div>
                  <VerdictBadge
                    label={String(
                      item.last_verdict || item.verdict || "CANT_VERIFY",
                    )}
                  />
                  <button
                    className="icon-button"
                    onClick={() => setRemove(item)}
                    aria-label={`Remove ${batch} from cabinet`}
                  >
                    <Trash2 size={18} />
                  </button>
                </article>
              );
            })}
          </div>
        ) : (
          <Empty
            icon={<Bookmark size={32} />}
            title="A home for the packs you check."
            description="After checking a pack, choose “Save to cabinet”. Its batch, details and result will be waiting here."
            action={
              <a href="/" className="button primary">
                Check your first pack <ArrowRight size={18} />
              </a>
            }
          />
        )}
      </section>
      <div className="quiet-note">
        <FingerprintIcon />
        <p>
          Saved details stay with this local StripCheck installation. Rechecking
          uses the official lists currently loaded.
        </p>
      </div>
      {remove && (
        <Modal title="Remove this saved pack?" onClose={() => setRemove(null)}>
          <p>
            The pack will leave your cabinet. Its original check remains in your
            activity.
          </p>
          <div className="button-row">
            <button className="button danger" onClick={deleteItem}>
              Remove pack
            </button>
            <button
              className="button secondary"
              onClick={() => setRemove(null)}
            >
              Keep it
            </button>
          </div>
        </Modal>
      )}
      {selected && (
        <Modal title="Your saved check." onClose={closeSelected} wide>
          {selected.final ? (
            <VerdictCard
              snapshot={selected}
              onSave={() => toast("This pack is already in your cabinet")}
              onToast={toast}
            />
          ) : (
            <p>
              This check is still waiting for confirmation. Resume it from
              Activity.
            </p>
          )}
          <StepTimeline steps={selected.history || []} />
        </Modal>
      )}
    </div>
  );
}
function FingerprintIcon() {
  return <Bookmark size={20} />;
}
export function ActivityScreen({ toast }: Props) {
  const [items, setItems] = useState<Snapshot[]>([]);
  const [selected, setSelected] = useState<Snapshot | null>(null);
  const [error, setError] = useState("");
  const detailRequests = useRef(createRequestGate());
  useEffect(() => {
    const gate = detailRequests.current;
    return () => gate.cancel();
  }, []);
  const closeSelected = () => {
    detailRequests.current.cancel();
    setSelected(null);
  };
  useEffect(() => {
    api<{ items: Snapshot[] }>("/api/checks?limit=100")
      .then((d) => setItems(d.items))
      .catch((e) => setError(e.message));
  }, []);
  const open = async (s: Snapshot) => {
    const gate = detailRequests.current;
    const signal = gate.begin();
    try {
      const snapshot = await api<Snapshot>(
        `/api/checks/${encodeURIComponent(s.thread_id)}`,
        { signal },
      );
      if (gate.isCurrent(signal)) setSelected(snapshot);
    } catch (e) {
      if (gate.isCurrent(signal)) toast((e as Error).message);
    }
  };
  return (
    <div className="inner-page page-enter">
      <PageTitle
        eyebrow="NOTHING HIDDEN IN THE PROCESS"
        title="Follow every step."
        description="A clear record of your checks, the questions asked, and the evidence considered."
      />
      {error && <div className="notice error-notice">{error}</div>}
      <div className="glass-card">
        <div className="table-toolbar">
          <h2>
            Recent activity <span className="count-chip">{items.length}</span>
          </h2>
          <Activity size={21} />
        </div>
        {items.length ? (
          <div className="activity-list">
            {items.map((s) => (
              <button
                className="activity-item"
                key={s.thread_id}
                onClick={() => open(s)}
              >
                <span className="activity-icon">
                  <Activity size={22} />
                </span>
                <span className="activity-main">
                  <strong>
                    {s.fields?.product || s.fields?.batch || "Pack check"}
                  </strong>
                  <span>
                    {s.fields?.batch || "Photo check"} ·{" "}
                    {readableDate(s.created_at)} {s.demo ? "· Demo" : ""}
                  </span>
                </span>
                {s.final ? (
                  <VerdictBadge label={s.final.label} />
                ) : (
                  <span className="status-pending">
                    {s.status === "waiting" ? "Needs confirmation" : s.status}
                  </span>
                )}
                <ChevronRight size={19} />
              </button>
            ))}
          </div>
        ) : (
          <Empty
            icon={<Activity size={32} />}
            title="Your checks will leave a trail."
            description="Each check records its steps here, including the source of every decision."
            action={
              <a className="button primary" href="/">
                Start a check <ArrowRight size={18} />
              </a>
            }
          />
        )}
      </div>
      {selected && (
        <Modal title="Every step, explained." onClose={closeSelected} wide>
          <div className="trace-heading">
            <BatchStrip batch={selected.fields?.batch || ""} />
            <span>{readableDate(selected.created_at)}</span>
          </div>
          {selected.demo && (
            <p className="notice demo-notice">
              This was a synthetic demonstration, not an official record check.
            </p>
          )}
          {selected.final ? (
            <VerdictCard
              snapshot={selected}
              onSave={async () => {
                try {
                  await api(
                    "/api/cabinet",
                    json({ thread_id: selected.thread_id }),
                  );
                  toast("Saved to cabinet");
                } catch (e) {
                  toast((e as Error).message);
                }
              }}
              onToast={toast}
            />
          ) : (
            <a
              className="button primary"
              href="/"
              onClick={() =>
                storage.set("stripcheck.current", selected.thread_id)
              }
            >
              Continue this check <ArrowRight size={18} />
            </a>
          )}
          <StepTimeline steps={selected.history || []} />
        </Modal>
      )}
    </div>
  );
}
export function EvaluationScreen({ toast }: Props) {
  const [report, setReport] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    api<Record<string, unknown>>("/api/eval/latest")
      .then((r) => setReport(r.available === false ? null : r))
      .catch((e) => setError(e.message));
  }, []);
  const run = async () => {
    setBusy(true);
    setError("");
    try {
      await stream("/api/eval/quick", json({}), (event, d) => {
        if (event === "error") throw new Error(String(d.message));
        if (event === "final" || event === "report") setReport(d);
      });
      setReport(await api("/api/eval/latest"));
      toast("Diagnostic checks completed");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  const rows = (report?.cases || report?.results || []) as Record<
    string,
    unknown
  >[];
  const passed = Number(report?.passed ?? rows.filter((r) => r.passed).length);
  const total = Number(report?.total ?? rows.length);
  return (
    <div className="inner-page page-enter">
      <PageTitle
        eyebrow="BUILT TO BE QUESTIONED"
        title="Put the checks to the test."
        description="Run the built-in scenarios and inspect how the checking rules behave."
        action={
          <button className="button primary" onClick={run} disabled={busy}>
            {busy ? (
              <LoaderCircle size={18} className="spin" />
            ) : (
              <Play size={18} />
            )}{" "}
            {busy ? "Running diagnostics…" : "Run diagnostic checks"}
          </button>
        }
      />
      <div className="notice demo-notice">
        <FlaskConical size={20} />
        <p>
          These are synthetic software diagnostics. They do not measure
          performance on real medicine photographs or certify any medicine.
        </p>
      </div>
      {error && <div className="notice error-notice">{error}</div>}
      {report && total > 0 ? (
        <>
          <div className="diagnostic-summary glass-card">
            <div className="diagnostic-ring">
              <strong>
                {passed}
                <span>/{total}</span>
              </strong>
            </div>
            <div>
              <h2>
                {passed === total
                  ? "All diagnostic scenarios passed."
                  : "Some scenarios need attention."}
              </h2>
              <p>Expected outcomes compared with the actual checking engine.</p>
              <span className="muted">
                Last run{" "}
                {readableDate(
                  report.created_at || report.ran_at || report.finished_at,
                )}
              </span>
            </div>
            <button
              className="button secondary"
              onClick={() => {
                const url = URL.createObjectURL(
                  new Blob([JSON.stringify(report, null, 2)], {
                    type: "application/json",
                  }),
                );
                const a = document.createElement("a");
                a.href = url;
                a.download = "stripcheck-diagnostics.json";
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              <Download size={18} />
              Export report
            </button>
          </div>
          <div className="table-card glass-card">
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Scenario</th>
                    <th>Expected</th>
                    <th>Actual</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r, i) => (
                    <tr key={i}>
                      <td>
                        {String(
                          r.name ||
                            r.title ||
                            r.id ||
                            r.case_id ||
                            `Scenario ${i + 1}`,
                        )}
                      </td>
                      <td>{String(r.expected || "—")}</td>
                      <td>{String(r.actual || r.label || "—")}</td>
                      <td>
                        <span
                          className={`diagnostic-status ${r.passed ? "passed" : "failed"}`}
                        >
                          {r.passed ? "Passed" : "Review needed"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <section className="glass-card">
          <Empty
            icon={<FlaskConical size={34} />}
            title="Confidence in the process starts with testing."
            description="Exercise exact matches, misread characters, conflicting details and missing evidence. Every test has an explicit expected result."
            action={
              <button className="button primary" onClick={run} disabled={busy}>
                <Play size={18} />
                Run the scenarios
              </button>
            }
          />
        </section>
      )}
      <div className="evaluation-note">
        <h3>What these checks tell you</h3>
        <p>
          The diagnostic suite verifies the application’s rules using invented
          records. Research evaluation, accuracy on real photos, and human
          review of regional translations require separate datasets and
          validation.
        </p>
      </div>
    </div>
  );
}
