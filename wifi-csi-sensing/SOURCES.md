# Sources — Wi-Fi sensing with channel state information

This kit teaches a general method. It carries no measured numbers from any specific product,
home, or study.

## What this kit is

Study notes (rung 1 of a four-rung learning kit: notes → diagram → explorer → video) for one
question: **how do you turn the Wi-Fi signals already present in a home into a presence, motion, and
room-level location sensor, and how do you know whether it works?** Part A covers the physics and the
signal. Part B covers the processing chain. Part C covers what it takes to make a product of it: KPIs,
data campaigns, co-existence, on-device architecture, and the open problems.

## Provenance of the method

The engineering ideas in Parts B and C — the preprocessing chain and the measured value of each step,
the feature comparison, the cross-device correlation rule, the sorted-node / sorted-link localisation,
metric learning for rooms, the staged KPI ladder, the scenario taxonomy, the co-existence test design,
and the edge-plus-cloud split — are abstracted from **internal design documents of a device-health
programme, 2023–2025**. No internal material is reproduced. No product, team, person, device, tool,
place, or internal identifier from those documents appears here. The figures in those documents are
not copied, traced, or described.

The internal documents are cited only by a generic tag, so that each claim can be traced to its kind
of source without naming it:

| Tag | Kind of document |
|---|---|
| I1 | a method white paper: single-link detection, power-fading simulation, single-link corner cases, multi-link joint detection |
| I2 | a feature-extraction and machine-learning study note: preprocessing, candidate features, classifiers, train/test split experiment |
| I3 | a data-collection campaign design: tool workflow, device placement, scripted scenarios, naming scheme |
| I4 | a co-existence test report: mesh access points on the same channel as the sensing links |
| I5 | a KPI definition document: four detection stages with six KPIs each |
| I6 | a product-framing FAQ: use cases, alternative sensing technologies, risks |
| I7 | a programme summary: a multi-home motion study, feature comparisons, band and chipset comparisons, subcarrier selection, preprocessing impact, metric learning, software architecture, field results |

## Number rules

Every number in this kit is one of two classes, recorded in [`constants.json`](constants.json):

1. **public** — a value from a public standard, paper, or vendor document, or arithmetic on such
   values. Arithmetic is labelled "my arithmetic" in `constants.json` and in the prose.
2. **illustrative** — a round value of the same order of magnitude as an internal study figure. It
   keeps only the relation the figure teaches (a direction, a ratio, a ranking). The prose says
   "an illustrative …" every time. **An illustrative number is never a measurement.**

Key names in backticks in the notes (for example `devices_tpr_illustrative`) point into
`constants.json`.

## Public sources cited

Standards and vendor documentation:

- IEEE Std 802.11 (OFDM PHY of 802.11a/g, HT of 802.11n, VHT of 802.11ac, HE of 802.11ax): subcarrier
  spacing, FFT sizes, used-subcarrier counts, beacon interval, channel plan, beamforming-feedback
  grouping Ng.
- IEEE 802.11bf task group, WLAN sensing amendment: https://www.ieee802.org/11/Reports/tgbf_update.htm
- Espressif, ESP-IDF programming guide, "Wi-Fi Channel State Information":
  https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/wifi.html

CSI extraction tools:

- Halperin, Hu, Sheth, Wetherall, "Tool release: gathering 802.11n traces with channel state
  information", SIGCOMM Computer Communication Review 41(1), 2011.
- Xie, Li, Li, "Precise power delay profiling with commodity WiFi", MobiCom 2015 (Atheros CSI Tool).
- Gringoli, Schulz, Link, Hollick, "Free your CSI: a channel state information extraction platform for
  modern Wi-Fi chipsets", WiNTECH 2019 (Nexmon CSI).

Surveys and models:

- Ma, Zhou, Wang, "WiFi sensing with channel state information: a survey", Computing Surveys
  52(3), article 46, 2019.
- Wang et al. (H. Wang, D. Zhang, …), "Human respiration detection with commodity WiFi devices: do
  user location and body orientation matter?", UbiComp 2016 (Fresnel-zone model).
