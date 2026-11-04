# B1 — Reference and baseline before anything else

**Source:** generalised from internal methodology notes, 2026 (§3.1; checklist steps 2 and 6). Comparison hardware (L40S, A10G, CPU) is named as in the brief; no device result is reproduced. · **Status:** concept note.

## In one sentence
Before the first optimization, fix the inputs and their randomness, compute a trusted output on a different stack, collect at least two legitimate-but-different outputs to calibrate "equivalent", and benchmark the baseline across devices so the new platform's number has context.

## What it is
Four artefacts exist before any candidate is written.

- **Frozen inputs.** A small fixed set of real inputs (in the first campaign, an illustrative `c1_frozen_inputs_illustrative` = 10 recorded robot observations) and fixed randomness. For a diffusion model the randomness is the initial noise; it is stored and reused, so two runs of the same model see the same noise.
- **Trusted reference.** The output of the unmodified model on a different, simpler stack, at full precision (here: CPU at 32-bit floating point). It answers "what is the right answer for these inputs?".
- **Legitimate-noise references.** Outputs of implementations that are correct but not bit-identical: the same model at reduced precision on the CPU, and the unmodified model on the target device. They answer "how far apart can two correct answers be?".
- **Cross-device baseline.** The same protocol run on other hardware (for example an L40S GPU, an A10G GPU and a CPU), so a number on the new platform can be read against known platforms.

## How it works
The reference and the legitimate-noise references together define **equivalent**: a candidate's output is equivalent if it is no further from the trusted reference than a legitimate implementation is. This turns "is it still correct?" into a measurement.

- **Why a different stack.** A reference computed on the device under test shares that device's bugs. A CPU reference does not.
- **Why at least two legitimate-noise references.** One legitimate implementation gives one distance. A limit set from one distance is a guess about the spread. Two or more give a spread to calibrate from (see [[B2-the-frozen-evaluator]] and [[C4-lessons-about-the-method]], lesson 1).
- **Why fixed randomness.** A diffusion model run twice with different noise gives two different correct answers. With fixed noise, any difference comes from the implementation.
- **Why stage-wise outputs.** The first campaign stored the output of every model stage (vision, language, each denoising step), not only the final action. A stage-wise comparison localises a fault to one stage.

## How it is used in a campaign
- The baseline is reproduced **through the evaluator** and recorded as the first evidence record (checklist step 6, [[C5-the-checklist]]).
- The first **profile** runs on the baseline, and its result reorders the plan (see [[C4-lessons-about-the-method]], lesson 4).
- In the scheduling topic the same roles exist in another form: the "input" is a workload file and a seed list, the "reference" is the set of deadlines and completion rules, and the baseline is a FIFO scheduler with shortest-execution placement ([[C2-the-scheduling-topic]]).

## Common confusions
- **"The reference is the baseline."** They differ. The reference defines correct output; the baseline defines the speed to beat. In the first campaign the reference ran on a CPU and the baseline on the accelerator.
- **"Random test inputs are fine."** Real inputs matter. The first campaign found that random inputs changed the device's power behaviour and slowed stand-alone profiles (lesson 2 in [[C4-lessons-about-the-method]]).
- **"Cross-device numbers predict the target."** They give context. A published peak or another device's latency is not a latency prediction for the new device.

## Why it matters
Without a reference, the first wrong-but-fast candidate is accepted. Without a calibration source, the limit for "equivalent" is a guess, and a guessed limit is either too tight (it rejects correct work) or too loose (it accepts broken work).

## Terms introduced
- **frozen inputs** — a fixed input set with fixed randomness, used by every run.
- **trusted reference** — the full-precision output of the unmodified system on a different stack.
- **legitimate-noise reference** — the output of a correct but not bit-identical implementation, used to calibrate limits.
- **equivalent** — no further from the trusted reference than legitimate implementations are, per calibrated limit.
- **cross-device baseline** — the same protocol on other hardware, for context.
- **stage-wise comparison** — comparing every intermediate stage's output with the reference, not only the final output.
