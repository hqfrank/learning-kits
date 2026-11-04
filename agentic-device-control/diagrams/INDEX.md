# Diagrams — Agentic control of a consumer device (Rung 2, learn-diagram)

Six diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. This is the picture
layer for the rung-1 notes: it turns the message path (01), the agent graph (02), the vision
specialist (04), the ReAct loop (06), cost and caching (07), and safety (08) into diagrams. **Every
number on every canvas is loaded from this kit's `constants.json` by key** (shown in a sources
footnote on the canvas) or cited to a public paper/doc, and is tagged `[Pn]` public or `[In]`
illustrative; derived values are tagged `[calc]` with the arithmetic written out. **No measured
number from any specific system appears.** Each canvas carries its own legend and a sources
footnote so the exported image stands alone. A combined 6-page source,
`agentic-device-control.drawio`, is also written so the browser shows all pages at once.

**Public-safety.** This kit is published on a public GitHub repo. These diagrams name only public
protocols, papers and platform APIs (ReAct / Yao et al. 2022; LangGraph `StateGraph`, conditional
edges, recursion limit; the computer-use tool actions and prompt-caching rules; Android
MediaProjection, AccessibilityService `dispatchGesture` / `performGlobalAction`, intents,
WorkManager; OWASP LLM01/02/06; the Wilson interval) and generic subjects ("a consumer device", "a
tablet", "the cloud message channel", "a large multimodal model (orchestrator / vision / actuator
tiers)"). No employer, product, team, programme, tool, service or person name from the source
material is used, and no internal number. `learning/tools/public-scan.sh learning/agentic-device-control KIT-agentic.md`
was run on the finished kit and reported clean.

**How these were built (no drawio MCP).** The drawio MCP export pipeline is unreliable in this
sandbox (see the sibling `../../robot-workload-benchmarking/diagrams/INDEX.md` and agent memory), so
each page is described once as a list of cells in a `specNN.py` module and rendered two ways from
the SAME list by `.render_local.py`: (1) an editable `.drawio` (draw.io-compatible), and (2) a
standalone `.svg` (a `<rect>` per box plus a `<foreignObject>` XHTML label, polyline edges with a
per-colour arrow marker and waypoints), rasterised to `.png` via headless Chrome at 2x. Chrome
renders the foreignObject HTML, so wrapping, `<br>`, bullets and glyphs like `->`, `|`, `x`, `×`, `÷`,
`≈`, `^` render without the cairo glyph/no-wrap issues of the older pipeline. The self-rendered SVG
carries no draw.io "Text is not SVG" banner, so no strip step is needed; every SVG is validated with
ElementTree before rasterising. Shared palette and the `constants.json` loader live in `_common.py`:
a spec never types a number — it calls `V("key")` for the value and `T("key")` to register the
footnote tag, so a canvas cannot silently drift from the source. ASCII `->` is used for arrows and
`x` for multipliers; any literal `<` in a label is avoided or written `&lt;`.
To regenerate: `python3 .render_local.py spec01.py ... spec06.py` then `python3 .render_local.py --combine`.

| File | Teaches (the finding in the title) | Sources used |
|---|---|---|
| `01-message-path` | Four cheap guards (validate, de-duplicate, lock, watchdog) run before any model token is spent, and every accepted task ends as exactly one result (SUCCESS/ERROR/BUSY/TIMEOUT); de-duplication is not task idempotency. | Note 01; `constants.json` dedup_window_illustrative, watchdog_timeout_illustrative, task_wall_time_illustrative; Android WorkManager guide (public) |
| `02-agent-graph` | One planner, two doer specialists and a plain-code router in a hub-and-spoke state machine; every specialist turn returns to the orchestrator until FINISH; why a hand-written graph on a Java/Android runtime and why three agents. | Notes 02, 03, 05; `constants.json` orchestrator_temperature_illustrative, specialist_temperature_illustrative, max_output_tokens_illustrative, actuator_vs_screen_illustrative, graph_step_limit_illustrative; LangGraph Graph API docs (public) |
| `03-vision-cycle-and-scaling` | The five-step capture->scale-down->decide->scale-up->act cycle; the model taps in its reference frame and the device taps in its own pixels, drawn to scale, so a consistent offset is a scaler bug not a model error. | Note 04; `constants.json` cu_reference_frame_recommended, cu_max_resolution_advised, device_native_resolution_illustrative, model_click_illustrative, settle_delay_illustrative, cu_tokens_per_screenshot, cu_screenshots_kept; computer-use tool docs, MediaProjection, AccessibilityService (public) |
| `04-react-loop-and-limits` | The thought->action->observation loop with its two exits (no tool call; loop detection) nested inside three limits (iteration < graph step < watchdog); recovery breaks the compounding p^n, which is why the loop matters. | Notes 06, 09; `constants.json` react_iteration_limit_illustrative, graph_step_limit_illustrative, watchdog_timeout_illustrative, settle_delay_illustrative, per_step_success_illustrative, steps_without_recovery_illustrative, react_alfworld_gain_pp, react_webshop_gain_pp, react_in_context_examples; ReAct (Yao et al. 2022), computer-use tool docs (public) |
| `05-cost-and-caching` | Where one illustrative task's time goes (model calls carry all the tokens and most of the time) and what prompt caching saves on a repeat vision call, both bars drawn to scale; the caching rules, the pruning trap, and model tiers per role. | Note 07; `constants.json` the 07 budget-table latencies and token counts, cache_* multipliers/breakpoints/TTLs, price_tier_pair_input, price_output_to_input_ratio, cu_screenshots_kept, cu_prune_interval, cu_tokens_per_screenshot; prompt-caching + computer-use tool docs (public) |
| `06-safety-layers` | Screen content is untrusted data; the model proposes and device code disposes across five layers (instruction hierarchy, allow-list, scope limits, confirmation gate, audit log), each assuming the one before it failed; maps OWASP LLM01/02/06 to the layer that answers each. | Note 08; OWASP Top 10 for LLM Applications 2025 (LLM01, LLM02, LLM06), computer-use tool docs 'Limitations' and 'Batch actions' (public). No numbers: note 08 states none. |

## Files

Each diagram has three files: `NN-slug.drawio` (editable single-page source), `NN-slug.svg` (vector,
self-rendered, no draw.io banner), `NN-slug.png` (raster, 2x via headless Chrome, read back and
checked for legibility). `agentic-device-control.drawio` is the combined 6-page document
(concatenated `<diagram>` blocks) for viewing all pages at once. `specNN.py` is the cell list each
page is rendered from; `_common.py` holds the palette and the `constants.json` loader/tagger;
`.render_local.py` is the renderer (drawio + SVG + PNG from one list).

Two `constants.json` entries are intentionally not drawn: `eval_runs_illustrative` and
`eval_successes_illustrative` feed the Wilson-interval worked example in note 09, which is a
statistics derivation better left to the explorer/video rungs than to a picture.
