# B1 — Preprocessing: outliers, phase, normalisation, subcarrier selection

**Source:** internal I1 §3.1, I2 (preprocessing), I7 (preprocessing chain, impact study, subcarrier selection, grouping, normalisation), generalised; Hampel 1974 and Pearson 2002 (Hampel filter); Kotaru et al. 2015 (SpotFi, linear phase fit); Li et al. 2017 (IndoTrack, conjugate multiplication); Zeng et al. 2019 (FarSense, CSI ratio); IEEE 802.11n/ac (grouping Ng). · **Status:** concept note. Study numbers are illustrative.

## In one sentence
Raw CSI from a commodity chip is not usable as it arrives: you normalise each report's power, remove outliers with a robust filter, sanitise or discard the phase, drop bad subcarriers, and separate the slowly varying background from the motion-induced dynamics, and this chain improved detection more than any change of model did.

## What it is
**Preprocessing** is every step between the raw CSI reports and the feature extractor. Its job is to remove variation that is not caused by people: gain jumps, corrupt reports, phase offsets, noisy subcarriers, and slow environmental drift. The danger is to remove the motion as well.

## How it works
The chain below is the one the programme converged on (internal I7). Each step names the problem it solves.

1. **Power normalisation.** Divide each report by its L2 norm across subcarriers. This removes the per-frame gain jump from AGC (see [[A2-what-the-hardware-gives-you]]). For wide channels, normalise each 20 MHz sub-band first and then normalise once more across the whole band. Skipping the final normalisation cost an illustrative few TPR points in one comparison (internal I7).
2. **Remove known-bad subcarriers.** Drop the guard-adjacent subcarriers and the subcarriers with very low amplitude, which are noise-dominated. In early work a small set of subcarriers showed large variance in an empty room; dropping the highest-variance subcarriers removed them (internal I1 §3.1).
3. **Background estimation.** Estimate the static channel per subcarrier with a moving average.
4. **Dynamics extraction.** Subtract the background from the amplitude. What is left is the dynamic part from [[A1-csi-and-multipath]].
5. **Energy series.** Take the L2 norm of the dynamics per report. This is one number per report.
6. **Outlier detection with a Hampel filter.** For each sample, compute the median and the **median absolute deviation (MAD)** of a window of neighbours. Flag the sample if it is more than *t* scaled MADs from the median. The scale factor is 1.4826 and *t* = 3 is conventional (`hampel_mad_scale`, `hampel_threshold_typical`; Pearson 2002). The programme used a neighbourhood of an illustrative ±10 reports (`hampel_halfwidth_illustrative`).
7. **Outlier replacement.** Replace flagged reports with the window median.
8. **Smoothing (optional).** An exponential moving average acts as a low-pass filter against fast random noise (internal I1 §3.1, I2).

**Why a Hampel filter and not a mean-and-standard-deviation rule.** One outlier inflates the standard deviation and hides itself. The median and the MAD do not move much when a few samples are wild. The filter therefore removes isolated jumps but keeps a sustained change, such as a person walking (my explanation; Hampel 1974).

- **Caution:** running the Hampel filter on the energy series, after power normalisation, removed outliers without removing motion. Running it on raw amplitudes risks treating the start of real motion as an outlier (internal I7; interpretation).

**Do not resample.** Interpolating the CSI to a uniform time grid degraded detection clearly. Compute statistics on the reports as received, with their real timestamps (internal I7).

**Phase sanitisation.** If the chip gives more than one receive antenna, the random offsets in [[A2-what-the-hardware-gives-you]] can be cancelled. Three public methods:

- **linear fit** — fit and subtract a line across subcarriers from the unwrapped phase; this removes the STO slope and the common offset (Kotaru et al. 2015, SpotFi);
- **conjugate multiplication** — multiply the CSI of one antenna by the conjugate of another; the common offsets cancel (Li et al. 2017, IndoTrack);
- **CSI ratio** — divide the CSI of two antennas; the offsets cancel and the result is a well-behaved function of the dynamic path (Zeng et al. 2019, FarSense).

A single-stream link cannot use these methods. The programme's endpoints were single-stream, so it used amplitude only (internal I2, I7).

**Subcarrier selection and grouping.** Fewer subcarriers mean less on-device compute.

| Scheme | Result (internal I7, illustrative) |
|---|---|
| keep all subcarriers | baseline |
| keep the top 10% by mean amplitude (`subcarrier_keep_fraction_illustrative`) | lost an illustrative 4 TPR points and saved about 90% of feature compute (`subcarrier_selection_cost_illustrative`); the best selection rule |
| top 10% (illustrative) by amplitude × variance | worse than amplitude alone |
| top 10% (illustrative) by short-lag ACF | between the two |
| **group** every 4 adjacent subcarriers (an illustrative factor; Ng = 4 is also a public 802.11 value), keep one value per group | no loss against all subcarriers, 4× less data |

The grouping factor 4 matches the grouping parameter Ng that 802.11n/ac already uses for beamforming feedback (`beamforming_grouping_ng`). Grouping works because adjacent subcarriers are strongly correlated; averaging them reduces noise and loses little information (my explanation).

**Noise level drift.** In an empty room the CSI noise level changed in steps over time. A step looks like motion to a variance detector. The programme added three features of the variance time series: its mean, its deviation, and its slope. A noise step raises the mean but stays flat; motion makes the variance fluctuate (internal I7).

## What the studies showed (illustrative)
- **Caution:** event-level results from one multi-home study; the numbers are illustrative.
- Preprocessing raised the average true-positive rate by an illustrative 10 points (`preprocessing_gain_illustrative`).
- The gain was largest in the hardest scenarios: motion in a room with no device, slow or small motion, motion near the AP. There it reached an illustrative 30 points (`preprocessing_gain_illustrative`).
- Easy scenarios (large motion close to a device) gained only a few points, because they were already near the ceiling.

## Common confusions
- **"The model will learn to ignore the noise."** It did not. The hardest scenarios are exactly where noise masks motion, and preprocessing helped them most.
- **"Outlier removal removes motion."** A robust filter on the normalised energy series removes isolated jumps and keeps sustained change. A naive standard-deviation filter on raw amplitude can remove motion onsets.
- **"Interpolating to a uniform grid is harmless clean-up."** It manufactured smooth samples where reports were missing and hurt detection.
- **"Selecting the best subcarriers is free."** Aggressive selection cost a few points. Grouping adjacent subcarriers reduced data with no loss.

## Why it matters
In sensor machine learning the signal chain often matters more than the model. The preprocessing chain is also cheap: every step is a median, a norm, or a moving average, which fits a small device ([[C4-sensing-endpoint-architecture]]).

## Terms introduced
- **preprocessing** — the steps that turn raw CSI reports into clean input for the feature extractor.
- **power normalisation** — dividing each report by its norm to remove gain jumps.
- **background (CSI)** — the slowly varying static channel, estimated by a moving average.
- **dynamics (CSI)** — amplitude minus background; the part caused by motion.
- **Hampel filter** — an outlier filter that compares each sample with the median of its neighbours in units of scaled MAD.
- **MAD (median absolute deviation)** — the median of absolute deviations from the median; a robust spread.
- **exponential moving average (EMA)** — a recursive low-pass filter.
- **phase sanitisation** — removing the random offsets from CSI phase.
- **conjugate multiplication / CSI ratio** — combining two antennas' CSI so that common offsets cancel.
- **subcarrier selection** — keeping a subset of subcarriers.
- **subcarrier grouping (Ng)** — replacing every Ng adjacent subcarriers with one value.
