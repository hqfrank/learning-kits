# A2 — What the hardware gives you

**Source:** IEEE 802.11 (subcarrier counts, beacon interval, channel plan); Halperin et al. 2011 (Intel 5300 CSI Tool); Xie, Li, Li 2015 (Atheros CSI Tool); Gringoli et al. 2019 (Nexmon CSI); Espressif ESP-IDF "Wi-Fi Channel State Information"; Kotaru et al. 2015 (SpotFi, phase offsets). Band and chipset comparisons from internal I7, generalised. · **Status:** concept note. Study numbers are illustrative.

## In one sentence
The CSI you can sense with is limited by the chip, not by the standard: the chip decides how often you get a report, how many subcarriers and antenna pairs it contains, how noisy the phase is, and how often a report is corrupt, and in practice CSI quality decided the result more than the algorithm did.

## What it is
A **CSI report** is one CSI matrix, produced by the chip for one received frame, plus metadata (timestamp, transmitter MAC address, RSSI, antenna count). Four properties of the report stream matter for sensing:

1. **Report rate** — reports per second per link.
2. **Shape** — subcarriers × antenna pairs.
3. **Phase quality** — how much random offset each report's phase carries.
4. **Corruption** — the fraction of reports that are outliers or fail to parse.

## How it works
**Report rate.** The chip produces a report only when it receives a frame from the chosen transmitter. Passive sensing listens to **beacons**, which an AP sends every 100 TU by default, about 9.77 Hz (`beacon_interval_default`, `beacon_rate_default`). Faster sensing needs injected traffic, for example pings or dedicated test frames, at an illustrative 100 Hz (`csi_rate_injected_illustrative`). Injected traffic costs airtime and power. Ping traffic may also be given the lowest priority and dropped, so the rate is not guaranteed (internal I7). Fast events such as falls want rates of the order of an illustrative 100 Hz (`fall_detection_rate_illustrative`).

- **Caution:** the achieved rate is not the nominal rate. In a side-by-side test of two chips, the achieved rate ranged from below to slightly above nominal (an illustrative 0.85–1.05 of nominal, `actual_vs_nominal_rate_illustrative`) because of interference and chip processing. Use timestamps, not an assumed rate, for every time-domain feature (internal I7).

**Shape.** The standard fixes the number of used subcarriers per channel width: 56 at 20 MHz, 114 at 40 MHz, 242 at 80 MHz, and 484 at 160 MHz for 802.11n/ac (`used_subcarriers_ht_20MHz`, `used_subcarriers_ht_40MHz`, `used_subcarriers_vht_80MHz`, `used_subcarriers_vht_160MHz`). The chip decides how many it reports:

| Tool or chip | What it reports | Source |
|---|---|---|
| Intel 5300 CSI Tool | 30 subcarrier groups per antenna pair, up to 3×3 antennas | Halperin et al. 2011 (`intel5300_csi_groups`, `intel5300_max_antennas`) |
| Atheros CSI Tool | 56 subcarriers at 20 MHz, 114 at 40 MHz | Xie et al. 2015 (`atheros_csi_subcarriers`) |
| Nexmon CSI (Broadcom/Cypress) | per-subcarrier CSI on modern chips, up to 80 MHz | Gringoli et al. 2019 |
| ESP32 | 64 subcarrier entries from the L-LTF at 20 MHz | Espressif ESP-IDF (`esp32_csi_lltf_subcarriers`) |

- **Caution:** beacons are sent in the legacy (non-HT) OFDM format, so beacon CSI has the 52 legacy subcarriers (`used_subcarriers_legacy_20MHz`), even on an 802.11n/ac network (my explanation from the 802.11 frame formats).

Wider channels improve **delay resolution**, which is 1/bandwidth: 50 ns (15 m of path) at 20 MHz, 6.25 ns (about 1.9 m) at 160 MHz (`delay_resolution_by_width`, my arithmetic). Finer delay resolution separates more paths, so it gives a richer fingerprint and, in principle, better localisation.

**Phase quality.** The raw CSI phase of each report includes offsets that have nothing to do with the room (Kotaru et al. 2015; Ma et al. 2019):

