# Sources — A platform for many robot experiences

This kit teaches a general architecture for running many reviewed interaction stories on one social robot: a coordinator kernel, experiences as reducers, an effect vocabulary, and simulation-first verification. It carries no measured numbers from any specific system.

## What this kit is

Study notes (rung 1 of a four-rung learning kit: notes → diagram → explorer → video) for one question: **how do you let a team add the second, third and tenth interaction story to a public humanoid robot without copying, weakening or forking the rules that protect visitors?** The thirteen notes cover why a platform is needed and the two roles inside it (A0–A1), the kernel design (B1–B6), and verification and operation (C1–C5).

## Provenance

The architecture and its design trade-offs are generalised from **internal product, design and research documents of a public humanoid-robot demonstration programme, 2026**. No internal material is reproduced: no robot, company, programme, team, product, vendor, place, show, specification or person name, no internal identifier, file path, revision or decision number, and no internal number or figure appears in this kit. The notes state the generic mechanism and the reasoning behind each design choice only.

The internal material was of these kinds, described here by kind only:

| Tag | Kind of document | Used for |
|---|---|---|
| I1 | Architecture design for supporting many interaction experiences on one coordinator (the primary source) | A0, A1, B1–B6, C1–C3 |
| I2 | Earlier design for a single authoritative interaction state tracker and the reactions of each component | B4, C5 |
| I3 | Umbrella orchestrator and software-architecture documents | A0, A1, B4, B6 |
| I4 | Alignment note between a rehearsed scripted act and the autonomous coordinator | A0 |
| I5 | Design and requirements of a browser-accessible simulation of the robot and its room | C1 |
| I6 | Plans for an off-robot and a cloud observatory harness | B6, C4 |
| I7 | Implementation contract and layout notes for the coordinator | B3, B4 |

How the internal material was used:

- Read for the structure of the system (roles, ownership tables, state split, effect vocabulary, resource claims, admission and interception, catalogs, lifecycle, verification ladder, comparators, migration steps) and for the stated reason behind each choice and each rejected alternative.
- Every number it contained (timeouts, budgets, grace periods, queue depths, counts, cold-start times, test counts) was replaced by a round illustrative value of the same order of magnitude, tagged `illustrative` in [`constants.json`](constants.json) and in the prose. Design limits are labelled "design parameter" in their `source` field. Illustrative values keep the relations the design relied on: each settle bound is at most the catalog ceiling and strictly shorter than the cleanup deadline; a launch timeout is longer than the cold start; turn budgets fit inside the session bound.
- Internal names were replaced by roles: "the robot" (a child-sized humanoid), "the reasoner (a speech-to-speech LLM session)", "the behaviour library", "the motion layer", "the physics simulator", "a public demo stand", "a small gift". Internal code identifiers were replaced by plain-English names of the same concepts.

## How the material was read

- The primary source (I1) went through two revisions. The second inverted the role of the richest existing experience: from a compatibility constraint to a non-blocking validation experiment. The kit teaches the second revision and records the first as a rejected alternative (A0, C2, C3).
- The single-tracker design (I2) and the kernel design (I1) overlap. Where they differ, the kit presents I2 as the earlier state model that I1 generalises (C5).
- The simulation design (I5) was written for the single-experience coordinator. The kit keeps its authority boundaries and session rules, which carry over unchanged, and drops its story-specific detail.
- Some source statements were explicitly marked as not yet wired or not yet measured (for example the output-broker binding and the profile-cycle time). The kit reports them as design requirements, not as working features or measurements.
- No internal figures or screenshots were copied, traced or described. Diagrams for later rungs are drawn fresh from the mechanisms in the notes.

## Numbers

Every number in this kit is one of:

1. **Public** — a value from a cited public document, as published.
2. **Illustrative** — a round number invented to explain an idea or to stand in for a design parameter, labelled "illustrative" in the prose and in [`constants.json`](constants.json). Never a measurement.

Derived values (sums, products, a clamped deadline) are labelled "my arithmetic" where they appear. Every `constants.json` entry has `class` and `source`.

## Public sources cited

State machines, reducers and architecture:

