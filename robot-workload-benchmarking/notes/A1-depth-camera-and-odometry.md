# A1 — Depth camera and odometry

**Source:** Stereolabs ZED SDK documentation (https://www.stereolabs.com/docs/); NVIDIA Video Codec SDK (https://developer.nvidia.com/video-codec-sdk). · **Status:** concept primer, illustrative rates only.

## In one sentence
The depth-camera service is the robot's eyes: it turns a stereo image pair into a depth map and a point cloud, tracks the robot's own motion (visual-inertial odometry), and optionally encodes video to send away — and it is heavy on CPU, GPU and memory all at once, so its frame rate is a good single health signal.

## What it is
A stereo depth camera has two image sensors a known distance apart. Software compares the two views, finds where each point appears in both, and from the difference (the disparity) computes distance. The outputs are:

- a **depth map** — one distance value per pixel;
- a **point cloud** — the depth map projected into 3D points;
- **visual-inertial odometry (VIO)** — an estimate of how the camera (and so the robot) has moved, from the image stream plus an inertial measurement unit (IMU).

A ZED-class stereo camera (Stereolabs) provides all three through its SDK.

## How it works
**Stereo depth, classic versus neural.** Classic stereo matches image patches along scan-lines and is cheap but noisy at edges and textureless surfaces. Neural stereo depth runs a convolutional network that learns to fill those gaps; it is far more accurate and runs on the GPU. The ZED SDK offers a neural depth mode that is the common choice on robots. Neural depth is the camera service's largest single GPU cost.

**The pipeline per frame.** For each captured frame the service: rectifies the two images (removes lens distortion), runs depth, optionally retrieves the colour image, optionally builds the point cloud, updates VIO, and publishes the results on topics (`/camera/depth`, `/camera/rgb`, an odometry topic). The IMU is read at a much higher rate than the camera (hundreds of Hz) and feeds VIO between frames.

**Video encode and streaming.** To send video to an operator or a recorder, the service encodes frames to H.264 using the GPU's dedicated video encoder (NVENC). Encode does not use the main GPU compute units, but it does use memory bandwidth and a separate hardware block. Streaming (WebRTC) adds CPU work for packetisation and congestion control.

**Why it is heavy on every resource.** The camera service reads large images (CPU and memory-copy work), runs neural depth and VIO (GPU), moves whole frames between CPU and GPU memory (bandwidth), and may encode and stream (NVENC plus CPU). On an integrated SoC all of this shares one memory controller.

## How it is measured or used in a benchmark
- **Frame rate as a health signal.** If the camera service cannot keep its configured frame rate (an illustrative 30 Hz), something is overloaded. A single number — published depth frames per second — catches many problems at once.
- **Demand-gated work is a trap.** Much of the camera service's cost only happens when someone subscribes. Depth and VIO usually run every frame regardless, but colour retrieval, the point cloud, video encode, and streaming run only when a consumer is attached. A benchmark that attaches no consumers measures a **lower bound** on the camera's cost. To measure the real cost, attach stand-in consumers that subscribe to the same topics the deployed robot subscribes to (see [[C3-the-harness-and-fakes]]).
- **The real camera runs the real SDK.** The depth and VIO networks are inside a closed SDK, so the benchmark runs the real SDK on recorded or live video rather than trying to reproduce it.

## Common confusions
- **"No subscriber, no cost."** Depth and VIO typically run every frame whether or not anyone reads them; only the extra outputs are demand-gated. Measuring with no subscribers understates the cost.
- **"Encode uses the GPU, so it shows up in GPU-busy."** Hardware video encode runs on a separate NVENC block, not the compute units, so it does not appear in the usual GPU-busy metric; it shows up in memory bandwidth and a separate encoder counter.
- **"Depth is just one number per pixel, so it is cheap."** Neural depth is a full network inference per frame and is usually the service's largest GPU cost.

## Why it matters for robotics workloads
The camera service is the widest single load in the stack: it touches CPU, GPU compute, the video encoder, and memory bandwidth together. If a benchmark gets the camera wrong — wrong resolution, no subscribers, no streaming — every downstream number is wrong too, because the camera feeds navigation, mapping and perception. It is also the clearest example of demand-gated work, which [[C3-the-harness-and-fakes]] returns to.

## Terms introduced
- **stereo depth** — distance per pixel computed from the disparity between two camera views a known distance apart.
- **disparity** — the pixel shift of the same point between the left and right images; it is inversely proportional to distance.
- **neural / classic stereo depth** — depth from a learned network (accurate, GPU-heavy) versus from patch matching (cheap, noisier).
- **depth map** — an image whose pixels are distances.
- **point cloud** — the depth map projected into 3D points.
- **visual-inertial odometry (VIO)** — an estimate of the camera's own motion from the image stream plus an inertial sensor.
- **inertial measurement unit (IMU)** — a sensor reporting acceleration and rotation rate, read at hundreds of Hz.
- **NVENC** — the GPU's dedicated hardware video encoder, separate from the compute units.
- **demand-gated work** — processing a service does only when a consumer subscribes to its output.
- **rectification** — removing lens distortion and aligning the two images so matching runs along straight scan-lines.
