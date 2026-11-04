# Story spec — 01 The spider's web

Page: [`01-the-spiders-web.html`](01-the-spiders-web.html) · kit: [Wi-Fi CSI sensing](../README.md) · guide: story.md

## The question
"My Wi-Fi router can tell that someone walked into the room? How — and why can't it tell me *which* room?"

## The one-sentence answer (headline)
- Web view: *Wi-Fi feels a moving person the way a spider feels a fly: by the trembling of its web. One spider can tell that something moved; it usually takes several spiders comparing their threads to say where.*
- Engineer view: *A moving person makes the CSI fluctuate. One link can sense that motion happened; it usually takes several devices comparing their links to say where.*

Hedge source: A0 ("coarse … needs several devices before it can say which room"), B4 (one link cannot tell which end).

**Hero picture:** a web strung across a home: the hub spider (AP), two listener spiders (devices) and the threads between them. A fly buzzes near spider A; both of A's threads tremble, the third thread is calm. A side panel reads the three threads and concludes "the fly is near A".

## Metaphor and cast

The brief's spider's web is kept: it has high mechanism fidelity. A web carries vibration along threads, a spider at a junction feels the threads it holds, a fly near a junction shakes that junction's threads most, and wind shakes a web with no fly. That covers sensitivity near the radios, the end-of-link ambiguity, joint detection by comparing links, inanimate motion and still presence.

| Metaphor | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| the web | the room's multipath: every path the signal takes | the whole web vibrates as one structure | radio paths are not threads; they fill the room and pass through walls |
| strands | propagation paths (direct line, wall bounces) | each strand is one route from sender to listener | there are infinitely many weak paths, not a few strands |
| hub spider | the access point (AP), sending beacons | every thread meets at the hub | the AP sends; it does not "feel" anything in the basic setup |
| listener spider | a sensing device (endpoint, receiver) | it feels the threads it holds | a device feels only frames sent to/heard by it |
| thread | a link: one sender–receiver pair | trembles when something moves near it | a link is a bundle of paths, not one line |
| notes of the hum | OFDM subcarriers | the hub plucks a chord; each note comes back louder or softer | subcarriers are radio tones 312.5 kHz apart, not sound |
| loudness meter | RSSI | one number for the whole chord | — |
| fly | a moving person | small, moves, shakes the threads near it | a person does not touch the paths; they reflect, block and diffract them |
| tremble | CSI fluctuation (amplitude and phase change) | bigger and closer → stronger | — |
| wind | inanimate motion: fans, vents, curtains | shakes the web with no fly | — |
| a sleeping fly | a still person | a fly that stops struggling is not felt | a real spider feels a still fly's weight; CSI barely sees a still person |
| the neighbour's web | the next room, through a wall | its trembling leaks in weakly | walls are not web joins; they attenuate |

## Scenes

| # | Claim | Beat | Figure | What moves and what it means | Interaction | Note | Numbers (key · class) |
|---|---|---|---|---|---|---|---|
| hero | One spider feels that something moved; several spiders comparing say where | — | static + ambient | threads near the fly tremble (scaleY oscillation = vibration); calm thread = no motion | label switch | A0, B4 | — |
| 1 | The listener hears every note separately (CSI); the meter hears only the total (RSSI). A few cm of movement reshapes the notes far more than the total | first, concretely | **live** + predict | 56 bars = per-subcarrier amplitude; ghost = before the move; meter = RSSI | slider: how far the fly moved (cm); predict: what changes more | A1 | `used_subcarriers_ht_20MHz`, `ofdm_subcarrier_spacing_11a_n_ac`, `wavelength_5g`, `speed_of_light`, `link_length_illustrative` (public/illustrative); room model `room_width_assumption`, `room_margin_assumption`, `wall_reflectivity_assumption`, `story_body_case_assumption` (assumption, explorer 01) |
| 2 | Therefore placement matters: a thread trembles most near its spiders, less in the middle, faintly far away, almost not through a wall | therefore | predict + **scene player** (5 steps) | the fly moves; the tremble meter changes height; the Fresnel ellipse shows the narrow ends | ←/→ | A1 | `fresnel_first_zone_mid_radius_example` (public), `single_link_range_illustrative`, `wall_attenuation_assumption` |
| 3 | But every web hums differently: a "how much it shakes" threshold from one home fails in another; "does it still look like a moment ago" (ACF) holds its scale — yet homes still differ | but | **scene player** (4 steps) | bars per home vs one threshold line; the false-alarm mark | ←/→ | B2 | `acf_vs_variance_illustrative`, `home_spread_illustrative` |
| 4 | But one thread cannot tell which end the fly is near; comparing threads can | but (twist) | predict + **scene player** (5 steps) | trembling threads together vs alone; new device-to-device threads; summed tremble per spider | ←/→ | B4 | — |
| 5 | Therefore more spiders help mostly because threads grow with the square of the spiders | therefore | **live** | threads drawn for N spiders, with and without device-to-device threads | slider N, checkbox | B4 | `devices_tpr_illustrative` |
| 6 | But a spider that runs out for nothing 1% of the time is a disaster: fix the false-alarm budget first | but (twist) | predict + gated static | a calendar full of false rushes vs four dots | predict | C1 | `seconds_per_30_days` (public), `window_short_illustrative`, `false_alarm_budget_illustrative`, `story_research_fpr_illustrative` |
| 7 | What still fools the spider | and so | 6 flip cards | — | flip | C5, B4 | `single_device_home_fraction_illustrative`, `beacon_rate_default` |
| end | Your turn: the three explorers, the quiz, the notes | sandbox | links | — | — | — | — |

## Palette meaning
sun = the AP (hub spider) · sky = sensing devices and their links (listener spiders, threads) · coral = motion (the fly, the tremble, the dynamic path) · leaf = a correct decision · plum = things that fool the spider (wind, next door, false alarms) · stone = the static room (walls, strands).
