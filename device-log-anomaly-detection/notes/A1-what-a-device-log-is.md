# A1 — What a device log is

**Source:** generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)); Android logging architecture (https://source.android.com/docs/core/tests/debug/understanding-logging and https://developer.android.com/tools/logcat); wpa_supplicant control-interface events (https://w1.fi/wpa_supplicant/devel/ctrl_iface_page.html). · **Status:** concept primer.

## In one sentence
A device log is a long stream of short, semi-structured text lines, each with a timestamp, a process and thread, a severity, a component tag, and a free-text message, written by many threads at once into a small buffer that overwrites itself.

## What it is
Each line of a log has a fixed **header** and a free **message**. A common layout, used by Android's `logcat` "threadtime" format, is:

```
<date> <time> <pid> <tid> <level> <tag>: <message>
```

- **pid / tid** — the process ID and thread ID of the writer.
- **level** (severity) — how serious the writer thinks the line is. Android uses V (verbose), D (debug), I (info), W (warning), E (error), F (fatal) (Android logcat documentation).
- **tag** (component) — the name of the software part that wrote the line, for example the Wi-Fi supplicant or a diagnostics service.
- **message** — free text, produced by a print statement in the source code, with run-time values filled in.

A line from the open-source Wi-Fi supplicant (wpa_supplicant) shows the shape of a message:

```
CTRL-EVENT-DISCONNECTED bssid=<mac> reason=3 locally_generated=1
```

The constant words come from the print statement. The values after `=` are **parameters** that change from line to line. The reason value is an IEEE 802.11 reason code; code 3 means the station is leaving and code 2 means the previous authentication is no longer valid (IEEE 802.11 reason-code table, also in wpa_supplicant's `ieee802_11_defs.h`). Splitting constant words from parameters is the job of log parsing ([[B1-log-parsing-to-templates]]).

## How it works
**Many writers, one stream.** Dozens of components write at the same time. Their lines **interleave**: two lines next to each other in the file can come from unrelated threads. Order within one thread is meaningful; order across threads mostly is not ([[B5-from-anomaly-to-root-cause]]).

**Timestamps collide.** The timestamp has a fixed resolution, typically milliseconds. Several lines can carry the same timestamp, from one component or from many. Their true order is then unknown.

**Buffers and overwrite.** On Android-style systems a logging daemon (`logd`) keeps several named buffers in memory: main, system, radio, events, crash, and a kernel buffer (Android logging documentation). Each buffer has a fixed size. When it is full, new lines overwrite the oldest lines. This is a **ring buffer**. At an illustrative 500 000 lines per device-day, a buffer of an illustrative few megabytes holds only hours of history.

**Log types.** Three kinds of output share the mechanism but serve different readers:

- **normal logs** — free-text lines for engineers, from the kernel (`printk`), native code, and applications;
- **metrics** — structured event records sent to the cloud (see [[A2-fleet-metrics]]);
- **counters and timers** — small numeric records of how often or how long something happened.

**Volume and relevance.** Most lines are irrelevant to any one question. For a Wi-Fi question, keeping only the Wi-Fi components can leave an illustrative 1 % of the lines.

## How it is measured or used
**Collection constraints decide what you can analyse.**

- **Upload is selective.** Production devices usually upload logs only on demand (a support request, a user report). A small test population (for example, internal pre-release users) may upload periodically.
- **Retention is short.** Uploaded logs are kept for a limited time (an illustrative 60 days). On-device data may be limited by privacy policy (an illustrative 14 days).
- **The window may be too short.** If a crash ends the log, the lines after the crash do not exist ([[C1-the-ground-truth-problem]]).
- **Formats differ.** Lab test frameworks, local developer captures, and production uploads can use different line formats. A parser built for one may not read the others.
- **Privacy limits content.** A design that never collects user identity, location, browsing history, or IP addresses, offers opt-out, and limits on-device retention is the baseline expectation (see [[C5-from-service-to-tool]]).

## Common confusions
- **"The log is a record of what happened, in order."** It is a record of what each thread *chose to print*, interleaved, with ties in time. Order across threads is not guaranteed.
- **"Error lines are where the fault is."** Error-severity lines are frequent in healthy devices too. A fault often shows as a change in *which* lines appear and *how often* ([[B2-windows-and-count-vectors]]).
- **"The log will be there when we need it."** Ring buffers overwrite, and on-demand collection happens after the fault. Lost evidence is the normal case.
- **"Kernel faults appear in the application log."** A driver crash writes to the kernel buffer. An analysis that reads only the main buffer will not see it.

## Why it matters for fleet operations
Every design choice downstream — what to parse, how to window, what to keep on the device — depends on these properties. A pipeline that assumes ordered, complete, single-format logs will fail on real device logs in quiet ways: missed faults, not errors.

## Terms introduced
- **log line** — one record of a log: header (time, pid, tid, level, tag) plus message.
- **severity (level)** — the writer's label for how serious a line is (verbose to fatal).
- **component (tag)** — the name of the software part that wrote a line.
- **parameter** — a run-time value inside a message, such as a reason code or an address.
- **interleaving** — lines from concurrent threads mixed together in one stream.
- **ring buffer** — a fixed-size buffer in which new entries overwrite the oldest ones.
- **log buffer** — one of the named in-memory stores (main, system, radio, events, crash, kernel) that a logging daemon keeps.
- **reason code** — the IEEE 802.11 number that states why a Wi-Fi association ended.
