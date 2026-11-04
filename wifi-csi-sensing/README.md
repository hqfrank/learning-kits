# Wi-Fi sensing with channel state information: presence detection, motion, and room-level localisation — study notes

**Start here: the story** — [The spider's web](stories/01-the-spiders-web.html): a 10-minute picture-first walk through CSI, where a link is sensitive, joint detection and the false-alarm budget ([all stories](stories/INDEX.md)).

## In one paragraph

Every Wi-Fi frame carries a known training signal, and the receiver already estimates how the room
changed it, subcarrier by subcarrier and antenna pair by antenna pair: that estimate is channel state
information (CSI). A person who moves changes the lengths of some propagation paths, so the CSI
fluctuates, and a software update can turn radios already installed in a home into a motion sensor
with no camera and no microphone. This kit teaches how that works and why it is hard. **Part A**
covers the physics and the signal: why Wi-Fi at all, what CSI is and what motion does to multipath,
and what a real chip actually delivers — the recurring lesson being that CSI quality, report rate,
and band decide more than the algorithm. **Part B** covers the processing chain: preprocessing
(normalisation, Hampel outlier removal, phase sanitisation, subcarrier selection), features whose
scale does not depend on the room (ACF, PCA, FFT without its DC term), classifiers judged on
held-out days and homes, multi-device joint detection that separates AP-side from client-side motion,
and room localisation by metric learning. **Part C** covers what it takes to make it real: KPIs that
start from a false-alarm budget per month, scenario-taxonomy data campaigns, co-existence with a mesh
access point, the on-device architecture, and the open problems (one-device homes, drift, fans,
pets, still people). The kit carries no measured numbers from any study; every number is a public
value or a labelled illustrative figure (see [`SOURCES.md`](SOURCES.md)).

This is rung 1 of a four-rung learning kit (notes → diagram → explorer → video). It assumes basic
signal processing (FFT, correlation) and basic machine learning (classifiers, train/test splits); it
does not assume any radio background.

## How to read these notes

Read Part A → Part B → Part C. Part A gives you the signal; Part B turns it into decisions; Part C
tells you whether the decisions are good enough to ship. Each note starts with a one-sentence
takeaway; a reader who stops there still leaves with something true.

### Start here
- [`SOURCES.md`](SOURCES.md) — what this kit is, how the internal material was generalised, the public sources, and the number rules.

### Part A — the physics and the signal
- [`notes/A0-why-sense-with-wifi.md`](notes/A0-why-sense-with-wifi.md) — no new hardware; the privacy framing; use cases by difficulty; the alternatives (mmWave, ultrasonic, PIR, BLE, camera); lab versus field.
- [`notes/A1-csi-and-multipath.md`](notes/A1-csi-and-multipath.md) — OFDM subcarriers; amplitude and phase per antenna pair; CSI versus RSSI; static and dynamic paths; Doppler; Fresnel zones; where one link is sensitive.
- [`notes/A2-what-the-hardware-gives-you.md`](notes/A2-what-the-hardware-gives-you.md) — report rate; subcarriers per band and width; phase offsets; AGC; outliers; two public chips compared; 2.4 versus 5 GHz.

### Part B — the processing chain
- [`notes/B1-preprocessing.md`](notes/B1-preprocessing.md) — power normalisation, background and dynamics, Hampel filter, phase sanitisation, subcarrier selection and grouping, and the measured value of the chain.
- [`notes/B2-features.md`](notes/B2-features.md) — variance, ACF, PCA eigenvalues, FFT and DWT; Parseval; removing DC; environment-independent features; the home-to-home spread.
- [`notes/B3-classifiers-and-windows.md`](notes/B3-classifiers-and-windows.md) — threshold to SVM to small nets; TPR at fixed FPR; random versus held-out-day and held-out-home splits; link labelling; window length versus latency.
- [`notes/B4-multi-device-joint-detection.md`](notes/B4-multi-device-joint-detection.md) — softAP device-to-device links; cross-correlation for AP-side versus client-side motion; sorted nodes and links; through-wall false positives; the device-count result.
- [`notes/B5-room-localisation-by-metric-learning.md`](notes/B5-room-localisation-by-metric-learning.md) — why not a room classifier; contrastive and triplet loss; one calibration walk per room; nearest-neighbour rooms.

### Part C — making it real
- [`notes/C1-kpis.md`](notes/C1-kpis.md) — the four-stage KPI ladder; six KPIs per stage; false alarms per month versus per-window FPR; time to detect and to clear; per-scenario breakdown.
- [`notes/C2-data-collection-campaigns.md`](notes/C2-data-collection-campaigns.md) — the collection tool; the scenario script; the target and link taxonomy; marking the home; labelling; multi-home studies; consent.
- [`notes/C3-coexistence.md`](notes/C3-coexistence.md) — a mesh AP on the same channel; the 2 × 2 test; mean survives, spread does not; what to control.
- [`notes/C4-sensing-endpoint-architecture.md`](notes/C4-sensing-endpoint-architecture.md) — cloud, edge + cloud, or edge; the layered stack; the sensing daemon; start, stop, and health; on-device cost.
- [`notes/C5-limits-and-open-problems.md`](notes/C5-limits-and-open-problems.md) — coverage, CSI quality, sampling rate, symmetry, inanimate motion, ground truth, drift, still presence, pets, several people; fusion and virtual sensing.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical.
- [`constants.json`](constants.json) — every number this kit cites, each labelled public or illustrative, each with a source.

## Question a reader asks → note that answers it

| Question | Note |
|---|---|
| Why use Wi-Fi for presence instead of a camera or a radar? | [[notes/A0-why-sense-with-wifi]] |
| What exactly is CSI, and why is it better than RSSI? | [[notes/A1-csi-and-multipath]] |
| Why is motion near the radios easier to see than motion in the middle of the link? | [[notes/A1-csi-and-multipath]] |
| What does my chip actually give me, and why not 2.4 GHz? | [[notes/A2-what-the-hardware-gives-you]] |
| Why is the raw phase useless on a single-antenna link? | [[notes/A2-what-the-hardware-gives-you]] |
| Which preprocessing steps matter, and by how much? | [[notes/B1-preprocessing]] |
| Why does a variance threshold from one room fail in another? | [[notes/B2-features]] |
| Why remove the DC term from FFT features? | [[notes/B2-features]] |
| My model scores well on a random split — why does it fail tomorrow? | [[notes/B3-classifiers-and-windows]] |
| How long a window, and what does it cost in latency? | [[notes/B3-classifiers-and-windows]] |
| Is the motion near the AP or near my device? Is it next door? | [[notes/B4-multi-device-joint-detection]] |
| Why do device-to-device links help so much? | [[notes/B4-multi-device-joint-detection]] |
| How do I find the room when every home has different rooms? | [[notes/B5-room-localisation-by-metric-learning]] |
| What does "1% false positives" mean for a user? | [[notes/C1-kpis]] |
| How do I design a data campaign that generalises? | [[notes/C2-data-collection-campaigns]] |
| Will a busy mesh AP on the same channel ruin my CSI? | [[notes/C3-coexistence]] |
| What runs on the device and what runs in the cloud? | [[notes/C4-sensing-endpoint-architecture]] |
| Why did a lab success miss the field target, and what is still unsolved? | [[notes/C5-limits-and-open-problems]] |

## Conventions

- Notes use the ASD-STE100-at-80% style: one fact per sentence, active voice, one term per concept, caveats before results, numbers with units.
- The subject is generic: "a home", "a sensing device" or "endpoint", "the AP", "a mesh Wi-Fi access point", "the programme".
- Every number is public (standard, paper, vendor document, or labelled arithmetic) or labelled illustrative; the backticked key after a number points into [`constants.json`](constants.json). No number is a measurement from a specific study.
- Internal material is cited only by the generic tags I1–I7 described in [`SOURCES.md`](SOURCES.md). "(my explanation)" and "(interpretation)" mark reasoning that is mine, not a source's.
- `[[wikilinks]]` connect notes inside this kit (Obsidian-compatible).
