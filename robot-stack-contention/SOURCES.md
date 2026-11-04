# Sources — Why a robot software stack runs slower than its parts

This kit teaches a mechanism-by-mechanism diagnosis. It carries no measured numbers from any
specific robot.

## What this kit is

Study notes (rung 1 of the learning kit: notes → diagram → explorer → video) for one question:
**why does each service of a home-robot software stack run slower when the whole stack shares one
small on-board computer, and how do you find the mechanism per service from evidence?**

- **Part A** — CPU-side mechanisms: queueing on a shared core pool, the same work costing more
  cycles, priorities in containers, costs that grow with history, and where to put the observers.
- **Part B** — GPU-side mechanisms: time-slicing between processes and the dose curve, why a low
  issue rate is not free room, MPS in practice, compute-bound versus near the ridge.
- **Part C** — what a bench number means for the deployed robot.

The mechanisms come from public documentation (listed below) and from general benchmarking
practice, as taught in the sibling kit
[`../robot-workload-benchmarking/`](../robot-workload-benchmarking/README.md). **All measurements
in this kit are illustrative round numbers.** They keep the shape of typical findings (which term
is largest, which way a value moves, where a result sits against a pre-registered line), but they
are not data from any specific robot. The investigation is written as one worked case of a generic home-robot stack. Its numbers are illustrative, and its qualitative steps and outcomes are simplified to teach the method. They do not describe any specific product.

The reader is assumed to know the sibling kits and is not re-taught their content:

- [`../nvidia-gpu-anatomy/`](../nvidia-gpu-anatomy/README.md) — SMs, warps, occupancy, CUDA
  contexts and streams, time-slicing, MPS and MIG
  ([note 07](../nvidia-gpu-anatomy/notes/07-sharing-the-gpu.md)).
- [`../jetson-orin-thor-metrics/`](../jetson-orin-thor-metrics/README.md) — the example boards'
  compute and memory ceilings, the roofline and its ridge, co-tenancy interference.
- [`../robot-workload-benchmarking/`](../robot-workload-benchmarking/README.md) — how to benchmark
  a robot stack: run-queue wait, the observer effect, pre-registration, validity gates, bench
  artefacts.

## The three classes of number

Every number in this kit lives in [`constants.json`](constants.json) and is cited by its key. Each
entry carries a `class` field:

1. **public** — taken from a public document; the entry's `source` field is its URL.
2. **sibling** — a value already in a sibling public kit; the `source` field names that kit's
   `constants.json` key. The example-board numbers (SM count, per-SM limits, tensor and DRAM
   ceilings) come from `../jetson-orin-thor-metrics/`.
3. **illustrative** — a round teaching number that keeps the shape of a finding. It is never a
   measurement. The notes call it "illustrative" the first time it appears in each file.

Arithmetic derived from constants is labelled "my estimate from `<key>` and `<key>`".

## Public sources cited

The URLs that carry `public` entries in `constants.json`:

- Linux kernel documentation, Control Group v2, `cpu` controller and `cpu.weight` —
  https://docs.kernel.org/admin-guide/cgroup-v2.html
- NVIDIA Multi-Process Service, Architecture — https://docs.nvidia.com/deploy/mps/architecture.html
- NVIDIA Multi-Process Service, When to use MPS —
  https://docs.nvidia.com/deploy/mps/when-to-use-mps.html
- NVIDIA CUDA for Tegra application note, sections 4.6–4.7 (MPS on Tegra) —
  https://docs.nvidia.com/cuda/cuda-for-tegra-appnote/index.html
- NVIDIA CUDA Programming Guide, technical specifications per compute capability and occupancy —
  https://docs.nvidia.com/cuda/cuda-c-programming-guide/ (reading note: NVIDIA has reorganised the
  guide, and the current base is https://docs.nvidia.com/cuda/cuda-programming-guide/).

Further public documentation that the notes cite for mechanisms only (no numbers):

- Python `asyncio` — https://docs.python.org/3/library/asyncio.html
- Python `logging` — https://docs.python.org/3/library/logging.html
- ROS 2 concepts (topics, logging through `/rosout`) — https://docs.ros.org/en/rolling/Concepts.html

## How it was read

The public values were taken from `constants.json`, where each one carries its URL; the notes
did not re-fetch the documents. The sibling kits were read from their folders in this repository
for terms, links and the sibling constants.
