Status: COMPLETE

Checklist
- [x] KQ1 PyPI versions/dates/requires_python/Windows wheels/breaking changes for all listed packages; Python 3.11 vs 3.12
- [x] KQ2 LangGraph 1.x API (interrupt, Command(resume), stream modes, durability, SqliteSaver, deprecations)
- [x] KQ3 RapidOCR 3.x (PP-OCRv5, word boxes, GPU on Windows, latency)
- [x] KQ4 Ollama small LLMs (structured output, tool calling, 6 GB VRAM)
- [x] KQ5 Ollama small VLMs as OCR second reader
- [x] KQ6 Phoenix, FastAPI SSE, Python MCP SDK
- [x] KQ7 Frontend npm versions and @fontsource availability
- [x] KQ8 Proposed requirements.txt and package.json

Final takeaways
1. Original lower-bound/upper-bound pins all still admit current releases; the real traps are: RapidOCR defaults to PP-OCRv6 (not v5); numpy 2.5 / scipy 1.18 need Python >=3.12; mcp is 2.x with FastMCP renamed MCPServer; fresh majors (pillow 13, pandas 3, opencv 5, reportlab 5, typescript 7, react-router 8).
2. Recommend Python 3.12 (3.11 works with numpy<2.5, scipy<1.18). The laptop's default python is 3.10.11, which most packages no longer support.
3. Ollama 0.17.7 is ~23 minor versions behind (current 0.40.11, 24 Oct 2026); gemma4 (support PR dated 2 Apr 2026) will not run on it; qwen3.5 is documented to ignore `format` when think=False on 0.17.6 (issue #14645, fixed 0.31.2). Structured output has regressed repeatedly: validate every reply with Pydantic, never send `tools` and `format` together, record the Ollama version in experiments.
4. LLM shortlist (6 GB, 8k ctx): qwen2.5:3b (spec default), qwen3:4b, gemma3:4b, phi4-mini, granite4:3b; VLM second reader: qwen3-vl:4b, qwen2.5vl:3b, glm-ocr (version requirement undocumented). No independent pharma-packaging OCR benchmark for any VLM was found.
5. Phoenix: run `phoenix serve` in a separate venv; app uses only arize-phoenix-otel + openinference-instrumentation-langchain. FastAPI native SSE (>=0.135.0) replaces sse-starlette.

# StripCheck engineering scan: tech stack, October 2026

## KQ1 PyPI versions, Python support, Windows wheels, breaking changes

### Cited Findings (raw PyPI JSON scan, performed 25 Oct 2026; "latest" = info.version i.e. latest non-prerelease; date = earliest upload time of that release's files; Windows wheel info from the file list of the latest release)
Each package URL is https://pypi.org/pypi/NAME/json.
Format: name latest (date) | requires_python | Win cp311 / cp312 wheel status | recent releases

- langgraph 1.2.17 (2026-10-24) | >=3.10 | pure py3-none-any wheel (OK on 3.11 and 3.12) | 1.2.16 2026-10-16, 1.2.15 10-12, 1.2.14 10-06, 1.2.13 10-05, 1.2.12 09-21 — [PyPI](https://pypi.org/pypi/langgraph/json)
- langgraph-checkpoint-sqlite 3.1.2 (2026-10-12) | >=3.10 | pure wheel | 3.1.1 2026-07-30, 3.1.0 2026-05-12, 3.0.3 2026-01-19 — [PyPI](https://pypi.org/pypi/langgraph-checkpoint-sqlite/json)
- langgraph-checkpoint 4.3.0 (2026-10-12) | >=3.10 | pure wheel | 4.2.0 2026-08-07, 4.1.1 2026-05-22 — [PyPI](https://pypi.org/pypi/langgraph-checkpoint/json)
- langgraph-prebuilt 1.1.1 (2026-10-15) >=3.10 — [PyPI](https://pypi.org/pypi/langgraph-prebuilt/json); langgraph-sdk 0.4.9 (2026-10-23) >=3.10 — [PyPI](https://pypi.org/pypi/langgraph-sdk/json)
- langchain 1.4.7 (2026-10-21) | >=3.10 — [PyPI](https://pypi.org/pypi/langchain/json)
- langchain-core 1.7.0 (2026-10-22) | >=3.10 | pure wheel | 1.6.13 2026-10-21 (very fast cadence) — [PyPI](https://pypi.org/pypi/langchain-core/json)
- langchain-ollama 1.1.0 (2026-04-07) | >=3.10 | pure wheel | 1.0.1 2025-12-12, 1.0.0 2025-10-17 — [PyPI](https://pypi.org/pypi/langchain-ollama/json)
- ollama (python client) 0.6.3 (2026-09-29) | >=3.8 | pure wheel | 0.6.2 2026-04-29, 0.6.1 2025-11-13 — [PyPI](https://pypi.org/pypi/ollama/json)
- pydantic 2.14.1 (2026-10-11) | >=3.10 | pure wheel (pydantic-core ships separate wheels) | 2.14.0 2026-10-08, 2.13.5 2026-08-28 — [PyPI](https://pypi.org/pypi/pydantic/json)
- rapidocr 3.10.0 (2026-10-08) | <4,>=3.8 | pure wheel, NO sdist | 3.9.2 2026-07-21, 3.9.1 2026-07-02, 3.9.0 2026-06-23, 3.8.4 2026-06-15 — [PyPI](https://pypi.org/pypi/rapidocr/json)
- onnxruntime 1.31.0 (2026-10-09) | >=3.11 (3.10 dropped) | cp311-win_amd64 and cp312-win_amd64 present | 1.30.0 2026-09-10, 1.29.0 2026-08-17, 1.28.0 2026-07-25 — [PyPI](https://pypi.org/pypi/onnxruntime/json)
- onnxruntime-gpu 1.31.0 (2026-10-09) | >=3.11 | cp311/cp312 win_amd64 present — [PyPI](https://pypi.org/pypi/onnxruntime-gpu/json)
- onnxruntime-directml 1.24.4 (2026-03-17) | >=3.11 | cp311/cp312 win_amd64 present; LAGS onnxruntime (1.24.x vs 1.31.0) — [PyPI](https://pypi.org/pypi/onnxruntime-directml/json)
- opencv-python-headless: PyPI info.version shows 5.0.0.93 (2026-07-02) but 4.14.0.94 was uploaded LATER (2026-07-28); both ship cp37-abi3-win_amd64 wheels; requires_python >=3.6; 4.13.0.92 2026-02-05 — [PyPI](https://pypi.org/pypi/opencv-python-headless/json). OpenCV 5.0 is a major version and the 4.x line is still being released.
- pdfplumber 0.11.10 (2026-06-15) | >=3.8 | pure wheel | 0.11.9 2026-01-05 — still 0.11.x, so original pin >=0.11,<0.12 is valid — [PyPI](https://pypi.org/pypi/pdfplumber/json)
- pypdfium2 5.14.0 (2026-10-04) | >=3.6 | py3-none-win_amd64 wheel | 5.13.0 2026-08-13 — [PyPI](https://pypi.org/pypi/pypdfium2/json)
- rapidfuzz 3.14.6 (2026-08-30) | >=3.11 (3.10 dropped) | cp311/cp312 win_amd64 present — [PyPI](https://pypi.org/pypi/rapidfuzz/json)
- qrcode 8.2 (2025-05-01) | <4.0,>=3.9 | pure wheel (qrcode[pil] pulls pillow) — [PyPI](https://pypi.org/pypi/qrcode/json)
- zxing-cpp 3.1.1 (2026-07-29) | >=3.9 | cp311-win_amd64 and cp312-abi3-win_amd64 wheels present | 3.1.0 2026-07-07, 3.0.0 2026-02-10 (major bump) — [PyPI](https://pypi.org/pypi/zxing-cpp/json)
- pillow 13.0.0 (2026-10-16) | >=3.11 | cp311/cp312 win_amd64 present (MAJOR bump 12 -> 13 nine days ago) | 12.3.0 2026-07-01 — [PyPI](https://pypi.org/pypi/pillow/json)
- numpy 2.5.4 (2026-10-10) | >=3.12 (!) | NO cp311 wheel in latest; cp312 win_amd64 present — [PyPI](https://pypi.org/pypi/numpy/json). Python 3.11 is capped at an earlier numpy (to be confirmed below).
- scipy 1.18.1 (2026-08-21) | >=3.12 (!) | NO cp311 wheel; cp312 win_amd64 present — [PyPI](https://pypi.org/pypi/scipy/json)
- pandas 3.1.0 (2026-10-22) | >=3.11 | cp311/cp312 win_amd64 present (pandas 3.x major) — [PyPI](https://pypi.org/pypi/pandas/json)
- httpx 0.28.1 (2024-12-06) is still the latest STABLE; 1.0.dev6 (2026-08-31) pre-release exists — [PyPI](https://pypi.org/pypi/httpx/json)
- requests 2.34.2 (2026-05-14) | >=3.10 | pure wheel — [PyPI](https://pypi.org/pypi/requests/json)
- python-dotenv 1.2.4 (2026-10-01) | >=3.10 | pure wheel — [PyPI](https://pypi.org/pypi/python-dotenv/json)
- arize-phoenix 20.26.0 (2026-10-23) | <3.15,>=3.11 (3.10 dropped) | pure wheel; extremely fast cadence (20.24.0 on 10-21, 20.25.0 and 20.26.0 both on 10-23) — [PyPI](https://pypi.org/pypi/arize-phoenix/json)
- arize-phoenix-otel 0.17.2 (2026-09-28) | <3.15,>=3.11 | pure wheel | 0.17.1 2026-08-10, 0.17.0 2026-08-08 — [PyPI](https://pypi.org/pypi/arize-phoenix-otel/json)
- arize-phoenix-client 3.5.0 (2026-09-08) | <3.15,>=3.10 — [PyPI](https://pypi.org/pypi/arize-phoenix-client/json)
- openinference-instrumentation-langchain 0.1.80 (2026-10-23) | <3.15,>=3.10 | pure wheel | 0.1.79 2026-10-09 — [PyPI](https://pypi.org/pypi/openinference-instrumentation-langchain/json)
- fastapi 0.162.0 (2026-10-23) | >=3.10 | pure wheel; 0.159 to 0.162 all released 10-21..10-23 — [PyPI](https://pypi.org/pypi/fastapi/json)
- uvicorn 0.54.0 (2026-09-25) | >=3.10 — [PyPI](https://pypi.org/pypi/uvicorn/json)
- sse-starlette 3.5.1 (2026-10-24) | >=3.10 — [PyPI](https://pypi.org/pypi/sse-starlette/json)
- python-multipart 0.0.32 (2026-06-04) | >=3.10 — [PyPI](https://pypi.org/pypi/python-multipart/json)
- mcp (official Python SDK) 2.3.0 (2026-10-02) | >=3.10 | 1.30.0 also published 2026-09-07 (1.x maintenance continues) | 2.0.1 2026-08-26, 2.1.0/2.1.1 2026-08-24/25, 2.2.0 2026-09-07 — MAJOR VERSION 2 exists — [PyPI](https://pypi.org/pypi/mcp/json)
- reportlab 5.1.0 (2026-10-22) | <4,>=3.9 | pure wheel; major 5.0.0 on 2026-06-18 — [PyPI](https://pypi.org/pypi/reportlab/json)
- pytest 9.1.1 (2026-06-19) | >=3.10 — [PyPI](https://pypi.org/pypi/pytest/json)
- hypothesis 6.170.9 (2026-10-23) | >=3.11 (3.10 dropped) | cp311-abi3 win_amd64 present — [PyPI](https://pypi.org/pypi/hypothesis/json)
- matplotlib 3.11.2 (2026-09-11) | >=3.11 | cp311/cp312 win_amd64 present — [PyPI](https://pypi.org/pypi/matplotlib/json)
- statsmodels 0.15.0 (2026-08-27) | >=3.10 | cp311/cp312 win_amd64 present; first release since 0.14.6 (2025-12-05) — [PyPI](https://pypi.org/pypi/statsmodels/json)
- streamlit 1.66.1 (2026-10-21) | >=3.11 | pure wheel — [PyPI](https://pypi.org/pypi/streamlit/json)

### Dependency constraints read from PyPI `requires_dist` (25 Oct 2026)
- langgraph 1.2.17 requires langchain-core>=1.4.7,<2; langgraph-checkpoint>=4.3.0,<5; langgraph-prebuilt>=1.1.0,<1.2; langgraph-sdk>=0.4.6,<0.5; pydantic>=2.7.4; xxhash>=3.5.0 — [PyPI](https://pypi.org/pypi/langgraph/json)
- langgraph-checkpoint-sqlite 3.1.2 requires aiosqlite>=0.20; langgraph-checkpoint>=4.3.0,<5; sqlite-vec>=0.1.6 — [PyPI](https://pypi.org/pypi/langgraph-checkpoint-sqlite/json). Note: 3.1.2 needs langgraph-checkpoint>=4.3.0 so it must be installed together with langgraph 1.2.x (langgraph-checkpoint 4.x).
- langchain-ollama 1.1.0 requires langchain-core>=1.2.21,<2 and ollama>=0.6.1,<1.0 — [PyPI](https://pypi.org/pypi/langchain-ollama/json)
- langchain-core 1.7.0 requires langsmith>=0.14.9,<1; pydantic>=2.7.4,<3 — [PyPI](https://pypi.org/pypi/langchain-core/json)
- rapidocr 3.10.0 requires pyclipper>=1.2.0, opencv-python-headless>=4.5.1.48, numpy>=1.19.5,<3, six, Shapely!=2.0.4,>=1.7.1, PyYAML, Pillow, tqdm, omegaconf!=2.2.1, requests, colorlog; extra "rtl" adds python-bidi. It does NOT depend on any onnxruntime package: the user must install onnxruntime (or -gpu / -directml) separately — [PyPI](https://pypi.org/pypi/rapidocr/json)
- arize-phoenix 20.26.0 requires fastapi>=0.142.0, grpcio, numpy, pandas>=1.0, pydantic>=2.1.0, sqlalchemy[asyncio]>=2.1.1,<3, starlette>=0.37.0, strawberry-graphql==0.335.0 (exact), pydantic-ai-slim[...]>=2.53.0,<3, pydantic-monty==1.1.0 (exact), opentelemetry-sdk/exporter-otlp, openinference-instrumentation>=0.1.60, openinference-instrumentation-openai>=0.1.41 — heavy install, many exact pins; install in a SEPARATE venv/server process from the app to avoid resolver conflicts — [PyPI](https://pypi.org/pypi/arize-phoenix/json)
- arize-phoenix-otel 0.17.2 requires openinference-instrumentation>=0.1.38, opentelemetry-exporter-otlp, opentelemetry-exporter-otlp-proto-http>=1.45.0, opentelemetry-sdk, wrapt — [PyPI](https://pypi.org/pypi/arize-phoenix-otel/json)
- openinference-instrumentation-langchain 0.1.80 requires openinference-instrumentation>=0.1.71, opentelemetry-api, opentelemetry-instrumentation, wrapt; langchain-core is only in the optional extra "instruments" (>=0.3.9) — [PyPI](https://pypi.org/pypi/openinference-instrumentation-langchain/json)
- mcp 2.3.0 requires mcp-types==2.3.0, httpx2>=2.10.0 (NOTE: a package named "httpx2", not httpx), jsonschema>=4.20, opentelemetry-api>=1.28, pydantic>=2.12.0, pyjwt[crypto]>=2.10.1, python-multipart>=0.0.9, pywin32>=311 on Windows, sse-starlette>=3.0.0, starlette, uvicorn>=0.31.1, anyio>=4.9 — [PyPI](https://pypi.org/pypi/mcp/json). I did not verify what httpx2 is; treat as unverified.
- numpy: newest release with a cp311 win_amd64 wheel is 2.4.6 (2026-05-18); 2.4.5 2026-05-15 — [PyPI](https://pypi.org/pypi/numpy/json)
- scipy: newest release with a cp311 win_amd64 wheel is 1.17.1 (2026-02-23) — [PyPI](https://pypi.org/pypi/scipy/json)

### npm registry (registry.npmjs.org `dist-tags.latest`, 25 Oct 2026)
- react 19.3.1 (2026-10-14); react-dom 19.3.1 (2026-10-14, peer react ^19.3.1) — [react](https://registry.npmjs.org/react), [react-dom](https://registry.npmjs.org/react-dom)
- vite 8.3.5 (2026-10-21), engines node ^20.19.0 || >=22.12.0 — [npm](https://registry.npmjs.org/vite)
- @vitejs/plugin-react 6.1.2 (2026-10-05), peer vite ^8.0.0, node ^20.19.0 || >=22.12.0 — [npm](https://registry.npmjs.org/@vitejs%2fplugin-react)
- typescript 7.0.2 (2026-07-08) — major 7 is latest — [npm](https://registry.npmjs.org/typescript)
- react-router 8.5.0 (2026-10-19), engines node >=22.22.0, peer react/react-dom >=19.2.7 — [npm](https://registry.npmjs.org/react-router); react-router-dom latest 7.18.4 (2026-09-15) node>=20 peer react>=18 — [npm](https://registry.npmjs.org/react-router-dom)
- @types/react 19.3.0 and @types/react-dom 19.3.0 (2026-09-09) — [npm](https://registry.npmjs.org/@types%2freact)
- vitest 5.0.5 (2026-10-15), node ^22.12 || ^24 || >=26, peer vite ^6.4||^7||^8 — [npm](https://registry.npmjs.org/vitest); eslint 10.13.0 (2026-10-16) — [npm](https://registry.npmjs.org/eslint); @tanstack/react-query 5.104.5 (2026-10-19) — [npm](https://registry.npmjs.org/@tanstack%2freact-query)
- @fontsource packages ALL EXIST at 5.3.0 (published 2026-07-19), both static ("@fontsource/…") and variable ("@fontsource-variable/…"): archivo, atkinson-hyperlegible-next, atkinson-hyperlegible-mono, atkinson-hyperlegible, noto-sans-devanagari, noto-sans-kannada — e.g. [@fontsource/atkinson-hyperlegible-next](https://registry.npmjs.org/@fontsource%2fatkinson-hyperlegible-next), [@fontsource/noto-sans-kannada](https://registry.npmjs.org/@fontsource%2fnoto-sans-kannada), [@fontsource-variable/archivo](https://registry.npmjs.org/@fontsource-variable%2farchivo)

### Takeaway (preliminary)
Every original lower-bound pin is satisfied by current releases, and all upper-bounded pins (langgraph<2, checkpoint-sqlite<4, langchain-ollama<2, rapidocr<4, pdfplumber<0.12, arize-phoenix<21, arize-phoenix-otel<1, openinference-instrumentation-langchain<0.2) still admit the latest releases. Traps: numpy 2.5 and scipy 1.18 need Python >=3.12; mcp is at 2.x; pillow 13, pandas 3, opencv 5, reportlab 5 are fresh majors.

### Cited Findings (re-checks on 26 Oct 2026, PyPI JSON via curl)
- Versions moved since the first scan: arize-phoenix 20.26.1 (2026-10-25 18:34 UTC, requires >=3.11,<3.15); sse-starlette 3.6.0 (2026-10-25, now requires >=3.11); httpx2 2.16.0 (2026-10-21, >=3.11); mcp still 2.3.0 (>=3.10); langgraph still 1.2.17; langchain-ollama still 1.1.0 (>=3.10,<4.0.0); ollama client still 0.6.3; numpy 2.5.4 requires >=3.12 and the newest numpy with a cp311 win_amd64 wheel is 2.4.6 (2026-05-18) — [arize-phoenix](https://pypi.org/pypi/arize-phoenix/json), [sse-starlette](https://pypi.org/pypi/sse-starlette/json), [httpx2](https://pypi.org/pypi/httpx2/json), [mcp](https://pypi.org/pypi/mcp/json), [numpy](https://pypi.org/pypi/numpy/json)
- The Windows terminal's default `python` on the user's machine reported "Python 3.10.11 (MSC v.1929 64 bit)" when I accidentally opened it (no code run). Python 3.10 is below the minimum of arize-phoenix, onnxruntime, rapidfuzz, hypothesis, pillow, pandas, matplotlib, streamlit — so a new 3.11 or 3.12 venv is required — observed locally, no URL.
- ONNX Runtime GPU: from 1.27 the `onnxruntime-gpu` PyPI package is built for CUDA 13.0 by default (cuDNN 9.x); CUDA 12.8-or-newer builds are separate packages; 1.21-1.26 defaulted to CUDA 12.8 — [ONNX Runtime CUDA EP docs](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)
- langchain-ollama `ChatOllama`: `format="json"` (JSON mode), `reasoning` (True returns reasoning in `additional_kwargs["reasoning_content"]`, False disables, None model default), `num_ctx`, `keep_alive`, `temperature`, `num_predict`, `validate_model_on_init`, `with_structured_output()`, `bind_tools()`; the reference page documents no deprecations and does not state the default structured-output method — [LangChain reference ChatOllama](https://reference.langchain.com/python/integrations/langchain_ollama/ChatOllama/)

### Inferences
- Recommend Python 3.12 (64-bit) for the app venv. Reasons: every package in the list ships a cp312 Windows wheel (or a pure/abi3 wheel); numpy 2.5.x and scipy 1.18.x need >=3.12 while 3.11 forces numpy<=2.4.6 and scipy<=1.17.1; the LangGraph docs note `get_stream_writer` problems only on Python <3.11, so both 3.11 and 3.12 are fine for LangGraph. Python 3.11 remains fully workable (all other packages support it) if the caps are applied; the original spec pin of 3.11 is therefore not wrong, only more restrictive. The exact end-of-life dates were not verified in this run.
- Pin pip packages tightly, and run `pip install --dry-run -r requirements.txt` (or `uv pip compile`) once before coding; I did not run a resolver (instructed not to install), so the combined set below is checked only pairwise against the `requires_dist` I read.
- opencv-python-headless: pip would choose 5.0.0.93 (highest version) although 4.14.0.94 was uploaded later; rapidocr 3.10.0 only demands >=4.5.1.48 and I found no statement that it is tested against OpenCV 5, so pin `<5` for safety.
- onnxruntime (CPU) is the conservative choice for RapidOCR; onnxruntime-gpu 1.31 needs CUDA 13 and cuDNN 9 on the machine, and onnxruntime-directml lags at 1.24.4.

### Gaps
- Breaking changes between pins and latest for pillow 13, pandas 3, reportlab 5, opencv 5, zxing-cpp 3, matplotlib 3.11, statsmodels 0.15 were not read in changelogs (only versions/dates/Python support). Windows wheel presence was read from PyPI file lists only for the latest release of each package.

## KQ2 LangGraph 1.x API

### Takeaway
interrupt() / Command(resume=...) are stable and un-deprecated in langgraph 1.2.17; the new 1.2 additions are `stream_events(..., version="v3")`, `interrupt(..., response_schema=...)` (needs langgraph>=1.2.12) and `stream(version="v2")` typed chunks. SqliteSaver is a sync, lock-serialised saver for light use; use AsyncSqliteSaver for async graphs. The original pins (langgraph>=1.2,<2; checkpoint-sqlite>=3.1,<4) are correct and current.

### Cited Findings
- Import paths: `from langgraph.types import interrupt, Command`; the value passed to interrupt() must be JSON-serialisable; the resume value becomes the return value of interrupt(). Requires a checkpointer and `thread_id` in `config["configurable"]`; resume on the same thread — [LangGraph interrupts docs](https://docs.langchain.com/oss/python/langgraph/interrupts)
- On resume the node restarts from its beginning (code before interrupt() re-runs); do not wrap interrupt() in bare try/except; do not reorder or conditionally skip interrupt() calls (resume matching is index-based within a node); use a conditional edge, not a `while True`, for re-asking; keep pre-interrupt side effects idempotent — [interrupts docs](https://docs.langchain.com/oss/python/langgraph/interrupts)
- Parallel interrupts: resume with a dict mapping interrupt id to value: `Command(resume={i.id: ... for i in stream.interrupts})` — [interrupts docs](https://docs.langchain.com/oss/python/langgraph/interrupts)
- Typed resume: `interrupt({...}, response_schema=Decision)` accepts Pydantic model / TypedDict / dataclass, validates on resume, raises pydantic.ValidationError on invalid input, retry possible; requires langgraph>=1.2.12 — [interrupts docs](https://docs.langchain.com/oss/python/langgraph/interrupts)
- `graph.invoke(...)` still surfaces interrupts under `result["__interrupt__"]`; the docs now recommend `graph.stream_events(input, config=config, version="v3")` which exposes `.output`, `.interrupted`, `.interrupts` — [interrupts docs](https://docs.langchain.com/oss/python/langgraph/interrupts). The streaming page does not document those stream_events properties ([streaming docs](https://docs.langchain.com/oss/python/langgraph/streaming.md)), so treat v3 details as only partly verified.
- Static `interrupt_before`/`interrupt_after` breakpoints are "not recommended" for human-in-the-loop; `Command(resume=...)` is the only Command form intended as graph input — [interrupts docs](https://docs.langchain.com/oss/python/langgraph/interrupts)
- Stream modes: `values`, `updates`, `messages`, `custom`, `checkpoints`, `tasks`, `debug`; list allowed. `get_stream_writer` is imported from `langgraph.config`; call `writer({...})` inside a node/tool and consume with `stream_mode="custom"`. On Python <3.11 in async code get_stream_writer does not work (use a `writer: StreamWriter` parameter from `langgraph.types`) — a point in favour of Python >=3.11 — [streaming docs](https://docs.langchain.com/oss/python/langgraph/streaming)
- `stream(..., version="v2")` (needs LangGraph 1.1+) makes each chunk a dict with `type`, `ns`, `data`; v1 is still the "current default". Dict-style access on `GraphOutput` (`result["key"]`) is documented as deprecated: use `.value` and `.interrupts`. `subgraphs=True` streams subgraph events — [streaming docs](https://docs.langchain.com/oss/python/langgraph/streaming)
- Durability modes passed per call, e.g. `durability="sync"`: `"exit"` (persist only when graph run exits; fastest; no mid-run crash recovery), `"async"` (persist while the next step executes; small risk if process crashes), `"sync"` (persist before next step starts; highest durability) — [checkpointers docs](https://docs.langchain.com/oss/python/langgraph/checkpointers.md). The default mode was not stated on the page I read (gap).
- SqliteSaver import `from langgraph.checkpoint.sqlite import SqliteSaver`; `AsyncSqliteSaver` in `langgraph.checkpoint.sqlite.aio` (needs aiosqlite); package must be installed separately — [checkpointers docs](https://docs.langchain.com/oss/python/langgraph/checkpointers.md)
- SqliteSaver source: `__init__(self, conn: sqlite3.Connection, *, serde: SerializerProtocol | None = None)`; `from_conn_string(cls, conn_string: str)` is a classmethod CONTEXT MANAGER (`with SqliteSaver.from_conn_string("x.db") as saver:`) that opens `sqlite3.connect(..., check_same_thread=False)` and closes on exit; every DB op is serialised through a `threading.Lock`; `setup()` sets `PRAGMA journal_mode=WAL` and creates `checkpoints` and `writes` tables (auto-called, don't call directly); class docstring says it is for lightweight sync use and "does not scale to multiple threads"; its async methods (aget_tuple, alist, aput) raise NotImplementedError and point to AsyncSqliteSaver — [source on GitHub main](https://raw.githubusercontent.com/langchain-ai/langgraph/main/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py)
- Default serializer JsonPlusSerializer "uses ormsgpack and JSON under the hood"; unsupported types (e.g. pandas DataFrames) need `JsonPlusSerializer(pickle_fallback=True)`; encryption via `EncryptedSerializer.from_pycryptodome_aes()` reading `LANGGRAPH_AES_KEY` — [checkpointers docs](https://docs.langchain.com/oss/python/langgraph/checkpointers.md). Keep thread_id < 255 chars (Postgres limit) — [persistence docs](https://docs.langchain.com/oss/python/langgraph/persistence)
- Deprecation since 1.0: `langgraph.prebuilt.create_react_agent` is deprecated in favour of LangChain's `create_agent`; no breaking changes to core APIs were listed for v1 — [LangGraph v1 release notes](https://docs.langchain.com/oss/python/releases/langgraph-v1)
- Recent releases: 1.2.17 (24 Oct) sets explicit recursion limit equal to default, fixes RemoteGraph subgraph namespace, removes precautionary upper bounds on third-party deps; 1.2.16 (16 Oct) fixes several resume bugs (invalid resume values no longer stop other tasks, resumed Command update applies once, subgraphs don't rerun finished tasks on resume, pending writes from resumed exit-durability run saved once); langgraph-prebuilt 1.1.1 (15 Oct) fixes ToolNode swallowing invalid resume values — [LangGraph GitHub releases](https://github.com/langchain-ai/langgraph/releases). Resume-path fixes in 1.2.16 argue for pinning langgraph>=1.2.16.

### Inferences
- Cross-process checkpointer behaviour is NOT documented on pages I read. From the source: WAL mode + per-connection thread lock means one SqliteSaver connection is safe across threads in one process; two processes (e.g. FastAPI server and a CLI) opening the same .db file is possible via SQLite file locking but nothing in the docs guarantees it. For the StripCheck design (HITL pause in one request, resume in another) keep one process owning the checkpoint DB, and resume by thread_id.
- Because FastAPI is async, use AsyncSqliteSaver (aiosqlite) in the server, or run graphs in a worker thread with sync SqliteSaver.
- The default durability mode, and the need for a checkpointer to be passed at compile time vs run time, should be tested in a smoke test rather than assumed.

### Gaps
- Default value of `durability` not seen. `AsyncSqliteSaver` constructor / `from_conn_string` signature not read. stream_events v3 return type not fully documented on pages read. Strict msgpack / allowed-modules serializer behaviour not found in docs read.

## KQ3 RapidOCR 3.x

### Takeaway
RapidOCR 3.10.0 (8 Oct 2026) defaults to PP-OCRv6 (det small + rec small, since 3.9.0) with PP-OCRv4 mobile as the text-line classifier, NOT PP-OCRv5 as the original spec assumed; PP-OCRv5/v4 remain selectable per stage. Per-word and per-character boxes are exposed via `return_word_box` and `return_single_char_box` (both Global config keys, default false). ONNX Runtime GPU/DirectML are enabled with `EngineConfig.onnxruntime.use_cuda` / `use_dml`. No Kannada recogniser exists in the routing table.

### Cited Findings
- rapidocr 3.10.0 released 08 Oct (2026); notes: PyTorch>=1.13 needed for secure model loading, OpenCV is headless by default, models are loaded lazily on first det/cls/rec call (first call slower), raw memory image buffers accepted, multilingual model routing in YAML; not labelled breaking — [RapidOCR GitHub releases](https://github.com/RapidAI/RapidOCR/releases), [usage docs](https://rapidai.github.io/RapidOCRDocs/main/install_usage/rapidocr/usage/)
- 3.9.0 (23 Jun): PP-OCRv6 det small and rec small became the DEFAULT models; wheel grew ~15 MB to ~29 MB; at that release only ONNXRuntime and OpenVINO were supported. 3.9.1 (02 Jul) added PaddlePaddle/MNN/PyTorch engines for PP-OCRv6. 3.9.2 (21 Jul) added `use_preprocess_img` and vertical-padding options. 3.8.4 (15 Jun) raised minimum Python to 3.8. 3.8.0 (08 Apr) added PP-OCRv5 cls, `model_root_dir` and `download_models` — [RapidOCR GitHub releases](https://github.com/RapidAI/RapidOCR/releases)
- Default config (main branch config.yaml): Det engine onnxruntime, lang_type "ch", model_type "small", ocr_version "PP-OCRv6", limit_side_len 736, limit_type min, thresh 0.3, box_thresh 0.5, unclip_ratio 1.6; Cls ocr_version PP-OCRv4 mobile, cls_thresh 0.9; Rec PP-OCRv6 small, rec_batch_num 6; Global text_score 0.5, return_word_box false, return_single_char_box false, use_preprocess_img true, min_side_len 30, max_side_len 2000 — [config.yaml](https://raw.githubusercontent.com/RapidAI/RapidOCR/main/python/rapidocr/config.yaml)
- EngineConfig.onnxruntime has `use_cuda: false` with `cuda_ep_cfg` (device_id 0, cudnn_conv_algo_search EXHAUSTIVE), `use_dml: false` with `dml_ep_cfg: null`, `use_cann`, `use_coreml`; EngineConfig.openvino (inference_num_threads, performance_hint...); EngineConfig.torch has `use_cuda`, `use_npu`, `use_mps` — [config.yaml](https://raw.githubusercontent.com/RapidAI/RapidOCR/main/python/rapidocr/config.yaml)
- Official docs show only the Torch GPU example: `RapidOCR(params={"Det.engine_type": EngineType.TORCH, "EngineConfig.torch.use_cuda": True, "EngineConfig.torch.cuda_ep_cfg.device_id": 0})`. Params use dotted keys matching config.yaml, e.g. `RapidOCR(params={"Det.model_type": ModelType.TINY, "Rec.model_type": ModelType.TINY})`; imports `from rapidocr import EngineType, LangDet, ModelType, OCRVersion, RapidOCR` — [usage docs](https://rapidai.github.io/RapidOCRDocs/main/install_usage/rapidocr/usage/)
- Word boxes: `engine(img, return_word_box=True)` fills `result.word_results` with entries `(text, confidence, [[tl],[tr],[br],[bl]])`; outputs also: `boxes` (N,4,2), `txts`, `scores`, `elapse_list`, `elapse`. The docs page I read does not explain `return_single_char_box` (flag exists only in config.yaml) — [usage docs](https://rapidai.github.io/RapidOCRDocs/main/install_usage/rapidocr/usage/)
- Install: rapidocr does NOT bundle an inference engine since 2.0.6; run `pip install rapidocr onnxruntime`; from 3.10.0 opencv-python-headless is the default (do not install both opencv variants); `rapidocr[rtl]` extra adds python-bidi; `rapidocr check` verifies install — [install docs](https://rapidai.github.io/RapidOCRDocs/main/install_usage/rapidocr/install/)
- Model routing table (docs, rapidocr>=3.9.0): Det/Rec PP-OCRv6 tiny/small/medium keyed `multi_PP-OCRv6_{det,rec}_{tiny,small,medium}`; PP-OCRv5 rec mobile exists for `en_`, `latin_`, `devanagari_`; PP-OCRv5 server rec is Chinese only; PP-OCRv4 rec mobile has `en_`, `latin_`, `devanagari_`. English is supported by v6 (tiny/small/medium), v5 mobile, v4 mobile. Devanagari supported by v5 mobile and v4 mobile but NOT in the v6 language list. Kannada does not appear in any route; Tamil (ta) and Telugu (te) are listed — [RapidOCR model list](https://rapidai.github.io/RapidOCRDocs/main/model_list/)
- PP-OCRv6 (PaddleOCR): tiny 1.5M, small 7.7M, medium 34.5M parameters; medium/small support 50 languages in one model (Simplified/Traditional Chinese, English, Japanese, 46 Latin-script languages), tiny 49 (no Japanese); medium reaches 86.2% det Hmean and 83.2% rec accuracy on PaddleOCR's in-house benchmark, 4.6 and 5.1 points above PP-OCRv5_server; Apache 2.0 — [PaddleOCR PP-OCRv6 docs](https://www.paddleocr.ai/main/en/version3.x/algorithm/PP-OCRv6/PP-OCRv6.html); summarised in [AI Weekly](https://aiweekly.co/alerts/paddlepaddles-pp-ocrv6-beats-billion-scale-vlms-at-ocr). Vendor-run benchmark, not independent.
- CPU latency: PaddleOCR table reports end-to-end 200-image set on Intel Xeon 8350C with OpenVINO at 1.40 s/image (medium), 0.59 s (small), 0.20 s (tiny) vs 7.30 s for PP-OCRv5_server (column order read from search-result snippet, so medium/small/tiny assignment is only partly verified) — [PaddleOCR PP-OCRv6 docs](https://www.paddleocr.ai/main/en/version3.x/algorithm/PP-OCRv6/PP-OCRv6.html). RapidOCR docs example run (CPU, hardware unspecified): det 0.146 s, cls 0.018 s, rec 0.401 s, total 0.565 s per image — [usage docs](https://rapidai.github.io/RapidOCRDocs/main/install_usage/rapidocr/usage/)
- Third-party summary (DeepWiki, not official): use_cuda and use_dml are bool flags defaulting to false, use_dml is Windows-only, provider name for DirectML is DmlExecutionProvider; with onnxruntime-gpu the version must match the installed CUDA/cuDNN — [DeepWiki RapidOCR runtime configuration](https://deepwiki.com/RapidAI/RapidOCR/7.2-runtime-configuration-options)

### Inferences
- For a 6 GB RTX 4050 laptop the OCR stack is small enough (v6 small is 7.7M params) that CPU onnxruntime is probably adequate; the GPU is better reserved for the Ollama LLM/VLM. Use onnxruntime (CPU) for OCR and keep onnxruntime-gpu out of the same venv: onnxruntime and onnxruntime-gpu/-directml share the same module name and conflict when co-installed (a general known pip behaviour; not verified in sources above).
- Because defaults changed from v5 to v6 silently, pin `ocr_version` explicitly in params if reproducibility matters in the paper (e.g. `Det.ocr_version`, `Rec.ocr_version`). English-only strips could use `lang_type` en with v5 mobile if v6 multi misreads digits; this needs an empirical test.
- Kannada / Devanagari strings on Indian cartons (mfr address, Hindi text) will not be reliably read; the batch/expiry fields are Latin digits, so this is acceptable.

### Gaps
- Exact `return_single_char_box` semantics not documented on pages read (re-checked 26 Oct: usage page only has an untitled "single-character coordinates" table column). The usage page has no ONNX Runtime CUDA or DirectML example (only the Torch GPU example). OpenVINO/DirectML latency numbers on this laptop not available. The correct langs for `LangRec` enum values in v6 (e.g. "en" vs "multi") not verified. ONNX Runtime GPU package is CUDA 13.0 / cuDNN 9 by default from 1.27 (see KQ1 re-checks) — [ONNX Runtime CUDA EP docs](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html).
- Added in KQ4 re-check: qwen2.5:3b is 1.9 GB, 32K ctx, tagged tools, under the Qwen licence (not Apache 2.0; 7b is Apache 2.0); llama3.2 3b is 2.0 GB, 128K, tools — [Ollama qwen2.5](https://ollama.com/library/qwen2.5), [Ollama llama3.2](https://ollama.com/library/llama3.2)

## KQ4 Small local LLMs in Ollama

### Cited Findings (landscape scan, part 1)
- Ollama library, sorted by popularity (25 Oct 2026): gemma4 (capabilities vision, tools, thinking, audio, cloud; sizes e2b, e4b, 12b, 26b, 31b; 27.8M pulls; updated "1 week ago"); qwen3.5 (vision, tools, thinking; 0.8b, 2b, 4b, 9b, 27b, 35b, 122b; 23.4M; 1 week ago); qwen3.6 (vision, tools, thinking; 27b, 35b; 1 week ago); qwen3.8 (vision, tools, thinking; 27b; 1 month ago); qwen3 (tools, thinking; 0.6b-235b; 41.5M; 1 year ago); gemma3 (vision; 270m, 1b, 4b, 12b, 27b; 41.4M; updated 2 weeks ago); qwen3-vl (vision, tools, thinking; 2b, 4b, 8b, 30b, 32b, 235b; 6.8M; updated 5 days ago); glm-ocr (vision, tools; 8.6M; 1 week ago); qwen2.5vl (vision; 3b, 7b, 32b, 72b; 5.6M; 1 year ago); minicpm-v (vision; 8b; 5.6M); llama3.2 (tools; 1b, 3b; 86.2M); gpt-oss (tools, thinking, cloud; 20b, 120b) — [Ollama library](https://ollama.com/library?sort=popular)
- Ollama search (260 models listed) shows newer niche families: "decision" models (d1 3B on LFM2.5-VL-3B, tev1 0.8b/4b, strands-decider 2b, nimble-v3 9b), bonsai-2 (vision/tools/thinking 2b,4b,9b,27b), nemotron-3.5-bolt (e4b; vision, tools, thinking, audio) — [Ollama search](https://ollama.com/search?o=newest). I did not evaluate them as they are new and obscure.
- Ollama blog 2026 posts: "Improved performance and model support with GGUF" (Jun 5, 2026, Ollama 0.30), "Faster Gemma 4 on MLX with multi-token prediction" (Jun 29, 2026, Ollama 0.31), "Ollama now supports Jev-style decision models" (Sep 29, 2026), "Speech models in Ollama" (Oct 24, 2026). Last blog posts on structured outputs (Dec 6, 2024) and thinking (May 30, 2025) — [Ollama blog](https://ollama.com/blog)
- IMPORTANT: user's Ollama is 0.17.7 while the blog implies Ollama has reached at least 0.31 by June 2026. Models like gemma4 and qwen3.5 may require a newer Ollama than 0.17.7 (to be checked).

### Cited Findings (part 2: model pages and Ollama version, fetched 25-26 Oct 2026)
- Latest Ollama is v0.40.11 (24 Oct 2026); recent versions 0.40.4 to 0.40.11 (12-24 Oct). The user's 0.17.7 is roughly 23 minor versions behind. The releases page I fetched did not state the first version that supports Gemma 4, Qwen3.5 or Qwen3-VL — [Ollama GitHub releases](https://github.com/ollama/ollama/releases)
- Gemma 4 (Google DeepMind, released 2 Apr 2026, Apache 2.0 per a secondary guide): secondary guides say Ollama 0.22 or newer is needed, but no official statement was found. UNVERIFIED — [pasqualepillitteri.it guide](https://pasqualepillitteri.it/en/news/616/google-gemma-4-open-source-ai-guide) (secondary source). Conclusion: gemma4 and qwen3.5 almost certainly need an Ollama upgrade from 0.17.7; the official model pages do not say which version.
- qwen3.5 tags (Ollama library): 0.8b 1.2-1.3 GB, 2b 2.7-3.1 GB, 4b 3.3-4.0 GB, 9b (latest) 6.6-7.6 GB, 27b 17-20 GB, 35b 22 GB; context 256K; input text+image (all qwen3.5 are multimodal); capabilities vision, tools, thinking; licence and min Ollama version NOT stated on the page — [Ollama qwen3.5](https://ollama.com/library/qwen3.5)
- gemma4 tags: e2b 4.6-7.5 GB (about 2.3B effective, 5.1B with embeddings), e4b 6.6-9.5 GB (about 4.5B effective, 8B with embeddings), 12b 7.7-8.0 GB (256K ctx), 26b 16-19 GB, 31b 19-20 GB; e2b/e4b 128K context and take text+image+audio; capabilities vision, tools, thinking, audio; page claims "native function-calling support"; licence and min Ollama version NOT stated on the page — [Ollama gemma4](https://ollama.com/library/gemma4)
- qwen3 (original, text only): 0.6b 523 MB (40K ctx), 1.7b 1.4 GB (40K), 4b 2.5 GB (256K, i.e. the 2507 refresh), 8b (latest) 5.2 GB (40K), 14b 9.3 GB, 30b 19 GB (256K), 32b 20 GB; tags tools + thinking; there is no separate "instruct-2507" tag in the list I fetched (4b and 30b carry the 2507 weights) — [Ollama qwen3](https://ollama.com/library/qwen3)
- gemma3: latest/4b 3.4 GB (128K, vision), 1b 806 MB (32K, text only), 12b 8.2 GB (128K, vision), 27b 17 GB; QAT variants exist (1b/4b/12b/27b it-qat; "3x less memory" than unquantised); requires Ollama 0.6 or later; tagged vision only (no "tools" tag) — [Ollama gemma3](https://ollama.com/library/gemma3)
- qwen3-vl: 2b 1.9 GB, 4b 3.3 GB, 8b (latest) 6.2 GB, 30b 20 GB, 32b 21 GB; 256K context; capabilities vision, tools, thinking; "requires Ollama 0.12.7"; readme says OCR supports 32 languages (up from 10) and is more robust to low light, blur and tilt — [Ollama qwen3-vl](https://ollama.com/library/qwen3-vl)

### Inferences (KQ4 so far)
- The 6 GB VRAM budget at 8k context realistically admits: <= 4B at Q4 with comfortable headroom (qwen3:4b 2.5 GB, gemma3:4b 3.4 GB, qwen3.5:4b 3.3 GB, gemma4:e2b ~4.6 GB), and 7-8B models only partly offloaded (qwen3:8b 5.2 GB leaves about 0.8 GB for KV cache and compute buffers, so expect partial CPU offload and slower tokens). 31 GB system RAM makes partial offload feasible. These fit estimates are my arithmetic from file sizes, not benchmarks.
- Because the user's Ollama (0.17.7) predates the 2026 families, the safe default that works today without an upgrade is qwen3:4b / qwen3:8b / gemma3:4b / qwen2.5:3b; upgrading Ollama to 0.40.x is recommended if gemma4 / qwen3.5 / qwen3-vl are wanted.

### Cited Findings (part 3: other small LLMs, structured-output bugs, Ollama settings)
- phi4-mini 3.8b: 2.5 GB, 128K context, text, tag "tools"; requires Ollama 0.5.13; licence not stated on the page — [Ollama phi4-mini](https://ollama.com/library/phi4-mini)
- granite4: 350m 708 MB (32K), 1b 3.3 GB (128K), 3b/micro 2.1 GB (128K), latest 2.1 GB; Apache 2.0; "tools" badge; readme lists function calling, text extraction, classification, RAG; no JSON/structured claims; min Ollama version not stated — [Ollama granite4](https://ollama.com/library/granite4)
- ministral-3 (vision + text): 3b 3.0 GB, 8b/latest 6.0 GB, 14b 9.1 GB; 256K context; Apache 2.0; requires Ollama 0.13.1 (page text says pre-release); page claims "native function calling and JSON outputting" — [Ollama ministral-3](https://ollama.com/library/ministral-3). Works on the user's 0.17.7 by version number.
- smollm3: https://ollama.com/library/smollm3 returned HTTP 404 on 26 Oct 2026, i.e. no such library entry was found at that URL (not evaluated further).
- Ollama structured outputs: pass a JSON schema object (e.g. `Model.model_json_schema()`) as `format`, validate with `Model.model_validate_json(response.message.content)`; page recommends also describing the schema in the prompt, and temperature 0; "Ollama's cloud currently does not support structured outputs"; the page says nothing about combining with thinking or tools — [Ollama structured outputs docs](https://docs.ollama.com/capabilities/structured-outputs). Secondary source claims property `description` fields in the schema are not seen by the model (unverified) — [web search summary, makandracards.com](https://makandracards.com/makandra/626409-ollama-structured-input-output)
- think parameter: bool or string level (low/medium/high); unset uses the model default from `/api/show`; `false` disables if the model permits; output in `message.thinking` vs `message.content`; interaction with structured output not covered on the page — [Ollama thinking docs](https://docs.ollama.com/capabilities/thinking)
- KNOWN BUG relevant to the user's version: "format is ignored when think is disabled for qwen3.5 series" (issue #14645, created 5 Mar 2026 on Ollama 0.17.6, i.e. one release before the user's 0.17.7). With think=False and a JSON schema, qwen3.5 returns prose; with think=True the schema is enforced. Reported also for qwen3.6 and gemma4 (v0.21.0; gemma4 fixed in 0.21.1, #15678). Closed 7 Jul 2026 via PR #15901; reporter confirmed fixed in 0.31.2; a user on 0.21.1 asked for a backport. Workarounds: use `/api/generate` instead of `/api/chat`, or a custom model without the thinking capability flag — [GitHub issue 14645](https://github.com/ollama/ollama/issues/14645)
- OPEN regression: "Models can't use tool-calls when format is set to json" (#18944, created 11 Oct 2026, Ollama 0.40.3, qwen3.5:9b; both thinking and non-thinking models fail). Maintainer: a JSON schema constrains output so a tool call cannot be produced; tool use with format worked for thinking models through 0.34.3 and broke in 0.34.4 after PR #18479. Fix PR #18975 open. Workaround: do not set `format` in the same request as `tools`; request JSON via the prompt — [GitHub issue 18944](https://github.com/ollama/ollama/issues/18944)
- Open: gemma3:12b `format` truncates prematurely on double-quoted terms in the input (#18094, 28 Aug 2026); qwen3.5:9b completes but replaces double quotes with single quotes — [GitHub issue 18094](https://github.com/ollama/ollama/issues/18094) (seen only via search summary: [GitHub search](https://api.github.com/search/issues?q=repo:ollama/ollama+qwen3.5+structured+format+think+is:issue&per_page=8)). Open: "Thinking + tools + qwen3 = empty output" (#10976, Jun 2025) — [GitHub issue 10976](https://github.com/ollama/ollama/issues/10976)
- Ollama 0.17.7 (released 5 Mar 2026) notes: thinking levels such as "medium" now correctly interpreted for all thinking models; no mention of qwen3.5 or gemma — [Ollama v0.17.7](https://github.com/ollama/ollama/releases/tag/v0.17.7). Qwen3.5 architecture PR #14378 opened 23 Feb 2026, so qwen3.5 inference very likely exists in 0.17.x (inference; first-supported release not confirmed) — [PR 14378](https://github.com/ollama/ollama/pull/14378). Gemma 4 support PR #15214 opened 2 Apr 2026, i.e. AFTER 0.17.7 was released — [PR 15214](https://github.com/ollama/ollama/pull/15214). So gemma4 will NOT run on 0.17.7 (inference from dates).
- Ollama settings (FAQ): keep_alive default 5 minutes, per-request `keep_alive` accepts duration string, seconds, negative (forever) or 0 (unload) and overrides OLLAMA_KEEP_ALIVE; default context length 4096 (override `OLLAMA_CONTEXT_LENGTH=8192` or `options.num_ctx`); OLLAMA_FLASH_ATTENTION=1 forces flash attention; OLLAMA_KV_CACHE_TYPE needs flash attention, q8_0 halves KV memory vs f16; OLLAMA_NUM_PARALLEL default 1; OLLAMA_MAX_LOADED_MODELS default 3x GPUs — [Ollama FAQ](https://docs.ollama.com/faq)

### Inferences (KQ4 final)
- Recommended small-LLM shortlist for 6 GB VRAM, 8k context, reliable JSON: (1) qwen2.5:3b (spec default, no thinking flag so none of the think/format bugs; not re-checked on the library page in this run, see Gaps), (2) qwen3:4b (2.5 GB; thinking model, so call with think=True or accept the bug class, parse `message.content` only), (3) gemma3:4b (3.4 GB, 128K, no thinking flag; but see open truncation bug on double quotes, reported on 12b), (4) phi4-mini 3.8b (2.5 GB), (5) granite4:3b (2.1 GB, Apache 2.0) as a small fallback, (6) qwen3:8b / ministral-3:8b (5.2-6.0 GB, will partially offload). Upgrade Ollama before using qwen3.5 / gemma4.
- Because the structured-output path has regressed repeatedly across Ollama releases (0.17.x think/format, 0.34.4 tools/format, 0.40.3 open), StripCheck should (a) pin and record the Ollama version in each experiment, (b) validate every LLM reply with Pydantic and retry once, and (c) keep the deterministic rule fallback. Do not combine `tools` and `format` in one call.
- Unless the user upgrades Ollama, avoid `think=False` with qwen3.5 (format ignored). A non-thinking family (qwen2.5, gemma3, llama3.2, phi4-mini, granite4) sidesteps the issue.

## KQ5 Small local VLMs in Ollama

### Cited Findings
- qwen3-vl: 2b 1.9 GB, 4b 3.3 GB, 8b 6.2 GB; 256K ctx; vision+tools+thinking; requires Ollama 0.12.7 (so OK on 0.17.7); OCR "32 languages (up from 10)", robust to low light/blur/tilt — [Ollama qwen3-vl](https://ollama.com/library/qwen3-vl)
- qwen2.5vl: 3b 3.2 GB, 7b/latest 6.0 GB, 32b 21 GB, 72b 49 GB; 125K ctx; requires Ollama 0.7.0; page says it can produce structured outputs from scanned invoices, forms and tables; no OCR benchmark on the page; licence not stated — [Ollama qwen2.5vl](https://ollama.com/library/qwen2.5vl)
- gemma3 vision: 4b 3.4 GB, 12b 8.2 GB (128K; requires Ollama 0.6+) — [Ollama gemma3](https://ollama.com/library/gemma3). qwen3.5 (all sizes multimodal: 0.8b-4b 1.2-4.0 GB) and gemma4 e2b/e4b (4.6-9.5 GB, also audio) are vision models too but need the Ollama-version/format caveats above — [Ollama qwen3.5](https://ollama.com/library/qwen3.5), [Ollama gemma4](https://ollama.com/library/gemma4)
- glm-ocr: 0.9B-parameter multimodal OCR model on the GLM-V encoder-decoder; latest 2.7 GB (bf16), q8_0 1.8 GB; 128K ctx; tags vision, tools; cites 94.62 on OmniDocBench V1.5 (vendor claim); prompt format "Text Recognition: ./image.png" (also Table / Figure Recognition); licence and min Ollama version not stated; library listing shows 8.6M pulls and a recent update — [Ollama glm-ocr](https://ollama.com/library/glm-ocr)
- minicpm-v 8b (MiniCPM-V 2.6): 5.5 GB, 32K ctx; SigLip-400M + Qwen2-7B; claims state of the art on OCRBench (at its 2024 release), 1.8 megapixel input encoded to about 640 visual tokens; requires Ollama 0.3.10; "updated 1 year ago" — [Ollama minicpm-v](https://ollama.com/library/minicpm-v)
- granite3.2-vision 2b: 2.4 GB, 16K ctx, vision+tools, requires Ollama 0.5.13, aimed at documents, tables, charts — [Ollama granite3.2-vision](https://ollama.com/library/granite3.2-vision)
- moondream 1.8b: 1.7 GB, 2K ctx, requires Ollama 0.1.33; page does not mention OCR and lists accuracy limitations; "updated 2 years ago" — [Ollama moondream](https://ollama.com/library/moondream)
- ministral-3 3b/8b take image input (3.0 / 6.0 GB, 256K, Apache 2.0, Ollama >=0.13.1) — [Ollama ministral-3](https://ollama.com/library/ministral-3)

### Inferences
- Best fits for an independent second reader on 6 GB VRAM and Ollama 0.17.7: qwen3-vl:4b (3.3 GB, the best-documented OCR claims), qwen2.5vl:3b (3.2 GB), glm-ocr (2.7 GB, dedicated OCR; but its Ollama version requirement is not documented and it may need a newer Ollama than 0.17.7), minicpm-v:8b (5.5 GB, tight). qwen3-vl:8b (6.2 GB) will not fully fit in 6 GB with an image's visual tokens plus KV cache, so expect CPU offload. These are arithmetic from sizes, not measured.
- A VLM only helps StripCheck if its read is independent of the OCR read; run it with a short prompt, temperature 0, and a Pydantic schema for fields {batch, product, mfg, expiry, maker} with null allowed, then compare character by character with the OCR result. Hallucination of plausible batch numbers is the main risk and is not covered by any source read here.

### Gaps
- No independent OCR benchmark (e.g. on pharma packaging) for any of these VLMs was found in this run; claims above are vendor/model-card claims. First-supported Ollama version for glm-ocr, qwen3.5 and gemma4 not confirmed from official release notes. Licences for several libraries not on the Ollama pages. qwen2.5:3b library page and llama3.2 not re-fetched this run.

## KQ6 Phoenix, FastAPI SSE, MCP SDK

### Takeaway
Phoenix 20.26.1 (25 Oct 2026) still installs with `pip install arize-phoenix` and starts with `phoenix serve` on port 6006; `phoenix.otel.register(project_name=..., auto_instrument=True, batch=...)` is the one-call setup. FastAPI now has native SSE (`fastapi.sse`, since 0.135.0), so sse-starlette is optional. The Python MCP SDK is at 2.x where `FastMCP` was renamed `MCPServer` and `mcp.server.fastmcp` no longer imports; pin `mcp>=2.3,<3` with the new import, or `mcp>=1.30,<2` to keep FastMCP.

### Cited Findings
- arize-phoenix latest is 20.26.1, uploaded 2026-10-25T18:34 UTC, requires_python `<3.15,>=3.11` (my earlier scan saw 20.26.0 at 23 Oct; the version moves almost daily) — [PyPI JSON, fetched via curl 26 Oct](https://pypi.org/pypi/arize-phoenix/json). Release notes for 20.24-20.26.1 list no breaking changes; 20.24.0 raised certifi to 2026.10.18 and required patched Node releases — [Phoenix GitHub releases](https://github.com/Arize-ai/phoenix/releases)
- Run locally: `pip install arize-phoenix` then `phoenix serve`; UI at http://localhost:6006; gRPC OTLP collector on 4317 — [Arize terminal deployment docs](https://arize.com/docs/phoenix/self-hosting/deployment-options/terminal.md), ports and `PHOENIX_WORKING_DIR` (default `~/.phoenix/`, holds the default SQLite DB) per search summary of [Arize configuration docs](https://www.arize.com/docs/phoenix/self-hosting/configuration.md) (page itself not fetched)
- `phoenix.otel.register` parameters per docs: `project_name` (or `PHOENIX_PROJECT_NAME`), `auto_instrument` (instruments every installed OpenInference instrumentor), `batch` (default False), `endpoint`, `protocol` ("grpc" or "http/protobuf"), `headers`; env vars `PHOENIX_COLLECTOR_ENDPOINT` (default http://localhost:6006 for local, no key needed), `PHOENIX_API_KEY`, `PHOENIX_PROJECT_NAME`; LangChain/LangGraph needs `pip install openinference-instrumentation-langchain` and `register(project_name="my-llm-app", auto_instrument=True)` — [Arize Phoenix OTEL setup docs](https://www.arize.com/docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-using-phoenix-otel.md). Third-party mirror lists also `set_global_tracer_provider` and `verbose` (unverified on the official page) — [mintlify mirror](https://mintlify.com/Arize-ai/phoenix/sdk/python/otel)
- FastAPI native SSE: `from fastapi.sse import EventSourceResponse, ServerSentEvent`, added in FastAPI 0.135.0; use `response_class=EventSourceResponse` on a generator endpoint (async or sync), yield Pydantic items (JSON in `data:`) or `ServerSentEvent(data=..., event=..., id=..., retry=...)`, `ServerSentEvent(raw_data="[DONE]")` for non-JSON; supports POST streams and `Last-Event-ID`; auto 15 s keep-alive ping, `Cache-Control: no-cache`, `X-Accel-Buffering: no`; page does not mention sse-starlette — [FastAPI SSE tutorial](https://fastapi.tiangolo.com/tutorial/server-sent-events/). Latest fastapi on PyPI is 0.162.0 — [PyPI](https://pypi.org/pypi/fastapi/json)
- sse-starlette is now 3.6.0 (2026-10-25), requires_python >=3.11 — [PyPI JSON via curl](https://pypi.org/pypi/sse-starlette/json). mcp 2.3.0 itself depends on sse-starlette>=3.0.0 so it will be installed anyway if mcp is used — [PyPI](https://pypi.org/pypi/mcp/json)
- Python MCP SDK: mcp 2.3.0 (2026-10-02) requires_python >=3.10 on PyPI, while the repo README says Python 3.11+ is required (conflict; treat 3.11+ as safe); 1.30.0 (2026-09-07) is the last seen 1.x. README now uses `from mcp.server import MCPServer`, tools via `@mcp.tool()`, transports stdio / streamable-http / sse, install `pip install "mcp[cli]"`, dev inspector `mcp dev server.py` — [python-sdk README](https://github.com/modelcontextprotocol/python-sdk), [PyPI](https://pypi.org/pypi/mcp/json)
- v1 to v2 migration: `mcp.server.fastmcp` raises ModuleNotFoundError, use `from mcp.server.mcpserver import MCPServer, Context`; `FastMCP` renamed `MCPServer`; WebSocket transport removed; transport settings (host, port) moved from constructor to `run()`; fields snake_case; `McpError` renamed `MCPError`; protocol types moved to `mcp-types`; `httpx` and `httpx-sse` replaced by `httpx2`; Streamable HTTP bodies capped at 4 MiB; OpenTelemetry on by default — [MCP Python SDK migration guide](https://py.sdk.modelcontextprotocol.io/migration/)
- `httpx2` 2.16.0 (2026-10-21), requires_python >=3.11, from github.com/pydantic/httpx2, described as "The next generation HTTP client" — [PyPI](https://pypi.org/pypi/httpx2/json), [project page](https://github.com/pydantic/httpx2). This resolves my earlier "unverified httpx2" note: it is a real, separate package under the pydantic org (note: mcp 2.x therefore needs Python >=3.11 in practice).

### Inferences
- Run Phoenix in its own venv/process (`phoenix serve`) and have the StripCheck app depend only on `arize-phoenix-otel` + `openinference-instrumentation-langchain`; this avoids the heavy server dependency tree (fastapi, strawberry-graphql==0.335.0 exact pin, sqlalchemy, grpcio) from clashing with the app's own fastapi pin.
- For SSE use FastAPI's native `fastapi.sse` (fewer dependencies); sse-starlette is only needed if code must support fastapi < 0.135.
- If MCP is used only to expose StripCheck's lookup as a tool for the demo, pin `mcp>=2.3,<3` and write `from mcp.server.mcpserver import MCPServer`; any tutorial using `from mcp.server.fastmcp import FastMCP` will fail on 2.x.

### Gaps
- Phoenix configuration page and `phoenix serve` flags (`--port`, etc.) were not read directly; the exact `register()` signature defaults other than `batch` are undocumented on the page read. Whether Phoenix 20 can run when installed with an older `fastapi` was not tested.

## KQ7 Frontend npm versions and fontsource

### Takeaway
All requested npm packages and @fontsource packages exist and were re-verified on 26 Oct 2026 against registry.npmjs.org: react/react-dom 19.3.1, vite 8.3.5, @vitejs/plugin-react 6.1.2, typescript 7.0.2, react-router 8.5.0 (react-router-dom 7.18.4), and all five requested fonts at @fontsource 5.3.0.

### Cited Findings
- react 19.3.1 and react-dom 19.3.1 (2026-10-14); vite 8.3.5 (2026-10-21; Node ^20.19.0 || >=22.12.0); @vitejs/plugin-react 6.1.2 (2026-10-05; peer vite ^8); typescript 7.0.2 (2026-07-08); react-router 8.5.0 (2026-10-19; Node >=22.22.0); react-router-dom 7.18.4 (2026-09-15; Node >=20) — [react](https://registry.npmjs.org/react), [vite](https://registry.npmjs.org/vite), [plugin-react](https://registry.npmjs.org/@vitejs%2fplugin-react), [typescript](https://registry.npmjs.org/typescript), [react-router](https://registry.npmjs.org/react-router), [react-router-dom](https://registry.npmjs.org/react-router-dom)
- @fontsource 5.3.0 (2026-07-19) exists for archivo, atkinson-hyperlegible-next, atkinson-hyperlegible-mono, noto-sans-devanagari, noto-sans-kannada (static `@fontsource/...`); variable builds `@fontsource-variable/...` confirmed for archivo, atkinson-hyperlegible-next and noto-sans-kannada (variable builds of atkinson-hyperlegible-mono and noto-sans-devanagari not checked) — [@fontsource/archivo](https://registry.npmjs.org/@fontsource%2farchivo), [@fontsource/atkinson-hyperlegible-next](https://registry.npmjs.org/@fontsource%2fatkinson-hyperlegible-next), [@fontsource/atkinson-hyperlegible-mono](https://registry.npmjs.org/@fontsource%2fatkinson-hyperlegible-mono), [@fontsource/noto-sans-devanagari](https://registry.npmjs.org/@fontsource%2fnoto-sans-devanagari), [@fontsource/noto-sans-kannada](https://registry.npmjs.org/@fontsource%2fnoto-sans-kannada), [@fontsource-variable/archivo](https://registry.npmjs.org/@fontsource-variable%2farchivo)
- Also (from first scan): @types/react and @types/react-dom 19.3.0 (2026-09-09); vitest 5.0.5 (Node ^22.12 || ^24 || >=26); eslint 10.13.0; @tanstack/react-query 5.104.5 — [@types/react](https://registry.npmjs.org/@types%2freact), [vitest](https://registry.npmjs.org/vitest)

### Inferences
- Choose react-router-dom 7.18.4 unless the laptop's Node is >=22.22; react-router 8.5.0 will refuse to install on older Node (engines). Node version on the laptop is unknown (not checked).
- TypeScript 7 is a new major and I did not verify that @vitejs/plugin-react 6 / vite 8 / vitest 5 declare support for it; if the build complains, fall back to the newest 5.x/6.x (version not verified here).

### Gaps
- Node version installed on the user's machine, TypeScript 7 compatibility with the Vite 8 toolchain, and whether Fontsource ships Devanagari and Kannada glyph subsets as separate files (they normally do via unicode-range subsets, not verified) were not checked.

## KQ8 Proposed requirements.txt and package.json

### Takeaway
A pin-ready set follows. It is checked against PyPI `requires_python`, wheel lists and `requires_dist` I read, but NOT resolver-tested (instructed not to install). Run `pip install --dry-run` first.

### Cited Findings
Every version below comes from the PyPI/npm checks cited under KQ1, KQ6 and KQ7 (as of 25-26 Oct 2026); recommendations on bounds are mine.

requirements.txt (Python 3.12 venv; app only)
```
# --- agent / orchestration ---
langgraph>=1.2.16,<2
langgraph-checkpoint-sqlite>=3.1.2,<4
langchain-core>=1.7,<2
langchain-ollama>=1.1,<2
ollama>=0.6.3,<1
pydantic>=2.12,<3

# --- OCR / vision (CPU onnxruntime; keep GPU for Ollama) ---
rapidocr>=3.10,<4
onnxruntime>=1.31,<2
opencv-python-headless>=4.14,<5
numpy>=2.5,<3          # Python 3.11 only: numpy>=2.4,<2.5
pillow>=12.3,<14
zxing-cpp>=3.1,<4
qrcode[pil]>=8.2,<9

# --- documents / matching ---
pdfplumber>=0.11.10,<0.12
pypdfium2>=5.14,<6
rapidfuzz>=3.14,<4
pandas>=3.1,<4

# --- server / ui ---
fastapi>=0.135,<1      # native SSE (fastapi.sse) since 0.135.0
uvicorn>=0.54,<1
python-multipart>=0.0.32,<1
python-dotenv>=1.2.4,<2
requests>=2.34,<3
httpx>=0.28.1,<0.29    # latest stable httpx is still 0.28.1

# --- observability (client side only) ---
arize-phoenix-otel>=0.17.2,<1
openinference-instrumentation-langchain>=0.1.80,<0.2

# --- optional ---
# mcp>=2.3,<3          # use: from mcp.server.mcpserver import MCPServer
# streamlit>=1.50      # only if a Streamlit UI is kept (latest 1.66.1)
# reportlab>=5.1,<6

# --- dev / evaluation ---
pytest>=9.1,<10
hypothesis>=6.170,<7
matplotlib>=3.11,<4
scipy>=1.18.1,<2       # Python 3.11 only: scipy>=1.17.1,<1.18
statsmodels>=0.15,<0.16
```
requirements-phoenix.txt (separate venv or process: `phoenix serve`)
```
arize-phoenix>=20.26.1,<21
```
package.json dependency block
```json
{
  "dependencies": {
    "react": "^19.3.1",
    "react-dom": "^19.3.1",
    "react-router-dom": "^7.18.4",
    "@fontsource-variable/archivo": "^5.3.0",
    "@fontsource/atkinson-hyperlegible-next": "^5.3.0",
    "@fontsource/atkinson-hyperlegible-mono": "^5.3.0",
    "@fontsource/noto-sans-devanagari": "^5.3.0",
    "@fontsource/noto-sans-kannada": "^5.3.0"
  },
  "devDependencies": {
    "vite": "^8.3.5",
    "@vitejs/plugin-react": "^6.1.2",
    "typescript": "^7.0.2",
    "@types/react": "^19.3.0",
    "@types/react-dom": "^19.3.0",
    "vitest": "^5.0.5"
  },
  "engines": { "node": ">=22.12.0" }
}
```
Model/runtime recommendations
- Ollama: upgrade from 0.17.7 to the current 0.40.x (v0.40.11 on 24 Oct 2026) if qwen3.5 / gemma4 / glm-ocr are wanted; stay on 0.17.7 and use qwen2.5:3b, qwen3:4b/8b, gemma3:4b, phi4-mini, granite4:3b, ministral-3:3b, qwen3-vl:4b, qwen2.5vl:3b otherwise — [Ollama releases](https://github.com/ollama/ollama/releases), [Ollama library](https://ollama.com/library?sort=popular)
- Call Ollama with `OLLAMA_CONTEXT_LENGTH=8192` (default is 4096), per-request `keep_alive`, `format=<pydantic schema>`, temperature 0 — [Ollama FAQ](https://docs.ollama.com/faq), [structured outputs](https://docs.ollama.com/capabilities/structured-outputs)

### Inferences
- npm "^" ranges on v0/major-new packages can pull breaking minors; commit package-lock.json and `requirements.lock` (from `pip freeze` or `uv pip compile`) after the first successful install so the paper's experiments are reproducible.
- Original spec pins that must change: `rapidocr` default models are now PP-OCRv6 (not v5) — pin `ocr_version` explicitly; `mcp` 2.x needs the new import; `numpy`/`scipy` cap at Python 3.11; default `python` on the laptop is 3.10 so a new interpreter is needed. Pins that need no change: langgraph, checkpoint-sqlite, langchain-ollama, rapidocr, pdfplumber, arize-phoenix<21, arize-phoenix-otel<1, openinference<0.2.

### Gaps
- Resolver test not performed; compatibility of rapidocr 3.10 with opencv-python-headless 4.14 and numpy 2.5 is by metadata only (rapidocr requires numpy<3, opencv>=4.5.1.48).

## BibTeX
@misc{pypi_json_2026, title={PyPI JSON API (package metadata for langgraph, rapidocr, onnxruntime, arize-phoenix, mcp, etc.)}, howpublished={\url{https://pypi.org/pypi/<name>/json}}, note={Accessed 25-26 October 2026}}
@misc{npm_registry_2026, title={npm registry (react, vite, typescript, react-router, @fontsource/*)}, howpublished={\url{https://registry.npmjs.org/}}, note={Accessed 25-26 October 2026}}
@misc{langgraph_interrupts_2026, title={LangGraph interrupts documentation}, author={{LangChain}}, howpublished={\url{https://docs.langchain.com/oss/python/langgraph/interrupts}}, note={Accessed 25 October 2026}}
@misc{langgraph_checkpointers_2026, title={LangGraph checkpointers and durability documentation}, author={{LangChain}}, howpublished={\url{https://docs.langchain.com/oss/python/langgraph/checkpointers.md}}, note={Accessed 25 October 2026}}
@misc{rapidocr_docs_2026, title={RapidOCR documentation and releases}, author={{RapidAI}}, howpublished={\url{https://rapidai.github.io/RapidOCRDocs/main/install_usage/rapidocr/usage/}; \url{https://github.com/RapidAI/RapidOCR/releases}}, note={Accessed 25 October 2026}}
@misc{ppocrv6_2026, title={PP-OCRv6 documentation}, author={{PaddlePaddle}}, howpublished={\url{https://www.paddleocr.ai/main/en/version3.x/algorithm/PP-OCRv6/PP-OCRv6.html}}, note={Accessed 25 October 2026}}
@misc{ollama_library_2026, title={Ollama model library (qwen3.5, gemma4, qwen3, gemma3, qwen3-vl, qwen2.5vl, glm-ocr, minicpm-v, phi4-mini, granite4, ministral-3, granite3.2-vision, moondream)}, author={{Ollama}}, howpublished={\url{https://ollama.com/library}}, note={Accessed 25-26 October 2026}}
@misc{ollama_releases_2026, title={Ollama GitHub releases and issues \#14645, \#18944}, author={{Ollama}}, howpublished={\url{https://github.com/ollama/ollama/releases}}, note={Accessed 26 October 2026}}
@misc{ollama_docs_2026, title={Ollama documentation: structured outputs, thinking, FAQ}, author={{Ollama}}, howpublished={\url{https://docs.ollama.com/capabilities/structured-outputs}}, note={Accessed 26 October 2026}}
@misc{phoenix_docs_2026, title={Arize Phoenix documentation and releases}, author={{Arize AI}}, howpublished={\url{https://arize.com/docs/phoenix/}; \url{https://github.com/Arize-ai/phoenix/releases}}, note={Accessed 26 October 2026}}
@misc{fastapi_sse_2026, title={FastAPI: Server-Sent Events tutorial}, author={Ram\'irez, Sebasti\'an}, howpublished={\url{https://fastapi.tiangolo.com/tutorial/server-sent-events/}}, note={Accessed 26 October 2026}}
@misc{mcp_python_sdk_2026, title={MCP Python SDK README and v1 to v2 migration guide}, author={{Model Context Protocol}}, howpublished={\url{https://github.com/modelcontextprotocol/python-sdk}; \url{https://py.sdk.modelcontextprotocol.io/migration/}}, note={Accessed 26 October 2026}}
@misc{onnxruntime_cuda_2026, title={ONNX Runtime CUDA Execution Provider}, author={{Microsoft}}, howpublished={\url{https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html}}, note={Accessed 26 October 2026}}
