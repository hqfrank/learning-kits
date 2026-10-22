# C1 — Predict, then measure

**Source:** roofline method from [[../jetson-orin-thor-metrics/notes/A5-l1-bandwidth-ceiling|the sibling roofline notes]] and [[../nvidia-gpu-anatomy/notes/08-measuring-a-gpu|measuring a GPU]]; general measurement method, abstracted. · **Status:** concept primer, illustrative numbers only.

## In one sentence
Before running anything, the benchmark writes down a compute-budget ledger that predicts each stage's time from first principles — arithmetic over a measured compute rate, bytes over a measured bandwidth, plus CPU overhead — classifies what each stage is bound by, and commits falsifiable predictions, so that the result is the *ratio* of measured to predicted, and the surprises are visible.

## What it is
A **compute-budget ledger** is a table, written before any measurement, with one row per stage of each service. For each stage it predicts the time as

> t = FLOP / R + bytes / B + t_CPU

where FLOP is the stage's arithmetic, R is the measured compute rate for that precision and shape, bytes is the stage's memory traffic, B is the measured memory bandwidth, and t_CPU is the predicted CPU overhead. The compute term and the memory term are reported separately, and the larger one names the **bound class** (compute-bound or memory-bound) unless launch or CPU overhead is predicted to dominate.

## How it works
**Why predict first.** A prediction made before the data cannot be tuned to fit it. The prediction states what the designer believes the hardware will do; the measurement tests that belief. The headline result is the **measured ÷ predicted ratio** — a ratio near 1 confirms the model, a ratio far from 1 points at a mechanism the model missed. The sibling kit's VLA note is exactly this: a first-principles prediction that turned out consistently optimistic, and the gap was the finding ([[../jetson-orin-thor-metrics/notes/C1-pi05-solo-latency|the sibling C1 note]]).

**The roofline frames it.** Each stage sits on a roofline (see [[../jetson-orin-thor-metrics/notes/A5-l1-bandwidth-ceiling|the sibling roofline note]] and [[../nvidia-gpu-anatomy/notes/08-measuring-a-gpu|measuring a GPU]]): its arithmetic intensity (FLOP per byte) decides whether it is capped by the compute roof or the bandwidth roof. The ledger places each stage on that plot and predicts accordingly.

**Why small batch-1 models are launch-bound.** A robot runs most of its networks at batch 1, in real time, one input at a time. A batch-1 model does little arithmetic per launch and re-reads its weights every time, so it rarely saturates the compute roof. Worse, a chain of small kernels spends much of its wall-clock time *between* kernels, while the CPU prepares and launches the next one — this is **launch overhead** (see [[B4-profilers-and-the-observer-effect]]). The ledger therefore predicts that small models will measure far slower than their roofline time, and names launch/latency as their bound class. The gap between the roofline floor and the measured time is itself a result.

**Measured inputs, not guessed ones.** R and B in the formula are measured on the target board (a GEMM rate at the relevant shape, a streaming-bandwidth probe), not taken from a datasheet — the sibling kit's whole lesson is that datasheet peaks are not delivered rates. Any term that cannot be measured yet (an activation-traffic estimate, an un-shippable model's shape) is labelled an estimate with its basis.

**Falsifiable predictions.** Beyond the per-stage times, the ledger commits a short list of named, falsifiable predictions: which resource binds first, which stages are launch-bound, where a model switches from memory- to compute-bound as a batch grows. Each is written with the measurement that would decide it. These are registered before data (see [[C5-experimental-design]]).

## How it is measured or used in a benchmark
- **Write the ledger before the first run.** One row per stage; compute and memory terms separate; a bound class each.
- **Measure R and B on the target.** Use a real GEMM rate at the stage's shape and a streaming-bandwidth probe, not datasheet peaks. Beware zero-operand benchmarks (see [[C7-how-the-bench-can-lie]]).
- **Report measured ÷ predicted.** That ratio, per stage, is the result; a large ratio for a small model is expected and is itself informative.
- **Label every estimated term.** Activation traffic, un-shippable shapes: estimate with a stated basis, not a silent guess.
- **Commit falsifiable predictions.** Name the first-limit resource and the launch-bound stages, each with its deciding measurement, before data.

## Common confusions
- **"The datasheet rate is R."** Delivered rates are well below datasheet peaks; measure R on the board (the sibling A3/A4 notes).
- **"A small model should hit its roofline time."** Batch-1 models are usually launch-bound and measure far slower; the gap is the result.
- **"Predict after measuring to be accurate."** A post-hoc prediction can be tuned to the data and proves nothing; predict first.
- **"Compute and memory can be lumped together."** Reporting them separately is what names the bound class and locates the surprise.

## Why it matters for robotics workloads
Predict-then-measure turns a pile of numbers into a test of understanding. Without a prediction, a measured latency is just a fact; with one, the measured ÷ predicted ratio tells you whether you understand the hardware, and where you do not. For a robot full of small batch-1 models, the prediction also sets the right expectation — launch-bound, not roofline-bound — so the benchmark reads the large gaps as the expected result rather than as an error.

## Terms introduced
- **compute-budget ledger** — a pre-run table predicting each stage's time as FLOP/R + bytes/B + t_CPU.
- **bound class** — compute-, memory-, or launch/latency-bound, named by the larger predicted term.
- **measured ÷ predicted ratio** — the headline result: how far the measurement departs from the first-principles prediction.
- **arithmetic intensity** — FLOP per byte; places a stage on the roofline. Also in [[../jetson-orin-thor-metrics/glossary|the sibling glossary]].
- **launch overhead / launch-bound** — time spent between small kernels while the CPU launches the next; the usual bound for batch-1 models.
- **measured R and B** — the compute rate and bandwidth measured on the target board, not from a datasheet.
- **falsifiable prediction** — a named claim committed before data, with the measurement that would decide it.
