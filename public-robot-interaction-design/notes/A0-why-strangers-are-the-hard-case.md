# A0 — Why talking to strangers is the hard case

**Source:** internal experience-design documents I1, I2 (see [`../SOURCES.md`](../SOURCES.md)); Nielsen 1993 for response limits; Bohus & Horvitz 2009 for open-world engagement. · **Status:** concept primer; every number is public or labelled illustrative ([`../constants.json`](../constants.json)).

## In one sentence
A robot that talks to strangers in a public place gets no training time, a few seconds of attention, groups instead of individuals, a loud room and a wide audience that includes children, so the design must make every success need nothing from the visitor and make every failure invisible to them.

## What it is
This kit is about one setting: a child-sized humanoid robot at **a public demo stand**, greeting people who walk past, talking with them for about a minute, offering a small gift, and saying goodbye. The team behind it calls the visitor-facing designer **the HRI designer** (HRI = human-robot interaction). The robot's speech comes from **the reasoner**, a speech-to-speech large language model (LLM) session that takes audio in and gives audio out (see [[B1-the-voice-pipeline]]).

A **stranger** here means a visitor with no prior knowledge of the robot, no instructions and no reason to learn a ritual. Bohus & Horvitz (2009) call this the *open-world* setting: people come and go, groups form and dissolve, and the system must decide on its own whom to engage and when.

Five properties make the setting hard:

1. **No training.** A button, a wake phrase or a sign is a ritual. Anything that needs a ritual fails the most common visitor.
2. **Seconds of attention.** A passer-by judges the stand in an illustrative 5 s (`attention_window_illustrative`). The hook must land before any instruction could.
3. **Groups.** The normal visitor is two or three people, often a parent with children. The nearest body is often not the person who talks.
4. **Noise.** A public venue runs at an illustrative 70–85 dB SPL (`venue_noise_illustrative`). Wake-word detection and speech recognition are least reliable exactly where the show runs.
5. **A wide audience.** Visitors include children, people who will not or cannot speak, people who do not share the language, deaf and hard-of-hearing people, and people who are only passing.

## How it works: the design stance
The sources answer these properties with a short set of principles. Each one is written so that a test can check it.

- **The robot acts first.** The hook is the robot coming alive and looking at the visitor. The visitor needs zero knowledge and zero action to get an "it noticed *me*" moment.
- **No instruction is a prerequisite for delight.** The main way into a conversation is to answer the robot. A wake phrase exists only as a shortcut for people who already know it.
- **The robot may speak unsolicited; it may not listen unsolicited.** Speaking and gesturing are output and need no consent. Capturing a visitor's voice needs a visitor action first (see [[A3-consent-and-privacy-by-design]]).
- **The reward is not gated on the most fragile channel.** Silence, noise, refusal or inability to speak still produces a gift and a good moment. Conversation is enrichment, not a toll.
- **One visitor-observable state at all times.** Resting, greeting me, listening to me, talking to me, offering, celebrating, saying goodbye. "Listening to you now" must be clear without a button light.
- **Generous, never needy.** Invite once, do not nag, notice the visitor leaving and let them go.
- **The hook works in silence.** The robot's voice is quiet and close-range. Gaze, a wave and the face lights must read across the room with no audio.
- **The visitor must never tell.** A visitor must not be able to tell whether the show runs fully autonomous, runs on canned lines, or is driven by a hidden operator.

The last principle is the one that shapes the engineering most. It means a degradation step is never announced: there is no "sorry, I can't hear you" line that exposes the machine. The robot always has a graceful line ready, the gift path works at every degradation step, and a skipped flourish is skipped silently. The worst thing a visitor should notice is a chattier robot versus a quieter one, never a broken one. [[C1-failure-and-degradation-ux]] turns this into tiers.

The sources also name an anti-goal: **a host, not a vending machine**. A robot that reads a menu aloud ("I can do four things, which would you like?") gives the visitor the work of choosing from a list they never asked for. The robot carries the initiative; the visitor keeps every decision.

**Analogy:** a good host at a garden gate greets each guest, looks at whoever speaks, offers one small thing, and lets people go without a word of complaint.

## How it is designed and tested
Each principle maps to a check the team can run:

- "The robot acts first" → a first-time visitor understands what to do with no instruction, in a walk-up test.
- "Speak but not listen" → the listening indicator matches microphone capture at every moment (an audit of logs against the indicator).
- "Reward not gated on voice" → the gift path completes with the microphone disabled.
- "Never tell" → observers cannot say which degradation step was running during a session.
- Timing → the delay from a visitor's action to a visible reaction stays below the public 1 s flow limit (`response_limit_flow`, Nielsen 1993). Past that limit a visitor concludes it did not work and repeats themselves.

## Common confusions
- **"A wake word makes it simple."** It makes the *robot* simple. It makes the hook conditional on the visitor knowing something, which is the same failure as a button.
- **"Degradation should be honest, so announce it."** Honesty applies to claims (the robot never claims to remember someone, never celebrates a gift that was not taken). It does not require narrating the machine's internal state. The visitor needs a coherent experience, not a status report.
- **"More features make a better demo."** A list of tricks reads as a vending machine. One well-timed gesture that lands with a line is worth more.

## Why it matters for public-robot interaction
A lab user forgives a slow or confused robot because they know it is a prototype. A stranger does not. The design for strangers inverts the usual priority: first make the cheapest, least fragile path delightful (gaze, a wave, a gift), then add conversation on top, and make sure every failure of the fragile layer falls back to the robust one without a visible seam.

## Terms introduced
- **public demo stand** — a counter in a public venue where a robot greets and serves walk-up visitors.
- **stranger** — a visitor with no prior knowledge, instructions or training for the robot.
- **open-world engagement** — engagement where people arrive and leave freely and the system decides whom to engage (Bohus & Horvitz 2009).
- **the reasoner** — the speech-to-speech LLM session that produces the robot's conversational speech.
- **the HRI designer** — the person who owns the visitor-facing experience.
- **"the visitor must never tell"** — the requirement that a visitor cannot perceive which degradation step is running.
- **host, not vending machine** — the stance that the robot offers one thing at a time and never reads a menu.
