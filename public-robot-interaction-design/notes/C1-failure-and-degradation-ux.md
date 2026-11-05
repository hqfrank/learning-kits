# C1 — Failure and degradation UX

**Source:** internal experience-design documents I1 and the scripted-act debrief I2 (see [`../SOURCES.md`](../SOURCES.md)); Kelley 1984 (Wizard-of-Oz); ISO 13482:2014 for safety framing. · **Status:** concept primer; numbers are labelled illustrative.

## In one sentence
Plan failure as a ladder of tiers, each of which still delivers a coherent visit and the gift, bound every retry and wait, never claim what did not happen, and keep a hidden operator and a physical curtain as the last two rungs.

## What it is
**Degradation** is running with less capability than the design intends. **Graceful degradation** keeps the visitor's experience coherent while capability drops. The guiding requirement is from [[A0-why-strangers-are-the-hard-case]]: the visitor must never tell which tier is running. Safety is a separate axis: personal-care and service robots in public are framed by ISO 13482 (safety requirements for personal care robots), and a safety stop always outranks the experience.

## How it works

### The conversation ladder
| Rung | What runs | What the visitor experiences | Entered when |
|---|---|---|---|
| 1 Full voice | proactive show, consent by answering, open microphone, full duplex | greeted, chats, gets the gift | default |
| 2 Constrained voice | short listening window, terser canned-leaning replies | a slightly quieter robot | automatically, on a rolling recognition-confidence or noise signal |
| 3 No voice | the robot speaks and gestures; the gift needs no microphone | greeted, invited, "reach out and grab one" | room too loud, wake word failing, visitor cannot or will not speak |
| 4 Operator-driven | a hidden operator triggers each step; scripted lines | looks the same | any time, and as the first milestone |

Rung 4 is the **Wizard-of-Oz floor** (Kelley 1984): "the floor, not a prototype". Any beat that is not ready runs exactly as rehearsed.

### The duplex ladder
Full duplex with barge-in is the target, *conditional* on acoustic feedback cancellation passing a readiness check on the actual robot ([[B4-turn-taking-and-self-hearing]]). If it fails: half duplex (the microphone closes while the robot speaks, or the robot transcribes itself). Below that: push-to-talk or a button. Until the check passes on the robot, the full-duplex posture is treated as unproven and the fallback is documented.

### The show ladder
| Level | Trigger | Who acts | What the visitor sees |
|---|---|---|---|
| L0 self-recovery | a grasp miss | the robot | a second attempt with a light line ("stubborn one…") |
| L1 beat swap | the second attempt fails | a supervisor | "that one's not cooperating — how about a gift bag instead?" |
| L2 graceful close | a beat or session time box is exceeded | a supervisor | "I'm a learning robot — let's stop here; come back later." Wave, reset. |
| L3 curtain | fall, emergency stop, stack down, repeated L2 | the stand | lights to "back soon", a physical curtain drops, an operator is paged |

The emergency stop stays in firmware; the curtain is what happens *after* the stop, so a real fault ends behind a curtain, never in front of the audience. The curtain must be operator-triggerable as well as automatic. The in-character excuse ("I'm a learning robot") was planted earlier in the visit as the reason the robot has new tricks, so it reads as character, not apology.

### Supervisor and director
A proposed two-layer show director separates deciding from advising:
- a **deterministic supervisor** (state machine, per-beat timers, hard rules) **decides**; only it can end a session or drop the curtain;
- a **director model** (a vision-language model over the scene and telemetry) **advises** which line or beat comes next; the supervisor accepts within policy; it never touches the arm.

The source's reasoning: a language model is right for reading a messy scene and picking a graceful line, and wrong for holding a stopwatch or deciding the robot is unsafe. "The director replaces the operator's judgement, never the operator's button."