- Harel, D., "Statecharts: a visual formalism for complex systems", *Science of Computer Programming* 8(3), 231–274, 1987. — hierarchical states; a story nested inside a lifecycle state (A0, B2).
- Redux documentation, "Three principles" — https://redux.js.org/understanding/thinking-in-redux/three-principles — single source of truth, read-only state, changes by pure functions (A0, B1).
- The Elm Architecture — https://guide.elm-lang.org/architecture/ — model, update, view (B1).
- Bernhardt, G., "Functional core, imperative shell" (2012 screencast and talk) — the reducer as the functional core (B1).
- Cockburn, A., "Hexagonal architecture" (ports and adapters) — https://alistair.cockburn.us/hexagonal-architecture/ — catalogs as ports, per-target contracts as adapters (B5, C1).
- Hewitt, C., Bishop, P., Steiger, R., "A universal modular ACTOR formalism for artificial intelligence", IJCAI 1973 — single-writer, message-driven components (background for B4, C5).

Events, ordering and delivery:

- Lamport, L., "Time, clocks, and the ordering of events in a distributed system", *Communications* 21(7), 558–565, 1978 — total order from deterministic tie-breaks (B4).
- Kleppmann, M., *Designing Data-Intensive Applications*, O'Reilly, 2017, chapters 11–12 — idempotence and "effectively once" processing (B3).
- Richardson, C., "Pattern: Transactional outbox" — https://microservices.io/patterns/data/transactional-outbox.html — commit state and intent together, then send (B3).
- Fowler, M., "Event sourcing" — https://martinfowler.com/eaaDev/EventSourcing.html (C5).
- Fowler, M., "CQRS" — https://martinfowler.com/bliki/CQRS.html (C5).
- Fowler, M., "Strangler fig application" — https://martinfowler.com/bliki/StranglerFigApplication.html — a parallel line retired only when the replacement carries the load (C3, C5).

Middleware:

- ROS 2 documentation, "Quality of Service settings" — https://docs.ros.org/en/kilted/Concepts/Intermediate/About-Quality-of-Service-Settings.html (read 2026-11). Used for history and depth, reliability, durability (transient local versus volatile, and the "latched" analogy), the default profile (keep last, depth 10, reliable, volatile), and the request-versus-offered compatibility table (a best-effort publisher does not connect to a reliable subscription) (C4, C5).

Testing:

- Pact documentation — https://docs.pact.io/ — consumer-driven contract testing (C2).
- North, D., "Introducing BDD", 2006 — https://dannorth.net/introducing-bdd/ — given/when/then scenarios (C2).
- RFC 2119, "Key words for use in RFCs to Indicate Requirement Levels" — https://www.rfc-editor.org/rfc/rfc2119 — the MUST/SHALL/SHOULD convention the design documents use; the notes paraphrase these as plain statements.

LLM safety:

- Yao, S., et al., "ReAct: Synergizing reasoning and acting in language models", arXiv:2210.03629, 2022 — the tool-calling loop the design deliberately limits (A1).
- OWASP Top 10 for LLM Applications 2025, LLM06 "Excessive Agency" — https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ (B6).

## Sibling kits

- [`../robot-workload-benchmarking/`](../robot-workload-benchmarking/) — the robot stack as concurrent pipelines, ROS 2 middleware and QoS from the compute side ([A7](../robot-workload-benchmarking/notes/A7-middleware-containers-and-platform.md)).
- [`../agentic-device-control/`](../agentic-device-control/) — a contrasting design in which an LLM agent *does* choose actions, with allow-lists and confirmation gates as the guard.

## Rung 2 (diagrams)

[`diagrams/`](diagrams/) holds six diagrams drawn fresh from notes A0, A1, B1–B6 and C1–C3, with every number loaded from [`constants.json`](constants.json) by key (all used keys are class illustrative). No internal figure was used. See [`diagrams/INDEX.md`](diagrams/INDEX.md).

## Rung 3 (explorers)

[`explorers/`](explorers/) holds four single-file interactive pages built from notes B1–B6 and C1–C3 only: a reducer sandbox,
switching experiences, effect dispatch, and conformance coverage. Every number is loaded from [`constants.json`](constants.json)
(copied verbatim into `explorers/params.json`, all class illustrative) or is a separate `page_*` entry labelled "page model
choice"; no page has a measured overlay, because the kit has no measurements. No internal material was used. See
[`explorers/INDEX.md`](explorers/INDEX.md).
