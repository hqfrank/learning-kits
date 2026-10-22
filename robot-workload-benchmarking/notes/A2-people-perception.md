# A2 — People perception

**Source:** model papers cited inline (YOLOX arXiv:2107.08430, SCRFD arXiv:2105.04714, ArcFace arXiv:1801.07698, OSNet arXiv:1905.00953, BlazePose arXiv:2006.10204, Light-ASD CVPR 2023); One Euro filter (Casiez et al., CHI 2012). · **Status:** concept primer, illustrative rates only.

## In one sentence
People perception finds and follows the people around the robot through a chain of small neural networks and a lot of CPU post-processing, its cost grows with the number of people N, and the surprising part is that the CPU bookkeeping around the networks often costs more than the GPU inference itself.

## What it is
People perception is a pipeline that, per camera frame, answers: who is in view, where are they in 3D, which face is whose, who is the same person as last frame, and who is speaking. It chains several public models, each doing one job:

- **Person detection** — **YOLOX** draws a box around each person (arXiv:2107.08430).
- **Face detection with landmarks** — **SCRFD** finds each face and five key points (eyes, nose, mouth corners) (arXiv:2105.04714).
- **Face recognition** — **ArcFace** turns a face crop into an embedding, a vector that is close for the same person and far for different people (arXiv:1801.07698).
- **Body re-identification** — **OSNet** turns a body crop into an embedding used to re-identify a person across frames even when the face is hidden (arXiv:1905.00953).
- **2D pose** — **BlazePose** places body joints on each person (arXiv:2006.10204).
- **Active-speaker detection** — **Light-ASD** decides, from lips and audio, who is speaking (CVPR 2023).

## How it works
**Per-frame work.** Detection runs once per frame on the whole image. **Non-maximum suppression (NMS)** then removes overlapping boxes so each person is counted once.

**Per-person work.** Face recognition, re-identification and pose run once per detected person. So the total cost has a fixed per-frame part plus a part that scales with N, the number of people.

**Tracking-by-detection.** The pipeline must keep a stable identity for each person across frames. It predicts where each known track should be next with a **Kalman filter**, then matches this frame's detections to the predicted tracks by solving an assignment problem with the **Hungarian algorithm**. New detections start new tracks; unmatched tracks are aged out.

**Smoothing.** Raw per-frame positions jitter. A **One Euro filter** smooths each tracked quantity with a speed-dependent cut-off, so slow motion is smoothed hard and fast motion is left responsive (Casiez et al., CHI 2012).

**3D projection.** Each 2D detection is lifted to 3D by sampling the depth map (from [[A1-depth-camera-and-odometry]]) at the detection's pixels.

**Why the CPU post-processing can dominate.** The networks run on the GPU and are individually small. But NMS, the Kalman filters, the Hungarian matching, the depth sampling, the coordinate transforms and the One Euro filtering run on the CPU, usually in a scripting language, once per person per frame. On a small robot computer this CPU work frequently exceeds the GPU inference time. The benchmark's job is to show that, not to assume the GPU is the cost.

## How it is measured or used in a benchmark
- **Scale with N.** Run the pipeline at N = 1, 2, 5, 10 people and measure how CPU, GPU and output rate grow. The per-frame part stays flat; the per-person part grows roughly linearly, until a resource caps.
- **Separate per-frame from per-person.** Report the fixed cost and the per-person slope, not one average.
- **Feed N people reliably.** Recorded footage rarely contains a chosen number of people, so the benchmark injects synthetic detections of N moving people, or overwrites the detector's output with ground-truth boxes, so that everything downstream (tracking, projection, filtering) does real work at a controlled N (see [[C3-the-harness-and-fakes]]).
- **Watch for a software rate cap.** Many perception services hold a minimum interval between outputs, so the published rate is a fixed ceiling, not a measure of spare compute. A rate held by a software throttle is not a compute signal (see [[B2-rates-periods-and-latency]]).

## Common confusions
- **"The networks are the cost."** The per-person CPU post-processing (NMS, Kalman, Hungarian, projection, filtering) often costs more than the GPU inference on a small computer.
- **"N people means N× everything."** Only the per-person stages scale with N; detection and NMS of the whole frame are per-frame.
- **"The output rate shows the compute limit."** If the service caps its own rate, the published rate is the cap, and you must look at CPU and latency to see the real limit.
- **"More people detected equals N."** Occlusion means fewer than N people may actually be detected in a crowded frame, so "N" is people in view, not people detected.

## Why it matters for robotics workloads
People perception is the clearest case of the central lesson of robot benchmarking: the headline cost is not the neural network. It is the CPU glue around a chain of networks, and it grows with the scene. A benchmark that measures only GPU-busy will conclude the robot has plenty of headroom while its CPU cores are already full. Getting N right, and separating per-frame from per-person work, is what makes the perception numbers mean anything.

## Terms introduced
- **embedding** — a vector produced by a network such that same-identity inputs are close and different-identity inputs are far.
- **non-maximum suppression (NMS)** — removing overlapping detections so each object is counted once.
- **tracking-by-detection** — keeping stable identities across frames by matching each frame's fresh detections to existing tracks.
- **Kalman filter** — a predictor-corrector that estimates a moving quantity and predicts its next value.
- **Hungarian algorithm** — the optimal solution to the assignment problem; here it matches detections to tracks.
- **One Euro filter** — a speed-dependent low-pass filter: more smoothing when slow, more responsiveness when fast.
- **per-frame vs per-person work** — the fixed cost paid once per frame versus the cost paid once per detected person.
- **active-speaker detection** — deciding from lips and audio which visible person is speaking.
- **N (people in view)** — the number of people the pipeline is processing; the per-person cost scales with it.
