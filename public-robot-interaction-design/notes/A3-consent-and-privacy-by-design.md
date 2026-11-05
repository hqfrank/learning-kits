# A3 — Consent and privacy by design

**Source:** internal experience-design documents I1, I3 (see [`../SOURCES.md`](../SOURCES.md)); GDPR (Regulation (EU) 2016/679) Art. 4(11), 6, 7, 8, 9; WCAG 2.2. · **Status:** concept primer; this note describes design patterns, not legal advice. Numbers are public or labelled illustrative.

## In one sentence
Separate speaking from listening: the robot may greet anyone, but it opens its microphone only after a visible, revocable visitor action, shows "listening" exactly while it captures, keeps nothing after the visit, and gives everyone, including people who cannot or will not speak, the same reward.

## What it is
**Consent** in GDPR terms is a "freely given, specific, informed and unambiguous indication" of the person's wishes, by a statement or a clear affirmative action (Art. 4(11)). It is one lawful basis among several (Art. 6(1)(a)). It must be as easy to withdraw as to give (Art. 7(3)). Biometric data used to identify a person uniquely is a special category (Art. 9). A child's own consent to online services is valid from 16 by default, and member states may lower that to 13 (`gdpr_child_consent_age_default`, `gdpr_child_consent_age_floor`, Art. 8). Some jurisdictions also require all parties to agree before a conversation is recorded. A public robot that hears people meets all of these at once.

**Privacy by design** means the system's structure makes the privacy promise true, rather than a policy document asserting it.

## How it works

### Speak first, listen on consent
The chosen entry mechanism decouples the two halves:

- The robot **speaks first**: it looks up, waves and greets. This is output and needs no consent.
- The microphone opens only on a **consent action**. All consent sources feed one audio gate:
  1. **answering the robot** after it greets you (the primary path);
  2. a stand-local **wake phrase** (a shortcut for people who know it);
  3. an **operator console** trigger (always available);
  4. a **physical button** (off by default; for noisy venues and accessibility).

A content-free local voice-activity detector that only recognises "someone is speaking", never "what", does not count as capture.

