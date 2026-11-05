# C3 — The two client stacks

**Source:** internal design (phone clients), Android transport follow-up design (library survey, build, JNI plan, fallback), phone-side tunnel-manager, SOCKS5-handler and pinning implementations, generalised; Apple Network.framework documentation (`NWConnectionGroup`, `NWMultiplexGroup`, `NWProtocolQUIC.Options`, `NWParameters.multipathServiceType`); msquic documentation (API table, `QUIC_CONNECTION_EVENT_PEER_STREAM_STARTED`, MIT licence); RFC 9000 §9 (migration). · **Status:** concept note.

## In one sentence
On iOS the operating system's own QUIC stack does everything the design needs, including accepting server-opened streams and migrating between networks; on Android no packaged library did, so the team cross-compiled an open-source C QUIC library, wrote a thin native bridge, and kept a protocol change in reserve in case that library proved unstable.

## What it is
Both phone apps run the same three pieces:

- a **tunnel manager** that fetches the config, connects, sends the control hello, and reconnects with backoff ([[B5-the-control-stream]], [[C2-limits-and-failure-handling]]);
- a **certificate pinner** that hashes the server's leaf certificate and compares it with the pin ([[B4-trust-without-a-ca]]);
- a **per-stream SOCKS5 handler** that negotiates, resolves, filters, connects and relays ([[B1-socks5-in-ten-minutes]], [[C1-threat-model]]).

The hard requirement is the reverse stream pattern: the **phone is the QUIC client, but the server opens the streams** ([[B3-who-dials-whom]]). Many client libraries do not expose that.

## How it works
**iOS: the native stack.** Apple's Network.framework provides QUIC directly. The mapping (Apple documentation; internal implementation, generalised):

| Need | Network.framework feature |
|---|---|
| one QUIC connection with many streams | `NWConnectionGroup` over an `NWMultiplexGroup` |
| ALPN and stream limits | `NWProtocolQUIC.Options` (ALPN list; initial bidirectional stream limit) |
| TLS 1.3 only, custom trust | the security options: minimum version TLS 1.3; a verify block that calls the pinner |
| server-initiated streams | the group's new-connection handler, which hands each incoming stream to a new SOCKS5 handler |
| the control stream | extracting a new outgoing stream from the group |
| migration from Wi-Fi to cellular | `multipathServiceType = .handover` on the parameters |

Three implementation details carry lessons:

- **Name resolution blocks.** The handler calls the system resolver (`getaddrinfo`), a blocking call, on a background thread. It then connects to the exact address it filtered ([[C1-threat-model]]).
- **Every wait has a timeout.** The TCP connect to the destination races a timer (an illustrative 8 s, `phone_connect_timeout_illustrative`).
- **Callbacks must resume once.** The async wrappers around state callbacks guard against resuming the same continuation twice, because a state handler can fire more than once.

iOS suspends an app's network activity soon after it leaves the foreground. The tunnel therefore lives only while the chat is in the foreground. The app stops it on background and restarts it on foreground.

**Android: choosing a library.** The team surveyed about a dozen QUIC libraries (an illustrative 12, `android_libraries_surveyed_illustrative`) against four requirements: server-initiated bidirectional streams, a usable binding from Kotlin or Java, a licence compatible with a closed-source app, and a working Android build. The rejections fell into four groups (internal survey, generalised):

| Group | Why rejected |
|---|---|
| HTTP/3-only client libraries | they expose request streams that the client opens; no raw server-initiated streams |
| a pure-Java library with streams | copyleft licence |
| Rust and C libraries with good stream support | no Java binding and no Android packaging |
| a Java networking framework with a native core | no prebuilt Android native library; the native build was not tested on Android |

**The choice: msquic with a custom native bridge.** msquic is an open-source C implementation under the MIT licence. Its API is a flat table of about twenty functions. It delivers each server-opened stream as a `PEER_STREAM_STARTED` connection event (msquic documentation). Its build system supports the Android NDK with CMake. The work was (internal design, generalised):

1. Cross-compile the library for 64-bit ARM devices and for x86-64 emulators, with TLS statically linked, so each ABI ships one shared library of a few megabytes (an illustrative 4 MB, `native_lib_size_illustrative`).
2. Patch the library's export list to expose the function that DER-encodes a certificate, because the pinner needs the DER bytes.
3. Write a small JNI layer: open and close, registration, configuration with ALPN and credentials, connection and stream calls, and upcalls from C callbacks to Kotlin.
4. Wrap it in a coroutine-friendly Kotlin client behind a transport interface. The SOCKS5 handler works on any input and output stream, so it does not know which transport it runs on.
5. Commit the prebuilt libraries and rebuild them only on a version change; add code-shrinker keep rules for the native methods.

**Accepted risk.** The library's maintainers do not officially support Android: their CI builds it but runs no Android runtime tests. The team accepted this because the protocol surface it uses is narrow (one client connection, server-opened streams, stream reads and writes) and a reference prototype had used the same pattern.

**The reserve plan: invert the protocol.** If the native library proved unstable, the phone could open every stream itself. The server would ask for one over the control stream ("I need a connection"), and the phone would open a client-initiated stream and run SOCKS5 on it. Any client-only library would then work. The cost is one more signal before each proxied connection, plus coordinated changes on the server and on iOS (internal design, generalised).

**Migration on each platform.** On iOS the handover service type makes the stack move the connection to the new interface and validate the new path. On Android the library supports migration in the protocol, but the source marked it as unverified on Android. The fallback is the normal one: the idle timeout ends the dead connection, and the phone reconnects with backoff ([[C2-limits-and-failure-handling]]).

## How it is measured or used
**Migration testing** has three levels (internal test plans, generalised):

1. **Loopback simulation:** rebind the client's UDP socket to a new local port during a relay; the connection and the relay must survive with no data loss.
2. **Network toggle on a device or emulator:** turn the network off and on; the tunnel must go disconnected → connecting → connected, and proxied requests must work afterwards.
3. **Real handover:** move a phone from Wi-Fi to cellular during a transfer; on iOS the transfer should continue; on Android, record whether it migrated or reconnected.

**Android-specific checks:** the native library loads on a real 64-bit ARM device; server-opened streams reach the Kotlin handler; the state flow emits the expected sequence; a connection to an unreachable documentation address times out to "failed".

## Common confusions
- **"Any QUIC client library will do."** The reverse stream pattern rules many out.
- **"HTTP/3 support means QUIC stream support."** An HTTP/3 client exposes requests, not raw streams.
- **"Native code means a large app."** With TLS statically linked and symbols stripped, each ABI added a few megabytes.
- **"Migration works because the protocol supports it."** It works when the platform rebinds sockets and the library handles it; test it per platform.

## Why it matters for an agent service
The phone is the half of the system you control least: two operating systems, many network types, background rules. Keeping the SOCKS5 logic transport-agnostic and the transport behind an interface made a library swap, or the protocol inversion, a contained change.

## Terms introduced
- **tunnel manager** — the phone component that owns the QUIC connection's life cycle.
- **reverse stream pattern** — the client dials the connection, the server opens the streams.
- **JNI (Java Native Interface)** — the bridge between Kotlin/Java code and native C code on Android.
- **ABI (application binary interface)** — a processor and calling-convention target for native code, for example 64-bit ARM.
- **NDK** — the Android Native Development Kit for building native libraries.
- **protocol inversion** — the reserve design in which the phone opens every stream on the server's request.
- **handover (iOS)** — the multipath service type that moves a connection to a new interface when the current one fails.
