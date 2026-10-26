"""Render docs/prompts/brief/*.txt into a shareable copy-button page (docs/prompts/brief_page.html).

Usage: python docs/prompts/build_brief.py && python docs/prompts/build_brief_page.py
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
BRIEF = HERE / "brief"

master = (BRIEF / "00_MASTER_PROMPT.txt").read_text(encoding="utf-8").strip()
cards = []
for p in sorted(BRIEF.glob("T*.txt")):
    body = p.read_text(encoding="utf-8").strip()
    m = re.search(r"THEME CARD (T\d+) · (\w+) · Priority (\d)(?: \((.+?)\))?", body)
    obj = re.search(r"\*\*Objective\.\*\*\s*(.+)", body)
    cards.append({
        "id": m.group(1), "key": m.group(2), "priority": int(m.group(3)), "isNew": bool(m.group(4)),
        "objective": obj.group(1).strip() if obj else "",
        "questions": len(re.findall(r"(?m)^- Q\d", body)),
        "known": len(re.findall(r"(?m)^- `", body)),
        "text": body,
    })
order = {"T13": 0, "T14": 1, "T15": 2, "T11": 3, "T12": 4, "T10": 5, "T08": 6}
cards.sort(key=lambda c: (c["priority"], order.get(c["id"], 99), c["id"]))
data = json.dumps({"master": master, "cards": cards}, ensure_ascii=False).replace("</", "<\\/")
total_known = sum(c["known"] for c in cards)

PAGE = r"""<title>StripCheck Survey Brief</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..800&family=Atkinson+Hyperlegible+Mono:wght@400..600&family=Atkinson+Hyperlegible+Next:wght@400..700&display=swap">
<style>
/* Layout: one reading column (instructions, master prompt) above a grid of theme cards; StripCheck tokens from docs/design/ui_direction.md */
:root {
  --paper: #F4F5F7; --card: #FFFFFF; --ink: #14171C; --ink-2: #4B5462; --ink-3: #6E7787; --rule: #DCDFE5;
  --foil: #E3E7EC; --foil-mid: #C5CBD3; --pen: #22389E; --pen-soft: #E7EAF8; --on-pen: #FFFFFF; --ok: #1F6B45;
  --display: "Archivo", "Arial Narrow", Arial, sans-serif;
  --body: "Atkinson Hyperlegible Next", "Segoe UI", Roboto, Arial, sans-serif;
  --mono: "Atkinson Hyperlegible Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #0F1216; --card: #161A20; --ink: #E8EBF0; --ink-2: #AEB6C2; --ink-3: #8C95A3; --rule: #2A313B;
  --foil: #232931; --foil-mid: #3A424D; --pen: #8EA2F0; --pen-soft: #1C2340; --on-pen: #0F1216; --ok: #7CC9A0; color-scheme: dark } }
:root[data-theme="dark"] {
  --paper: #0F1216; --card: #161A20; --ink: #E8EBF0; --ink-2: #AEB6C2; --ink-3: #8C95A3; --rule: #2A313B;
  --foil: #232931; --foil-mid: #3A424D; --pen: #8EA2F0; --pen-soft: #1C2340; --on-pen: #0F1216; --ok: #7CC9A0; color-scheme: dark }
* { box-sizing: border-box; }
body { background: var(--paper); color: var(--ink); font: 400 16.5px/1.55 var(--body); margin: 0;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 64px; }
.wrap { max-width: 1080px; margin: 0 auto; display: grid; gap: 28px; }
:focus-visible { outline: 3px solid var(--pen); outline-offset: 2px; }
h1, h2 { font-family: var(--display); font-stretch: 84%; text-wrap: balance; margin: 0; letter-spacing: -.005em; }
h1 { font-size: clamp(30px, 5vw, 44px); font-weight: 760; line-height: 1.05; }
h2 { font-size: 24px; font-weight: 700; }
p { margin: 0; }
.muted { color: var(--ink-2); }
.eyebrow { font: 600 12.5px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--ink-3); }
.mark { justify-self: start; display: inline-flex; gap: 4px; padding: 6px; border-radius: 10px; background: linear-gradient(180deg, var(--card), var(--foil) 45%, var(--foil-mid)); }
.mark span { width: 22px; height: 28px; display: grid; place-items: center; border-radius: 6px; background: var(--card); font: 600 14px/1 var(--mono); color: var(--ink); box-shadow: inset 0 -2px 3px rgba(0,0,0,.06); }
.mark span.gap { width: 8px; background: none; box-shadow: none; }
header { display: grid; gap: 14px; }
.lead { max-width: 68ch; font-size: 17.5px; }
.facts { display: flex; flex-wrap: wrap; gap: 8px 18px; font: 500 14px/1.4 var(--mono); color: var(--ink-2); }
.panel { background: var(--card); border: 1px solid var(--rule); border-radius: 10px; padding: 20px 22px; display: grid; gap: 14px; min-width: 0; }
ol.steps { margin: 0; padding-left: 22px; display: grid; gap: 8px; max-width: 72ch; }
ol.steps li::marker { font: 600 14px var(--mono); color: var(--pen); }
code, .mono { font-family: var(--mono); font-size: .92em; }
.row { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
label { font-weight: 600; }
input[type=text] { font: 500 15px var(--mono); padding: 8px 10px; border-radius: 8px; border: 1px solid var(--rule); background: var(--paper); color: var(--ink); min-width: 0; width: min(320px, 100%); }
button { font: 600 14.5px var(--body); border-radius: 8px; padding: 9px 14px; cursor: pointer; border: 1px solid var(--rule); background: var(--card); color: var(--ink); }
button.primary { background: var(--pen); border-color: var(--pen); color: var(--on-pen); }
button:hover { border-color: var(--pen); }
button[data-done] { border-color: var(--ok); color: var(--ok); }
button.primary[data-done] { background: var(--ok); border-color: var(--ok); color: var(--on-pen); }
details { border-top: 1px solid var(--rule); padding-top: 12px; min-width: 0; }
summary { cursor: pointer; font-weight: 600; color: var(--ink-2); }
pre { margin: 12px 0 0; padding: 14px; background: var(--paper); border: 1px solid var(--rule); border-radius: 8px; font: 13.5px/1.5 var(--mono); white-space: pre-wrap; overflow-wrap: anywhere; max-height: 420px; overflow: auto; color: var(--ink); }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr)); gap: 16px; }
.cards.four { grid-template-columns: repeat(auto-fill, minmax(min(100%, 228px), 1fr)); }
.cards.four .card h3 { font-size: 16px; }
.subh { font: 600 13px/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--ink-3); margin-top: 6px; }
.card { background: var(--card); border: 1px solid var(--rule); border-radius: 10px; padding: 16px 18px; display: grid; gap: 10px; grid-template-rows: auto auto 1fr auto auto; min-width: 0; }
.card .top { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; }
.card .id { font: 700 13px var(--mono); color: var(--ink-3); }
.card h3 { margin: 0; font: 650 18px/1.25 var(--mono); overflow-wrap: anywhere; }
.chip { font: 600 12px/1 var(--mono); padding: 5px 8px; border-radius: 999px; border: 1px solid var(--rule); color: var(--ink-2); white-space: nowrap; }
.chip.p1 { border-color: var(--pen); color: var(--pen); background: var(--pen-soft); }
.card .obj { color: var(--ink-2); font-size: 15px; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
.card .meta { font: 500 13px var(--mono); color: var(--ink-3); }
.fname { font: 500 12.5px var(--mono); color: var(--ink-2); background: var(--paper); border: 1px dashed var(--rule); border-radius: 6px; padding: 6px 8px; overflow-wrap: anywhere; }
.group-h { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.note { font-size: 14px; color: var(--ink-3); }
textarea.fallback { position: fixed; left: -9999px; top: 0; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<div class="wrap">
  <header>
    <div class="mark" aria-hidden="true"><span>S</span><span>T</span><span>R</span><span>I</span><span>P</span><span class="gap"></span><span>C</span><span>H</span><span>E</span><span>C</span><span>K</span></div>
    <p class="eyebrow">Literature-survey brief · v1.0 · 26 Oct 2026</p>
    <h1>Help us survey the literature for StripCheck</h1>
    <p class="lead muted">StripCheck is a college Agentic AI project that checks whether a photographed medicine pack's batch is on India's CDSCO drug-quality alert lists. Your model researches one theme at a time and returns a report in a fixed format, which we check, verify and fold into our paper and thesis.</p>
    <div class="facts"><span>1 master prompt</span><span>15 theme cards</span><span>__KNOWN__ references already verified</span><span>1 conversation per theme</span></div>
  </header>

  <section class="panel" aria-labelledby="how-h">
    <h2 id="how-h">How to run it</h2>
    <ol class="steps">
      <li>Use a model with live web search or a deep-research mode. Without browsing it can still help, but it must say <code>browsing: no</code>.</li>
      <li>Open a <b>new conversation for each theme</b>. Press <b>Copy master + card</b> on a theme below and paste it as your first message.</li>
      <li>If the answer stops early, send <code>Continue exactly where you stopped, in the same format.</code> and keep every part.</li>
      <li>Save the whole answer, unedited, as a Markdown file with the name shown on the card.</li>
      <li>Send the files back to the StripCheck team. Start with the Priority 1 themes; even three or four help.</li>
    </ol>
    <div class="row">
      <label for="model">Your model's name</label>
      <input type="text" id="model" placeholder="e.g. gemini-deep-research" autocomplete="off" spellcheck="false">
      <span class="note">Used only to fill in the file names below. Stays in your browser.</span>
    </div>
  </section>

  <section class="panel" aria-labelledby="master-h">
    <div class="group-h"><h2 id="master-h">Master prompt</h2><span class="note">__MASTER_WORDS__ words · the same for every theme</span></div>
    <p class="muted">It describes the project, the research rules and the exact output format. The theme buttons below already include it, so you only need this button if you want to paste the two parts separately.</p>
    <div class="row"><button type="button" id="copy-master">Copy master prompt only</button></div>
    <details><summary>Read the master prompt</summary><pre id="master-text"></pre></details>
  </section>

  <section aria-labelledby="p1-h" class="wrap" style="gap:14px">
    <div class="group-h"><h2 id="p1-h">Priority 1 · gaps and new topics</h2><span class="note">Run these first.</span></div>
    <p class="subh">New topics</p>
    <div class="cards" id="p1new"></div>
    <p class="subh">Gaps in our survey</p>
    <div class="cards four" id="p1gap"></div>
  </section>

  <section aria-labelledby="p2-h" class="wrap" style="gap:14px">
    <div class="group-h"><h2 id="p2-h">Priority 2 · independent cross-checks</h2><span class="note">Themes we have covered; a second model finds what we missed.</span></div>
    <div class="cards four" id="p2"></div>
  </section>

  <section class="panel" aria-labelledby="next-h">
    <h2 id="next-h">What happens to your files</h2>
    <p class="muted">A checker validates each file against the format (header, eleven sections, source fields, citation keys, matching BibTeX, a DOI or URL for every source) and flags sources we already have. Every new source is then verified against Crossref, arXiv, Semantic Scholar or the publisher before it can enter the paper's bibliography. The thesis credits the external model in its survey method.</p>
  </section>
</div>
<textarea class="fallback" id="fallback" aria-hidden="true" tabindex="-1"></textarea>

<script type="application/json" id="data">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const now = new Date();
const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
let model = '';
try { model = localStorage.getItem('sc-model') || ''; } catch (e) {}
const modelInput = document.getElementById('model');
modelInput.value = model;
const slug = s => (s || '').trim().toLowerCase().replace(/[^a-z0-9.]+/g, '-').replace(/^-|-$/g, '') || '<model>';
function fileName(c) { return `${c.key}__${slug(model)}__${today}.md`; }

async function copyText(text, btn, label) {
  try { await navigator.clipboard.writeText(text); done(btn, 'Copied'); }
  catch (e) {
    const ta = document.getElementById('fallback');
    ta.value = text; ta.focus(); ta.select();
    let ok = false; try { ok = document.execCommand('copy'); } catch (e2) {}
    done(btn, ok ? 'Copied' : 'Selected: press Ctrl+C');
  }
  function done(b, msg) { b.dataset.done = ''; b.textContent = msg; setTimeout(() => { delete b.dataset.done; b.textContent = label; }, 2200); }
}

document.getElementById('master-text').textContent = D.master;
document.getElementById('copy-master').addEventListener('click', e => copyText(D.master, e.currentTarget, 'Copy master prompt only'));

function render() {
  for (const id of ['p1new', 'p1gap', 'p2']) document.getElementById(id).replaceChildren();
  for (const c of D.cards) {
    const el = document.createElement('article');
    el.className = 'card';
    el.innerHTML = `
      <div class="top"><span class="id">${c.id}</span><span class="chip ${c.priority === 1 ? 'p1' : ''}">${c.isNew ? 'new topic' : 'priority ' + c.priority}</span></div>
      <h3>${c.key}</h3>
      <p class="obj"></p>
      <p class="meta">${c.questions} questions · ${c.known ? c.known + ' known refs listed' : 'no known refs yet'}</p>
      <div class="fname" title="Save the model's answer under this name"></div>
      <div class="row">
        <button type="button" class="primary" data-act="both">Copy master + card</button>
        <button type="button" data-act="card">Card only</button>
      </div>
      <details><summary>Read the card</summary><pre></pre></details>`;
    el.querySelector('.obj').textContent = c.objective;
    el.querySelector('pre').textContent = c.text;
    el.querySelector('.fname').textContent = fileName(c);
    el.querySelector('[data-act=both]').addEventListener('click', e => copyText(D.master + '\n\n' + c.text, e.currentTarget, 'Copy master + card'));
    el.querySelector('[data-act=card]').addEventListener('click', e => copyText(c.text, e.currentTarget, 'Card only'));
    document.getElementById(c.priority === 1 ? (c.isNew ? 'p1new' : 'p1gap') : 'p2').appendChild(el);
  }
}
modelInput.addEventListener('input', () => {
  model = modelInput.value;
  try { localStorage.setItem('sc-model', model); } catch (e) {}
  document.querySelectorAll('.card').forEach(el => { const c = D.cards.find(x => x.id === el.querySelector('.id').textContent); el.querySelector('.fname').textContent = fileName(c); });
});
render();
</script>
"""
html = (PAGE.replace("__DATA__", data).replace("__KNOWN__", str(total_known))
        .replace("__MASTER_WORDS__", f"{len(master.split()):,}"))
(HERE / "brief_page.html").write_text(html, encoding="utf-8")
print(f"wrote brief_page.html ({len(html) // 1024} KB, {len(cards)} cards, {total_known} known refs)")
