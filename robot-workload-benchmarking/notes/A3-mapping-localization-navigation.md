# A3 — Mapping, localization, navigation

**Source:** DISK (arXiv:2006.13566), LightGlue (ICCV 2023, arXiv:2306.13643), MixVPR (WACV 2023, arXiv:2303.02190), Open3D TSDF docs (http://www.open3d.org/docs/), iSAM2 (Kaess et al., IJRR 2012; GTSAM, https://gtsam.org/). · **Status:** concept primer, no measured numbers.

## In one sentence
Mapping and navigation build and reuse a map of the robot's surroundings from keyframes and learned image features, close loops when the robot revisits a place, fuse depth into a 3D volume, and plan paths over it — and the key point for a benchmark is that this work is bursty: busy while mapping or relocalising, near-idle otherwise.

## What it is
This pipeline answers three questions: where is the robot in its map (localization), what does the world look like (mapping), and how does it get to a goal (navigation). It uses several public components:

- **Keyframes** — a subset of camera frames kept as map anchors, chosen when the robot has moved enough.
- **Keypoint detection and description** — **DISK** finds distinctive points in an image and describes each with a vector (arXiv:2006.13566).
- **Learned matching** — **LightGlue** matches keypoints between two images, learning which pairs truly correspond (arXiv:2306.13643).
- **Visual place recognition** — **MixVPR** turns a whole image into one compact descriptor used to recognise a previously seen place (arXiv:2303.02190).
- **Loop closure** — detecting that the robot has returned to a known place, using MixVPR to propose candidates and LightGlue to confirm.
- **Pose-graph optimisation** — **iSAM2** adjusts all past poses so the map stays consistent after a loop closure (Kaess et al., IJRR 2012).
- **Volumetric fusion** — **TSDF fusion** (truncated signed distance function) merges many depth frames into one 3D surface (Open3D).
- **Occupancy / height maps** — a 2D grid of where the robot can and cannot go, derived from depth.
- **Path planning** — searching that grid for a route to a goal.

## How it works
**The mapping loop.** On each keyframe the pipeline runs DISK to get keypoints, matches them to recent keyframes with LightGlue, and fuses the depth into the TSDF volume. When MixVPR flags a candidate loop, LightGlue confirms it and iSAM2 re-optimises the pose graph, which corrects drift across the whole map.

**Localization versus mapping.** When the robot already has a map, it localises against it: recognise the place (MixVPR), match features (DISK + LightGlue), and update its pose. Building a new map additionally fuses depth and extends the graph.

**Navigation.** The occupancy or height map is updated from depth each frame; a planner searches it for a path and replans periodically.

**Why it is bursty.** Keyframes are produced only when the robot moves; a stationary robot adds few. Loop closures happen occasionally. So the pipeline's load swings from near-zero (idle, holding a map) to a short, heavy burst (a keyframe with feature extraction, matching and fusion, or a loop closure with a full graph optimisation). This matters for a benchmark because the average load is misleading: the peak is what competes with the other services.

## How it is measured or used in a benchmark
- **Drive the pipeline into its busy state.** Measuring a stationary robot measures the idle floor, not the cost. The benchmark replays recorded motion (a bag) so that keyframes, matches and fusions actually happen (see [[C3-the-harness-and-fakes]]).
- **Public weights at real shapes.** If the deployed model weights cannot be shipped, the benchmark runs public DISK / LightGlue / MixVPR weights at the same input shapes. The compute is set by the shape, not the weight values, so the cost is representative while the output is not (see [[C0-reference-not-replica]]).
- **Separate idle from working cost.** Report both the idle floor (holding a map) and the per-keyframe and per-loop-closure cost. An average over a window that mixed both is uninformative.
- **Watch fused attention.** LightGlue's cost depends on whether its attention is fused into one kernel or split into separate matrix-multiply and softmax kernels; the profiler's kernel names decide which, and so whether the stage is compute- or memory-bound (see [[B4-profilers-and-the-observer-effect]]).

## Common confusions
- **"Mapping has a steady cost."** It does not; it alternates between idle and heavy bursts, and the burst is what the benchmark must capture.
- **"A stationary test is fine."** A stationary robot produces almost no keyframes, so a static test measures the idle floor only.
- **"Loop closure is cheap because it is rare."** Each loop closure triggers a full pose-graph optimisation, a large momentary cost.
- **"Wrong weights give wrong cost."** For fixed network shapes the compute is weight-independent, so public weights at real shapes give a representative cost (but not a representative map).

## Why it matters for robotics workloads
Mapping and navigation are the stack's bursty tenant. Their peak load competes with the camera and perception for the same GPU and memory controller, so a benchmark that reports only their average will miss the moment when a keyframe burst and a camera frame collide. Driving the pipeline into its busy state, and reporting idle and working costs apart, is what reveals that collision.

## Terms introduced
- **keyframe** — a camera frame kept as a map anchor, chosen when the robot has moved enough.
- **keypoint detection / description** — finding distinctive image points and describing each with a vector (DISK).
- **learned matching** — matching keypoints between images with a trained network (LightGlue).
- **visual place recognition (VPR)** — recognising a previously seen place from a whole-image descriptor (MixVPR).
- **loop closure** — detecting a return to a known place and using it to correct accumulated drift.
- **pose-graph optimisation** — adjusting all past poses for consistency after a loop closure (iSAM2).
- **TSDF fusion** — merging many depth frames into one 3D surface via a truncated signed distance function.
- **occupancy / height map** — a 2D grid of traversable and blocked space derived from depth.
- **bursty workload** — a load that alternates between near-idle and short heavy peaks; its peak, not its average, competes with other services.
- **bag replay** — replaying recorded sensor data so a pipeline does realistic work (see [[C3-the-harness-and-fakes]]).
