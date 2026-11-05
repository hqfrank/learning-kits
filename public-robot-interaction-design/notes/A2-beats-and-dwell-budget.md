# A2 — Beats and the dwell budget

**Source:** internal experience-design documents I1, I2 (see [`../SOURCES.md`](../SOURCES.md)); Nielsen 1993; Stivers et al. 2009. · **Status:** concept primer; every duration below is illustrative ([`../constants.json`](../constants.json)), chosen only to show the arithmetic.

## In one sentence
Write the visit as timed beats, add them up to a dwell time, add the reset to get a cycle, and the cycle sets how many people per hour the stand can serve, which in turn sets how long any one beat may be.

## What it is
**Dwell time** is how long one visitor spends in the interaction. The **dwell budget** is the planned dwell time, split into beats (see [[A1-the-experience-as-a-state-machine]]). The **cycle** is dwell time plus the reset and turnover before the next visitor. **Throughput** is visitors served per hour.

The illustrative budget in this kit:

| Beat | Illustrative length | Key |
|---|---|---|
| Greet (look up, wave, one line) | 6 s | `beat_greet_illustrative` |
| Reply window (listening armed) | 12 s | `beat_reply_window_illustrative` |
| Converse (a few turns) | 35 s | `beat_converse_illustrative` |
| Offer (self-serve gift, includes take timer) | 15 s | `beat_offer_illustrative` |
| Celebrate | 8 s | `beat_celebrate_illustrative` |
| Goodbye | 4 s | `beat_goodbye_illustrative` |
| **Typical interaction** | **80 s** | `interaction_typical_illustrative` (my arithmetic, sum) |

Around the beats sit three bounds: an illustrative 150 s cap for a chatty visitor (`interaction_cap_illustrative`), an illustrative 10 s cap on one visitor turn (`per_turn_cap_illustrative`), and an illustrative 45 s global inactivity timeout that sends any beat to goodbye (`inactivity_timeout_illustrative`).

## How it works

### From beats to throughput
Add an illustrative 20 s reset and turnover (`reset_turnover_illustrative`) and the cycle is an illustrative 100 s (`cycle_illustrative`). That gives 3600 / 100 = 36 visitors per hour in theory (`throughput_theoretical_illustrative`, my arithmetic). Crowd and queue friction discount this; with an illustrative factor of 0.7 (`queue_friction_factor_illustrative`) the realistic figure is about 25 per hour (`throughput_realistic_illustrative`), or about 150 visits in an illustrative 6 h show day (`visits_per_day_illustrative`). The daily count then feeds other gates: an endurance test must cover that many cycles, and the gift tray and refill cadence must keep up.

The arithmetic runs both ways. If the venue needs more visitors per hour, the budget tells you which beat to shorten. The converse beat is the largest and the most variable, so it is where a cap does the most work. The reset is pure overhead; every second removed from it is a second returned to visitors.

### Short beats that start early
The greet line is short on purpose. The reply window opens only after the line ends, so a longer greeting delays the visitor's natural reply. The source treats the greet's speak timeout as a failsafe, not a target.

### The responsiveness budget
A visitor's consent action (answering the robot, or saying the wake phrase) must produce a *visible* listening signal fast. The design budget is an illustrative 500 ms (`listening_indicator_budget_illustrative`), split into an illustrative 300 ms for detection (`listening_indicator_detect_illustrative`) and 200 ms for permit, audio gate and indicator (`listening_indicator_signal_illustrative`). The budget sits under the public 1 s limit for uninterrupted flow (`response_limit_flow`, Nielsen 1993). Human conversation is faster still: the typical gap between turns is about 200 ms (`turn_gap_typical`, Stivers et al. 2009). A robot does not need to match humans, but every stage of the budget must be named and measured.

### What a rehearsed scripted act taught about pacing
The team ran a fully rehearsed, timed act with a rehearsed visitor before any autonomy. Every line was pre-recorded and keyed by a stable id, so one line could be re-recorded or dropped without touching the others. The act became the **timing baseline**: each scene got a stopwatch column and a target column, and every later autonomy target is anchored to it. Pacing rules it produced:

- **One line per beat, then let the action carry it.** Do not fill silence; do not stack a second sentence when a gesture already lands the moment.
- **Never move an arm in silence on a long motion.** A long reach gets running commentary at a steady cadence; a short motion gets none.
- **Never two robot audio clips at once.** A gesture's sound effect plays first, speech starts while the gesture continues, and the next line waits for both.
- **Short pauses by default, with designed long silences.** An extra filler line in the photo beat made it sound like "machine-gun talking"; the fix was fewer lines and tuned pauses, including a settling pause and a gap between shutter and reaction.
- **Show the thing the visitor cannot find.** First-time visitors could not find the photo camera, so the robot points to it and looks at it, twice. People follow the robot's gaze and arm.
- **Give a feedback channel to self-correct.** A live mirror screen let visitors fix their own position; the robot waits instead of nagging.
- **Once the music starts, stop talking.**

The longest scripted beat, a staged miss-and-recover reach, ran an illustrative 80 s (`reach_beat_scripted_illustrative`); the target for the autonomous version is half of that (`reach_beat_target_illustrative`). See [[C3-lessons-from-a-live-show]].

### Order of offerings
The default order is a product judgement, not a measurement: chat first (an object pushed at someone in the first seconds reads as a vending machine), the gift in the middle (generosity lands better after rapport), the photo last (it ends with everyone smiling and avoids the "…so, anything else?" tail). A visitor's request always outranks the planned order.

**Lingering is a success, not a loose end.** Do not hurry the visitor out, and never re-offer the thing that just finished.

### Anti-repeat pools
Every beat draws its line and gesture from a pool with anti-repeat selection (several greetings, several celebrations). Queue watchers and repeat visitors see the show many times; a visible loop breaks the character.

## How it is designed and tested
- Time each beat with a stopwatch in a rehearsal, then with logs in autonomy, against the same table.
- Report the dwell distribution (median and a high percentile), not only the mean; the cap exists for the tail.
- Check that the daily visit count fits the endurance gate and the supply of gifts.
- Measure the responsiveness budget per stage on the real robot and network.

## Common confusions
- **"Shorter is always better."** A rushed visit loses the delight that justifies the stand. The budget is a trade between throughput and the quality of each visit.
- **"Throughput is 3600 divided by dwell."** It is 3600 divided by the *cycle*; the reset counts.
- **"A timeout is a target."** A timeout is a failsafe set above the intended length.

## Why it matters for public-robot interaction
At a busy stand the queue is part of the audience. A budget written as beats lets the team reason about the crowd, the supply chain and the character in one table, and lets them change one beat without breaking the others.

## Terms introduced
- **dwell time** — how long one visitor spends in the interaction.
- **dwell budget** — the planned dwell time, split into beats.
- **cycle** — dwell time plus reset and turnover.
- **throughput** — visitors served per hour; 3600 s divided by the cycle, discounted for queue friction.
- **responsiveness budget** — the planned delay from a visitor's action to a visible reaction, split by stage.
- **timing baseline** — the stopwatch times of a rehearsed act, used as the reference for autonomy targets.
- **anti-repeat pool** — a set of variants for a beat from which the robot picks without repeating recent choices.
