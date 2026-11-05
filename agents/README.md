# The learning-kit agents

Every kit on this site was produced by six [Kiro CLI](https://kiro.dev) agents, one per rung of the method, plus a
shared set of style guides they read. This folder is a portable copy: the agent definitions with machine-specific
paths removed, the style guides, and empty memory files. Nothing here is required to *read* the kits; it is for
anyone who wants to make a kit of their own.

| Agent | Rung | Produces | Style guide |
|---|---|---|---|
| `learn-notes` | 1 | `notes/` (one note per unit, controlled language), `glossary.md`, `constants.json`, `SOURCES.md`, `README.md` | `context/ste100.md` |
| `learn-story` | 1.5 | `stories/01-<slug>.html` — a picture-first interactive story on the shared runtime in [`../stories/`](../stories/) | `context/story.md` |
| `learn-diagram` | 2 | `diagrams/` — draw.io + SVG/PNG, every number on the canvas source-tagged | `context/diagram.md` |
| `learn-explorer` | 3 | `explorers/` — single-file HTML with sliders over a pure model and self-tests | `context/explorer.md` |
| `learn-video` | 4 | `videos/` — a 3–6 minute narrated explainer (Manim + local TTS + ffmpeg) | `context/video.md` |
| `learn-quiz` | 5 | `../quiz/banks/<slug>__<section>.js` — one spaced-repetition bank per note | `context/quiz.md` |

`context/principles.md` holds the rules all six share: every number carries its source or the tag *illustrative*;
constants are loaded from `constants.json`, never retyped; a short spec is agreed before building; agents write only
under `learning/<slug>/` and never commit. Section 8 is the clarification rule: when a reader's question clarifies a
point, the note, the glossary and the quiz are updated together.

## Install

```bash
# from the root of a clone of this repository
mkdir -p ~/.kiro/agents/learn
cp agents/learn-*.json ~/.kiro/agents/
cp -r agents/context ~/.kiro/agents/learn/
```

The definitions reference their style guides at `.kiro/agents/learn/context/…`; Kiro resolves that under the home
directory. Each agent's memory file (`context/memory-<rung>.md`) starts empty and fills with what worked.

Tooling the agents expect:
- `node` (quiz validator `quiz/check-banks.js`), `pdftotext` (notes from PDFs), `git`.
- A Python venv at `~/.local/share/learn-kit/venv` with `playwright` (and its Chromium) for the story screenshot
  check `stories/tools/shoot.py`; `manim` and a TTS helper only if you use `learn-video`.
- `learn-diagram` was written against a draw.io MCP server; without one it falls back to writing `.drawio` XML and
  rendering SVG itself.

## Run

Agents run one at a time per kit, in rung order, each as its own session:

```bash
kiro-cli chat --agent learn-notes --agent-engine v1 --no-interactive --trust-all-tools \
  "Build rung 1 of a learning kit for <topic> from <sources>; slug learning/<slug>/. Proceed without waiting for approval."
```

Then `learn-diagram`, `learn-explorer`, `learn-story`, `learn-quiz` with the same shape of prompt. The agents
read the previous rungs' output from the kit folder; the prompt only needs the slug and any constraints (for
example "the repo is public: keep content generic"). The `--agent-engine v1` flag matters: the v2 engine does not
load the `resources` files.

## Adapting

- The style guides are plain markdown; edit them to change the bar. `story.md` §1 is the twelve-point bar a story
  page must meet, §9 the rubric.
- `principles.md` §8 and the public-safety scan (`tools/public-scan.sh`, denylist outside the repo) are what keep a
  public kit publishable when its sources are not.
- The reference implementation every story agent reads first is
  [`../robot-workload-benchmarking/stories/01-the-robots-kitchen.html`](../robot-workload-benchmarking/stories/01-the-robots-kitchen.html).
