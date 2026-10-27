/** Storage may be disabled or full; optional preferences must never break a check. */
export const storage = {
  get(key: string): string | null {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(key: string, value: string): void {
    try {
      localStorage.setItem(key, value);
    } catch {
      /* optional persistence */
    }
  },
  remove(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch {
      /* optional persistence */
    }
  },
};

/** Only the latest operation may update a screen, including delayed restores. */
export function createRequestGate() {
  let current: AbortController | undefined;
  return {
    begin() {
      current?.abort();
      current = new AbortController();
      return current.signal;
    },
    isCurrent(signal: AbortSignal) {
      return current?.signal === signal && !signal.aborted;
    },
    cancel() {
      current?.abort();
      current = undefined;
    },
  };
}

export function requestScope(parent?: AbortSignal | null, timeoutMs = 30_000) {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout>;
  const forward = () => controller.abort(parent?.reason);
  const reset = (ms = timeoutMs) => {
    clearTimeout(timer);
    timer = setTimeout(
      () =>
        controller.abort(
          new DOMException(
            "The server took too long to respond. Your saved checks remain in Activity. Please retry.",
            "TimeoutError",
          ),
        ),
      ms,
    );
  };
  if (parent?.aborted) forward();
  else parent?.addEventListener("abort", forward, { once: true });
  reset();
  return {
    signal: controller.signal,
    reset,
    dispose() {
      clearTimeout(timer);
      parent?.removeEventListener("abort", forward);
    },
  };
}
