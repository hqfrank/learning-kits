# Story 01 — The stage manager (spec)

**The question.** "We have one robot and want more than one interaction on it. Why not let the LLM run the show, or
just add a second story to the first state machine?"

**Headline (the answer).** *One stage manager runs every act: the voice may improvise and ask, but only the stage
manager calls the cues, owns the stations, and drops the safety curtain.*
Engineer view: *One deterministic kernel runs every experience: the LLM may improvise and propose, but only the
kernel dispatches, owns the resources, and handles safety first.*

**Hero picture (one sentence).** A small puppet theatre: a child-sized puppet robot on stage with one volunteer from
the audience; the voice actor in the wings holds out a request slip; every slip travels to the stage manager's
prompt desk (the act's cue sheet open on it), and only from there does a cue travel to the three crew stations —
the control bar, the follow-spot, the microphone; the safety curtain hangs above, wired to the desk; a rehearsal
room door at the side.

The kit's own note A0 already uses this analogy ("the kernel is the stage manager; each experience is one act in
the repertoire"). The brief's "improv troupe" is kept as *the voice*, and a **puppet** is added: the robot's body is
a thing the voice can never touch, which is the core of A1 (the model holds no motion tool).

## Metaphor + cast

| Metaphor | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| The stage manager | coordinator kernel | Calls every cue, owns the stations, the curtain, the house rules and the show report; the same for every act (A0, B4) | A stage manager uses judgement; the kernel is deterministic code with closed rules |
| The voice (an improviser in the wings) | reasoner (speech-to-speech LLM session) | Improvises every line; may ask for a move on a slip; cannot reach the strings (A1, B6) | A voice actor knows the show has limits; the reasoner is never told it is bounded |
| A request slip | typed intent in the turn result | A proposal from a closed list, which the stage manager may refuse (A1) | — |
| An act / its cue sheet ("given this, do that") | experience / pure reducer over a transition matrix | Reads the cue sheet only; never touches a station; output is a list of cues to request (B1) | A cue sheet is paper; the reducer is a pure function the kernel calls per event |
| The repertoire (one act per show) | registry; one profile per coordinator process | Acts are fixed before curtain-up (B5) | — |
| The puppet | the robot (body, head, voice out) | Acts only through the crew (B3) | The robot's motion layer has its own rules; "crew" = adapters + motion layer, not people |
| The control bar | action slot (+ body, head) | One puppeteer bar: one physical act at a time (B3) | — |
| The follow-spot | gaze lease | Its own station; but it moves the same head as the bar (head and gaze share actuators) (B3) | A real follow-spot lights, it does not steer the puppet's head |
| The microphone | audio out through a per-turn speech lease | The voice gets the mic one turn at a time (B3, B6) | — |
| The volunteer | current session participant | Only the volunteer's wave counts; an audience member's wave is ignored at the door (B2, B4) | — |
| "Clear!" from the crew | quiescence proof | The stage manager frees a station only after the crew calls clear (B3) | — |
| The safety curtain | kernel safety interception | Comes down before the act sees the alarm (B4) | In a theatre the curtain *is* the guarantee; on the robot the guarantee is a hardware stop and software is additive |
| The rehearsal room | simulation target | Same stage manager, same cue sheets; stand-ins replace the world (C1) | The real crew software stays in the loop in simulation; a theatre rehearsal room usually lacks the real crew |

## Palette meaning (whole page)
- **sky** = an act / its cue sheet (experience, story)
- **plum** = the voice (reasoner, LLM) and the microphone it holds
- **sun** = the crew stations and cues (resources, dispatched commands, held intervals)
- **leaf** = the volunteer and "clear" (participant, positive proof, accepted)
- **coral** = safety, refusal, stuck
- **stone** = the audience, stand-ins and the rehearsal room
- navy ink = the stage manager (kernel)

## Scenes

| # | Claim | Beat | Figure | What moves and what it means | Interaction | Note | Numbers |
|---|---|---|---|---|---|---|---|
| 1 | One act fits one cue sheet; a second act collides over the puppet and copies the safety rules | — | scene player, 4 steps | Act 1's cues reach the bar and mic alone; act 2 arrives and both cue the bar and mic (collision rings); both carry a curtain rule that drifts; *therefore* one stage manager owns the stations and rules, acts only ask | ←/→ | A0 | `old_effect_kinds_illustrative` (illustrative) |
| 2 | The voice asks; the stage manager calls | therefore | predict + scene player, 4 steps | A slip travels voice → desk; the desk checks the page's allowed moves and the bar; a cue travels to the bar (allowed), or "not now" travels back to the voice (refused) | predict: a wave not on this beat's page | A1, B6 | none |
| 3 | An act is a cue sheet: given this, do that; time is a cue too | therefore | **live figure** | Timeline of the wave act: greet → await wave (timer) → wave, or timer → "no wave seen" → cleanup. A wave from an audience member is torn up at the door | slider: when the wave comes; toggle: who waves | B1, B2, B4 | `gesture_wait_timeout_s_illustrative`, `story_wave_at_s` (illustrative) |
| 4 | Stations decide what may overlap | but | predict + scene player, 7 steps (the C2 showcase order) | Held-interval bars grow on three lanes (bar, spot, mic): spot on; voice talks over it; spot cleared with an ack; voice talks over the wave; wave completes; spot back; cleanup leaves nothing held | predict: can the voice talk while the puppet waves? | B3, C2 | schematic (order only, no times) |
| 5 | The safety curtain comes down first | but | scene player, 4 steps | Slips queue at the stage door sorted by priority; a safety slip jumps the queue; the desk drops the curtain and cancels every cue; the act's page never sees it; out only by staff reset + clear into cleanup | ←/→ | B4 | none |
| 6 | "Stopped" means the crew said "clear" | but | predict + **live figure** | Timeline after a cancel: settle deadline = min(settle bound, cleanup time left); proof before it releases; after it → forced cleanup, claims kept; none by the cleanup deadline → recovery | sliders: when "clear" comes; cleanup time left | B3, B2 | `cancel_settle_target_ms_illustrative`, `cancel_settle_ceiling_ms_illustrative`, `cleanup_ack_timeout_ms_illustrative`, `page_timing_01/quiesce_s` |
| 7 | Rehearse first; open night is a separate gate; acts change only between shows | therefore | predict + scene player, 5 steps | Climb the ladder: house rules (with negative tests) → act's own rehearsal → rehearsal room → named milestone → opening night; what the rehearsal room cannot prove | predict: may it open tonight? | C1, C2, B5 | `sim_cold_start_s_illustrative`, `sim_retire_timeout_s_illustrative` |
| — | Your turn | — | link cards | — | — | explorers 01–04, quiz, notes | — |

Requirements check: 7 scenes; predicts in 2, 4, 6, 7; live figures 3 and 6; scene players 1, 2, 4, 5, 7.