- Wang, Liu, Shahzad, Ling, Lu, "Understanding and modeling of WiFi signal based human activity
  recognition" (CARM), MobiCom 2015 (CSI-speed model, PCA across subcarrier streams).
- Zhang, Chen, Wang, Liu, "WiSpeed: a statistical electromagnetic approach for device-free indoor speed
  estimation", IEEE Internet of Things Journal 5(3), 2018 (ACF of CSI under motion).
- Zhang et al. (F. Zhang, C. Wu, B. Wang, …, K. J. R. Liu), "WiDetect: robust motion detection with a statistical electromagnetic
  model", Proc. IMWUT 3(3), 2019 (ACF-based motion statistic).
- Qian et al., "Widar: decimeter-level passive tracking via velocity monitoring with
  commodity Wi-Fi", MobiHoc 2017; Qian et al., "Widar2.0: passive human tracking with a single Wi-Fi link", MobiSys 2018; Zheng et
  al., "Zero-effort cross-domain gesture recognition with Wi-Fi" (Widar3.0), MobiSys 2019.
- Qian et al., "Inferring motion direction using commodity Wi-Fi for interactive
  exergames" (WiDance), CHI 2017.
- Kotaru, Joshi, Bharadia, Katti, "SpotFi: decimeter level localization using WiFi", SIGCOMM 2015
  (linear-fit removal of sampling-time offset from CSI phase).
- Li et al., "IndoTrack: device-free indoor human tracking with commodity
  Wi-Fi", Proc. IMWUT 1(3), 2017 (conjugate multiplication across antennas).
- Zeng et al., "FarSense: pushing the range limit of WiFi-based respiration
  sensing with CSI ratio of two antennas", MobiCom 2019.

Statistics and machine learning:

- Hampel, "The influence curve and its role in robust estimation", JASA 69(346), 1974; Pearson,
  "Outliers in process modeling and identification", IEEE Trans. Control Systems Technology 10(1), 2002
  (Hampel filter, MAD scale).
- Pearson, "On lines and planes of closest fit to systems of points in space", 1901; Jolliffe,
  *Principal Component Analysis*, Springer 2002 (PCA).
- Cortes, Vapnik, "Support-vector networks", Machine Learning 20, 1995 (SVM).
- Hadsell, Chopra, LeCun, "Dimensionality reduction by learning an invariant mapping", CVPR 2006
  (contrastive loss).
- Schroff, Kalenichenko, Philbin, "FaceNet: a unified embedding for face recognition and clustering",
  CVPR 2015 (triplet loss).
- Fawcett, "An introduction to ROC analysis", Pattern Recognition Letters 27(8), 2006 (ROC, AUC).

General physics (Parseval's theorem, Doppler shift, wavelength, delay resolution) is textbook
material and is cited as such.

## How the material was read

The internal documents were read in full as text. Only the generic mechanism, the reasoning behind
each design choice, the failure modes, and the direction of each result were carried over. Every
internal number was replaced by a round illustrative value or dropped. The public sources are cited
for mechanisms and for every public number. Where a statement is my own reasoning rather than a
source's, the note says "(my explanation)".

## Public-safety check

Before hand-off the kit was scanned with the repository's public-content scanner
(`tools/public-scan.sh`) and with the generic name check from the kit brief. Both returned no hits.

## Rung 2 — diagrams

`diagrams/` (six pages, see `diagrams/INDEX.md`) was drawn only from this kit's `notes/` (A1, A2, B1–B5,
C1, C2, C5), `glossary.md` and `constants.json`; every on-canvas number is loaded from
`constants.json` and tagged with its key and class. No internal figure was copied, traced or described.

## Rung 3 — explorers

`explorers/` (three single-file HTML pages, see `explorers/INDEX.md`) was built only from this kit's `notes/` (A1,
A2, B1–B4, C1, C5), `glossary.md` and `constants.json`. Every constant is copied verbatim from `constants.json` into
`explorers/params.json` and each page's inline params block. Page-only model choices carry the class `assumption`
and are labelled on each page. All signals are synthetic. No measurement is shown, and no internal figure was copied,
traced or described. One wording issue was reported back: the mean-removed versus un-centred ACF sign convention
in B2 (see `explorers/INDEX.md`).
