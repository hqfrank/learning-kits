# A1 — The experience as a state machine

**Source:** internal experience-design documents I1, I4 (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer; no measured numbers. The offering set is illustrative (`offerings_illustrative`).

## In one sentence
A public interaction is easiest to get right when it is written as a small state machine with a hub of optional offerings, a handful of rules that must always hold, and recovery paths that each end in a bounded, honest outcome.

## What it is
A **visit** is one interaction between the robot and one visitor or one group, from first notice to reset. The sources model a visit at two levels.

- **The spine** is a linear sequence of beats: ATTRACT → GREET → ENGAGE → OFFER → CELEBRATE → GOODBYE, with SAFE able to pre-empt every beat. A **beat** is one timed stage of the visit (see [[A2-beats-and-dwell-budget]]).
- **The offer hub** sits inside the visit. An **offering** is one optional thing the robot can do for the visitor. This kit uses an illustrative set of three (`offerings_illustrative`): chat, a small gift that the visitor takes from a tray, and a photo on the visitor's own phone. All offerings hang off the hub as equals; no offering connects directly to another.

A single large diagram of the whole visit was unreadable in the sources, so the team split it into one overview plus five close-ups (arrival, offer hub, following the visitor's lead, celebrating and closing, groups). Two transitions are global and drawn only once: **the visitor walks away** and **safety pause**.

## How it works

### Overview states
Waiting → someone arrives → the visit → (celebration ↔ visit) → closing → close the visit and clear the slate → waiting. Two side states exist: **needs staff** (the slate could not be cleared) and **safety pause** (stays stopped until staff clear it).

### Arrival
The robot always gives a generic hello, and **a hello is never the last word**: it is always followed by one specific thing. If the visitor says nothing, the robot names one more specific thing, then lets them go. If the visitor steps out of view and returns within a short window, it is **the same visit**: no fresh hello, no repeated offers. When the window passes, the visit closes.

### The offer hub
From the hub the robot raises one offering, or the visitor asks for one. "No thanks" sends the robot back to the hub to try a different offering. Silence sends it to a **no-answer** state, which names one specific thing; still nothing closes the visit gently. A repeated decline, or "I'm fine, thanks", moves to **just talking**: offering stops, the robot stays warm. Chat returns to the hub only if something is left to raise *and* offering is still permitted.

### Following the visitor's lead
An off-topic question gets a short human answer, or a kind one-sentence boundary for topics the robot will not discuss, then a **bridge**: one sentence linking back to the stand. A bridge is not a hand brake; the robot does not snap back after every remark. A **change of mind** mid-utterance gets one acknowledgement, the robot stops mid-sentence, and it goes straight to the new thing.

### Celebrating and closing
When something lands well, the robot checks whether something safe is available to celebrate with. If yes, a brief celebration; if not, skip it silently. Then the visitor may linger, take one more thing, or close.

### Groups
Two or more people arriving together are **one visit**. Attention follows a clearly identified talker; otherwise the robot addresses the group. A materially changed group, or the group leaving, goes through the reset before anyone new is greeted.

### The rules that must always hold
A rule that must always hold is called an **invariant**. The sources keep a short list of them.

1. **The robot offers first.** The visit never depends on the visitor knowing what to ask for.
2. **Silence never strands the visit.** On silence or unclear input the robot names one *specific* thing. It never repeats an open "what would you like?".
3. **One thing at a time.** One offering per turn, never a list, except when the visitor asks "what can you do?".
4. **A no is a no.** A decline is accepted once and that offering is not raised again in the visit. A repeated decline stops all offering.
5. **Nothing stays a secret.** Before goodbye, every available offering has been *mentioned* at least once, unless the visitor left, said they were done, asked to stop, or declined it.
6. **Offering always runs out.** Each offering is offered at most once, so the visit provably terminates. Nothing reopens the loop.
7. **Celebration is a reaction, never a request.** It is brief, always returns to the visit, uses only what is safe now, and never reopens anything that rules 4 or 6 closed.
8. **The robot never claims to remember anyone.** After the visit closes, a returning person is a stranger again, "because that is the truth".

Two facts that look alike must stay separate. A **mention** says a thing exists and expects no answer. An **offer** names the thing and waits for yes or no. Every offer is a mention; a mention is not an offer. Rule 5 is discharged by a mention; rule 6 caps offers. Rules 3 and 5 pull against each other on purpose, and the craft is spreading mentions out.

### State the hub must track
All per visit, all cleared on close: which offerings are available now; which were mentioned; which were offered; which were declined; the count of consecutive unanswered offers; whether offering is still permitted; whether a celebration is possible; and which offering completed most recently (so the next offer is never that one). A celebration must not change any of these facts.

### Transition hygiene
- **Stop before start.** In-flight speech and motion must finish or be cancelled, and the stop must be *confirmed, not assumed*, before the next offering starts. Starting a new offering while the last one still talks reads as the robot talking over itself.
- **Change of mind cancels only the in-flight utterance or gesture.** It must not clear any per-visit fact.
- **Close the visit is an interaction-level reset**: confirmed stop, discard all conversation and offer state, return to the waiting posture. If the reset cannot be confirmed, the stand shows "needs staff" and never starts a visit on top of an unfinished one.
- **Keep handlers separate.** A decline consumes an offering; a non-answer consumes a retry. A silence is not a departure, and a departure must not be answered as a silence.

## How it is designed and tested
The invariants make the state machine testable without a robot. A test drives synthetic visitor inputs (yes, no, silence, leave, return, change of mind, group change) through the machine and asserts each rule after every step. Rule 6 gives a termination proof: with a finite offering set and at most one offer each, every visit ends. Rule 8 is checked by asserting that no per-visit field survives the reset.

## Common confusions
- **"A decline ends the visit."** A decline ends that offering. The others remain, and the visitor may keep chatting.
- **"Mentioned" and "offered" are the same flag.** Merging them breaks either rule 5 (things stay secret) or rule 6 (offering never runs out).
- **"Resumption is recognition."** Resuming a visit within a short window is bookkeeping. Greeting a returning stranger as "welcome back" is a privacy claim the robot must not make.
- **"Celebrate after every success."** A celebration after every sentence is noise; after a decline it is wrong.

## Why it matters for public-robot interaction
An LLM can make a robot sound natural, but it cannot by itself guarantee termination, non-repetition or "a no is a no". The state machine supplies those guarantees; the language model supplies the words inside each state. [[B1-the-voice-pipeline]] shows how much of this machine a speech-to-speech model can hold through its prompt, and where a deterministic layer is still needed.

## Terms introduced
- **visit** — one interaction between the robot and one visitor or group, from notice to reset.
- **beat** — one timed stage of a visit (greet, converse, offer, celebrate, goodbye).
- **spine** — the linear sequence of beats, with a safety state that pre-empts all of them.
- **offering** — one optional thing the robot can do for the visitor.
- **offer hub** — the state from which offerings are raised, all as equals.
- **mention / offer** — saying a thing exists (no answer expected) / naming it and waiting for yes or no.
- **invariant** — a rule that must hold in every state of the visit.
- **bridge** — one sentence that links an off-topic exchange back to the stand.
- **reset (close the visit)** — a confirmed stop plus deletion of all per-visit state.
