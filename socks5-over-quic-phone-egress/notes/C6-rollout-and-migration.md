# C6 — Rollout, migration and rollback

**Source:** internal deployment runbook (per-environment steps, verification, teardown, known issues), deploy-automation design, firewall-migration runbook, task list (delivery slicing, boot and reconfiguration tasks), and the design's rollback section, generalised. · **Status:** concept note; the lessons are the value.

## In one sentence
Ship the tunnel in independently mergeable slices behind a feature flag that defaults to off, make every infrastructure step idempotent and environment-scoped, open the new port only after the listener that guards it runs, roll back in the order flag → front door → firewall, and expect most failures to be silent drops or stale state rather than errors.

## What it is
The tunnel touches five layers: cloud networking (the front door and firewall rules), the instance image (boot script, certificate, kernel settings), the backend service, the provisioning service, and two phone apps. A **rollout** must change all of them across several environments without breaking users who are not in the feature.

## How it works
**Slice the delivery.** The source split the work into change sets that could merge separately (task list, generalised):

1. infrastructure: front-door setup and teardown scripts, permissions, the firewall rule, the boot script (certificate, kernel UDP buffers, host filter), and an infrastructure test script;
2. backend: QUIC server, listener, control stream, config endpoint;
3. provisioning: register each new instance with the front door and store its mapping;
4. and 5. the iOS and Android clients.

The boot script writes `ALL_PROXY` only when a front-door mapping exists, and the mapping exists only after slice 3. Slices can therefore land in any order without an interval in which tools point at a missing listener ([[A1-the-end-to-end-picture]]).

**A feature flag that fails closed.** The config endpoint asks a flag service before it returns "enabled". The flag reader treats a missing flag as "off". Rollout goes from an allowlist of named users, to more users, to everyone, per environment. The flag is also the kill switch ([[C4-observability-without-user-data]]).

**Idempotent, environment-scoped infrastructure.** The infrastructure-as-code tool of the time did not support the front door's custom-routing resources. The team used scripts instead, with three rules (internal runbook, generalised):

- **names carry the environment**, because several environments shared one cloud account; the teardown script uses the same naming, so that it can never delete another environment's front door;
- **every step checks before it acts** and can run twice;
- **every destructive script has a dry run.**

A later change moved front-door creation and flag seeding into the deployment pipeline, skipping when the resource already exists.

**The firewall migration.** The rule for the QUIC port was added to the code that creates a security group. Existing groups never got it, so existing instances silently dropped the front door's packets (firewall runbook, generalised). The migration script:

- requires an environment argument, and rejects anything else;
- selects groups by an environment name pattern; for production it also excludes the other environments' prefixes with an anchored match, so that a broad pattern cannot catch them;
- checks each group for the rule and skips it if present;
- only adds; it never edits or removes;
- has a dry run, prints counts, and documents the exact reverse command.

**Prerequisite:** confirm that the QUIC server listens on at least one instance before you open the port. An open port with no listener is a window with no handshake checks, no rate limits and no logs. The script runs on development, then staging, then production, with a verification query between stages. A later code change made provisioning **reconcile** the rule on every call, treating "already exists" as success; that removed the need for one-off migrations.

**A firewall rule is not the feature.** After the migration, existing instances still had no certificate, no front-door mapping and no environment entries, so the config call kept answering "disabled". The supported path was to **re-provision** each instance with the new image. The source wrote this down so that nobody declares victory after the firewall step.

**Do not lose configuration on rewrite.** A reconfiguration script rewrote the instance environment file from a fixed list of keys, which silently dropped the proxy and certificate entries. The fix re-derives those entries from their sources after each rewrite: the front-door mapping from the parameter store, the fingerprint from the certificate on disk, and the proxy variables as constants gated on the mapping. Re-deriving beats copying, because an operator's later change to the source is picked up (my reading of the source's reasoning).

**Rollback, in order** (internal design, generalised):

| Step | Effect | Restart needed |
|---|---|---|
| 1. turn the flag off | the config call says "disabled"; tunnels end at the next reconnect | no |
| 2. disable the front door | no UDP reaches any instance | no |
| 3. remove the firewall rule | the port is closed at the network edge | no |

Each step is independent, and step 1 is enough in most cases. Rollback does not disrupt the agent: the listener stays up and falls back to direct connections ([[C2-limits-and-failure-handling]]). Front-door teardown also deletes the stored mappings, so instances booted afterwards do not set `ALL_PROXY`; running instances keep it until a reboot, and their listener simply goes direct.

**Lessons the source recorded** (deployment runbook, generalised):

1. **Stop the old instance before re-provisioning.** The front door maps a port per private address; a still-running old instance keeps its mapping, the phone reaches it, and the pin from the new instance fails ([[B4-trust-without-a-ca]]).
2. **One front door per environment.** Two front doors over the same subnets create two sets of mappings; a mapping stored from one and traffic allowed on the other means denied packets.
3. **Silent drops at every gate.** A missing cloud firewall rule, a host accept rule after the final drop, an instance never allowed on the front door, a network that blocks UDP: each looks the same from the phone, a handshake that never completes. Check the gates in order ([[C4-observability-without-user-data]]).
4. **Non-blocking registration hides failures.** Provisioning continues if front-door registration fails, which is correct for availability, but it leaves an instance that silently lacks the feature. Check for the stored mapping after provisioning.
5. **A deploy can update one service and not its sibling.** In one environment the pipeline redeployed the runtime service but not the provisioning service, whose task definition pinned an image digest. Verify the version of every service a feature depends on.
6. **Check the certificate algorithm on a new image** ([[B4-trust-without-a-ca]]).

## How it is measured or used
A post-deployment checklist per environment: the QUIC socket is bound; the listener port is bound; the certificate has an elliptic-curve key; the environment has every proxy and certificate entry; the config call answers "enabled" for an allowlisted user; the front-door mapping is "allow". The source treats any token shown by the config check as a credential and keeps it out of shared logs.

## Common confusions
- **"Feature flags make infrastructure changes safe."** The flag gates behaviour, not the open port. The port needs its own order of operations.
- **"Idempotent means safe."** Idempotent means safe to repeat. Scope (which environment, which groups) is a separate guard.
- **"Rollback means revert the code."** Here rollback is three configuration switches, none of which needs a deployment.
- **"Re-provisioning is a last resort."** For a feature that lives in the boot image, it is the supported path.

## Why it matters for an agent service
A tunnel spans teams' boundaries: networking, images, services, apps. The order of changes, the defaults and the rollback switches are as much part of the design as the protocol.

## Terms introduced
- **rollout** — the staged change of every layer across environments.
- **feature flag** — a runtime switch that enables a feature per user or globally.
- **allowlist (flag mode)** — the flag is on only for named users.
- **idempotent** — safe to run more than once with the same result.
- **dry run** — a mode that reports what a script would change without changing it.
- **reconcile** — bring actual state to the desired state on every run, accepting "already done".
- **re-provision** — replace an instance with a fresh one from the current image.
- **rollback** — undoing a rollout, here by configuration switches.
