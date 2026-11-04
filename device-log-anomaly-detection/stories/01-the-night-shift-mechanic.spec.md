# Story 1 spec — The night-shift mechanic

**Question (the learner's words):** My fleet has millions of devices and the logs are huge, noisy and
often gone. How does anyone find a fault in that, and when should I believe the answer?

**Headline:** The dashboard lights pick which cars to look at; the logbook tells what happened; an odd
page is a lead, not a verdict.
(Engineer view: fleet metrics pick the devices; parsed logs tell what happened; an anomalous window is
a lead, not a verdict.) Hedges follow A0 and C4: the pipeline narrows the search, an engineer still decides.

**Hero picture:** at night, a road of cars; a few cars blink an amber dashboard light and send a ping to
the depot (most send nothing). In the depot, a board shows the share of lit cars per day, rising. At the
bench, the mechanic reads one car's logbook: pages are stamped lines, one page is marked odd, and a
single work order leaves the bench. A ticket row under the picture names the four stages
(detect → parse → find odd pages → one work order) with their notes.

## Why this metaphor (kept from the brief, made tighter)

The brief's "night-shift mechanic" fits because the mechanism is literally remote: the mechanic never
sees the car, only what it sent. Three choices raise fidelity:

- the logbook is a **ring-bound notebook with a fixed number of pages that tears out its oldest page** —
  the ring buffer, and the reason evidence is lost;
- every line is printed by a **rubber stamp with blanks** — the print statement → template + parameters;
- the household's network is **the road the car drives on** — so "the road, not the car" is the
  environmental anomaly, and it has a natural place in the picture.

I considered a post office (messages, sorting) and a hospital (vital signs + chart). The post office
models parsing but not the fleet trend; the hospital models both but invites "diagnosis" language the
notes avoid. The car fleet keeps both signals (lights and notebook) in one object.

## Cast

| Metaphor | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| the fleet of cars | the device fleet | many units of a few models, in use, far away | devices are in homes, not on a public road |
| dashboard light, phoned home | fleet metric (event-triggered) | sent only when an event happens; most cars send nothing | nobody sees the lamp; the record goes straight to the cloud |
| the logbook | the device log in a ring buffer | fixed pages, oldest torn out | a log is written by software at hundreds of thousands of lines a day |
| pens of different colours | threads / components | many writers on the same page | — |
| rubber stamp with blanks | template (print statement) + parameters | constant words, blanks filled per line | — |
| a page and its tally | window and log count vector | count each stamp on the page, ignore order | windows can overlap (sliding) |
| twenty random questions | isolation forest | the odd page is singled out after few questions | the questions are random and blind; the forest averages 100 games |
| the usual route | workflow / golden sequence (transition edges) | the normal order of stops, per pen | it is the observed graph, not the code's |
| the road | the household's access point / internet provider | a bad road makes a good car log oddly | each household has its own "road" |
| the night mechanic | the engineer | reads the lead, decides | — |
| work order | ticket | one per fault, with evidence | — |

## Scenes

| # | Claim | Beat | Figure / motion (what moving means) | Interaction | Note | Numbers (constants key, class) |
|---|---|---|---|---|---|---|
| 1 | The evidence is usually gone when you ask for it | setup | scene player, 4 steps: pages fill (writing = logging), the oldest page tears off (overwrite), the fault page leaves before the mechanic asks | step | A1 | `lines_per_device_day` ill., `ring_buffer_size` ill. |
| 2 | Three cars in 100 is not a fleet change | therefore (lights pick the cars) but (small fleets are noisy) | predict, then live figure: a car park of n cars with 3 % lit; a 95 % band that shrinks as n grows | slider n | A2 | `small_family_devices`, `large_family_devices`, `rare_reason_devices`, `rare_share_*_se` ill.; `z_95_two_sided` public |
| 3 | Weigh each day by its cars, then test the slope against a threshold, then turn p into a score | therefore | scene player, 6 steps: dots sized by cars; equal-weight line; weighted line; slope vs threshold; p → score ladder; 10 000 tests → ~100 false alarms | step | B4 | `trend_series_length` ill., `score_examples` public, `monitored_series`, `multiple_testing_false_alarms` ill.; the series itself is illustrative |
| 4 | Each line is a stamp with blanks; learn stamps from normal books and you miss the error stamps | therefore | scene player, 4 steps: raw line → stamp outline → blanks lift out as parameters → stamp drawer with error stamps missing | step | B1 | `ieee80211_reason_deauth_leaving` public; `component_print_statements`, `component_error_warning_share`, `miner_templates_found` ill. |
| 5 | Tally each page; the odd page is isolated after few random questions | therefore | scene player, 5 steps: overlapping pages, tally bars, page dots, random cuts (each cut = one question), a normal dot still crowded | step + predict + live slider (questions → score) | B2, B3 | `window_example` ill.; `iforest_trees_default`, `iforest_subsample_size_default`, `iforest_c_256`, `iforest_score_3_splits_psi256`, `iforest_score_at_average_path` public |
| 6 | Separate the pens, then see where the car left its usual route | therefore | scene player, 4 steps: interleaved stamps; rows per pen; normal route graph (thick = common edge); odd car: the "drop → rejoin" edge thins, "drop → full restart" thickens, reason=15 tag | step | B5 | `ieee80211_reason_4way_handshake_timeout` public |
| 7 | An odd page is a lead: often the road, and 6 of 10 is a wide range | but (twist) | predict (pilot of 10 work orders), then a live figure: k of n known faults caught → Wilson 95 % interval | sliders n, k | C4, C1 | `pilot_tickets`, `pilot_environmental`, `ground_truth_usable`, `ground_truth_detected`, `detection_rate_wilson95_6of10`, `detection_rate_wilson95_60of100` ill. |

Ending: "Your turn" cards to explorers 01 (isolation forest), 02 (fleet trend WLS vs OLS), 03 (log
windowing), the notes, and `../../quiz/`.

## Palette meaning (one hue per concept, whole page)

- **sun** = fleet metric (the dashboard light, its ping, the share of lit cars)
- **sky** = the log (notebook, pages, stamps, tallies)
- **coral** = odd / anomalous (odd page, departing edge, the alarm)
- **leaf** = normal (usual route, normal pages, the weighted fit)
- **plum** = the environment (the road, the household's network)
- **stone** = people (the mechanic, the work order)

Cars themselves stay neutral (paper fill, navy outline): a car is not a concept, its signals are.

## Truth rules for this page

- Every number is inlined verbatim from `../constants.json` into `<script id="params">` and rendered as
  the footer table; captions pull numbers through `{{key}}` placeholders, so nothing is retyped.
- Picture-only values (the 56-day series, dot positions, the threshold slope, the route edge shares)
  carry a visible `illustrative` tag on the figure.
- Self-tests (`console.assert`) reproduce: SE 1.7 pp at 100 cars and 0.17 pp at 10 000; score 0.82 at
  3 questions and 0.50 at 10.24; Wilson 31–83 % for 6/10 and 50–69 % for 60/100; 93 windows per day;
  score 20 at p = 0.01.
