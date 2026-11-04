# C3 — Co-existence: what a mesh AP's traffic and channel changes do to CSI

**Source:** internal I4 (mesh AP co-existence test: goal, set-up, 2 × 2 design, results), I7 (outliers under co-channel interference, softAP channel following), generalised; IEEE 802.11 (shared-medium MAC). · **Status:** concept note. Study numbers are illustrative.

## In one sentence
A busy mesh Wi-Fi access point on the same channel did not change the per-second mean of the CSI or stop CSI collection, but it did imprint a regular pattern on the per-second spread and slightly raised the outlier rate, so a sensing experiment must control the channel and the traffic and must say which statistic it relies on.

## What it is
**Co-existence** is the question whether two radio systems in one home disturb each other. Here the two systems are the sensing endpoints and a mesh Wi-Fi access point, which may also run its own sensing. The worst case is that all of them use the same channel (internal I4).

The 802.11 MAC shares one channel by listening before transmitting. It reduces collisions; it does not remove interference. Strong neighbouring transmissions can still corrupt the channel estimate or delay the frames that produce CSI (internal I4 Q&A; my explanation).

## How it works
**The test design** (internal I4):

- Four sensing devices connected to a separate reference AP.
- Five mesh AP nodes in the same room: one beside the reference AP, one beside each sensing device.
- Every radio forced to one 5 GHz channel. The mesh nodes normally choose channels automatically; the test set them to a static channel to create the worst case.
- A 2 × 2 design: **no motion / motion near one device** × **mesh off / mesh on**.
- CSI recorded on every link (AP–device and device–device), all subcarriers, at the beacon-driven rate.
- Airtime on the channel measured with a real-time Wi-Fi analyser.

**Two statistics per second.** The analysis reduced each second of reports on each link to two numbers per subcarrier (internal I4):

1. the **mean** of the reports in that second;
2. the **standard deviation** of the reports in that second.

**Results** (internal I4, I7):

| Question | Result |
|---|---|
| Data quantity | unchanged: every link delivered CSI in every condition, at a normal report count |
| Per-second mean | no clear effect of the mesh; motion near the device stayed clearly visible with mesh on and off |
| Per-second standard deviation | clear effect: deep notches when the mesh was on, at a consistent, repeatable pattern |
| Airtime | the mesh used over an illustrative 0.9 of the channel's airtime (`coexistence_airtime_illustrative`) |
| Outliers in a still room | slightly more with the mesh on than off |

**Recommendation.** The two systems can collect in parallel. Features built on the per-second mean are robust. Features built on short-term spread must either filter the regular notch pattern or be tested with the mesh on (internal I4).

**Why the mean survives** (interpretation from internal I7, my explanation): interference adds noise that is uncorrelated with the room and averages out over a second of reports. Human motion changes the multipath in a structured way that is correlated across subcarriers and persists over many reports. The per-second standard deviation, by contrast, measures exactly the fast variation that interference adds.

**What to control in a sensing experiment** (my explanation, from the test design and internal I7):

- **Channel.** Fix and record it. An AP that changes channel changes the CSI baseline, and every softAP must follow the change ([[B4-multi-device-joint-detection]]).
- **Band and width.** Fix and record them; results do not transfer across bands ([[A2-what-the-hardware-gives-you]]).
- **Other traffic.** Measure airtime during every session. A quiet lab is the best case, not the typical case.
- **Report rate.** Log achieved rate per link; interference lowers it.
- **The statistic.** State whether a feature uses short-term spread, which interference touches, or longer averages, which it barely touches.
- **The interference factor as a design factor.** Run "interferer on / off" as a factor crossed with "motion / no motion", not as a nuisance left uncontrolled.

## Common confusions
- **"No effect on the mean means no effect."** The spread showed a strong effect. A detector built on variance inherits it.
- **"The MAC prevents interference."** It schedules access; it does not make neighbouring energy disappear from the channel estimate.
- **"The lab result covers homes."** The lab test chose the worst-case channel but one room and one layout. Homes add neighbours, channel changes, and unscripted traffic.
- **"A regular artefact is harmless."** It is predictable, which makes it filterable; it is still an artefact until it is filtered.

## Why it matters
Sensing endpoints live in the noisiest radio environment in the house, next to the AP and to other radios. A 2 × 2 co-existence test is cheap and settles whether a feature family is safe before a field campaign spends months on it.

## Terms introduced
- **co-existence** — whether two radio systems in one place disturb each other's operation or measurements.
- **mesh Wi-Fi access point** — one node of a multi-node home Wi-Fi system.
- **co-channel interference** — transmissions on the same channel from another network or device.
- **airtime (utilisation)** — the fraction of time a channel is occupied by transmissions.
- **per-second mean / standard deviation (CSI)** — the average / spread of a subcarrier's amplitude over the reports in one second.
- **2 × 2 factorial design** — an experiment that crosses two factors at two levels each.
