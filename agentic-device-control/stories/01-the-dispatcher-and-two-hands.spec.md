# Story 01 spec — The dispatcher and the two hands

Kit: `learning/agentic-device-control/`. Sources: the kit's `notes/00`–`09`, `glossary.md`, `constants.json`
only. Every number on the page is inlined verbatim from `constants.json` (class `public` or `illustrative`);
derived values are labelled "my arithmetic".

## The question
"How can a server type one sentence — *open the video app and search for a title* — and have a tablet do it
on its own, without it clicking forever, costing a fortune, or obeying whatever the screen says?"

## The one-sentence answer (headline)
- Crew view: **The dispatcher never touches the device. It sends one hand to the screen or one to the
  switches, reads the report, and stops only on evidence.**
- Engineer view: **The orchestrator never acts. It routes each step to the vision specialist or the
  actuator, reads the result, and finishes only on visible evidence.**

Hero picture: head office sends a work order → it passes four checkpoints at the front desk → a dispatcher
at a radio (hub) talks to a Spotter at the screen and a Keyholder at the service hatch (spokes); every radio
turn comes back to the dispatcher; one reply slip travels back to head office.

## Metaphor choice
The brief proposed "a remote assistant on the phone with two helpers". I keep its shape but make it a **radio
dispatcher with two field hands**, because (a) note 02 already uses exactly this analogy ("a dispatcher on a
radio with two field workers … each worker reports back before the dispatcher sends the next job"), so the
story and the notes share one picture; (b) a radio is turn-by-turn and hub-and-spoke by nature, which is the
mechanism (helpers never talk to each other; every specialist turn returns to the orchestrator); (c) "a
phone call with a helper" suggests a continuous conversation, which a model call is not.

## Cast

| Metaphor | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| Head office | the cloud server | sends orders, gets reply slips | — |
| Work order (with an ID) | task message (message ID, session ID, payload) | one sheet, one job | — |
| Front desk, four checks | receiver + work executor guards: validate, de-duplicate, lock, watchdog | cheap checks before costly work | the desk is plain code, not judgement |
| Dispatcher | orchestrator (stronger model tier, low temperature) | plans one step, picks a hand, decides when to stop, never touches | the dispatcher is a fresh model call each turn, fed from shared state; it remembers nothing itself |
| Switch on the radio board | router (conditional edge, plain code) | picks the line from what the dispatcher said | — |
| Spotter | vision specialist | looks at a shrunk photo, points, taps | sees one photo per look, after a wait — never a live view |
| Keyholder | actuator | turns a named key in the service hatch: launch app, settings, home | keys cover the OS, not the inside of apps |
| Service hatch | OS interfaces (intents, global actions) | direct, no aiming | — |
| Radio call | one model call, billed in tokens | each call costs and takes seconds | the call goes to a cloud model; nobody "lives" on the device |
| Briefing binder | the prompt prefix (tools, system prompt, history) | read front to back each call; unchanged front pages are skimmed cheaply | a cache is exact byte-matching, not "skimming" |
| Reply slip | result message (SUCCESS / ERROR / BUSY / TIMEOUT) | exactly one per accepted order | — |
| Note taped on the panel | untrusted screen content (indirect prompt injection) | read it, never obey it | — |
| Key board, lockbox, logbook | allow-list, confirmation gate, audit log | only listed keys exist; irreversible acts need an outside OK; everything written down | — |

## Scenes

| # | Claim | Beat | Figure | What moves and what it means | Interaction | Note | Numbers (key, class) |
|---|---|---|---|---|---|---|---|
| 1 | Four cheap checks and "one reply slip per order" remove most edge faults before any model token is spent | *concrete first* | predict + scene player (5) | an order token passes gate by gate; a bad order bounces with ERROR, a duplicate falls in the bin, a second order gets BUSY, the timer bounds the job; slips run back | predict: what to do with a second order (queue / BUSY / interrupt) | 01 | `dedup_window_illustrative`, `watchdog_timeout_illustrative` (ill.) |
| 2 | The dispatcher plans one step, picks a hand, and every report comes back before the next step | *therefore* | scene player (5) | radio tokens out to a hand and back to the hub; the panel changes per step; a hop label changes at the switch; step 5 checks the photo before FINISH | step player | 02, 03, 05 | `orchestrator_temperature_illustrative`, `specialist_temperature_illustrative`, `actuator_vs_screen_illustrative` (ill.) |
| 3 | The Spotter points on a shrunk photo, so every point must be scaled back; a steady offset is a scaler bug | *but the photo is not the panel* | predict + live figure | the crosshair on the photo maps to a finger on the panel; choosing a buggy scaler moves the finger off the icon in one direction, more the further from the corner | predict (where to tap); slider icon position, select scaler | 04 | `cu_reference_frame_recommended` (pub.), `device_native_resolution_illustrative`, `model_click_illustrative` (ill.) |
| 4 | Steps compound (0.9⁵ ≈ 0.59), so the look–tap–look loop that fixes mistakes matters more than aim; three nested limits stop it | *but each step is fallible → therefore loop* | predict + gated figure + scene player (5) | a wrong tap opens a dialog; the next photo shows it; the Spotter backs out and retries; loop stations light; nested limit rings appear | predict compound probability | 06, 09 | `per_step_success_illustrative`, `steps_without_recovery_illustrative`, `settle_delay_illustrative`, `react_iteration_limit_illustrative`, `graph_step_limit_illustrative`, `watchdog_timeout_illustrative` (ill.) |
| 5 | Every radio call is billed; calls dominate time, and re-using the unchanged front of the binder (prompt caching) is the big lever | *therefore cost* | static budget bar + live figure | segment widths = seconds; binder pages recolour by read / written / full price; a cache miss costs more than no caching | select: no caching / cached / first call or early edit | 07 | task budget keys (ill.), `vision_call_tokens_illustrative` (ill.), cache multipliers, TTL, breakpoints, screenshots kept, prune interval, tier prices (pub.) |
| 6 | Screen text is data, keys are allow-listed, irreversible acts need an outside OK, all is logged | *but the screen can lie* | scene player (5) | a note on screen is stamped DATA; a "buy" request finds no key; the lockbox waits for a call; log tokens leave the device | step player | 08 | none |
| 7 | Judge by many runs with an interval, steps, cost and a failure taxonomy — never by a demo | *therefore measure* | static runs grid + Wilson bar + 6 flip cards | — | flip cards | 09 | `eval_runs_illustrative`, `eval_successes_illustrative` (ill.); Wilson interval my arithmetic |
| — | Your turn | sandbox | link cards | — | — | — | explorers 01, 02; quiz; notes |

## Palette meaning (whole page)
sky = head office and messages (orders, slips, radio) · plum = dispatcher / orchestrator · coral = Spotter /
screen route · leaf = Keyholder / OS route · sun = cost (tokens, cache) · stone = plain-code guards, limits,
logbook.
