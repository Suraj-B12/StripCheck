import { lazy, Suspense, useEffect, useState } from "react";
import { storage } from "./lib/runtime";
import {
  Activity,
  ArrowRight,
  Bookmark,
  Check,
  ChevronRight,
  FlaskConical,
  ListChecks,
  LoaderCircle,
  Moon,
  ScanLine,
  Smartphone,
  Sun,
  X,
  Wifi,
  ExternalLink,
  ShieldCheck,
} from "lucide-react";
import type { Health } from "./lib/api";
import { api, readableDate } from "./lib/api";
import CheckScreen from "./screens/CheckScreen";
const ListsScreen = lazy(() =>
  import("./screens/LibraryScreens").then((m) => ({ default: m.ListsScreen })),
);
const CabinetScreen = lazy(() =>
  import("./screens/LibraryScreens").then((m) => ({
    default: m.CabinetScreen,
  })),
);
const ActivityScreen = lazy(() =>
  import("./screens/LibraryScreens").then((m) => ({
    default: m.ActivityScreen,
  })),
);
const EvaluationScreen = lazy(() =>
  import("./screens/LibraryScreens").then((m) => ({
    default: m.EvaluationScreen,
  })),
);
import { Modal } from "./components/Shared";
import "./styles/tokens.css";
import "./styles/app.css";
const nav = [
  { path: "/", name: "Check a pack", short: "Check", icon: ScanLine },
  { path: "/lists", name: "Alert lists", short: "Lists", icon: ListChecks },
  { path: "/cabinet", name: "Cabinet", short: "Cabinet", icon: Bookmark },
  { path: "/traces", name: "Activity", short: "Activity", icon: Activity },
  { path: "/eval", name: "Diagnostics", short: "Tests", icon: FlaskConical },
];
function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [health, setHealth] = useState<Health | null>(null);
  const [online, setOnline] = useState(true);
  const [toastMessage, setToast] = useState("");
  const [phone, setPhone] = useState(false);
  const [about, setAbout] = useState(false);
  const [lan, setLan] = useState<Record<string, unknown> | null>(null);
  const [theme, setTheme] = useState(
    storage.get("stripcheck.theme") || "light",
  );
  const refreshHealth = () =>
    api<Health>("/api/health")
      .then((h) => {
        setHealth(h);
        setOnline(true);
      })
      .catch(() => setOnline(false));
  useEffect(() => {
    refreshHealth();
    const id = setInterval(refreshHealth, 60000);
    const pop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", pop);
    return () => {
      clearInterval(id);
      window.removeEventListener("popstate", pop);
    };
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    storage.set("stripcheck.theme", theme);
  }, [theme]);
  useEffect(() => {
    if (toastMessage) {
      const t = setTimeout(() => setToast(""), 4500);
      return () => clearTimeout(t);
    }
  }, [toastMessage]);
  useEffect(() => {
    if (phone)
      api<Record<string, unknown>>("/api/lan")
        .then(setLan)
        .catch((e) => setLan({ error: e.message }));
  }, [phone]);
  const navigate = (e: React.MouseEvent<HTMLAnchorElement>, target: string) => {
    if (e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    history.pushState({}, "", target);
    setPath(target);
    window.scrollTo({ top: 0, behavior: "instant" });
  };
  const active =
    path === "/"
      ? "/"
      : nav.find((n) => n.path !== "/" && path.startsWith(n.path))?.path || "/";
  const props = { toast: setToast, refreshHealth };
  const latest = health?.db?.latest_month;
  const lanUrl = String(lan?.url || lan?.lan_url || health?.lan_url || "");
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <a
          className="brand"
          href="/"
          onClick={(e) => navigate(e, "/")}
          aria-label="StripCheck home"
        >
          <span className="brand-mark">
            <ScanLine size={23} strokeWidth={2} />
          </span>
          <span>
            StripCheck<span className="brand-period">.</span>
          </span>
        </a>
        <nav className="desktop-nav" aria-label="Main navigation">
          {nav.map((n) => (
            <a
              href={n.path}
              key={n.path}
              aria-current={active === n.path ? "page" : undefined}
              onClick={(e) => navigate(e, n.path)}
            >
              {n.name}
            </a>
          ))}
        </nav>
        <div className="header-actions">
          <button
            className="icon-button theme-button"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} appearance`}
          >
            {theme === "light" ? <Moon size={18} /> : <Sun size={19} />}
          </button>
          <button
            className="phone-button"
            aria-label="Use your phone"
            onClick={() => setPhone(true)}
          >
            <Smartphone size={18} />
            <span>Use your phone</span>
          </button>
        </div>
      </header>
      <div className="system-strip">
        <span className={`connection-dot ${!online ? "offline" : ""}`} />
        <span>
          {!online
            ? "Server unavailable — reconnect to continue"
            : latest
              ? `Lists through ${readableDate(latest)}`
              : "Local workspace"}
        </span>
        {latest && <span className="system-divider">/</span>}
        {latest && (
          <span>
            {Number(health?.db?.alerts || 0).toLocaleString("en-IN")} records
          </span>
        )}
        <span className="system-divider">/</span>
        <span>Made for a closer look</span>
      </div>
      {!online && (
        <div role="alert" className="connection-warning">
          The local server is not responding. Start StripCheck and refresh this
          page.
          <button onClick={refreshHealth} className="text-button">
            Retry connection
          </button>
        </div>
      )}
      <main id="main" tabIndex={-1}>
        <Suspense
          fallback={
            <div className="loading-state" role="status">
              <LoaderCircle className="spin" />
              Opening this page…
            </div>
          }
        >
          {active === "/" ? (
            <CheckScreen health={health} toast={setToast} />
          ) : active === "/lists" ? (
            <ListsScreen {...props} />
          ) : active === "/cabinet" ? (
            <CabinetScreen {...props} />
          ) : active === "/traces" ? (
            <ActivityScreen {...props} />
          ) : (
            <EvaluationScreen {...props} />
          )}
        </Suspense>
      </main>
      <footer className="site-footer">
        <div>
          <a
            className="brand footer-brand"
            href="/"
            onClick={(e) => navigate(e, "/")}
          >
            <span className="brand-mark">
              <ScanLine size={18} />
            </span>
            StripCheck.
          </a>
          <p>Clarity in the little things.</p>
        </div>
        <div className="footer-advisory">
          <p>
            An independent student project. Not a CDSCO service.
            <br />A batch check is advisory and does not certify a medicine.
            <br />
            Discuss questions about your pack with your pharmacist.
          </p>
          <button className="text-button" onClick={() => setAbout(true)}>
            About this project <ChevronRight size={14} />
          </button>
        </div>
      </footer>
      <nav className="mobile-nav" aria-label="Mobile navigation">
        {nav.map((n) => (
          <a
            href={n.path}
            key={n.path}
            aria-current={active === n.path ? "page" : undefined}
            onClick={(e) => navigate(e, n.path)}
          >
            <n.icon size={22} />
            <span>{n.short}</span>
          </a>
        ))}
      </nav>
      {toastMessage && (
        <div className="toast" role="status">
          <Check size={19} />
          <span>{toastMessage}</span>
          <button
            className="icon-button"
            onClick={() => setToast("")}
            aria-label="Dismiss notification"
          >
            <X size={16} />
          </button>
        </div>
      )}
      {phone && (
        <Modal
          title="A closer look. On your phone."
          onClose={() => setPhone(false)}
        >
          <div className="phone-pair">
            <div className="phone-pair-icon">
              <Smartphone size={31} />
            </div>
            <p>
              Connect your phone to the same Wi-Fi as this computer, then scan
              the code to open StripCheck.
            </p>
            {lan ? (
              <>
                {lan.error ? (
                  <div className="notice error-notice">{String(lan.error)}</div>
                ) : (
                  <>
                    <div className="qr-frame">
                      <img
                        src="/api/lan/qr.png"
                        alt="QR code to open StripCheck on your phone"
                        width="220"
                        height="220"
                      />
                    </div>
                    <a className="pair-url" href={lanUrl}>
                      {lanUrl}
                      <ExternalLink size={15} />
                    </a>
                    <div className="notice">
                      <Wifi size={20} />
                      <p>
                        {lan.enabled === false || lan.lan_enabled === false
                          ? "Phone access needs LAN mode. Restart with the “Start for phone” launcher included with the project."
                          : "Keep this computer running while you use your phone."}
                      </p>
                    </div>
                    <button
                      className="button primary"
                      onClick={async () => {
                        try {
                          await navigator.clipboard.writeText(lanUrl);
                          setToast("Phone link copied");
                        } catch {
                          setToast("Select the link above to copy it.");
                        }
                      }}
                    >
                      Copy phone link <ArrowRight size={17} />
                    </button>
                  </>
                )}
              </>
            ) : (
              <LoaderCircle className="spin" />
            )}
          </div>
        </Modal>
      )}
      {about && (
        <Modal title="A little context." onClose={() => setAbout(false)}>
          <div className="about-copy">
            <ShieldCheck size={34} />
            <h3>Evidence comes first.</h3>
            <p>
              StripCheck compares the exact batch printed on a medicine pack
              with locally stored CDSCO quality and spurious alert records. When
              details are unclear or conflict, it asks for confirmation or
              abstains.
            </p>
            <p>
              “No listing found” describes only the records currently loaded. It
              is not a statement about the medicine’s quality.
            </p>
            <h3>Designed to stay local.</h3>
            <p>
              Photos, checks and saved packs are stored on the computer running
              StripCheck. Only the explicit list-sync action contacts the
              official data source. Native iPhone checks send photos to your
              configured StripCheck computer.
            </p>
            <p>
              Demonstrations use invented data and are always labelled.
              Diagnostics test software behaviour; research validation is a
              separate task.
            </p>
            <a
              className="text-link"
              href="https://github.com/Suraj-B12/StripCheck"
              target="_blank"
              rel="noreferrer"
            >
              Original project <ExternalLink size={16} />
            </a>
          </div>
        </Modal>
      )}
    </>
  );
}
export default App;
