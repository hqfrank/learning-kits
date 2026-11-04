# C5 — Limits and open problems

**Source:** internal I1 §3.5, §5 (corner cases, multi-target left open), I6 (adults/children/pets, through-wall risk), I7 (critical limitations, field root causes, virtual sensing, phased strategy), generalised; Ma, Zhou, Wang, Computing Surveys (CSUR) 2019 (open challenges); Zeng et al. 2019 (FarSense, breathing). · **Status:** concept note. Study numbers are illustrative.

## In one sentence
Wi-Fi motion sensing works in the lab and largely fails the product bar in homes for six reasons — one-device homes, poor chip CSI, low sampling rate, the end-of-link ambiguity, non-human motion, and environment drift — and still presence, several people, and telling people from pets remain open.

## What it is
This note lists the limits the programme met, the cause of each, and the mitigation proposed. Treat the mitigations as directions, not results.

## How it works
**The limits** (internal I7, generalised):

| Limit | Cause | Mitigation proposed |
|---|---|---|
| **Coverage** | most homes own one sensing-capable device (an illustrative 0.7 of homes, `single_device_home_fraction_illustrative`); one link senses only an elongated zone around itself | more endpoints; cheap dedicated sensing nodes; fusion with another sensor |
| **CSI quality** | single-stream links lack usable phase; chips differ in outliers and drift | chip benchmarking before design ([[A2-what-the-hardware-gives-you]]); multi-antenna chips |
| **Sampling rate** | beacons give about 10 Hz (`beacon_rate_default`); faster rates need injected traffic, which may be dropped | injected traffic where the use case needs it, for example falls |
| **Sensing symmetry** | one link cannot tell motion near its AP end from motion near its client end | device-to-device links and cross-correlation ([[B4-multi-device-joint-detection]]) |
| **Non-human motion** | fans, air vents, and other moving objects change CSI like a person (curtains and robot vacuums are my examples) | the hardest problem for security-grade false-alarm budgets; fusion; explicit "inanimate" training data |
| **Scalability of ground truth** | cameras conflict with privacy; models from some homes do not transfer to others | label-light methods such as calibration walks ([[B5-room-localisation-by-metric-learning]]); virtual sensing (below) |

**Environment drift.** The CSI baseline changes when furniture moves, doors open, the AP changes channel, or temperature and humidity change. A model trained on some days lost accuracy on the next day ([[B3-classifiers-and-windows]]). In the field study, CSI drift over time was one of the named root causes of the shortfall ([[C1-kpis]]). Self-normalised features slow the problem down; they do not stop it. Continuous adaptation of thresholds and reference embeddings is an open problem (internal I7; interpretation).

**Still presence.** A still person changes the CSI only by breathing and by absorbing energy. Public work detects breathing with multi-antenna CSI and phase-cancelling methods (Zeng et al. 2019, FarSense). Single-stream amplitude at beacon rates is a poor fit for it (my explanation). This is why stages 3 and 4 of the KPI ladder are hard ([[C1-kpis]]).

**Adults, children, and pets.** Bodies of different size produce different perturbation magnitudes. The programme named this as research, not solved in a first version (internal I6). A large dog near a device and a child far from it can look alike (my explanation).

**Several people.** The joint-detection method was designed for one target. The multi-target section of the white paper was left open (internal I1 §5). Several movers add their dynamic paths, and the cross-correlation rule can confuse "two people near two devices" with other patterns.

**Through-wall motion.** Wall attenuation helps, but thin interior walls let the neighbouring room's motion through. More endpoints and fusion with a non-penetrating sensor are the mitigations ([[B4-multi-device-joint-detection]]).

**Lab versus field.** Commercial systems that covered a lab well still produced false triggers overnight in real homes (internal I7). A lab test has no fans running for eight hours, no pets, and no neighbour behind a thin wall.

**Two strategic responses** (internal I7):

1. **Fusion on existing hardware.** Combine Wi-Fi with ultrasonic presence. Wi-Fi covers the room and sees through obstacles; ultrasound does not see through walls and is not fooled by air movement in the same way. Their difficult cases are largely independent.
2. **Virtual sensing.** Train a model to reproduce another sensor's output from CSI. Once trained, CSI alone gives that sensor's answer, even in a home with one device. Its weakness: it learns only the other sensor's field of view, and it costs an on-device network.

A longer-term option was purpose-built low-cost sensing nodes placed around the home's perimeter, with a central hub (internal I7).

## Common confusions
- **"The algorithm failed."** The first causes found were hardware CSI quality, drift, and coverage. The algorithm worked where the data was clean.
- **"More data will fix pets and fans."** Only if the data contains them, labelled. Scripted campaigns with one operator rarely do.
- **"Fusion is a fallback."** Fusion is the design: two sensors with independent failure modes beat either alone.
- **"Presence is a harder threshold on motion."** It is a different signal (breathing, absorption) that needs different hardware and processing.

## Why it matters
A team that starts Wi-Fi sensing should first test what its chips deliver, count how many endpoints its customers own, and fix the false-alarm budget. These three facts decide feasibility more than any choice in Part B.

## Terms introduced
- **coverage limit** — the area that a home's links can sense.
- **sensing symmetry** — the inability of one link to tell which end the motion is near.
- **inanimate motion** — CSI change caused by objects, not people: fans, vents, curtains, appliances.
- **environment drift** — slow change of the static channel over hours and days.
- **still presence** — a person present without gross motion; sensed through breathing and absorption.
- **virtual sensing** — training a CSI model to imitate another sensor's output.
- **multi-target detection** — detecting and locating more than one person at the same time.
