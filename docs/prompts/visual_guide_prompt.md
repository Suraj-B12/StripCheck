# Prompt: build a visual project guide (one HTML file)

Copy everything below the line into your AI coding assistant, opened inside the other project's repository. Fill in the three lines in square brackets first.

---

Build a single-file visual guide to this project: `docs/guide/index.html`. It is for our team, to help us understand the whole project deeply and explain it confidently in a viva. Readers are engineering students who know basic programming but not this codebase.

Project name: [PROJECT NAME]
One-sentence summary: [WHAT IT DOES AND FOR WHOM]
Audience and occasion: [e.g. final review with our professor on DATE]

## 1. First, understand the project (do not write anything yet)
- Read the README, design or spec documents, decision logs, the source code, the tests, the data folders and any evaluation results.
- Work out these facts and note the file each one comes from: the problem, users, inputs and outputs, architecture, data sources, how data is collected and cleaned, the main algorithm or agent loop, every model or API used, safety checks and fallbacks, limits (timeouts, retries, loop bounds), how it was tested and evaluated with the real numbers, known limitations, and the important design choices with the alternatives that were rejected.
- If the design documents and the code disagree, the code wins. Record the difference.
- Never invent a number, feature or result. If you cannot confirm something from the repository, leave it out or label it "not verified".

## 2. Language rules (most important)
- Plain English. Short sentences. One idea per paragraph. Prefer "is", "has", "uses" over fancy verbs.
- Explain every technical term the first time it appears, in one simple line, then use it precisely. Example: "OCR (optical character recognition): software that reads text from a photo."
- Use one everyday comparison where it helps understanding (for example, "the verifier works like a checklist a pilot runs before take-off"). Never use a comparison that is wrong in detail.
- Explain why, not only what: for every component say what problem it solves and what would go wrong without it.
- Show real examples from the project's own data or a test case, and walk through one concrete example from start to finish.
- No marketing words (revolutionary, seamless, cutting-edge, robust, leverage, delve, crucial). No exclamation marks. No emojis.
- Be honest: show weaknesses, failures and negative results as plainly as successes.

## 3. Sections (adapt the names to this project; keep the order and the intent)
1. **The problem in one picture.** The real-world problem, who has it, and a diagram of the before and after. List the only possible outputs the system can give.
2. **Big-picture architecture.** One diagram of every component and how data flows between them, with one line per component.
3. **Getting the data.** Where the data comes from, how it is fetched (rate limits, retries, formats), and what is stored.
4. **Parsing and cleaning.** Each cleaning rule as a before/after card using real examples. What happens to bad rows.
5. to 7. **The core pipeline, step by step.** One section per major stage (for example: reading input, finding candidates, deciding). Each has a diagram, the rules in the order they fire, and real examples.
8. **How the system thinks.** The decision loop or algorithm as a flowchart: states, branch points, what a model decides versus what fixed rules decide, and the bounds that guarantee it finishes.
9. **The human in the loop** (if any). When and why it asks the user, what it asks, and why the questions are designed that way.
10. **Safety checks and failsafes.** A table: "if X is missing or fails, then Y happens", covering network, model, bad input, empty data and timeouts.
11. **Memory and feedback** (if any). What it learns, where that is stored, and what it is never allowed to change.
12. **Testing and evaluation.** How it was tested, the dataset, the metrics explained in plain words with the formula, the real result tables, what was compared (A/B), and what the results do and do not prove.
13. **Why this and not that.** A table of design decisions: the choice made, the alternative, why we chose ours, and what we gave up.
14. **Viva cheat-sheet.** 15 to 20 likely examiner questions with short, accurate answers (3 to 6 sentences each), including hard ones about weaknesses and limitations.
15. **Glossary.** Every technical term, one line each, alphabetical.

At the top: a title, a one-paragraph summary and a "read this in 10 minutes" path that lists the five most important sections.

## 4. Visual components to use
- **Inline SVG diagrams** (at least 10 across the page): architecture, data flow, pipeline stages, the decision flowchart, the before/after of the problem, and one walkthrough example. Use boxes, arrows and short labels. Text in a diagram must be at least 12 px and must not overlap arrows or other text. Use the same colour for the same kind of thing everywhere (for example blue for agents, green for tools, grey for storage, amber for warnings).
- **Before/after cards** for cleaning and transformation rules.
- **Callout boxes** with consistent meanings, each with a small label:
  - "Key idea": the one thing to remember.
  - "Design vs build": an amber box wherever the original plan and the actual code differ, saying both.
  - "Why it matters": consequences.
  - "Watch out": known weaknesses.
- **Tables** for rules, failsafes, decisions, metrics and results. Keep tables narrow, or let them scroll inside their own box on phones.
- **A worked example strip** that follows one real input through every stage with the actual intermediate values.
- **Numbers as small stat tiles** (big number, short label, source) for headline facts.

## 5. Page design rules
- One self-contained HTML file: inline CSS and inline SVG. It must work offline. No JavaScript needed to read anything; collapsible parts use `<details>`. No external images. Fonts: system font stack, or one Google Font with a system fallback.
- A sticky table of contents (a sidebar on wide screens, a top bar on phones), with numbered sections and anchor links (`#problem`, `#architecture` and so on).
- Colours defined as CSS variables. Support light and dark mode with `prefers-color-scheme`. Text contrast at least 4.5:1.
- A calm, editorial look: generous white space, a readable body size (17 to 18 px), a line length of about 70 characters, and clear heading sizes. It must not look like a generic AI template: no gradients everywhere, no emoji icons, no glowing cards.
- Works at 375 px phone width with no horizontal page scroll. Wide diagrams and tables scroll inside their own box.
- Prints cleanly (`@media print`: hide the table of contents, avoid breaking inside diagrams).
- Accessible: semantic headings in order, `alt` or `<title>` text on diagrams, visible focus styles.

## 6. Check before you finish
- Every number and claim traced to a file in the repository. List those sources in an HTML comment at the end of the file.
- Open the page and check it at desktop width, at 375 px, and in dark mode. Fix overflow, overlapping labels and unreadable diagram text.
- Validate the HTML structure (no unclosed tags).
- Read the whole page once as a newcomer: if a paragraph needs knowledge that has not been explained yet, add a one-line explanation or reorder.
- Give me a short summary of: the sections written, the places where design and build differ, any facts you could not verify, and any gaps or risks in the project that the team should be ready to discuss.
