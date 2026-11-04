# Diagrams — Wi-Fi sensing with channel state information (Rung 2, learn-diagram)

Six diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. They are the picture layer
for the rung-1 notes: the signal (Part A), the processing chain (Part B) and the KPI framing (Part C).
Every number on every canvas is **loaded from this kit's `constants.json`** by `_common.py` (never
retyped) and carries an on-canvas tag `[n]` that the canvas's own footnote block maps to its
`constants.json` key, its class (public / ILLUSTRATIVE) and its source. Derived values (the Nyquist
limit, N x N link count, false windows per month, budget FPR, orders of magnitude) are computed in
the spec from those constants and labelled "my arithmetic", as in the notes. Each canvas has its own
legend and sources block, so an exported image stands alone. `wifi-csi-sensing.drawio` is the
combined 6-page document.

**Public-safety:** the only sources are this kit's `notes/`, `glossary.md` and `constants.json`, which
are already anonymised. No figure from any internal document was copied, traced or described; each
diagram is drawn fresh from the mechanism in the notes. Subjects are generic ("a home", "the AP",
"a device"); internal documents appear only as the generic tags I1–I7 inside `constants.json` source
strings. Illustrative numbers are marked ILLUSTRATIVE on the canvas and are never presented as
measurements. The folder was checked with `learning/tools/public-scan.sh` before hand-off.

**Rendering:** same pipeline as `../../robot-workload-benchmarking/diagrams/`. Each page is a cell list
in `specNN.py`; `.render_local.py` (a copy of that kit's renderer, extended with ellipses, free lines
above or under boxes, and arrowless edges) writes the editable `.drawio` and a self-rendered `.svg`
(foreignObject XHTML labels, no draw.io "Text is not SVG" banner), validated with ElementTree, then
rasterised to `.png` with headless Chrome at 2x. Every PNG was read back and checked for clipping and
overlaps. Regenerate one page with `python3 .render_local.py specNN.py` (run from this folder).

| File | Teaches (the finding in the title) | Sources used |
|---|---|---|
| `01-csi-vs-rssi` | CSI keeps the per-subcarrier fingerprint that RSSI averages away, and a moving body changes only the dynamic paths. | Note A1 (OFDM, CSI vs RSSI, H(f) as a sum of paths, static/dynamic paths, Doppler, Nyquist caution), A2; `constants.json` ofdm_subcarrier_spacing_11a_n_ac, used_subcarriers_legacy_20MHz, used_subcarriers_ht_20MHz, mimo_2x2_streams, wavelength_2g4, wavelength_5g, doppler_walk_example_5g, csi_rate_beacon_illustrative |
| `02-single-link-sensitivity` | One link sees motion best near its two radios, less mid-link, and almost nothing a few metres off the line of sight or behind a wall. | Note A1 (Fresnel zones, the three single-link patterns, range, wall), B4, C5; `constants.json` single_link_range_illustrative, small_motion_range_illustrative, link_length_illustrative, fresnel_first_zone_mid_radius_example |
| `03-processing-chain` | The signal chain moved the result more than the model did: cheap preprocessing, room-independent features, then any small classifier. | Notes B1 (eight-step chain, Hampel, grouping, selection, no resampling, phase), B2 (ACF, PCA, FFT without DC), B3 (classifier ladder, splits); `constants.json` hampel_threshold_typical, hampel_mad_scale, hampel_halfwidth_illustrative, window_short/long_illustrative, fft_high_freq_drop_illustrative, mlp_hidden_units_illustrative, beamforming_grouping_ng, subcarrier_keep_fraction_illustrative, subcarrier_selection_cost_illustrative, preprocessing_gain_illustrative, acf_vs_variance_illustrative, single_feature_tpr_illustrative, split_random/heldout_day_accuracy_illustrative, home_spread_illustrative |
| `04-joint-detection` | One link cannot tell AP-side from device-side motion; compare links across devices, and add device-to-device links because links grow as N x N. | Note B4 (softAP links, cross-correlation rule, sorted nodes and links, through-wall false positives, device-count result); `constants.json` home_study_size_illustrative, devices_tpr_illustrative, motion_type_tpr_illustrative |
| `05-room-metric-learning` | Learn "same room vs different room" once from many homes; a new home then needs one calibration walk, not a new model. | Note B5 (metric learning, triplet/contrastive loss, Siamese network, calibration walk, nearest neighbour with an "unknown" threshold), B3 (room labelling), C5 (drift); `constants.json` triplet_margin_facenet |
| `06-false-alarm-budget` | "1% FPR" is about 26 000 false alarms per home per month; a budget of 4 needs a per-window FPR near 1.5 x 10⁻⁶, so fix the budget first. | Note C1 (four-stage KPI ladder, six KPIs, false-alarm arithmetic, time to detect/clear, per-scenario breakdown, field shortfall), B3, C2; `constants.json` window_short_illustrative, seconds_per_30_days, false_alarm_budget_illustrative, field_tpr_vs_target_illustrative |

---

## Per-diagram specs (as built)

