# B4 — Trust without a certificate authority

**Source:** internal design (boot-time certificate generation, control-channel API, transport security, certificate lifetime and rotation), deployment runbook (certificate-algorithm issue), and the phone-side pinning implementation, generalised; RFC 8446 (TLS 1.3, alerts), RFC 9001 §4.8 and §8.1 (QUIC-TLS errors and ALPN), RFC 7301 (ALPN), RFC 9000 §20.1 (error codes), FIPS 180-4 (SHA-256). · **Status:** concept note.

## In one sentence
Each cloud instance makes its own self-signed ECDSA P-256 certificate at first boot, the phone learns that certificate's SHA-256 fingerprint over the already-authenticated HTTPS control channel, and the phone accepts the QUIC handshake only if the presented certificate has exactly that fingerprint and the server agrees on the private ALPN value.

## What it is
A TLS client normally trusts a server because a **certificate authority (CA)** signed the server's certificate for a host name. That does not fit here. The phone connects to an anycast address and a port, not to a host name, and every instance is a separate endpoint created at boot. A public CA needs a domain name per instance. A private CA needs its root distributed to every phone and a signing service.

**Certificate pinning** replaces the CA. The client is told in advance exactly which certificate to accept, by its **fingerprint**: the SHA-256 hash of the certificate's DER encoding (32 bytes, 64 hex characters, `sha256_digest`). Any other certificate fails, even a validly signed one.

The pin needs a trusted delivery channel. Here it is the **control channel**: the phone's existing HTTPS API session, authenticated by the user's login and protected by ordinary web PKI. Trust in the QUIC tunnel is therefore rooted in trust the app already has.

## How it works
**At first boot** (internal design, generalised):

1. The boot script pre-creates the key file with owner-only permissions (mode 600), then writes a fresh ECDSA P-256 private key into it. Pre-creating the file avoids a moment when the key exists with the wrong owner or mode.
2. It makes a self-signed X.509 certificate with a long validity (an illustrative 5 years, `cert_validity_illustrative`).
3. It computes the SHA-256 fingerprint and stores the certificate path, key path and fingerprint in the instance environment.
4. If a certificate and key already exist, for example on a re-attached data volume, it reuses them and recomputes the fingerprint.

The key pair is new. It is not derived from any other identity on the instance. The binding between "this certificate" and "this user's instance" comes only from the control channel.

**At every tunnel start:**

1. The phone calls the config endpoint and receives the front-door address, the port, the fingerprint, the ALPN value and a single-use token ([[B5-the-control-stream]]).
2. The phone starts the QUIC handshake. Its TLS **verify callback** extracts the leaf certificate's DER bytes, hashes them, and compares the hash with the pin. It normalises the pin first: it drops a `sha256:` prefix, colons and spaces, and compares hex case-insensitively.
3. A mismatch fails the handshake. The phone moves to the "failed" state.

The phone never caches the fingerprint. It fetches the config before every connection attempt, so a new certificate is picked up on the next reconnect.

**ALPN as a protocol gate.** **ALPN** (application-layer protocol negotiation, RFC 7301) lets the client name the protocol it wants inside the TLS handshake. QUIC requires it (RFC 9001 §8.1). The design uses a private value, `socks5-over-quic`. The server accepts no other value. A scanner that probes the port with an ordinary HTTP/3 client offers `h3` and gets the TLS alert `no_application_protocol` (alert 120, `tls_alert_no_application_protocol`). QUIC carries a TLS alert as a `CRYPTO_ERROR` code: `0x0100` plus the alert number (`quic_crypto_error_base`, RFC 9000 §20.1). The close code is therefore `0x0178` (my arithmetic, `quic_close_codes_example`). ALPN is not a secret. It stops protocol confusion and casual probing; it does not authenticate anyone.

**The algorithm lesson.** The first certificates used Ed25519. The handshake from the phone's native QUIC stack (Apple Network.framework) failed with close code `0x0128` (internal deployment runbook). That code decodes as `CRYPTO_ERROR` plus alert 40, `handshake_failure` (my arithmetic from `quic_crypto_error_base` and `tls_alert_handshake_failure`). The source concluded that this TLS stack did not accept Ed25519 server certificates for QUIC, and moved to ECDSA P-256. Decoding the close code is the fastest way to tell a TLS problem from a network problem (my explanation).

**Rotation, compromise and rollback** (internal design, generalised):

- **Rotation is implicit.** A replaced instance boots with a new key, or reuses the old one if its data volume survived. The phone follows either way, because it fetches the pin each time.
- **No revocation.** If a key leaks, the response is to replace the instance. The old fingerprint stops matching anything the config endpoint returns.
- **Long-lived instances never rotate.** The source accepts this for single-user instances and lists a periodic rotation job as later work.
- **Stale front-door mapping fails closed.** If an old instance is still running when its replacement is provisioned, the old port mapping can still deliver the phone to the old instance. The phone then sees the old certificate and the new pin, and refuses. The operational fix is to stop the old instance first ([[C6-rollout-and-migration]]).

**What the pin does not prove.** The pin authenticates the server to the phone. It says nothing about the phone. The server authenticates the phone with the single-use token on the control stream ([[B5-the-control-stream]]). Client certificates (mutual TLS) are later work.

**An accepted risk.** The private key file is readable by every process running as the instance's service user, including agent tools. A manipulated tool could copy it. The source accepts this under its single-user trust model and lists a separate service user for the QUIC server as a hardening step ([[C1-threat-model]]).

## How it is measured or used
- **Unit tests:** matching fingerprint passes; different fingerprint fails; empty pin fails; upper-case and lower-case hex both pass.
- **Integration test:** start the server with certificate A and pin A: success. Restart with certificate B and keep pin A: the handshake fails.
- **End-to-end negative test:** tamper with the fingerprint in the config response; the phone must reach "failed", not "connected", and no proxied traffic may flow.
- **Deployment check:** inspect the certificate's public-key algorithm on a new instance and expect an elliptic-curve key.

## Common confusions
- **"Self-signed means insecure."** A self-signed certificate with a pin delivered over a trusted channel is stronger than CA trust for this one connection, because no other CA-signed certificate can substitute for it.
- **"ALPN authenticates the client."** ALPN is a public label. It filters protocol mismatches only.
- **"Pinning the public key and pinning the certificate are the same."** Pinning the whole certificate fails on any re-issue, even with the same key. Here every re-issue comes with a new pin, so the stricter form costs nothing.
- **"The fingerprint is a secret."** It is not. Knowing it does not let anyone impersonate the server without the private key.

## Why it matters for an agent service
The design adds no PKI, no signing service and no domain names, and still gives the phone a precise yes/no answer about the server. It works because the app already has one trusted channel. The general pattern (my explanation): when two endpoints already share an authenticated channel, use it to deliver a pin for the second channel instead of building a second trust system.

## Terms introduced
- **certificate authority (CA)** — an issuer whose signature a client trusts to bind a key to a name.
- **certificate pinning** — accepting only a certificate (or key) known in advance.
- **fingerprint** — the SHA-256 hash of a certificate's DER encoding.
- **self-signed certificate** — a certificate signed by its own key.
- **ECDSA P-256** — the elliptic-curve signature algorithm on the NIST P-256 curve.
- **verify callback** — a hook in a TLS stack where the application decides whether to trust the peer's certificate.
- **ALPN** — the TLS extension that negotiates the application protocol; here a private protocol gate.
- **CRYPTO_ERROR** — the QUIC error range `0x0100`–`0x01ff` that carries a TLS alert number.
- **mutual TLS** — TLS in which the client also presents a certificate.
