# B4 — Multi-device joint detection: AP side or client side, this room or next door

**Source:** internal I1 §3.0, §3.5, §4 (single-link corner cases, deployment types, softAP topology, sorted-node / sorted-link method), I2 (multi-device approaches), I6 (cross-correlation rule, through-wall risk), I7 (device-count and motion-type results, link labelling), generalised. · **Status:** concept note. Study numbers are illustrative.

## In one sentence
One link cannot tell motion near its AP end from motion near its client end, or motion in the room from motion behind a wall, so the system adds links between every pair of devices and compares them: motion that changes every link at once is near the shared AP, motion that changes one device's links is near that device.

## What it is
**Joint detection** combines the CSI or the per-link scores of many links to decide whether there is motion in the home, and where. A home with an AP and N sensing devices has N AP–device links. If every device also hears every other device, there are N² directed links: for an illustrative 4 devices, 4 AP links become 16 links (my arithmetic). The link count grows with the square of the device count. This is the main reason extra devices help.

## How it works
**Single-link corner cases.** The method white paper listed what one link gets wrong (internal I1 §3.5):

- false negatives: the target is too far from the link; very slow motion such as typing; a blind spot behind a half-height obstacle;
- false positives: abrupt CSI cluster changes with no motion (handled by outlier removal, [[B1-preprocessing]]); a person who crosses the LoS outside the room; **motion near the other end of the link** (the largest single-link problem); motion in the neighbouring room; rarely, motion outside the building.

**Device-to-device links.** A client normally reports CSI only from frames sent by its AP. To get CSI between devices, each device also runs a software access point (**softAP**, for example with the open-source `hostapd`) on the same channel as the home AP. Each device then hears every other device's beacons and measures CSI from them. A MAC-address filter keeps only the frames from the devices of interest; otherwise neighbouring networks flood the pipeline (internal I1 §4.2, I3). An alternative is to send standard 802.11 action frames between devices, which needs no softAP but depends on chip support (internal I7).

- **Caution:** the softAP must follow the home AP when it changes channel, and it costs power and can conflict with other features that use the radio (internal I7).

**AP side or client side: cross-correlation.** All AP–device links share the AP end. Motion near the AP changes all of them in the same way at the same time. Motion near one device changes mainly that device's links. So compute the cross-correlation of the CSI variation across devices (internal I6):

- high correlation across all AP links → motion near the AP;
- low correlation, one device's links active → motion near that device;
- several devices active with low mutual correlation → several people, each near a device.

**Locating the motion: sorted nodes and sorted links.** Let *vᵢⱼ* be the observed variation on the link between nodes *i* and *j*. Let *wᵢ* = Σⱼ *vᵢⱼ* be the summed variation of node *i*. The node with the largest *w* is probably closest to the target (internal I1 §4.3). The method:

1. Sort the nodes by *w* and the links by *v*, both descending.
2. Take links in order of *v*. For each link, compare the *w* of its two end nodes.
3. If one end's *w* is clearly larger, split the plane at the perpendicular bisector of the link and keep the half on that side.
4. The intersection of kept half-planes is a polygon: the detected area. Often the first few links (an illustrative two or three) already decide the room.

- **Caution:** "clearly larger" must mean *wᵢ* > *wⱼ* + T, with a margin T found empirically. A target at the centre of three devices gives three nearly equal *w*; then the honest answer is "near several nodes" (internal I1 §4.3). The same margin applies when comparing two *v* values.
- **Caution:** links that overlap heavily vote twice for the same area. Pre-select links or correct for overlap.
- The method needs rough device positions. Options: a template floor plan, the user marking devices in a companion app, self-localisation by 802.11mc fine-timing or Bluetooth ranging, or clear placement instructions (internal I1 §4.3).

Two learned alternatives were proposed: a binary classifier per link whose confidences are fused on the device graph, and a regression from CSI to a position relative to each link pair, combined across pairs (internal I2). The multi-home study used the simplest fusion: average the per-link motion probabilities to get a home-level decision (internal I7).

**Through-wall false positives.** A wall attenuates the reflected paths from the next room, so their effect is smaller. Three further mitigations (internal I6, I1):

- more endpoints, so that the room with the motion has a link that responds much more strongly;
- per-home sensitivity settings for homes with thin walls;
- fusion with a sensor that does not see through walls, such as ultrasound, whose difficult cases are independent of Wi-Fi's.

**Deployment types.** The same link length gives very different CSI in open space and through a wall. One proposal was to classify each link's deployment (free-space LoS, symmetric wall, asymmetric wall, several walls, NLoS) and use a separate model per type, with the type set by the user or detected from the CSI (internal I1 §3.0).

## What the studies showed (illustrative)
- **Caution:** one multi-home study, home-level motion detection, TPR at 1% FPR; numbers illustrative.

| Setup | TPR (`devices_tpr_illustrative`) |
|---|---|
| 1 device, AP link only | an illustrative 0.5 |
| 4 devices, AP links only | an illustrative 0.75 |
| 4 devices, AP and device-to-device links | an illustrative 0.95 |

- With the same four devices, adding device-to-device links gave a larger gain than going from one device to four on AP links alone (internal I7).
- By scenario: large motion near any device was detected well (an illustrative 0.95); motion in a room with no device much less (an illustrative 0.6); small motion such as typing least (an illustrative 0.4) (`motion_type_tpr_illustrative`).

## Common confusions
- **"More devices help because there are more sensors."** They help mainly because the number of *links* grows with the square of the device count, and the new links cross rooms the AP links never cross.
- **"High variation on a link means the person is between the two radios."** It can mean the person is near either end. Only comparison across links resolves which.
- **"A room with no device is covered by its neighbours."** It is covered weakly. Its motion reaches other links through walls, which is the same mechanism that causes through-wall false positives.

## Why it matters
Room-level sensing is a network property, not a device property. The design lever is the link graph: how many devices, how they are placed, and whether they can hear each other. A single-device home is limited to a zone around one link (see [[C5-limits-and-open-problems]]).

## Terms introduced
- **joint detection** — a decision made from many links together.
- **link (sensing)** — one transmitter–receiver pair whose CSI is measured; device-to-device links are directed.
- **softAP** — a software access point run on a client device so that other devices can measure CSI from it.
- **MAC filter (CSI)** — a list of transmitter addresses whose frames are kept for CSI.
- **cross-correlation (across links)** — the similarity of CSI variation over time on two links.
- **AP-side / client-side motion** — motion near the shared AP / near one client device.
- **node variation (w)** — the summed variation of all links at one node.
- **decision margin (T)** — the minimum difference needed before one value is called larger than another.
- **through-wall false positive** — a detection caused by motion in another room.
- **deployment type** — the geometric class of a link: free-space LoS, wall between, several walls, NLoS.
