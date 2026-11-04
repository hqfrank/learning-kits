# A0 — Why sense presence with Wi-Fi

**Source:** internal I6 (use cases, alternatives, risks) and I7 (strategy, localisation landscape), generalised; Ma, Zhou, Wang, Computing Surveys (CSUR) 2019 (survey); IEEE 802.11bf task group page (https://www.ieee802.org/11/Reports/tgbf_update.htm). · **Status:** concept note. Every study number is illustrative.

## In one sentence
Wi-Fi sensing turns radios that are already in the home into a motion and presence sensor with a software update, and it uses no camera and no microphone, but it is coarse, it sees through walls, and it needs several devices before it can say which room a person is in.

## What it is
A home has Wi-Fi links between an access point (AP) and its client devices. Every frame on a link carries a known training signal. The receiver uses this signal to estimate how the channel changed the frame. A person who moves in the room changes the channel. **Wi-Fi sensing** reads these channel estimates and infers motion, presence, and coarse location from them.

The channel estimate per subcarrier is called **channel state information (CSI)** (see [[A1-csi-and-multipath]]). The sensing system needs no new hardware if the Wi-Fi chip exposes CSI to software (see [[A2-what-the-hardware-gives-you]]).

**Device-free sensing** is the case where the person carries no device. This kit is about device-free sensing. **Device-based tracking** (locating a phone or a tag by its own radio) is a different and easier problem.

## How it works
The product idea has four parts (internal I6, I7):

1. A firmware change on the Wi-Fi chip makes CSI available to the device software.
2. A program on each sensing device cleans the CSI, extracts features, and classifies each time window as "motion" or "no motion" (Part B).
3. Several devices combine their decisions to locate the motion at room level ([[B4-multi-device-joint-detection]], [[B5-room-localisation-by-metric-learning]]).
4. The result feeds a presence service that can fuse it with other presence signals and trigger home automations.

Use cases, in increasing order of difficulty (internal I6):

1. Fusion with another presence sensor (for example ultrasonic) to stop false "room empty" decisions.
2. Whole-home motion detection, for example a movement alert when the home should be empty.
3. Single-room presence, for example lights that turn off when a room becomes empty. This needs several devices.
4. Health uses: sleep, falls, gait, breathing.
5. Identification of who is present.

**The alternatives.** Each presence technology has a different failure mode (internal I6, I7):

| Technology | How it senses | Main limit |
|---|---|---|
| mmWave radar | reflections of high-frequency radio from a dedicated radar chip | extra hardware and cost; short range |
| Ultrasonic | a speaker emits ultrasound and a microphone array hears reflections | short range (an illustrative 2 m, `ultrasonic_range_illustrative`); needs audio-driver support; high-frequency noise causes false alarms |
| Sound event classification | classify ambient sound | "always listening" privacy perception; confusable sounds |
| Passive infrared (PIR) | changes in radiated heat | line of sight; a dedicated sensor |
| BLE / Zigbee RSSI | the signal strength of a radio the person carries | finds devices, not people |
| Camera | images | the strongest privacy objection, especially in bedrooms and bathrooms |
| **Wi-Fi CSI** | **perturbation of existing Wi-Fi links by the body** | **coarse; sees through walls; needs several endpoints for room level** |

**The privacy framing.** Wi-Fi sensing records no image and no sound. The CSI is processed on the device. This is the main reason to accept a coarser sensor than a camera (internal I6).

**The "glue" framing.** Wi-Fi sensing is weak at precise tracking. It is strong where precise sensors fail: through walls and furniture, in every direction. A useful role is to connect the small high-accuracy zones of radar or ultrasound into whole-home coverage (internal I7; interpretation).

**Standardisation.** The IEEE 802.11bf task group defines WLAN sensing as the use of 802.11 PHY and MAC features to estimate range, velocity, angle, and motion of objects. The amendment covers license-exempt bands between 1 GHz and 7.125 GHz and above 45 GHz (IEEE 802.11bf task group page). Before 802.11bf, CSI access depended on each chip vendor.

## What the programme found, in outline
- **Caution first:** the numbers below are illustrative. A two-room demonstration looked very good. A large field study in an illustrative 50 homes (`field_study_size_illustrative`) reached only about half the target true-positive rate (an illustrative 0.5 against 0.9, `field_tpr_vs_target_illustrative`) at a budget of a few false alarms per home per month (`false_alarm_budget_illustrative`). See [[C1-kpis]].
- The root causes were hardware CSI quality (outliers, drift) and environment change, not the idea itself (internal I7). See [[A2-what-the-hardware-gives-you]] and [[C5-limits-and-open-problems]].
- Commercial systems on better chips covered small labs well, but also produced false triggers overnight in real homes (internal I7). Lab performance did not predict field performance.

## Common confusions
- **"Wi-Fi sensing is Wi-Fi signal strength."** Signal strength (RSSI) is one number per frame. CSI is one complex number per subcarrier per antenna pair. The difference is the whole method (see [[A1-csi-and-multipath]]).
- **"It sees through walls, so it is better than a camera."** Seeing through walls is also its largest source of false alarms: motion next door looks like motion here (see [[B4-multi-device-joint-detection]]).
- **"Motion detection is presence detection."** A still person barely changes the channel. Presence of a still person is a much harder problem (see [[C1-kpis]]).
- **"One device is enough."** One link senses an elongated zone around the line between the two radios. It cannot say which end the motion is near (see [[B4-multi-device-joint-detection]]).

## Why it matters
The reason to build Wi-Fi sensing is distribution: millions of radios are already installed, and a software update turns them into sensors. The reason to be careful is that the evidence base is mostly lab results, and the gap from lab to home is large. The rest of this kit is about closing that gap honestly.

## Terms introduced
- **Wi-Fi sensing** — inference of motion, presence, or location from the channel estimates of Wi-Fi links.
- **device-free sensing** — sensing a person who carries no radio.
- **device-based tracking** — locating an object by its own radio transmissions.
- **access point (AP)** — the Wi-Fi device that a home's clients connect to.
- **endpoint** — a device that measures CSI and runs (part of) the sensing pipeline.
- **presence** — a person is in the area, moving or still. Contrast **motion**, where the person moves.
- **sensor fusion** — combining two sensors whose failure cases are independent so that each covers the other.
- **IEEE 802.11bf** — the IEEE amendment that standardises WLAN sensing.
