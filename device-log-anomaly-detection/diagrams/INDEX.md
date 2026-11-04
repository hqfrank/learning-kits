# Diagrams — Finding faults in a device fleet from logs and metrics (Rung 2, learn-diagram)

Six diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. This is the picture
layer for the rung-1 notes: it turns the pipeline (A0), the data (A1, A2), the methods (B1–B5) and
the evaluation (C1, C4) into diagrams. **Every number on every canvas is loaded from this kit's
`../constants.json`** through `Src.v()` in `_common.py` — none is retyped — and carries a tag on the
canvas: `[n]` = public (real value from a cited paper or standard), `[n*]` = illustrative (an invented
round number, never a measurement). Each canvas has its own legend and a sources footnote, built from
the same constants entries as the tags, so the exported image stands alone. A combined 6-page source,
`device-log-anomaly-detection.drawio`, shows all pages at once.

**Public-safety:** the only sources used are this kit's `notes/`, `glossary.md` and `constants.json`
(already anonymised). Subjects are generic ("a device", "the fleet", "the pipeline"); only public
methods, papers and open-source software are named (isolation forest, Drain, Spell, DeepLog, weighted
least squares, Wilson interval, IEEE 802.11 reason codes, wpa_supplicant, logcat). Log lines,
template names, thread IDs and count matrices on the canvases are toy examples, labelled as such.
`learning/tools/public-scan.sh learning/device-log-anomaly-detection` reports clean.

**Rendering:** the drawio MCP was not available, so each page is one cell list in `specNN.py`,
rendered two ways from the same list by `.render_local.py`: an editable `.drawio` (html=1 labels) and
a standalone `.svg` (rect/ellipse + `<foreignObject>` XHTML labels, polylines for edges and chart
lines), rasterised to `.png` by headless Chrome at 2x. Every `.drawio` and `.svg` is validated with
ElementTree. Regenerate: `cd diagrams && python3 .render_local.py spec0*.py`, then rebuild the
combined file by concatenating the `<diagram>` blocks.

| File | Teaches (the finding in the title) | Sources used |
|---|---|---|
| `01-pipeline-cascade` | Metrics choose which logs to read: detect -> fetch + parse -> score + explain -> group + report, a feedback loop from the engineer's root-cause label, and the on-device alternative. | Notes A0, A1, A2, B1–B6, C1, C4; constants lines_per_device_day, ring_buffer_size, on_device_retention, uploaded_log_retention, templates_per_component_set, flagged_windows, windows_scanned, time_per_case_before/after, deeplog_history_h, deeplog_top_g |
| `02-line-to-count-vector` | Parsing and windowing turn free text into a count matrix: each column is a readable template, and order inside a window is lost. | Notes A1, B1, B2, C2; constants templates_per_component_set, ieee80211_reason_deauth_leaving, component_print_statements, component_error_warning_share, miner_templates_found, drain_runtime_improvement, drain_eval_datasets, drain_eval_messages_min, window_example, he2016_fixed_window_default, he2016_sliding_window_default |
| `03-isolation-forest-score` | The isolation-forest score is a normalised path length, not a probability: 3 splits -> 0.82, the average 10.24 splits -> 0.5 (psi = 256). Curve computed from c(256). | Note B3; constants iforest_subsample_size_default, iforest_c_256, iforest_height_limit_psi256, iforest_score_3_splits_psi256, iforest_score_at_average_path, iforest_trees_default, euler_mascheroni, sklearn_iforest_offset_auto |
| `04-fleet-trend-test` | The same 3 % jump can be noise in 100 devices (SE 1.7 pp) but is a fleet change in 10 000 (SE 0.17 pp); WLS weights each day by n, tests the slope against a practical s, scores -10 log10 p, filters direction and false discoveries. | Notes A2, B3, B4; constants small/large_family_devices, rare_reason_devices, rare_share_small/large_family_se, trend_series_length, phred_factor, score_cap, score_examples, monitored_series, multiple_testing_false_alarms, family_reports_per_week |
| `05-anomaly-to-root-cause` | Root cause starts where the sequence leaves the normal path: partition by thread, count transitions, compare with the golden sequence; sequence vs distribution anomaly; output is a hypothesis for an engineer. | Notes A1, B5, C4; constant ieee80211_reason_4way_handshake_timeout; workflow idea from DeepLog §4.4 |
| `06-evaluating-without-labels` | Catching 6 of 10 known faults says "it works", not "it is better": Wilson 95 % interval 31–83 %, reported next to 4 of 10 environmental pilot flags; backward vs forward validation; misses name the missing signals. | Notes C1, C4; constants ground_truth_candidates/usable/detected, detection_rate_wilson95_6of10, detection_rate_wald95_6of10, detection_rate_wilson95_60of100, pilot_tickets, pilot_environmental |

---

## Per-diagram specs (as built)

