# B2 — State ownership: the kernel envelope, the local story, and who the guest is

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Harel 1987 (statecharts: a story nested inside a lifecycle state). · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
State is split in two: the kernel owns an **envelope** (lifecycle phase, session and generation, participant authority, leases, permits, timers, pending commands, cleanup and safety state) that no experience can write, and each experience owns an opaque, deeply immutable **local story state** that lives inside the envelope and runs only while the kernel phase is "in story".

## What it is
**The kernel envelope** carries, among other fields:

- execution mode and the kernel **lifecycle phase**;
- deployment generation and session ID;
- the provisional visitor candidate, the active participant binding, and reattachment, departure and retirement state;
- capability health;
- the session-scoped **visitor-audio permit** (listening) and the turn-scoped **speech-output lease** (speaking), tracked separately because their lifetimes differ;
- action leases and the per-invocation resource lifecycle (claims held, open intervals, pending cancellations with their deadlines);
- active timers, deadlines and pending commands;
- cleanup progress, safety, stop and recovery state;
- the selected experience ID and revision, and the opaque local state.

Experiences read the envelope through a read-only view.

**The lifecycle phase** is a closed set shared by every experience: not ready, ready, selecting, in story, cleanup, safe cleanup, stopped, recovery. A story runs entirely inside "in story". Local state names are private to each experience.

## How it works
**Two validators run after every reduction, in a fixed order.**

1. The kernel validates its own invariants on the tentative envelope: types, uniqueness, and the coherence of session, participant, lease, permit and cleanup fields. This step cannot be waived. A failure ends preparation and nothing is committed.
2. The experience's story validator then checks the local state together with the read-only envelope view. It needs the view because a story rule may relate a local chapter to a kernel timer or a pending command. It cannot change or waive any envelope value.

**One invariant shows why participant authority must be in the kernel.** The envelope must never hold a provisional candidate and an active participant at the same time. In the first coordinator this was checked only in certain story states. Once story states are private to each experience, the kernel cannot know which states those are, so the rule must hold independently of any state name.

**The current session participant track** is derived by the kernel: the active binding's track if there is one, otherwise the provisional candidate's track. It has no value before selection or after retirement. Every participant-bound input is compared against it at admission. An event that arrives while no value exists is rejected; it is never deferred and replayed for a later visitor.

The kernel also fixes a limit of the first coordinator. That coordinator compared a reacquired track only against a fixed recorded track and never updated it. In the kernel design, when the kernel's own "reattached" decision authorises a replacement track, the kernel updates the binding atomically before participant-bound input admission resumes.

**Participant authority is kernel-owned; participant policy is experience-owned.** The kernel selects the candidate, associates a handshake with a track, authorises lock, retarget, reattach and departure, and retires the participant. For each such event it derives a typed decision (provisional, locked, retargeted, reattached, departed) and passes it to the reducer. The experience chooses only its story response, plus the typed options the kernel exposes, for example "lock the participant when the handshake times out: yes or no". Adding a new lock mechanism, threshold or grace rule is a kernel change and a safety review.

**The local state has a strict contract.** "Frozen" is not enough for replay and evidence. Every local state type must have:

- a class-level schema version, incremented whenever a field changes;
- a required `state_name` drawn from the experience's declared names;
- deep immutability: scalars, enums, tuples and nested frozen records only; no lists, maps, sets, arbitrary objects or callables (registration walks the type annotations and rejects violations);
- one kernel-owned canonical encoding: declared field order, enums as qualified name plus value, fixed float form, no NaN or infinity;
- value equality defined as equality of canonical encodings.

Substrate code (the simulation, the browser, the gateway) may branch only on the kernel phase and on typed values the story projector publishes, such as "handshake window open". It must never branch on a local state name. A source fence test rejects runtime code that imports an experience's state type.

**Cleanup failure is a kernel transition.** If the cleanup deadline, an illustrative 10 000 ms (`cleanup_ack_timeout_ms_illustrative`), expires while any command, stream, lease or permit lacks positive proof that it is quiet, the kernel moves to *recovery*, keeps the unresolved claims in evidence, and keeps visitor admission off. Only explicit operator recovery or a clean restart that proves the old authority cannot act may leave recovery. The first coordinator treated this timeout as a clean stop; the kernel design deliberately does not, as a safety correction.

**Two levels of profile.** A deployment selects a content-addressed **experience profile** that pins the whole authority bundle: target, coordinator and reasoner images, configuration digest, message and transport ABI digests, the accepted input and primitive IDs, the catalog policy, readiness, cleanup, evidence and acceptance requirements, and the selected definition with its revision. The definition, inside the image, selects only story logic and its in-process policy. It cannot select images, ABIs, credentials, host lifecycle or adapters. One profile binds exactly one definition, and evidence records both identities.

## Design choices and trade-offs
- **Opaque local state** gives each experience freedom to model its story and keeps the kernel independent of every story. The cost is the type walk and canonical encoder that every state type must satisfy.
- **Two profile levels** keep deployment concerns (what image, which robot, which credentials) out of story code, so a story can never select its own privileges.

## Common confusions
- **"The experience owns the visitor."** The experience owns its *response* to participant decisions. Who the visitor is, and when that changes, is decided by the kernel.
- **"Lifecycle phase and story state are the same thing at two resolutions."** The phase set is closed and shared; story states are private and differ per experience.
- **"Recovery is an error state an experience handles."** Recovery is kernel-owned. No experience can enter or leave it.

## Why it matters for robot experiences
Visitor identity, microphone permission and cleanup are where a public robot can hurt trust. Putting them in a structure that story code cannot write makes those guarantees hold for every future experience, not only the reviewed ones.

## Terms introduced
- **kernel envelope** — the kernel-owned state record around the opaque local state; experiences read it through a read-only view.
- **lifecycle phase** — the closed, shared phase set: not ready, ready, selecting, in story, cleanup, safe cleanup, stopped, recovery.
- **local story state** — an experience's private, deeply immutable, canonically encoded state, valid only inside "in story".
- **current session participant track** — the kernel-derived track against which participant-bound inputs are admitted.
- **participant decision** — the kernel's typed verdict for a candidate, handshake, departure or reattachment event.
- **participant policy** — the typed story options an experience may choose about participant decisions.
- **visitor-audio permit / speech-output lease** — the session-scoped authority to listen / the turn-scoped authority to speak.
- **experience profile** — the deployment-level, content-addressed record that pins images, digests, ABIs, catalogs, requirements and one definition.
- **recovery** — the kernel phase entered when quiescence cannot be proved; admission stays off until operator recovery or a proven clean restart.
