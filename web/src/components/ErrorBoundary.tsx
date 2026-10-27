import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

/** Keep an unexpected rendering failure from leaving the user with a blank page. */
export class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(_error: Error, _info: ErrorInfo) {
    /* never log pack details */
  }
  render() {
    if (this.state.failed)
      return (
        <main className="inner-page">
          <section className="glass-card empty-state" role="alert">
            <h1>Let’s reopen StripCheck.</h1>
            <p>
              This screen could not be displayed. Your saved checks remain on
              this computer.
            </p>
            <button
              className="button primary"
              onClick={() => window.location.reload()}
            >
              Reload the website
            </button>
          </section>
        </main>
      );
    return this.props.children;
  }
}
