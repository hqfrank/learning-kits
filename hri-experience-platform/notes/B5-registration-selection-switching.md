# B5 — Registration, selection and switching: capability matching against an input catalog

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Cockburn, "Hexagonal architecture" (ports and adapters), https://alistair.cockburn.us/hexagonal-architecture/ . · **Status:** concept primer. Every number is labelled illustrative; derived values are labelled "my arithmetic".

## In one sentence
Experiences are registered statically in source, one is selected per coordinator process through a pinned profile, readiness fails unless every primitive and input it needs has a healthy adapter or producer *on that deployment's target*, and switching to another experience is a full stop–clean–restart cycle, never a hot swap during a visit.

## What it is
**Registration is static.** The registry is a source-code map from experience ID to definition. No module name, path or URL is accepted from configuration. A deployment selects one profile, and the profile names one definition and revision ([[B2-state-ownership]]).

Configuration loading rejects:

- an unknown profile ID or schema version;
- an image or configuration digest mismatch;
- an unknown experience ID, or a revision that differs from the registered one;
- a missing policy file or a policy schema mismatch;
- an undeclared effect kind;
- a primitive or input outside the profile or the definition;
- a reserved-policy violation ([[B1-experiences-as-reducers]]);
- a capability the readiness model cannot represent.

**The input catalog** is the mirror of the primitive catalog for things that flow *in*. Each input entry declares:

- its **ingress kind**: a normalised event; an authorised stream (browser microphone audio, which stays permit-gated bytes and is never wrapped as events); a simulated-world condition; or a kernel test control (simulation only);
- the event type and a registered immutable payload type, for normalised events;
- the required capabilities and an availability mode;
- a correlation policy (pre-session, session, command, or global kernel);
- the payload field, if any, that must match the current participant track;
- a privacy class (non-visitor, derived visitor data that is ephemeral, raw visitor data that is ephemeral) and a replay policy;
- the targets it supports, each with a producer contract;
- a comparison schema for cross-target evidence ([[C3-regeneration-and-comparison]]).

## How it works
**Capability matching.** Required capabilities and behaviour IDs are *derived* from the definition's primitive and input IDs through the two catalogs. Readiness combines that derived set with adapter health, the behaviour library's advertised inventory, and simulation compatibility. A missing required input or primitive prevents admission. An optional input may select only a degraded branch the definition declares, with evidence.

**Targets are explicit.** The target catalog starts with a simulation target and a physical target. Every primitive and every input names its targets, and every named target has an adapter or producer contract and target-specific acceptance scenarios. A simulation-only input therefore makes an experience simulation-only *explicitly*: readiness fails on the physical robot rather than failing at run time.

**Producer admission is target-scoped.** Runtime source IDs live inside the producer contract for one target. The admission binding for a profile is built from that target's contracts only. A simulation source in a physical profile is therefore unknown and is rejected before queue insertion; listing it in the physical source ranking is a configuration-load failure. Two targets may share one producer (for example a target-independent operator control) only through one registered shared-producer definition, never by two contracts that happen to use the same string.

**Adding an input.** The worked example is a visitor-gesture input whose first payload carries `gesture = wave`. No gesture concept existed before. It is a new registered payload under the existing "observation" event type, with session correlation, a mandatory track field matched by the kernel, its own replay-schema decision, a simulation producer (the scenario driver only), and an explicit *deferred* record for the physical target. Building a real gesture detector is separate perception work that the platform neither starts nor assumes.

**Lifecycle and switching.** Selection is fixed for one coordinator process. To change it:

1. stop admission;
2. retire any active session through normal cleanup;
3. prove every store clean;
4. stop;
5. start with the new pinned profile;
6. rerun readiness and qualification.

A simulation instance must not admit more than one profile with motion or story authority at a time, so validating several profiles is serial by design. A serial **profile-matrix runner** does exactly the cycle above per profile and fails closed on the first incomplete cleanup. Its cost is easy to estimate. With an illustrative cold start of 600 s (`sim_cold_start_s_illustrative`), an illustrative run of 300 s (`matrix_run_s_illustrative`) and an illustrative retirement of up to 300 s (`sim_retire_timeout_s_illustrative`), one profile cycle is up to 1 200 s, and an illustrative 5 profiles (`matrix_profiles_illustrative`) take up to about 100 min (my arithmetic). The design notes that end-to-end cycle time was not yet measured and asks the runner to record a phase breakdown; this is the right default, because the cold start dominates and is the term worth attacking.

## Design choices and trade-offs
- **No hot switching.** Switching mid-visit would need the kernel to prove that one story's leases, timers and gestures are gone while another story starts. A full cycle reuses the cleanup proof that already exists. The cost is minutes of downtime per switch, which a demo stand can schedule.
- **Catalogs as ports and adapters.** Primitives and inputs are the kernel's ports; per-target adapter and producer contracts are the adapters. This is why a new target (a second robot body, a new simulator) is adapter work, not story work.

## Common confusions
- **"If the simulation has a producer, the robot does too."** Producer contracts are per target. A simulation driver says nothing about the physical robot.
- **"Optional inputs are ignored when missing."** They may select only a declared degraded branch, and that choice is recorded.
- **"Registration happens when the profile is loaded."** Registration is in source and reviewed; loading only selects and verifies.

## Why it matters for robot experiences
"Can this robot run this experience here, today?" becomes a mechanical question answered at start-up, before a visitor arrives, instead of a surprise in the middle of a conversation.

## Terms introduced
- **registry** — the source-code map from experience ID to definition; the only way an experience becomes selectable.
- **input catalog** — the reviewed registry of inputs, each with ingress kind, payload, correlation, privacy and replay policy, targets and producers.
- **ingress kind** — the boundary type of an input: normalised event, authorised stream, simulated-world condition, or kernel test control.
- **target** — a registered execution environment, initially simulation and physical.
- **adapter contract / producer contract** — the per-target implementation and acceptance obligations of a primitive / of an input.
- **deferred record** — an explicit catalog entry saying a target is not yet supported, with owner and reason.
- **capability matching** — deriving required capabilities from declared primitives and inputs and checking them against target health and inventory.
- **profile-matrix runner** — the serial tool that cycles stop, clean, launch, qualify, run and retire for each profile and records phase timings.