### 01-csi-vs-rssi
```
Teaches: CSI = one complex value per subcarrier per antenna pair per frame; RSSI = one power number.
         Motion changes only H_dynamic, so the per-subcarrier shape changes while RSSI barely moves.
Type:    Block diagram (room from above: AP, receiver, LoS, static wall reflection, dynamic body
         reflection) + side-by-side output panels (schematic |H| bars before/after vs two RSSI boxes).
Elements: H(f) = sum_i a_i exp(-j 2 pi f tau_i) = static + dynamic [A1]; timing panel.
Numbers: 312.5 kHz spacing; 52 / 56 used subcarriers at 20 MHz; 2x2 -> 4 antenna pairs; 12.3 / 5.5 cm;
         up to ~36 Hz Doppler at 1 m/s, 5 GHz (public, arithmetic); beacon CSI 10 Hz (illustrative)
         -> nothing above 5 Hz representable (my arithmetic).
Colour:  blue radios, red/red dashed dynamic, grey static, purple model, green CSI, amber RSSI/caveat.
Left out: phase offsets and chip differences (A2); Fresnel geometry (diagram 02). Bars are a shape, no data.
```

### 02-single-link-sensitivity
```
Teaches: sensitivity is highest near either radio, lower mid-link on the LoS, falls steeply outside the
         first Fresnel zone, and a wall removes most of the effect.
Type:    Annotated geometry: link with nested Fresnel ellipses, example targets A-D, illustrative
         detectable band, wall; side panels with the three patterns and the r1 formula.
Numbers: walking ~4 m, hand-waving ~3 m from the LoS (illustrative); r1 = 0.5 sqrt(lambda d) for an
         illustrative 4 m link: 0.23 m at 5 GHz, 0.35 m at 2.4 GHz (public arithmetic).
Colour:  target fill red = large change, amber = smaller, grey = weak, dashed white = behind wall.
Left out: Doppler (diagram 01); the multi-link fix (diagram 04).
```

### 03-processing-chain
```
Teaches: the preprocessing chain and room-independent features matter more than the model.
Type:    Two-row pipeline (8 preprocessing steps; window -> 3 features -> classifier -> per-link score)
         + four design-choice cards + two evidence panels.
Numbers: Hampel 3 x 1.4826 MAD (public), +/-10 reports, windows 1 / 4 s, top third of FFT bins dropped,
         MLP 128 + 32, Ng = 4 (public grouping values 1/2/4), top 10 % subcarriers -> -4 TPR points / 90 %
         compute saved, preprocessing +10 / +30 points, variance 0.4 vs ACF 0.65 vs FFT+net 0.6,
         random split 0.9 vs unseen day 0.6, best home 0.95 vs worst 0.05 (all illustrative unless noted).
Colour:  blue preprocessing, green features/evidence, purple classifier, amber output, red traps.
Left out: noise-level-drift features and DWT (B1, B2 prose); joint fusion (diagram 04).
```

### 04-joint-detection
```
Teaches: cross-correlation across devices separates AP-side from device-side motion; device-to-device
         links (softAP) grow the link graph to N x N and help more than adding AP links.
Type:    Floor-plan topology (4 rooms, AP, 4 devices; AP links solid, D2D dashed) + decision-rule rows
         + sorted-node text + bar staircase.
Numbers: 4 devices -> 4 AP links -> 16 directed links (my arithmetic); TPR at 1 % FPR 0.5 / 0.75 / 0.95;
         by scenario 0.95 / 0.6 / 0.4 (illustrative).
Colour:  blue AP links, green devices + D2D links, red example motions, amber through-wall caveat.
Left out: deployment-type models and learned fusion alternatives (B4 prose).
```

### 05-room-metric-learning
```
Teaches: train an embedding once on many homes, calibrate a new home with one walk, answer by nearest
         reference embedding, and say "unknown" when everything is far.
Type:    Three-column flow (train / calibrate / infer) + schematic embedding space.
Numbers: FaceNet triplet margin 0.2 (public). The note gives no result numbers (proposed method).
Colour:  purple training, blue calibration, green inference, amber drift caveat, red design reason.
Left out: network-option trade-offs beyond one line; training curves (none in the source).
```

### 06-false-alarm-budget
```
Teaches: convert the per-window FPR into false alarms per home per month before choosing a model; the
         research "1 % FPR" is ~3.8 orders of magnitude from an illustrative product budget.
Type:    Log-scale ladder (per-window FPR with false-alarms-per-month ticks) + KPI ladder grid
         (motion/presence x home/room) + KPI, timing and field panels.
Numbers: 2 592 000 s per 30 days (public); 1 s window, 4 false alarms per month, field 0.5 vs target 0.9
         (illustrative); 25 920 false windows at 1 % FPR, budget FPR ~1.5e-6 (my arithmetic).
Colour:  red research point / shortfall, green budget, stage fills = increasing difficulty.
Left out: the scenario taxonomy itself (C2), which only appears as the list of reporting rows.
```

## Not diagrammed (candidates for a later pass)
Mesh-AP co-existence 2 x 2 test (C3), the layered on-device architecture and start/stop flows (C4),
band and chipset comparison (A2), and the open-problems list (C5).
