# -*- coding: utf-8 -*-
# 05 — Metric-collection map (B0-B4): each metric, the source it is read from, grouped into
#      CPU / GPU+memory / rates+latency / profilers, with a 'pitfall' tag on each.
# Source: notes B0 (CPU), B1 (GPU/power/memory), B2 (rates/latency), B3 (deadlines/stats), B4 (profilers).

PAGE = dict(name="05-metric-collection-map", w=1360, h=680)

CPUC = "#dae8fc"; CPUC_S = "#6c8ebf"
GPUC = "#d5e8d4"; GPUC_S = "#82b366"
RATEC = "#ffe6cc"; RATEC_S = "#d79b00"
PROFC = "#e1d5e7"; PROFC_S = "#9673a6"
NOTE = "#f5f5f5"; NOTE_S = "#999999"
SRC = "#fff2cc"; SRC_S = "#d6b656"

def metric(id, x, y, w, h, fill, stroke, name, source, pitfall):
    return dict(id=id, x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, font=10,
                align="left", valign="top",
                label="%s\nsource: %s\npitfall: %s" % (name, source, pitfall))

BOXES = [
    dict(id="title", x=20, y=12, w=1320, h=30, rounded=False, align="center", valign="middle",
         bold=True, font=15, fill=NOTE, stroke=NOTE,
         label="Every metric has a source it is read from and a pitfall that misreads it - four groups, read all four or the result lies"),
]

# ---- GROUP 1: CPU (B0) ----
G1X = 30
BOXES.append(dict(id="g1", x=G1X, y=64, w=320, h=26, rounded=False, bold=True, font=12,
                  fill=CPUC, stroke=CPUC_S, label="CPU  (B0)"))
BOXES += [
    metric("m_cgroup", G1X, 96, 320, 70, CPUC, CPUC_S,
           "CPU usage in CORES", "cgroup cpu.stat (time / window)",
           "convert to cores, not %, to compare across machines"),
    metric("m_throttle", G1X, 172, 320, 78, CPUC, CPUC_S,
           "quota throttling", "cgroup cpu.max, cpu.stat (nr_throttled, throttled_usec)",
           "throttled_usec is SUMMED over run-queues, NOT unmet demand - report fraction of throttled periods"),
    metric("m_percore", G1X, 256, 320, 64, CPUC, CPUC_S,
           "per-core busy", "/proc/stat",
           "pool near 100% busy = CPU is the limit"),
    metric("m_rq", G1X, 326, 320, 64, CPUC, CPUC_S,
           "run-queue wait", "/proc/schedstat",
           "rising wait (not GPU-busy) is the CPU-bound signature"),
    metric("m_load", G1X, 396, 320, 60, CPUC, CPUC_S,
           "load average", "kernel loadavg",
           "counts runnable+waiting incl. spikes; pair with per-core busy"),
    metric("m_census", G1X, 462, 320, 64, CPUC, CPUC_S,
           "foreign-CPU census", "per-window process list",
           "> ~0.3 cores foreign => window suspect [foreign_cpu_gate_illustrative]"),
]

# ---- GROUP 2: GPU + MEMORY (B1) ----
G2X = 370
BOXES.append(dict(id="g2", x=G2X, y=64, w=320, h=26, rounded=False, bold=True, font=12,
                  fill=GPUC, stroke=GPUC_S, label="GPU + MEMORY  (B1)"))
BOXES += [
    metric("m_gr3d", G2X, 96, 320, 70, GPUC, GPUC_S,
           "GPU-busy (GR3D %)", "tegrastats GR3D",
           "TIME a kernel ran, NOT occupancy; calibrate vs kernel-time trace"),
    metric("m_smi", G2X, 172, 320, 64, GPUC, GPUC_S,
           "utilization.gpu", "nvidia-smi",
           "also a time fraction; can read below true busy - calibrate"),
    metric("m_emc", G2X, 242, 320, 70, GPUC, GPUC_S,
           "memory-controller index (EMC %)", "tegrastats EMC",
           "integer RELATIVE to current mem clock, not GB/s; lock the clock"),
    metric("m_rails", G2X, 318, 320, 60, GPUC, GPUC_S,
           "power rails", "tegrastats rails",
           "coarse steps; GPU+SoC may share a rail - no sub-step claims"),
    metric("m_mem", G2X, 384, 320, 78, GPUC, GPUC_S,
           "memory: MemAvailable / cgroup / nvmap", "/proc/meminfo, memory.current, nvmap",
           "do NOT sum cgroup + GPU mem (overlap/uncharged); use MemAvailable as the honest total"),
    metric("m_clk", G2X, 468, 320, 58, GPUC, GPUC_S,
           "clock lock", "GPU + mem clock regime",
           "verify lock at BOTH window ends or the counters are incomparable"),
]

