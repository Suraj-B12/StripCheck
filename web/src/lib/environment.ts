/** GitHub Pages serves an authored, synthetic showcase without a local server. */
export const PUBLIC_DEMO = import.meta.env.MODE === "pages";
export const PROJECT_URL = "https://github.com/Suraj-B12/StripCheck";

export function appHref(path: string): string {
  const route = path.startsWith("/") ? path : `/${path}`;
  return PUBLIC_DEMO ? `${import.meta.env.BASE_URL}#${route}` : route;
}

export function currentPath(): string {
  if (!PUBLIC_DEMO) return window.location.pathname;
  const hash = window.location.hash.slice(1);
  return hash.startsWith("/") ? hash.split("?")[0] : "/";
}
