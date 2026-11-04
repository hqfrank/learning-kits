# B3 — Classifiers, train/test splits, and window length

**Source:** internal I2 (classifier survey, split experiment, window combination), I7 (multi-home pipeline, link labelling, window and event-length results), generalised; Cortes and Vapnik 1995 (SVM); Fawcett 2006 (ROC). · **Status:** concept note. Study numbers are illustrative.

## In one sentence
Any classifier from a threshold to a small neural network can separate motion from stillness in the room it was trained in; what decides the real result is how you split train and test data (by time and by home, never at random), how you label each link, and how long a window you wait before you decide.

## What it is
A **classifier** maps a feature vector from one window on one link to a score or a label: motion or no motion, or "near which device". The output of every link is later combined across links ([[B4-multi-device-joint-detection]]).

## How it works
**The classifier ladder.** The programme tried, in rough order of complexity (internal I2, I7):

1. **Threshold** on one feature, for example lag-1 ACF or the second eigenvalue. Cheap and interpretable. The threshold must transfer across rooms (see [[B2-features]]).
2. **Shallow learners** — **support vector machine (SVM)** with an RBF kernel, discriminant analysis, logistic regression, naive Bayes, decision trees, boosting. An SVM finds the boundary with the largest margin between the classes, and a kernel lets that boundary be curved (Cortes and Vapnik 1995). The SVM did best in early small-data tests (internal I2).
3. **Small neural networks** — a multi-layer perceptron (MLP) on concatenated FFT features; for example two hidden layers of an illustrative 128 and 32 units with L2 regularisation (`mlp_hidden_units_illustrative`). This was the model of the multi-home study (internal I7).
4. **Sequence and image models** — RNN/GRU/LSTM on the amplitude series; CNNs on the amplitude matrix or a spectrogram.
   - **Caution:** a window of a few dozen subcarriers by a few dozen reports is tiny compared with a normal CNN image input. Deep models also need far more data than a few days of collection (internal I2).
5. **Ensembles** — one classifier per subcarrier group, then a vote. The idea is to out-vote faulty subcarriers. In the experiment where it was tried, it did not help (internal I2).

**Scoring.** A detector outputs a score; a threshold turns it into a decision. The **ROC curve** plots the true-positive rate (TPR) against the false-positive rate (FPR) as the threshold moves (Fawcett 2006). The programme reported **TPR at a fixed FPR** (for example TPR at 1% FPR) and the **area under the curve (AUC)**. The fixed-FPR number is the honest one for a product, because the product's false-alarm budget fixes the FPR (see [[C1-kpis]]).

**Split by time and by home.** CSI windows close in time are highly correlated. A random split puts near-copies of test windows in the training set.

- **Caution:** in one experiment the same features and classifier scored an illustrative 0.9 accuracy on a random split of three days and an illustrative 0.6 when trained on two days and tested on the third (`split_random_accuracy_illustrative`, `split_heldout_day_accuracy_illustrative`). The day-to-day change of the room (furniture, doors, temperature, humidity) was enough to break the model (internal I2).
- The multi-home study therefore trained on an illustrative 20 homes and tested on 5 unseen homes (`home_study_size_illustrative`). Leave-one-home-out testing showed the home-to-home spread in [[B2-features]].

**Label each link, not each home.** A person in one room affects only the links whose Fresnel zones reach that room. The programme labelled a link window "motion" only if the motion happened in the same room as one of that link's two radios. Windows where the effect was uncertain were left out of training, not labelled "no motion" (internal I7). A wrong negative label teaches the model that real motion is noise.

**Window length and latency.** **Detection latency** is the time from the start of motion to the decision. It is at least the window length plus processing time.

- Doubling the window from an illustrative 4 s to 8 s added only about an illustrative 1 TPR point (`window_4s_vs_8s_gain_illustrative`).
- Deciding on short events cost accuracy: an illustrative 0.9 TPR on 2 s events against 0.95 on 15 s events (`event_length_tpr_illustrative`). A decision within 2–4 s was judged acceptable (internal I7).
- Windows can be combined: a weighted average of recent window scores, concatenated features of several windows, or overlapping (sliding) windows. A sliding window lowers latency at the cost of more computation (internal I2).

## Common confusions
- **"The model is the hard part."** The split and the labels decided the result. A random split reported a number that did not survive one day.
- **"Accuracy is the metric."** The class balance of "motion" and "no motion" windows is arbitrary in a scripted dataset. Report TPR at a fixed FPR.
- **"A longer window is always better."** Past a few seconds the gain is small and the latency cost is large.
- **"Deep learning will generalise better."** With a few days of data from a few homes, a shallow model on good features was as good or better. More homes, not more layers, is the first lever.

## Why it matters
A Wi-Fi sensing result is only as good as its weakest split. Report the held-out-day and held-out-home numbers first; report the random-split number, if at all, as an upper bound. Fix the FPR from the product's false-alarm budget before choosing a model.

## Terms introduced
- **classifier** — a function from a feature vector to a score or label.
- **SVM (support vector machine)** — a maximum-margin classifier; with an RBF kernel its boundary can be curved.
- **MLP (multi-layer perceptron)** — a small fully connected neural network.
- **ensemble vote** — combining several classifiers by majority.
- **ROC curve** — TPR against FPR as the decision threshold moves.
- **TPR at fixed FPR** — the true-positive rate at the threshold that gives a chosen false-positive rate.
- **AUC** — the area under the ROC curve.
- **random / held-out-day / held-out-home split** — test data drawn at random / from an unseen day / from unseen homes.
- **link labelling** — assigning a ground-truth label to each link's window, not to the whole home.
- **detection latency** — the time from the start of an event to the decision.
- **sliding window** — overlapping windows that advance by less than their length.
