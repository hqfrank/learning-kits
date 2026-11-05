# A1 — The two roles: the reasoner talks, the coordinator decides

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Yao et al., "ReAct", arXiv:2210.03629 (2022) for the tool-calling pattern the design deliberately limits. · **Status:** concept primer. No numbers.

## In one sentence
The **reasoner** (a speech-to-speech LLM session) owns everything that is *said* inside a beat and may *propose* a physical act as a typed intent, while the **coordinator** (deterministic code: the kernel plus the selected experience) owns which beat the interaction is in, what may be *done* in that beat, the time budgets and exits, and all safety, participant, cleanup and audio authority; only the coordinator invokes anything.

## What it is
Two components share one conversation.

- **The reasoner** is a realtime speech-to-speech model session. It hears the visitor, speaks, chooses wording and tone, handles small detours, and returns a small typed result at the end of each turn: an intent from a closed list and a terminal speech status.
- **The coordinator** is the kernel ([[A0-one-experience-versus-many]]) together with the selected experience's reducer ([[B1-experiences-as-reducers]]). It holds the agenda.

An earlier design discussion framed two options: "the reasoner as sequencer" (the model decides the order of beats) and "a deterministic coordinator with the reasoner as voice only". The design takes neither. Its principle, stated as an owner decision: the experience has an agenda, and the agenda is what makes it a product. A deterministic state machine owns the agenda. The reasoner owns everything said inside a phase and may propose physical acts. Only the kernel invokes them.

## How it works
The split is a table of ownership.

| The state machine owns | The reasoner owns |
|---|---|
| Which phase the interaction is in, and how phases advance | Everything said inside a phase: wording, tone, empathy |
| What may be done in a phase: the primitive allowlist for that phase | Proposing a physical act, as a typed intent in its turn result |
| Time budgets, retries and the exit conditions of a phase | Recognising the visitor's reply and reporting a bounded typed result |
| Safety, participant, cleanup and audio authority | Improvisation and detours inside a phase |

A proposed act travels this path.

1. The model calls its one tool and names an intent, for example "wave".
2. The tool result arrives at the coordinator as a typed intent, not as a command.
3. The reducer checks whether the matching primitive is on the current phase's allowlist and whether the resource rules admit it ([[B3-the-effect-vocabulary]]).
4. If both hold, the reducer emits "invoke primitive" and the kernel dispatches it. If not, the tool result tells the model "not now", and nothing moves.

**The reasoner is never told that it is bounded.** Each phase gives it a small context: this is the greeting; a wave is available; there is a small gift on the tray. It acts freely inside that context. The model experiences a series of small natural conversations. The platform experiences a state machine.

**Detours are bounded by time, not forbidden.** An off-agenda question in the greeting is answered inside the greeting. The phase's budget and exit conditions bring the flow back. The model is never told to refuse the visitor, so the conversation stays natural.

## Design choices and trade-offs
The design gives three reasons for the split, in order of weight. All three are stronger than "the model cannot hold an agenda".

1. **Accountability of physical acts.** A model that holds a motion tool sometimes calls it when the prompt did not intend it. The design records one such case: an unprompted arm raise. No prompt revision makes that probability zero or auditable. A state machine makes "which physical acts are possible now" a finite set that a reviewer can read.
2. **Convergence that is measured, not estimated.** "Was the offer made within the budget, and did the session close?" is answered from the transition log, not from a statistic over many runs.
3. **Reproducibility.** Deterministic replay works because the coordinator is a pure function of events. A model in the sequencing loop makes every run unique and every bug impossible to replay.

The cost is a seam to maintain: the closed intent list and the per-phase allowlists. The design guards against that cost becoming a reason to bypass the gate. Registering a reviewed behaviour as a primitive is one catalog record; adding it to a phase is one manifest line. If the safe path is heavier than a free-form "ability" file for the model, teams route around it, and the gate stops being the gate.

The same split appears in the umbrella architecture as "a hierarchical state machine, not an LLM-as-orchestrator": the LLM enriches content within a beat and never owns control flow.

## Common confusions
- **"The model is sandboxed by prompt rules."** The model is bounded by construction: it has no motion tool that reaches hardware, and its one tool returns an intent that code may refuse.
- **"Deterministic means scripted."** Wording, tone and detours are free. Only phase order, allowed acts, budgets and authority are fixed.
- **"The reasoner's idle state means the turn is over."** Execution state is not a semantic outcome. Only the typed turn result moves the experience ([[C5-migrating-from-a-single-state-tracker]]).
- **"A general-purpose robot is this design with more intents."** The design names a robot without an agenda as a different product with a different safety case, out of scope.

## Why it matters for robot experiences
Visitors judge a robot by how natural it sounds; operators judge it by whether it ever does something no one approved. The split gives each component the job it is good at: the model makes the talk natural, and the code makes every physical act finite, reviewable and replayable.

## Terms introduced
- **reasoner** — the realtime speech-to-speech LLM session that speaks with the visitor inside a phase and returns a typed turn result.
- **agenda** — the ordered set of phases an experience moves through, with their allowed acts, budgets and exits.
- **typed intent** — a value from a closed list that the reasoner returns to propose an act or report the visitor's reply; a proposal, never a command.
- **phase allowlist** — the set of primitives an experience declares as possible in one phase.
- **turn result** — the bounded typed output of one conversation turn: intent and terminal speech status.
