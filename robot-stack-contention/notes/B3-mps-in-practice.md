# B3 — MPS in practice on Jetson

**Source:** NVIDIA documentation: MPS Architecture (https://docs.nvidia.com/deploy/mps/architecture.html), When to use MPS (https://docs.nvidia.com/deploy/mps/when-to-use-mps.html), CUDA for Tegra application note §4.6–4.7 (https://docs.nvidia.com/cuda/cuda-for-tegra-appnote/index.html); MPS concepts from [`../../nvidia-gpu-anatomy/notes/07-sharing-the-gpu.md`](../../nvidia-gpu-anatomy/notes/07-sharing-the-gpu.md); every number from [`../constants.json`](../constants.json) by key · **Status:** method note. The NVIDIA facts are class `public`. **The probe results are illustrative** (class `illustrative`): round teaching numbers, not measurements.

## In one sentence
MPS works on an Orin-class board for clients of one Linux user and adds no per-launch cost, but suppose the stack runs its GPU services as two Linux users: and under single-user MPS clients of two users stall each other, so MPS needs deployment changes before it can be tried, and its gain for real services is a hypothesis.

## What it measures
**Caution first: every probe result here is from synthetic test kernels.** Each kernel is one block, so it uses one SM; it spins on the GPU clock and moves no memory. The real services were not run under MPS.

**MPS (Multi-Process Service)** lets several processes share one GPU context. Kernels from different processes can then run on different SMs at the same time, instead of taking turns in time slices (see [[B1-gpu-time-slicing-and-the-dose-curve]]). The sibling kits define it in [`../../jetson-orin-thor-metrics/glossary.md`](../../jetson-orin-thor-metrics/glossary.md) and [`../../nvidia-gpu-anatomy/notes/07-sharing-the-gpu.md`](../../nvidia-gpu-anatomy/notes/07-sharing-the-gpu.md).

## How
**Architecture (NVIDIA documentation).** A control daemon starts one server. The server owns a shared GPU context. Each CUDA process connects to it as a client, over UNIX domain sockets, when it first uses CUDA. Kernel launches do not pass through the server. NVIDIA states: "MPS clients submit work directly to the GPU without passing through the MPS server." (`mps_launch_path_quote`). Each client's buffers stay in its own GPU address space.

**Support.** MPS is supported on Tegra Linux since CUDA 12.5 (`mps_tegra_since`).

**The probe.** The board is idle. The steps are:

1. One client alone.
2. Two clients without MPS.
3. Start the control daemon.
4. One client, then two clients, under MPS.
5. One client with `CUDA_MPS_ACTIVE_THREAD_PERCENTAGE` set (`mps_thread_percentage_env`).
6. A client inside a stack container next to a client on the host, first as a different Linux user, then as the daemon's user.

Analogy: without MPS the cooks take turns at the whole stove; with MPS each cook gets burners at the same time, but all the cooks must belong to one family.

## Predicted
This expectation was not pre-registered. Without MPS, two one-SM clients should each get about half the GPU time, because contexts time-slice. Under MPS, each should run as fast as alone, because one SM each leaves room for the other.

## Measured
| Result | Value | Key |
|---|---|---|
| Busy fraction per client, two one-SM clients, without MPS / with MPS | 0.5 / 1.0 (illustrative) | `mps_probe_busy_frac` |
| SMs visible to a client with a 25 % thread cap | 4 of 16 (illustrative) | `mps_cap_visible_sms` |
| Per-launch cost, MPS minus no MPS | 0 µs (illustrative) | `launch_overhead_us` (`mps_difference`) |
| Empty kernel, launch and synchronise each time | 10 µs (illustrative) | `launch_overhead_us` (`sync_each`) |
| Empty kernel, queued launches | 2 µs (illustrative) | `launch_overhead_us` (`queued`) |
| Client of a second user next to a client of the daemon's user, under MPS | both hung until the daemon was stopped | — |

The 4 of 16 is what a 25 % cap gives on the 16-SM board (`sm_count_orin`).

## The gap, and what it means
**The probe behaves as predicted.** Time-slicing halves each client without MPS. MPS runs the two clients side by side (illustrative, `mps_probe_busy_frac`). These kernels use one SM each, so they overlap fully. Kernels that fill the GPU would still share SMs (see [[B2-low-issue-rate-is-not-free-room]]).

**Limits on Tegra (NVIDIA documentation).**

- Not supported on Tegra: `-multiuser-server`; GPU compute modes; under MPS, CUDA IPC, cooperative launches and the MPS client-termination control command (`mps_tegra_unsupported`).
- Dynamic parallelism is not supported under MPS on any platform (`mps_dynamic_parallelism`).

**The catch for the stack is Linux users.** This is single-user MPS. NVIDIA describes it this way: the control daemon runs one server per Linux user at a time, and other users' clients are queued (`mps_one_user`). In the probe's last step, clients of two users stalled each other. Suppose the stack runs its services as two Linux users, and its GPU services are split between the two. As deployed, MPS would therefore likely stall them rather than share the GPU, which is worse than time-slicing. This was not tested with the services themselves.

**A fault reaches every client.** A fatal GPU fault in one client is reported to all clients on the GPU. A client that is killed without synchronising its GPU work can leave the server and the other clients in an undefined state.

**Is a stack process ready for MPS?**

- **Code: yes.** The CUDA driver library attaches a process as an MPS client when `CUDA_MPS_PIPE_DIRECTORY` points to a running daemon, and runs it as usual otherwise. The probe ran unchanged both ways, also inside a stack container.
- **Libraries: not verified.** Search the stack's own code for CUDA IPC, cooperative-launch or EGLStream calls. The camera SDK, TensorRT, PyTorch and ONNX Runtime were not checked.
- **Deployment: not ready.** Four changes are necessary:
  1. One Linux user for all GPU services.
  2. The daemon's pipe directory mounted, and `CUDA_MPS_PIPE_DIRECTORY` set, in every GPU container.
  3. The daemon started before the GPU services.
  4. Fault handling in the stack's service supervision.

**The gain is a hypothesis.** About half the kernel time already fills the SMs (illustrative, `kernel_time_sms_full_share`; see [[B2-low-issue-rate-is-not-free-room]]). So MPS mainly lets the other process start sooner, as SM resources free up, rather than adding throughput. Under MPS, SM contention between processes appears for the first time: part of today's slice wait may become SM wait. The deciding test is the depth camera service, the object detector and the VLA, run without MPS, with MPS, and with the VLA capped at two SM fractions. Success means the detector's blocked time next to the VLA falls and no library fails. This test was not run.

**The SM cap is an MPS feature, not an alternative to MPS.** Today the VLA in effect gets a share of GPU time. Under MPS a cap would give it a share of SMs instead.

## So what
On Jetson, MPS is cheap per launch and needs no code change, but it is a deployment decision: one Linux user, one daemon, and a plan for faults (interpretation). Test it with the real services before counting on its gain. The sibling kit shows what an SM cap does for a control loop next to a VLA: [`../../jetson-orin-thor-metrics/notes/L4-scheduling-ladder.md`](../../jetson-orin-thor-metrics/notes/L4-scheduling-ladder.md).

## Terms introduced
- **MPS (Multi-Process Service)** — lets several processes share one GPU context, with an optional per-client SM cap. Reused from `../jetson-orin-thor-metrics/glossary.md`.
- **MPS control daemon / server / client** — the process that starts servers; the process that owns the shared context; a CUDA process attached to the server.
- **single-user MPS** — the Tegra mode in which one server serves one Linux user; clients of other users are queued.
- **SM reservation / cap** — `CUDA_MPS_ACTIVE_THREAD_PERCENTAGE`, limiting an MPS client to a fraction of the SMs. Reused from `../jetson-orin-thor-metrics/glossary.md`.
- **`CUDA_MPS_PIPE_DIRECTORY`** — the environment variable that points a client to the daemon's UNIX sockets.
- **launch and synchronise round trip** — the time to launch one kernel and wait for it to finish; for an empty kernel it is pure overhead.