# ---- GROUP 3: RATES + LATENCY + STATS (B2, B3) ----
G3X = 710
BOXES.append(dict(id="g3", x=G3X, y=64, w=320, h=26, rounded=False, bold=True, font=12,
                  fill=RATEC, stroke=RATEC_S, label="RATES + LATENCY + STATS  (B2, B3)"))
BOXES += [
    metric("m_rate", G3X, 96, 320, 64, RATEC, RATEC_S,
           "topic rate + period p50/p95/p99", "topic probes (msg timestamps)",
           "a SOFTWARE-capped rate is a ceiling, not a compute limit"),
    metric("m_stamp", G3X, 166, 320, 70, RATEC, RATEC_S,
           "receive-time vs header-stamp latency", "subscriber clock vs sender stamp",
           "mixing bases silently adds the clock offset to every number"),
    metric("m_offset", G3X, 242, 320, 70, RATEC, RATEC_S,
           "cross-machine clock offset", "SNTP probe (several/sec)",
           "bound must be < smallest latency measured [clock_offset_target_illustrative]"),
    metric("m_clockfree", G3X, 318, 320, 60, RATEC, RATEC_S,
           "clock-free latency", "two arrivals on the SAME machine",
           "the primary latency when the offset bound is too large"),
    metric("m_miss", G3X, 384, 320, 72, RATEC, RATEC_S,
           "deadline misses/min + p99 tail", "per-cycle times (control loop)",
           "Garwood Poisson interval; tails not means; block bootstrap for autocorrelation"),
    metric("m_samples", G3X, 462, 320, 64, RATEC, RATEC_S,
           "sample-count rule", "window length from B3",
           "too few samples => p99 noisy => flag the window, do not trust"),
]

# ---- GROUP 4: PROFILERS (B4) ----
G4X = 1050
BOXES.append(dict(id="g4", x=G4X, y=64, w=280, h=26, rounded=False, bold=True, font=12,
                  fill=PROFC, stroke=PROFC_S, label="PROFILERS  (B4)"))
BOXES += [
    metric("m_tegra", G4X, 96, 280, 60, PROFC, PROFC_S,
           "tegrastats", "periodic one-line summary",
           "cheap/coarse; duty + power only"),
    metric("m_nsys", G4X, 162, 280, 86, PROFC, PROFC_S,
           "Nsight Systems (timeline)", "kernel + API timeline",
           "MED intrusion: adds ~ms latency [nsys_perturbation_illustrative]; KPIs from UNTRACED windows only"),
    metric("m_ncu", G4X, 254, 280, 86, PROFC, PROFC_S,
           "Nsight Compute (counters)", "per-kernel hardware counters",
           "HIGH intrusion: serialises + replays kernels; take STRUCTURE not wall-times; never beside control loop"),
    metric("m_union", G4X, 346, 280, 64, PROFC, PROFC_S,
           "union of kernel intervals", "nsys timeline",
           "the true GPU-busy to CALIBRATE the coarse GR3D counter"),
    metric("m_safety", G4X, 416, 280, 72, PROFC, PROFC_S,
           "profiler safety", "privileged container",
           "min privilege, logged, time-bounded; NEVER next to the control loop"),
]

# legend + sources
BOXES += [
    dict(id="legend", x=30, y=556, w=640, h=96, rounded=False, align="left", valign="top",
         font=11, fill=NOTE, stroke=NOTE_S,
         label="Legend\nFour colour groups = four metric families: blue CPU, green GPU+memory, amber rates+latency+stats, purple profilers.\nEvery card carries: the metric name, the SOURCE it is read from, and the PITFALL that misreads it.\nRule: the headline KPIs (rates, latencies, misses) come from UNTRACED windows; profilers run in separate,\nlabelled trace-only windows for MECHANISM, never for a KPI (B4)."),
    dict(id="src", x=690, y=556, w=640, h=96, rounded=False, align="left", valign="top",
         font=9, fill=SRC, stroke=SRC_S,
         label="Source: B0 (cgroup cpu.stat/cpu.max, /proc/stat, /proc/schedstat, loadavg, foreign-CPU census); "
               "B1 (tegrastats GR3D/EMC/rails, nvidia-smi, MemAvailable /proc/meminfo, cgroup memory.current, nvmap, clock lock); "
               "B2 (topic rate + period percentiles, receive vs header stamp, SNTP offset RFC 4330, clock-free latency); "
               "B3 (misses/min Garwood Poisson interval, p99 tails, sample-count rule, moving-block bootstrap); "
               "B4 (tegrastats / Nsight Systems / Nsight Compute, union of kernel intervals, profiler safety). "
               "Illustrative thresholds from constants.json as tagged. No measured robot numbers."),
]

EDGES = []