**Answering as consent** is the least ceremonial path, so the sources qualify it. All four conditions must hold: the robot has greeted *this* visitor and the reply window is open; the visitor is present at counter distance and bearing; the robot is not speaking (the detector arms after the greeting plus a reverberation tail, so the robot's own voice cannot trip it); and the speech lasts past an energy and duration threshold, so a cough does not trip it.

### Options rejected, and why
- **Greet and open the microphone on presence.** Continuous capture without consent; also fails technically in venue noise.
- **The wake word gates everything.** The hook then depends on the visitor knowing something.
- **A wave-back gesture as the consent trigger.** The first release had no gesture recognition, so the wave stays social choreography.
- **A cloud "is this addressed to me?" classifier as the entry gate.** It streams audio off the stand before any visitor action, which inverts the consent posture. It is acceptable only downstream of consent, inside an engaged session.

### A session lease, not a per-turn permit
The consent action opens a bounded **session lease**: the microphone stays open across the conversation so the visitor can interrupt the robot (see [[B4-turn-taking-and-self-hearing]]). The lease has a maximum length (an illustrative 150 s, `interaction_cap_illustrative`) and closes fail-closed on lease expiry, permit loss, safety, reset, fault, decline, inactivity, departure, or the end of the beat. On permit loss the microphone must close within an illustrative 200 ms (`mic_close_on_permit_loss_illustrative`).

### The listening indicator
- **Listening is shown if and only if the microphone is capturing**, for the whole lease.
- Listening is visually distinct from every other state (resting, greeting, offering, speaking, safety hold).
- A research-recording light, if one exists, must not be confusable with listening.

Visibility matters *more* under a lease than under a per-turn microphone, because the open window is longer. A design note from accessibility practice: WCAG 2.2 Success Criterion 1.4.1 (Use of Color) says colour must not be the only carrier of information. The listening state should therefore change shape or motion (ears perked, a lean-in, a distinct face pattern), not only colour. WCAG is written for web content; it is used here as a design analogy.

### Say only what the architecture can keep
The detectors ran on compute inside the stand and consumed the robot's microphone audio over a private link. "Nothing leaves the robot" was therefore false. The accurate promise is that un-consented audio is never processed for content, never stored, and never leaves the stand ("locally, in the stand"). After consent, audio goes to one approved speech service, and network egress is restricted to that service. The source's rule: a visitor-facing promise the team cannot keep is the most expensive kind of drift.

### What is recorded, and what is not
- In the default profile, audio is processed in memory only: no transcripts, no audio files. A research-recording profile is off by default, separately approved, and has its own light and notice.
- No face recognition, no returning-visitor recognition, no persistent identity, no stored conversation, no stand-captured photo (the visitor's own phone only).
- Anonymous visitor ids exist only within one visit, in memory, and expire (see [[B2-who-is-speaking]]).
- In a group, nothing one person said is repeated to another or kept after the visit.

Camera images are a second channel. In the sources, a camera frame reached a cloud multimodal model on every utterance. That path needed its own governance review (provider, retention, training use, explicit approval for children's images, egress restriction) before any appearance-based feature could ship (see [[C2-the-validation-ladder]]).

### Commenting on people
An opening remark on something the visitor wears ("nice team shirt") makes the robot feel present. The rule is **comment on things, not people**. Prohibited categories: bodies, apparent age, gender, ethnicity, religious or cultural dress, medical or assistive devices, pregnancy, occupational uniforms and political symbols. When unsure, say nothing about appearance. Never infer a personal attribute from a logo.

### Disclosure
A stand sign that invited people in was removed because answering is the primary path. Its *disclosure* function was not redundant: removing the sign removed the carrier, not the obligation. Whether answering a greeting is adequate consent may depend on how disclosure is delivered, so the two questions must be settled together, with legal review, before public use. The operator carries a short script ("it opens a microphone for a short conversation, shows a listening light the whole time, closes when you step away, and keeps nothing").

### Children and accessibility
- The robot does not detect or infer age, and does not branch dialogue on age. Content is child-safe for everyone.
- The whole path (greet → offer → gift → celebrate → goodbye) runs output-only. Taking the gift needs no voice.
- Non-voice consent exists through the operator or the button.
- Deaf and hard-of-hearing visitors get a visual-first experience (face, gaze, gesture, gift, lights). Captions need a display, which is new hardware.
- Gestures and the gift are language-independent.
- Reach: the tray sits at the counter edge where a child can reach, and the operator assists anyone who cannot.
- A silent visitor hears, after one unanswered invitation, an offer that needs no speech ("no talking required").
- Light shows (a dance beat) must respect the public flash limit of 3 flashes in any 1 s period (`wcag_flash_limit`, WCAG 2.2 SC 2.3.1).

## How it is designed and tested
- Audit logs so that every capture interval lies inside a lease opened by a consent action, and the indicator was on for all of it.
- Measure false accepts and false rejects of the answer detector at venue noise, and choose the threshold (or enable the button) per venue from that data.
- Run the full visit with the microphone disabled; the gift path must complete.
- Grep the deployed configuration for any storage path or recording flag that is on by default.

## Common confusions
- **"On-device means private."** The boundary that matters is what is captured, for how long, and where it goes. State the boundary the architecture really has.
- **"Consent once covers the whole day."** Consent is per visit and bounded by the lease.
- **"No face recognition means no identity data."** Session embeddings are identity-like; they are acceptable only if in memory, scoped to the visit and deleted.

## Why it matters for public-robot interaction
Privacy failures in public are visible and social: a parent sees a light, or does not, and decides whether the robot can be trusted. Separating speaking from listening lets the robot be warm to everyone while asking for nothing until the visitor chooses to talk.

## Terms introduced
- **consent (GDPR)** — a freely given, specific, informed and unambiguous indication of wishes by a statement or clear affirmative action (Art. 4(11)).
- **privacy by design** — making a privacy promise true through system structure.
- **consent action** — a visible visitor action that opens the microphone: answering, a wake phrase, an operator trigger or a button.
- **answer-as-consent** — treating a reply to the robot's greeting as the consent action, under qualifying conditions.
- **session lease** — a bounded, fail-closed interval during which the microphone stays open after consent.
- **listening indicator** — the visible signal shown if and only if the microphone is capturing.
- **disclosure carrier** — the physical or spoken means by which a visitor is told what the robot captures.
- **comment on things, not people** — the rule that limits appearance remarks to objects and excludes personal categories.
