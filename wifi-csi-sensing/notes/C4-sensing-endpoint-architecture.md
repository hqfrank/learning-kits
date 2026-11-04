# C4 — Software architecture of a sensing endpoint

**Source:** internal I7 (where to run the model, layered stack, on-device daemon responsibilities, start/stop flows, softAP options), I1 §4 (topology, assembling node), generalised. Data-rate arithmetic is mine. · **Status:** concept note. Study numbers are illustrative.

## In one sentence
The endpoint runs the whole per-link pipeline on the device — capture, filter, buffer, preprocess, feature, classify — and sends only a small per-link score to a cloud service that makes the joint decision, because raw CSI from many links is too much traffic and a small classifier fits the device easily.

## What it is
A **sensing endpoint** is a device whose software turns its own CSI into decisions. Its architecture answers two questions: where does each stage run, and how is the pipeline started, stopped, and kept healthy?

## How it works
**Where to run the model.** Three options were compared (internal I7):

| Option | What runs where | For | Against | Decision |
|---|---|---|---|---|
| cloud only | devices upload raw CSI; cloud does everything | simplest device | constant upload traffic | rejected |
| edge + cloud | devices classify each link; cloud fuses the scores | low traffic, low latency per link | a model must fit on the device | **chosen** |
| edge only | devices exchange data and decide locally | lowest latency, no cloud | complex device-to-device protocol | rejected for a first version |

Why the traffic argument wins (my arithmetic): beacons are sent in the legacy OFDM format, so a beacon CSI report has 52 used subcarriers (`used_subcarriers_legacy_20MHz`; my explanation). At an illustrative 10 reports per second (`csi_rate_beacon_illustrative`) that is 520 complex values per link per second. With an illustrative 16 links per home (4 devices, all links; see [[B4-multi-device-joint-detection]]) it is about 8 300 complex values per second per home, continuously. Edge classification replaces this with one score per link per window.

**The layered stack** (internal I7), from the bottom:

- **Layer 0 — Wi-Fi driver and firmware.** Extract CSI from received beacons and hand it to user space. A command interface enables and disables CSI upload.
- **Layer 1 — the sensing daemon.** The core on-device program, written in C++ with a small inference runtime. It:
  1. reads raw CSI from the driver's output;
  2. keeps only frames from the MAC filter list and stamps each report with its time;
  3. buffers reports into sliding windows;
  4. runs preprocessing: power normalisation, Hampel filter, subcarrier selection ([[B1-preprocessing]]);
  5. extracts features: FFT, PCA ([[B2-features]]);
  6. runs the classifier: a linear model or SVM, or a small network of about an illustrative 1 million weights and 2 MB of memory (`model_size_illustrative`; [[B3-classifiers-and-windows]]);
  7. publishes a per-link, per-window motion probability;
  8. monitors CSI health: missing reports, driver errors, rate drops;
  9. optionally uploads raw CSI, only during data campaigns ([[C2-data-collection-campaigns]]).
- **Layer 2 — the device framework.** Two calls, start detection and stop detection.
- **Layer 3 — the cloud service.** Device management, the joint decision across a home's links, and dispatch of actions to automations.
- **Layer 4 — the companion app.** Pairing, enabling, and session control by the user.

**Start detection** (internal I7):

1. Check prerequisites: the device supports CSI; Wi-Fi is connected; the framework service is up; detection is not already running.
2. Validate arguments: whether to run a softAP; the target MAC addresses; the home AP's MAC address.
3. Read the regulatory country code, the AP's BSSID, and the AP's channel.
4. Start the softAP on that channel ([[B4-multi-device-joint-detection]]).
5. Start the daemon.
6. Schedule a result task that broadcasts each new decision to other device software.
7. Schedule a health-monitor task.

**Stop detection** reverses the order: stop the daemon, remove the result and health tasks, clear the stored state.

**Device-to-device CSI options** (internal I7): a softAP via `hostapd` is straightforward but costs power, must follow AP channel changes, and can conflict with other features that use the radio; standard 802.11 action frames avoid the softAP but depend on chip support.

**On-device cost** (internal I7; my explanation): every preprocessing step is a median, a norm, or a moving average over a few dozen values. Subcarrier selection or grouping removes most of the feature computation ([[B1-preprocessing]]). The daemon runs only while detection is enabled. The model budget above is small next to the memory of a typical smart-home device.

## Common confusions
- **"On-device ML means the device decides everything."** Each device decides per link. Room-level decisions need all links and are made where all links meet.
- **"The model is the expensive part."** The steady cost is moving and buffering reports; the model runs once per window.
- **"A health monitor is optional."** CSI streams stop silently when the driver, the channel, or the softAP changes. Without a health signal the cloud reads silence as "nobody home".
- **"Raw upload is needed for improvement."** Raw upload is needed for campaigns. Production devices need only scores and health.

## Why it matters
The edge-plus-cloud split sets the product's privacy and traffic profile: no raw radio data leaves the device in normal use. The start, stop, and health flows are where field reliability is won or lost, because the most common failure is not a wrong decision but a pipeline that silently stopped.

## Terms introduced
- **sensing endpoint** — a device whose software turns its CSI into decisions.
- **edge + cloud split** — per-link decisions on the device, joint decisions in the cloud.
- **sensing daemon** — the long-running on-device program that runs the CSI pipeline.
- **BSSID** — the MAC address that identifies an access point's network.
- **result task / health-monitor task** — scheduled jobs that publish decisions / check that the CSI stream is alive.
- **companion app** — the phone application that controls the feature.
