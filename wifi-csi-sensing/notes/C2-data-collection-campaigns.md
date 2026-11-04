# C2 — Data collection campaigns: scenarios, taxonomy, labelling, homes, consent

**Source:** internal I3 (collection tool workflow, device placement, scripted scenarios, naming scheme), I7 (scenario taxonomy, environment types, marking protocol, multi-home studies, ground-truth scalability), generalised. Consent practice is general research ethics, marked as my explanation. · **Status:** concept note. Study numbers are illustrative.

## In one sentence
A sensing dataset is only as general as its scenario design, so a campaign scripts each motion type, describes every target position and every link by a small taxonomy, marks the home so operators cover the taxonomy, records camera-synchronised ground truth with consent, and collects across many homes because the home is the unit of generalisation.

## What it is
A **data collection campaign** is a planned set of recording sessions in real homes. It produces CSI from every link plus a ground-truth label of where people were and what they did. Three parts define it: the **collection tool**, the **scenario script**, and the **scenario taxonomy**.

## How it works
**The collection tool.** The workflow automated every step that an operator would get wrong by hand (internal I3):

1. Discover each sensing device's current IP address from its known MAC address by scanning the subnet. Repeat at every session, because addresses change.
2. Connect to each device and run a real command to confirm it works. A "connected" status alone was sometimes false.
3. Start a softAP on each device on the home AP's channel (see [[B4-multi-device-joint-detection]]). Confirm by scanning that every softAP is visible; repeat the scan if needed.
4. Build the MAC filter list of all transmitters of interest and push it to every device.
5. Choose one device to assemble the data. The choice did not affect data quality.
6. Run for a fixed duration, then stop automatically.
7. Synchronise the CSI clock with a camera-based ground-truth recorder.

Each check that fails stops the run and tells the operator which device to restart. Restarting every device before every test avoided most failures (internal I3).

**Device placement.** One device per room, placed where people really put it: a bedside table, a TV stand. In a large open space, two well-separated devices with LoS between them. The AP in the living room (internal I3). Realistic placement matters more than ideal placement, because the product will meet realistic placement.

**The scenario script.** Each scripted session has a start condition, an action, and an end condition (internal I3):

| Type | Action | Tests |
|---|---|---|
| 1 | move within an illustrative 1 m of one device (`near_device_radius_illustrative`) | near-device motion |
| 2 | move just inside, then just outside, a door | entry and exit |
| 3 | stand still in a room, away from the device | still presence |
| 4 | walk from one device's room to another's and back | room-to-room transition |
| 5 | move between two devices in one open space | hand-over with LoS |
| 6 | everybody outside the home | empty-home baseline |

Sessions last an illustrative 15–30 s (`session_length_illustrative`). One apartment needs about an illustrative 25 sessions and 10 minutes (`campaign_session_illustrative`). Each session name encodes its type and the device or devices involved, for example `type_deviceA_deviceB`, with 0 for "none". This makes every file self-describing for automatic processing (internal I3).

**The scenario taxonomy.** A script says what the operator did. A taxonomy says where that put the target relative to each link, so that coverage can be checked (internal I7). The **target position** is a tuple of three attributes:

- distance to the link's end nodes: close to an end node / in the middle, inside the first Fresnel zone / far from both;
- relation to paths: on the LoS / on a main NLoS walking route between rooms / on no significant path;
- obstacle: close to a wall or bulky furniture / not.

The **link set-up** is another three-attribute tuple:

- LoS: available (same room) / one obstacle (adjacent rooms) / several obstacles (non-adjacent rooms);
- reflector: a device near a wall or large reflector / not;
- link length: short / long.

**Environment types.** Studio, one-bedroom and two-bedroom apartments, single-storey and two-storey family homes, and large spaces such as a warehouse or an office (internal I7).

**Marking the home.** Coloured tape on the floor made the taxonomy visible to operators: one colour for LoS paths, one for main NLoS routes, one for proximity zones around devices and obstacles, one for the operator's trajectory. The rules were: approach each device at least once, cross each LoS path, walk each NLoS route, and visit areas far from devices and paths (internal I7). The campaign target was an illustrative 200 homes (`campaign_target_illustrative`), chosen so that every link-set-up combination appeared in the dataset.

**Labelling.** Camera ground truth gives "who was where, when". The programme planned automatic annotation of the camera streams to split motion from no-motion periods (internal I2). The label is then mapped per link by the rule in [[B3-classifiers-and-windows]].

**Consent and privacy.** Camera ground truth is the opposite of the product's privacy promise. A campaign therefore needs informed consent from every occupant, cameras only during scripted sessions, and a clear rule for retaining and deleting video (my explanation). The programme named ground truth without cameras as an open scaling problem (internal I7; see [[C5-limits-and-open-problems]]).

**Multi-home studies.** The home, not the session, is the unit of generalisation. Split by home: train on an illustrative 20 homes, test on 5 others (`home_study_size_illustrative`). A larger field study in an illustrative 50 homes (`field_study_size_illustrative`) followed. Scripted scenarios measure TPR; unscripted days with no-one home, or with known occupancy, measure the false-alarm rate (my explanation, see [[C1-kpis]]).

## Common confusions
- **"More minutes of data is better."** More *homes* and more *taxonomy cells* is better. Minutes inside one home are highly correlated.
- **"Ideal placement shows the ceiling."** It shows a ceiling the product never meets. Place devices the way customers do.
- **"The script is the taxonomy."** The script controls actions; the taxonomy measures coverage of geometry. You need both.
- **"Scripted sessions measure false alarms."** Short scripted empty sessions cannot reach a budget of a few false alarms per month. That needs long unscripted recordings.

## Why it matters
The cross-home failure of simple features ([[B2-features]]) and the lab-to-field gap ([[C1-kpis]]) are both data-coverage problems. A taxonomy-driven campaign makes coverage measurable before the model is trained.

## Terms introduced
- **data collection campaign** — a planned set of recordings in real homes with ground truth.
- **collection tool** — the automation that sets up devices, filters, and recording.
- **scenario script** — the list of session types with start, action, and end conditions.
- **session** — one scripted recording of one scenario.
- **scenario taxonomy** — attributes that place each target position and each link set-up in a coverage grid.
- **target position tuple / link set-up tuple** — the two three-attribute descriptions in the taxonomy.
- **ground truth** — the reference record of where people were and what they did.
- **informed consent** — documented agreement of each occupant to be recorded.
- **unit of generalisation** — the grouping (here, the home) that must differ between train and test.
