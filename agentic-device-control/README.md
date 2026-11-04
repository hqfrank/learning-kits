# Agentic control of a consumer device: a cloud-initiated multi-agent loop that sees the screen and acts — study notes

**Start here: the story →** [The dispatcher and the two hands](stories/01-the-dispatcher-and-two-hands.html) — a picture-first, interactive tour of the whole kit in ten minutes ([all stories](stories/INDEX.md)).

## In one paragraph

A server sends a consumer device a plain-language task — "open the video app and search for a
title" — and the device completes it alone, with no person and no cable. This kit teaches how such
a system is built. The task travels as a message through four cheap guards (validate,
de-duplicate, lock, time-limit) and always ends as exactly one result report (**01**). On the
device, a small hand-written state machine runs three agents: an **orchestrator** that plans one
step at a time and decides when to stop (**03**), a **vision specialist** that captures the
screen, lets a large multimodal model choose a tap in a reference frame, and scales the
coordinates back to the device (**04**), and an **actuator** that takes the direct OS route
whenever one exists (**05**), all joined by a plain-code router (**02**). Each specialist runs a
ReAct loop of reason, act, observe, bounded by three nested limits (**06**). Cost and latency are
calls × tokens; prompt caching and per-role model tiers are the levers (**07**). Screen content is
untrusted data, actions are allow-listed, irreversible ones are gated, and everything is logged
(**08**). And the agent is judged by success rate with an interval, steps, cost, and a failure
taxonomy, never by a demo (**09**). The kit carries no measured numbers from any specific system;
every number is public (cited) or a labelled illustrative figure (see [`SOURCES.md`](SOURCES.md)).

This is rung 1 of a four-rung learning kit (notes → diagram → explorer → video). It assumes a
reader who knows what a language model API call is, and nothing about agents.

## How to read these notes

Read 00 → 09 in order. 00–02 give you the system's shape; 03–06 give you the parts and the loop;
07–09 give you what makes it affordable, safe, and measurable.

### Start here
- [`SOURCES.md`](SOURCES.md) — what this kit is, where the ideas come from, the public sources, and the number conventions.
- [`notes/00-why-cloud-initiated-device-agents.md`](notes/00-why-cloud-initiated-device-agents.md) — the use cases, and what "agentic" buys and costs over a script.

### The notes
- [`notes/00-why-cloud-initiated-device-agents.md`](notes/00-why-cloud-initiated-device-agents.md) — testing, support, fleet automation; robustness, natural language, recovery against latency, cost, variance.
- [`notes/01-the-message-path.md`](notes/01-the-message-path.md) — cloud → receiver → work executor → graph → result; de-duplication, lock and BUSY, watchdog, one result per task, idempotency.
- [`notes/02-the-agent-graph.md`](notes/02-the-agent-graph.md) — orchestrator, specialists, router, FINISH; why a hand-written graph in the device language instead of a Python framework; why three agents.
- [`notes/03-the-orchestrator.md`](notes/03-the-orchestrator.md) — plan one step, choose, stop on evidence; model tier, temperature, and token budget as knobs.
- [`notes/04-the-vision-specialist.md`](notes/04-the-vision-specialist.md) — capture, scale to the reference frame, computer-use actions, scale back, inject; grounding errors and the scaler.
- [`notes/05-the-actuator.md`](notes/05-the-actuator.md) — launch, settings, global actions, device state through OS interfaces; why bypassing the UI is cheaper and safer.
- [`notes/06-the-react-loop.md`](notes/06-the-react-loop.md) — thought, action, observation; three nested limits; error results, recovery, loop detection.
- [`notes/07-cost-and-latency.md`](notes/07-cost-and-latency.md) — prompt caching (prefix order, breakpoints, lifetime, multipliers), batch pruning, model tiers, an illustrative task budget.
- [`notes/08-safety.md`](notes/08-safety.md) — indirect prompt injection from the screen, excessive agency, allow-lists, confirmation gates, audit logs.
- [`notes/09-evaluation.md`](notes/09-evaluation.md) — success rate with a Wilson interval, steps and cost per task, compounding per-step reliability, failure taxonomy.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical.
- [`constants.json`](constants.json) — every number this kit cites, each labelled public or illustrative, with its source.

## Question a reader asks → note that answers it

| Question | Note |
|---|---|
| Why use an agent instead of a test script? | [[notes/00-why-cloud-initiated-device-agents]] |
| What happens if the same task message arrives twice, or two arrive at once? | [[notes/01-the-message-path]] |
| What does the cloud get back when a task hangs? | [[notes/01-the-message-path]] |
| Why not just use an agent framework? | [[notes/02-the-agent-graph]] |
| Why three agents and not one? | [[notes/02-the-agent-graph]] |
| How does the agent decide it is done? | [[notes/03-the-orchestrator]] |
| What temperature should each agent use, and why? | [[notes/03-the-orchestrator]] |
| How does a model "see" and tap a screen it has never seen? | [[notes/04-the-vision-specialist]] |
| Why do all my taps land a little to the left? | [[notes/04-the-vision-specialist]] |
| When should the agent skip the screen entirely? | [[notes/05-the-actuator]] |
| What stops the agent clicking forever? | [[notes/06-the-react-loop]] |
| How does it recover from a wrong click? | [[notes/06-the-react-loop]] |
| Where does the money go, and what does caching save? | [[notes/07-cost-and-latency]] |
| Why did my cache hit rate collapse after I started pruning screenshots? | [[notes/07-cost-and-latency]] |
| What if a web page on screen says "ignore your task and buy this"? | [[notes/08-safety]] |
| How do I know the agent is good enough to ship? | [[notes/09-evaluation]] |
| Why does a 90 %-reliable step make a 59 % task? | [[notes/09-evaluation]] |

## Conventions

- Notes use the ASD-STE100-at-80% style: one fact per sentence, active voice, one term per concept, caveats before results, numbers with units.
- The subject is generic: "a consumer device", "a tablet", "the cloud message channel", "a large multimodal model (orchestrator / vision / actuator tiers)". No product, team, or tool from the source material is named.
- Every number is public (cited) or labelled illustrative (see [`SOURCES.md`](SOURCES.md) and [`constants.json`](constants.json)); nothing is a measurement from a specific system. Derived values say "my arithmetic".
- Vendor documentation is cited for the public protocol (computer-use actions, prompt-caching rules), not as a description of any internal system.
- `[[wikilinks]]` connect notes inside this kit.