### 01-pipeline-cascade
```
Teaches: metrics (every device) trigger; logs (on demand) are read only for the devices and days
         the metric points at; four fleet-side stages end in one ticket per fault; an engineer
         decides and the root-cause label feeds back.
Type:    Block / pipeline diagram, with a feedback loop and an on-device vs fleet-side band.
Elements: device [A1]; 1 detect [B4, A2]; 2 fetch + parse [B1, B2]; 3 score + explain [B3, B5];
         4 group + report [B6]; engineer [C4]; feedback -> ground truth [C1] + rules [B4];
         on-device sequence model vs fleet-side cascade [A0, B3, B5].
Colour:  purple device/on-device; blue cloud stages; amber human decision; green dashed feedback;
         dashed purple = logs arrive only on demand.
Numbers: lines/day, ring buffer, retentions, template count, 20 of 50 000 windows, 90 -> 15 min
         (all illustrative); DeepLog h and g (public).
Left out: the statistics of each stage (pages 03, 04, 06).
```

### 02-line-to-count-vector
```
Teaches: line -> template + parameters -> window -> count vector; each column is a template;
         order inside a window is lost.
Type:    Pipeline + index-tree strip + window timeline + toy count matrix.
Elements: raw logcat-style line, template, parameters (reason 3); parse-tree matcher layers and
         unmatched bucket; template sources (mining vs source code; Drain speed); fixed / sliding /
         session windows on a 24 h axis; 5 x 5 toy matrix with an unusual row; order-lost example.
Colour:  grey raw; green templates; amber parameters / sliding windows / design choice; blue index
         and fixed windows; red dashed = information lost or unmatched.
Numbers: 400 templates, 100 statements, 50 %, 20 found, 24 h / 1 h / 0.25 h -> 93 windows
         (illustrative); reason 3, Drain 51.85–81.47 % / 5 data sets / 10 000 000 messages,
         He 2016 window defaults (public). Toy counts are labelled "not data".
Left out: semantic (embedding) features; normalisation details.
```

### 03-isolation-forest-score
```
Teaches: s = 2^(-E(h)/c(psi)); short paths -> near 1 -> anomalous; s = 0.5 at the average path;
         the score is not a probability; contamination is an alarm budget.
Type:    Annotated curve + 2-D isolation sketch + defaults panel.
Elements: curve over E(h) 0..16 for psi = 256; points at 3 splits (0.82) and c(256) = 10.24 (0.5);
         s = 0.5 line; height-limit line at 8; sketch with an outlier isolated by 3 cuts.
Colour:  blue curve; red anomaly square + region; amber 0.5 reference; grey height limit; green
         normal windows.
Numbers: all public (Liu et al. 2008; scikit-learn), the derived ones marked "my arithmetic".
Left out: feature importance (DIFFI, Shapley); sequence models (page 01 band).
```

### 04-fleet-trend-test
```
Teaches: SE of a share shrinks with sqrt(n); WLS weights days by n; test the slope against a
         practical threshold; p -> Phred-style score; direction filter and FDR.
Type:    Error-bar comparison + six-step flow + p -> score staircase + family vs device boxes.
Elements: 3 % share with +/- 1 SE for 100 and 10 000 devices; steps 1–6 of B4; ladder for
         p = 0.1 / 0.01 / 1e-5 / 1e-10; family-level vs device-level detection.
Colour:  red small population; green large; blue estimation steps; amber decision steps.
Numbers: device counts, SEs, 8 weeks / 56 points, cap 100, 10 000 series -> 100 by chance, 1 report
         per week (illustrative); phred factor 10 and the ladder (public).
Left out: attribute- and distribution-based variants (chi-square); autocorrelation fix detail.
```

### 05-anomaly-to-root-cause
```
Teaches: partition by thread before reading transitions; compare with the golden sequence; two
         graph anomalies (missing child, shifted edge probability); output is a hypothesis.
Type:    Stream -> partitions, transition-matrix rule, workflow / state-machine graph, 3-step row.
Elements: 8 toy interleaved lines (two threads, one timestamp tie); partitions; whole-log-sort trap;
         golden path scanning -> associating -> authenticating -> connected; ghost expected child;
         disconnected -> reconnect success (thick) / network bounce (dashed); cascade context,
         departure tools, human step.
Colour:  blue / purple threads; green normal; red dashed anomalies and traps; amber trigger + human.
Numbers: reason code 15 (public). Edge probabilities deliberately shown only as thickness.
Left out: parameter plots; execution replay mechanics.
```

### 06-evaluating-without-labels
```
Teaches: report the detection rate with its interval and beside the false-alarm side; backward
         validation is necessary, not sufficient; misses become the roadmap.
Type:    Funnel + range-bar interval chart + 2 x 2 confusion matrix + pilot strip + 3-step row.
Elements: 60 -> 10 -> 6 cases; Wilson 6/10, Wald 6/10, Wilson 60/100 with the 60 % point; TP/FP/
         FN/TN with formulas; 10 pilot tickets, 4 environmental; backward, forward, misses.
Colour:  green caught / Wilson; grey dashed Wald; blue usable / 100-case / device tickets; red
         dashed environmental false alarms; amber misses.
Numbers: all illustrative counts and their intervals (my arithmetic in constants.json).
Left out: time-ordered cross-validation mechanics beyond one sentence.
```

## Files

Per diagram: `NN-slug.drawio` (editable single page), `NN-slug.svg` (vector, self-rendered),
`NN-slug.png` (2x raster, read back and checked for legibility). `device-log-anomaly-detection.drawio`
is the combined 6-page document. `specNN.py` = the cell list per page; `_common.py` = constants
loader, tag/footnote builder, palette and axes; `.render_local.py` = the renderer.
