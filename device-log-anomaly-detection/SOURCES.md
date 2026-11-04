# Sources — Finding faults in a device fleet from logs and metrics

This kit teaches a general method. It carries no measured numbers from any specific company, product, or fleet.

## What this kit is

Study notes (rung 1 of a four-rung learning kit: notes → diagram → explorer → video) for one question: **how do you find faults in a fleet of connected consumer devices from their logs and metrics, and explain them well enough for an engineer to act?** Part A describes the problem and the data, Part B the methods, and Part C what makes the result trustworthy.

## Provenance of the method

The pipeline, the design trade-offs, the evaluation method, and the lessons are abstracted from **internal design documents of a device-health programme, 2023–2025**, that the author studied: system designs, research plans, evaluation write-ups, a data-quality audit, a user survey, and a tool design. **No internal material is reproduced here:** no measured number, no name of a company, product, team, programme, tool, or person, no identifier, path, or host, and no figure. Notes that draw on this material say "generalised from internal design documents" and state only the generic idea. Figures for later rungs are to be drawn fresh from the mechanisms in the notes.

## Number classes

Every number in this kit is one of two classes, recorded per entry in [`constants.json`](constants.json):

1. **public** — a real value from a cited public paper, standard, or documentation, with the section given.
2. **illustrative** — a round number of a realistic order of magnitude, invented to explain an idea. It is labelled "illustrative" in the prose and is never a measurement. Values derived from illustrative inputs are also illustrative and say "my arithmetic".

Derived values from public formulas (for example, *c*(256) ≈ 10.24 for the isolation forest) are labelled "my arithmetic" and keep class public.

## Public sources

| Topic | Source | Used in |
|---|---|---|
| Isolation forest: score, *c*(*n*), defaults ψ = 256, *t* = 100 | Liu, Ting, Zhou, "Isolation Forest", ICDM 2008, https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf | B3 |
| Isolation forest implementation and defaults | scikit-learn `IsolationForest`, https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html | B3 |
| Drain: fixed-depth parse tree, similarity threshold, runtime result | He, Zhu, Zheng, Lyu, ICWS 2017, https://jiemingzhu.github.io/pub/pjhe_icws2017.pdf | B1, C2 |
| Spell: longest-common-subsequence streaming parser | Du & Li, ICDM 2016 | B1 |
| DeepLog: LSTM next-key model, top-*g*, defaults, workflow diagnosis, HDFS statistics | Du, Li, Zheng, Srikumar, CCS 2017, https://nlp.cs.utah.edu/assets/pdfs/du2017deeplog.pdf | B3, B5, C1 |
| LogAnomaly: template embeddings, sequential + quantitative patterns | Meng et al., IJCAI 2019 | B3 |
| Windows, event count vectors, HDFS/BGL label counts, default windows, findings | He, Zhu, He, Lyu, ISSRE 2016, https://jiemingzhu.github.io/pub/slhe_issre2016.pdf | B2, B3, C1 |
| Public log data sets (sizes, spans) | Loghub, https://github.com/logpai/loghub | B3, constants |
| Weighted least squares; sample proportion SE; Wilson interval | NIST/SEMATECH e-Handbook of Statistical Methods §4.1.4.3, §7.2.4, §7.2.4.1; Wilson, JASA 1927 | A2, B4, C1 |
| Phred-style score −10·log₁₀ *p* | Ewing & Green, Genome Research 8:186–194, 1998 | B4 |
| False discovery rate | Benjamini & Hochberg, JRSS B 57:289–300, 1995 | B4 |
| Gower similarity for mixed data | Gower, Biometrics 27:857–871, 1971 | B6 |
| Hierarchical clustering | scikit-learn clustering guide, https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering | B6 |
| Isolation-forest feature importance (DIFFI) | Carletti, Terzi, Susto, arXiv:2007.11117, 2020 | B3 |
| Android logging (logd, buffers, logcat format, levels) | https://source.android.com/docs/core/tests/debug/understanding-logging; https://developer.android.com/tools/logcat | A1 |
| wpa_supplicant control events (CTRL-EVENT-DISCONNECTED) | https://w1.fi/wpa_supplicant/devel/ctrl_iface_page.html | A1, B1 |
| IEEE 802.11 reason codes; TKIP deprecation | IEEE Std 802.11 (reason-code table; 802.11-2012 deprecates TKIP); wpa_supplicant `ieee802_11_defs.h` | A1, B5, C4 |
| Data-quality dimensions | Wang & Strong, J. Manag. Inf. Syst. 12(4), 1996 | C3 |

## How the sources were read

- Internal documents: read in full as text, for mechanisms and trade-offs only. Every number met there was replaced by an illustrative value of the same order of magnitude, chosen so that it does not equal the internal value where that was practical.
- Public papers: Drain, DeepLog, the ISSRE 2016 experience report, and the isolation-forest paper were downloaded as PDFs and read with `pdftotext`; each cited number was checked against the extracted text. The scikit-learn page and the Loghub table were read online.

## Conventions

- "my arithmetic" marks a value computed from cited or illustrative inputs.
- "my interpretation" or "my note" marks a claim the sources do not make.
- "generalised" marks an idea taken from the internal material and restated generically.

## Rung 2 — diagrams

[`diagrams/`](diagrams/INDEX.md) holds six diagrams drawn fresh from the notes: A0, A1, A2, B1–B6, C1, C2 and C4. Every number on a canvas is loaded from `constants.json` (tag `[n]` = public, `[n*]` = illustrative). No other source was used.

## Rung 3 — explorers

[`explorers/`](explorers/INDEX.md) holds three single-file HTML explorers: an isolation forest on 2-D count vectors (B2, B3), the fleet trend test with WLS vs OLS and p → score (A2, B4), and log windowing (B2). Every constant is copied from `constants.json` into `explorers/params.json` and the inline blocks. The count-vector data and the daily series are simulated on the page with fixed seeds, and are illustrative. Modelling choices that the notes do not make are labelled "my model", "my assumption" or "my estimate" on the page: the Poisson count model, the 1/rank template mix, the extra-noise factor φ, and the expected-count delay rule. No other source was used.
