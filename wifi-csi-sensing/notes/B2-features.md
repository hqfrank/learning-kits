# B2 — Features: variance, ACF, PCA, and the frequency domain

**Source:** internal I1 §3.2 (variance vs PCA), I2 (candidate features), I7 (feature comparison, ACF note, DC removal, home-to-home spread), generalised; Zhang et al. 2018 (WiSpeed) and 2019 (WiDetect) for the ACF statistic; Wang et al. 2015 (CARM) for PCA across subcarrier streams; Parseval's theorem (textbook). · **Status:** concept note. Study numbers are illustrative.

## In one sentence
A feature turns a window of clean CSI into a few numbers that separate "motion" from "no motion", and the best features are the ones whose scale does not depend on the room: the self-normalised autocorrelation, PCA eigenvalue structure, and the frequency spectrum with its DC term removed.

## What it is
A **window** is a block of consecutive CSI reports on one link, for example an illustrative 1 s or 4 s (`window_short_illustrative`, `window_long_illustrative`). For a single-stream link with *K* subcarriers and *L* reports, the window is a K × L amplitude matrix. A **feature** is a function of this matrix. The programme compared three families (internal I7):

| Family | Examples | Size | What it captures |
|---|---|---|---|
| time-domain | variance, autocorrelation (ACF) per subcarrier | about K | how much and how fast the amplitude changes |
| subspace | eigenvalues of the K × K covariance | about K | how many independent patterns of change exist |
| frequency-domain | FFT, power spectral density, wavelet (DWT) per subcarrier | about K × L/2 | the spectrum of the amplitude change |

Other candidates were explored and not kept: raw amplitudes, kernel-matrix eigenvalues, the window as an image, spectrograms, and image features such as SIFT (internal I2).

## How it works
**Variance.** A still room gives low variance per subcarrier. Motion near the link gives high variance; motion far from it gives medium variance (internal I2). Variance is simple and cheap. Its problem is scale: the variance of an empty room changes from room to room and from hour to hour. A variance threshold therefore needs calibration per room (internal I1 §3.2).

**Autocorrelation (ACF).** The ACF at lag τ compares the amplitude with a copy of itself shifted by τ reports. A still channel stays similar to its own past, so the short-lag ACF is close to 1. Motion decorrelates the channel, so the ACF falls toward 0. The decay rate grows with the speed of the mover (Zhang et al. 2018, WiSpeed; Zhang et al. 2019, WiDetect).

- The ACF is normalised by construction: it lies between −1 and 1 in every room. This is its main advantage over variance (internal I7).
- The programme averaged the ACF over subcarriers and kept the first ten lags. The first lag was the most discriminative; longer lags added little (internal I7).
- A lag-1 ACF beat variance clearly: an illustrative 0.65 against 0.4 TPR at 1% FPR (`acf_vs_variance_illustrative`).

**Subspace (PCA).** Compute the covariance of the K subcarrier series over the window and its eigenvalues. **PCA (principal component analysis)** orders these eigenvalues by size. If the channel is still, every report is nearly the same vector, the matrix is close to rank 1, and one eigenvalue dominates. Motion adds patterns of change, so energy spreads to the second and later eigenvalues (internal I7; Wang et al. 2015, CARM).

- PCA thresholds were expected to transfer across rooms without calibration, with a tolerance band (a "critical zone") around each threshold (internal I1 §3.2).
- In a single-link comparison, the second eigenvalue did as well as or better than variance, and better than the first eigenvalue (internal I7).

**Frequency domain (FFT).** Take the FFT of each subcarrier's amplitude over the window and concatenate the magnitudes across subcarriers. Two choices made this feature portable across homes (internal I7):

1. **Remove the DC bin.** The DC bin is the window mean. It encodes the static channel: walls, furniture, device placement. It differs in every home. A model that sees it overfits to the training homes.
2. **Remove the highest-frequency bins.** The programme removed an illustrative top third (`fft_high_freq_drop_illustrative`), which was noise-dominated.

**Parseval's link between variance and FFT.** By Parseval's theorem, the variance of a series equals the summed squared FFT magnitudes without the DC bin, up to a normalising factor. Variance is therefore one number computed from the spectrum. The FFT keeps the spectrum's shape, which a classifier can use (internal I7; textbook).

**FFT versus wavelets.** The FFT describes the whole window. If motion fills only part of the window, the FFT dilutes it. A **discrete wavelet transform (DWT)** localises frequency content in time and catches short motion better. The programme explored DWT but kept the FFT for simplicity (internal I7).

## What the studies showed (illustrative)
- **Caution:** single-link, one dataset; numbers illustrative.
- Single features ranked roughly: variance and the best eigenvalue near an illustrative 0.4 TPR at 1% FPR; FFT features with a small neural network near an illustrative 0.6 (`single_feature_tpr_illustrative`). The FFT's advantage was largest at strict false-positive budgets.
- **Caution:** a simple ACF + variance + SVM detector was excellent in some homes and useless in others. In a leave-one-home-out test, the best home reached an illustrative 0.95 TPR and the worst an illustrative 0.05 (`home_spread_illustrative`). In the worst home the motion and no-motion feature distributions overlapped completely (internal I7).
- Lab papers report higher numbers than real homes. Treat a lab number as an upper bound (internal I7; interpretation).

## Common confusions
- **"Variance and FFT are different information."** Variance is a summary of the FFT. The FFT is strictly richer; whether the classifier can use the extra detail depends on data size.
- **"The DC term carries signal."** It carries the room. Removing it is what made features work in unseen homes.
- **"One good home means a good feature."** The spread across homes is the result that matters.
- **"Environment independence means no calibration ever."** Self-normalised features reduce calibration; they do not remove drift (see [[C5-limits-and-open-problems]]).

## Why it matters
A consumer product cannot ask each customer to calibrate each room. The feature, more than the classifier, decides whether a threshold learned in a lab carries over to a home. Pick features whose scale is fixed (ACF), whose structure is relative (eigenvalue ratios), or whose room-specific part is removed (FFT without DC).

## Terms introduced
- **window** — a block of consecutive CSI reports on one link.
- **feature** — a function of a window used as classifier input.
- **variance (CSI)** — the spread of a subcarrier's amplitude over a window.
- **ACF (autocorrelation function)** — the normalised similarity of a series with a lagged copy of itself.
- **ACF tap / lag** — one lag value of the ACF, in reports.
- **PCA (principal component analysis)** — eigen-decomposition of a covariance into ordered components.
- **eigenvalue spread** — how the variance is shared across principal components.
- **FFT feature** — the per-subcarrier spectrum of amplitude over a window.
- **DC bin** — the zero-frequency FFT bin; the window mean.
- **DWT (discrete wavelet transform)** — a transform that localises frequency content in time.
- **Parseval's theorem** — the energy of a series equals the energy of its spectrum.
- **environment-independent feature** — a feature whose decision threshold transfers across rooms.