- **carrier frequency offset (CFO)** — transmitter and receiver oscillators differ slightly; this adds a random common phase per report;
- **sampling time offset (STO)** and **sampling frequency offset (SFO)** — the receiver samples at a slightly wrong time or rate; this adds a phase slope across subcarriers;
- **phase-locked-loop offset** — a random phase at each radio start-up.

With two or more receive antennas on one chip, most of these offsets are common to the antennas and cancel in a ratio or a conjugate product (see [[B1-preprocessing]]). A single-stream (1×1) link has no second antenna, so in practice it gives amplitude only (internal I2, I7).

**Amplitude quality.** The receiver's **automatic gain control (AGC)** rescales each frame. This makes the overall CSI power jump from report to report. Per-report power normalisation removes it (see [[B1-preprocessing]]).

**Corruption.** Real chips produce bad reports. Two observations from the chipset comparison (internal I7):

- Outliers were a few percent of reports (an illustrative 0.02–0.08, `outlier_ratio_illustrative`). The MT7658 showed a lower outlier ratio than the MT7668 in a side-by-side test, and it gave better detection curves.
- Subcarriers next to the middle guard band showed sudden amplitude drops on both chips. They must be removed.
- **Caution on wide channels:** an 80 MHz report is four 20 MHz sub-bands. An outlier in any one sub-band spoiled the whole 80 MHz report. The proposed fix was to process the four 20 MHz sub-bands independently.

**2.4 GHz versus 5 GHz.**

| Property | 2.4 GHz | 5 GHz |
|---|---|---|
| Non-overlapping 20 MHz channels | 3 (`nonoverlapping_channels_2g4`) | many more |
| Congestion from neighbours | high | lower |
| Channel width available | mostly 20 MHz | up to 80 or 160 MHz |
| Wall loss and range | lower loss, longer range | higher loss, shorter range |
| CSI in a still room (internal I7) | several amplitude clusters, looks like motion; parse errors at high rate of the order of an illustrative 0.15 (`parse_error_2g4_illustrative`) | clean and stable after preprocessing |

The same detector reached an illustrative 0.7 true-positive rate at 1% false-positive rate on 5 GHz and an illustrative 0.1 on 2.4 GHz (`band_tpr_illustrative`). The programme concluded that sensing should run on 5 GHz (or 6 GHz) only (internal I7).

## Common confusions
- **"Wider is always better."** Wider channels give more subcarriers and finer delay resolution, but they also give more ways for one bad sub-band to corrupt a report. Process sub-bands separately.
- **"The CSI rate is the beacon rate."** Reports are lost, delayed, and corrupted. The achieved rate varies by chip and by channel load.
- **"A chip that supports CSI supports sensing."** Two chips with the same standard support gave clearly different detection quality in the same test. Benchmark the chip before you design the algorithm.
- **"2.4 GHz is fine because it reaches further."** It reaches further, but the congestion noise in a still room looked like motion.

## Why it matters
The field shortfall in [[A0-why-sense-with-wifi]] traced back first to CSI quality: outliers, drift, and a single stream without phase. No amount of model work recovers information that the chip does not deliver. The first engineering step for any Wi-Fi sensing product is a side-by-side CSI-quality test of candidate chips, bands, and widths in still and moving scenes.

## Terms introduced
- **CSI report** — one CSI matrix with metadata, produced for one received frame.
- **report rate** — CSI reports per second on one link.
- **beacon** — the periodic management frame an AP broadcasts; a free source of CSI.
- **injected traffic** — frames sent only to generate CSI reports at a higher rate.
- **delay resolution** — the smallest delay difference the channel width can separate, 1/bandwidth.
- **CFO / STO / SFO** — carrier frequency offset / sampling time offset / sampling frequency offset; sources of random CSI phase.
- **AGC (automatic gain control)** — the receiver function that rescales each frame's gain.
- **guard band** — unused subcarriers at the band edges and centre.
- **outlier (CSI)** — a report whose amplitude jumps for reasons unrelated to the room.
- **single-stream (1×1)** — one transmit and one receive antenna; one antenna pair.