### What the visitor sees, case by case
- **Walks past:** not greeted if uninterested; no chase.
- **Says nothing:** one specific thing, one more try, then stop. When they leave, do not follow, do not call after them, and **never invent an answer they never gave.**
- **Unintelligible:** never repeat an open question; name one concrete thing.
- **Steps away and returns quickly:** the same visit, no re-greeting.
- **Walks up after a visit closed:** a generic hello, even if it is the same person.
- **Declines:** accepted once; the other offerings remain. Nothing to celebrate in a no.
- **Says "done":** close warmly; do not squeeze in a last mention.
- **Asks for something not yet raised:** do it now.
- **Changes mind:** one acknowledgement, stop mid-sentence, go to the new thing. No "are you sure?".
- **Off-topic or a refused topic:** a short kind answer or boundary, then a bridge.
- **Offering unavailable:** never raised; if asked, say so plainly and steer to what is available.
- **Photo fails:** say so lightly, do not leave them mid-pose, and **never celebrate a failed photo**: a triumphant reaction to a non-existent picture shows the robot does not know what happened.
- **Safety pause:** everything stops; no visitor input resumes motion; staff clear it.
- **The visit cannot be reset:** do not greet the next person; show "needs staff".
- **Takes the gift and leaves wordlessly:** a success; a quick celebration toward them as they go.

### Bound everything
Retries, waits, celebrations, sessions and re-acquisition windows all have bounds. First pick miss → one bounded retry → a light line and operator assist. No take → "no rush" → one bounded wait (an illustrative 12 s, `take_timer_illustrative`) → retract. Empty supply → suppress the offer and cue a refill. Unbounded retries are out of scope. Bounds are what make termination provable ([[A1-the-experience-as-a-state-machine]]).

### Honesty constraints
The sources contain a real tension: one design moved to "celebrate" after the take timer as "assumed taken" while another says never claim a visitor took something they did not. The resolution in practice is a celebrate line written to work whether or not the gift was taken, plus tray perception that replaces the assumption with evidence. The general rule: degrade the *richness* of the experience, never its truthfulness.

### A release ladder for the gift
Carry alternatives so the show never depends on one unresolved path:
1. **Social only, self-serve tray.** Lowest risk; tests whether the character is lovable; loses "the robot gave this to me".
2. **Social plus a dispenser** the robot presses. Keeps the robot's agency without contact; adds jams, refills and cleaning, and the mechanism may steal the scene.
3. **Social plus full manipulation.** Highest delight, highest risk (balance, reach, release next to a person). Must pass with realistic supply geometry, not a hand-placed item.

A go/no-go review picks the mode on evidence. "Schedule pressure alone does not lower a gate." The visitor sees one coherent mode; the stand never explains the ladder during a visit.

### Operator fallbacks
A trained operator can trigger engage or consent from a console, flag an empty tray, refill, assist reach, manage the queue, reset after a safety stop, cue a photo and answer privacy questions from a script. This stays available throughout public operation.

## How it is designed and tested
- For each rung, run a full visit and check the gift path and the goodbye complete.
- For each failure case above, script a test visitor and assert what the robot says and does not say.
- Measure, per hour of operation: stall detection time, intervention latency, reset time, false interventions and curtain-down time.

## Common confusions
- **"Graceful degradation means apologising well."** It means the visitor rarely needs an apology.
- **"The operator is a crutch to remove."** The operator is the floor that makes autonomy safe to attempt.
- **"Retrying until it works is persistence."** Unbounded retries are a visible failure and a safety risk.

## Why it matters for public-robot interaction
Failures will happen in public. A stand that plans its failures as tiers, bounds every loop and keeps a hidden floor can attempt more autonomy, because the worst case is a quieter visit, not an incident.

## Terms introduced
- **degradation / graceful degradation** — running with less capability / doing so while the experience stays coherent.
- **degradation ladder** — an ordered set of tiers, each a complete fallback for the one above.
- **time box** — the maximum time a beat or session may take before a graceful close.
- **curtain** — a physical screen that hides the robot after a stop or fault.
- **supervisor / director** — the deterministic component that decides / the model that advises.
- **release ladder** — alternative modes of a feature carried so the show never depends on one path.
- **go/no-go review** — a cross-functional decision that picks a mode on recorded evidence.
