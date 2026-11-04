# Sources — Agentic control of a consumer device

This kit teaches a general architecture: a cloud-initiated, multi-agent loop that sees a device's
screen and acts on it. It carries no measured numbers from any specific system.

## What this kit is

Study notes (rung 1 of a four-rung learning kit: notes → diagram → explorer → video) for one
question: **how do you build an agent that a server can ask, in plain language, to perform a task
on a consumer device, and that completes the task by looking at the screen and acting?** The ten
notes cover the use case (00), the message path (01), the agent graph (02), the three agent roles
(03–05), the ReAct loop (06), cost and latency (07), safety (08), and evaluation (09).

## Provenance

The architecture and its design trade-offs are generalised from **internal design documents of a
device-health programme, 2023–2025**. No internal material is reproduced: no product, team,
programme, tool, service, or person name, no internal number, and no internal figure appears in
this kit. The notes state the generic mechanism and the reasoning behind each design choice only.

How the internal material was used:

- Read for the structure of the system (message path, graph, roles, loop, guards) and for the
  stated reasons behind each choice (hand-written graph against a framework, three agents against
  one, on-device screen capture against a debug cable, per-node model tier and temperature).
- Every number it contained (latencies, token counts, limits, temperatures, screen sizes) was
  replaced by a round illustrative value of the same order of magnitude, tagged `illustrative` in
  [`constants.json`](constants.json) and in the prose. Illustrative values are chosen to be
  self-consistent (the budget table in note 07 sums to the stated task time and token count).
- Model names were replaced by roles: a stronger, slower tier for the orchestrator and a faster,
  cheaper tier for the specialists.

## Numbers

Every number in this kit is one of:

1. **Public** — a value from a cited public paper or documentation page, as published.
2. **Illustrative** — a round number invented to explain an idea, labelled "illustrative" in the
   prose. Never a measurement.

Derived values (scale factors, cache arithmetic, a Wilson interval, a compound probability) are
labelled "my arithmetic" where they appear. See [`constants.json`](constants.json): every entry has
`class` and `source`.

## Public sources cited

Agent patterns and tools:

- ReAct — Yao, Zhao, Yu, Du, Shafran, Narasimhan, Cao, "ReAct: Synergizing Reasoning and Acting in
  Language Models", arXiv:2210.03629 (2022), ICLR 2023. https://arxiv.org/abs/2210.03629 — the
  reason–act–observe pattern; the ALFWorld and WebShop results quoted in note 06 are from the
  abstract.
- Toolformer — Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools",
  arXiv:2302.04761 (2023). https://arxiv.org/abs/2302.04761
- LangGraph Graph API documentation — state graphs, nodes, conditional edges, START/END, recursion
  limit. https://docs.langchain.com/oss/python/langgraph/graph-api (read 2026-11; the default
  recursion limit has changed between versions, so this kit does not quote it).

Vendor API documentation (public; cited for the protocol, not for any internal usage):

- Anthropic, computer-use tool documentation —
  https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool (redirects to the
  vendor's current docs host). Sections used: "Available actions", "The computing environment",
  "Understand the agent loop", "Optimize model performance with prompting", "Handle errors",
  "Size screenshots to fit image limits", "Manage screenshot history", "Diagnose click issues",
  "Batch actions", "Limitations".
- Anthropic, prompt-caching documentation —
  https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching. Used for prefix order,
  breakpoint count, cache lifetimes, and price multipliers (price table read 2026-11; prices
  change, the multipliers are the durable part).
- Anthropic, tool-use overview — https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview

Device platform (Android-type OS, public developer documentation):

- MediaProjection (screen capture) — https://developer.android.com/media/grow/media-projection
- AccessibilityService (`dispatchGesture`, `performGlobalAction`) —
  https://developer.android.com/reference/android/accessibilityservice/AccessibilityService
- Intents — https://developer.android.com/guide/components/intents-filters
- WorkManager — https://developer.android.com/topic/libraries/architecture/workmanager
- Android Debug Bridge — https://developer.android.com/tools/adb
- UI Automator — https://developer.android.com/training/testing/other-components/ui-automator

Security and statistics:

- OWASP Top 10 for LLM Applications 2025 (LLM01 Prompt Injection, LLM02 Sensitive Information
  Disclosure, LLM06 Excessive Agency) — https://genai.owasp.org/llm-top-10/
- E. B. Wilson, "Probable inference, the law of succession, and statistical inference", Journal of
  the American Statistical Association 22 (1927) 209–212.
  https://doi.org/10.1080/01621459.1927.10502953

## How the sources were read

- The internal documents were read in full as text. Nothing was copied; each note was written from
  the generic mechanism.
- The vendor documentation pages were fetched in November 2026 and read for the specific sections
  named above. Vendor docs change; re-check the numbers in `constants.json` (class `public`)
  before relying on them.
- No figure from any source is reproduced. Diagrams for this kit, when made, are drawn fresh from
  the notes.

## Public-safety check

`learning/tools/public-scan.sh learning/agentic-device-control` was run on the finished kit and
reported clean.

## Rung 2 — diagrams (learn-diagram)

Six diagrams in [`diagrams/`](diagrams/INDEX.md), drawn fresh from notes 01, 02, 03, 04, 05, 06, 07,
08 and 09 (compounding reliability only) and from this kit's `glossary.md`. Every number on a canvas is loaded
from `constants.json` by key and footnoted on the canvas with its class and source; derived values
are tagged `[calc]`. No other source was opened: no internal material and no figure from any source
was used.

## Rung 3 — explorers (learn-explorer)

Two single-file HTML explorers in [`explorers/`](explorers/INDEX.md): steps, completion and cost (notes 06, 07, 09), and an
agent-graph stepper (notes 01, 02, 04, 05, 06, 08). Every parameter is copied verbatim from `constants.json` into an inline
params block and `explorers/params.json`, with its class and source. The pages contain no measured numbers. The tasks, screens
and extra tap points in the stepper are invented on the page and labelled as such. No other source was opened: no internal
material and no figure from any source.
