# A5 — Audio and voice

**Source:** Silero VAD (https://github.com/snakers4/silero-vad), openWakeWord (https://github.com/dscripka/openWakeWord), ECAPA-TDNN (arXiv:2005.07143), Whisper (arXiv:2212.04356). · **Status:** concept primer, illustrative framing only.

## In one sentence
The voice pipeline turns a microphone-array stream into words and replies through a chain of small models — voice-activity detection, wake-word spotting, speaker identification, speech recognition, and speech synthesis — and its defining benchmark lesson is that the per-message overhead of moving audio packets around can cost more than the models themselves.

## What it is
A microphone-array board captures several channels of audio and sends them to the computer as a stream of small packets. The voice services consume that stream:

- **Voice activity detection (VAD)** — **Silero VAD** decides, on short windows, whether anyone is speaking, so the heavier models only run on speech (https://github.com/snakers4/silero-vad).
- **Wake-word detection** — **openWakeWord** continuously scores the audio for a chosen wake phrase (https://github.com/dscripka/openWakeWord).
- **Speaker identification** — **ECAPA-TDNN** turns a speech window into an embedding that identifies the speaker (arXiv:2005.07143).
- **Automatic speech recognition (ASR)** — a Whisper-class model transcribes speech to text (arXiv:2212.04356). This may run on-board or in the cloud.
- **Text-to-speech (TTS)** and a **real-time speech-to-speech model** — produce the robot's spoken reply; often cloud services.

## How it works
**Packets, framing and message rate.** The microphone board groups audio samples into **frames** and sends a fixed number of frames per packet. The middleware then groups several packets into one message on the audio topic. So the **message rate** on the audio topic is set by the framing: frames per packet, and packets per message. An illustrative example: 48 frames per packet at a 16 kHz sample rate is one packet every 3 ms; grouping six packets per message gives one message every 18 ms, about 55 messages per second.

**Why framing matters for cost.** The downstream models work on fixed-length windows of audio (for example, VAD on short windows, wake-word on an 80 ms window). The *model* work per second depends only on the sample rate and window, not on the packet framing. But every message carries a **per-message overhead**: receive the packet, decode it, deserialise the middleware message, run a callback. If the benchmark's fake microphone board uses the wrong framing — more frames per packet means fewer, larger messages — the per-message overhead changes even though the model work does not. A fake that sends packets at the wrong rate biases every audio service's CPU.

**Why per-message overhead can exceed model cost.** The models here are tiny (VAD is well under two million parameters). On a small CPU core, the fixed cost of handling each message in a scripting pipeline — deserialise, copy, call — can be larger than the model's arithmetic. The headline audio cost is message plumbing, not inference.

**On-board versus cloud.** VAD and wake-word always run on-board (they gate everything and must work offline). ASR, TTS and the speech-to-speech model may run in the cloud; the benchmark replaces the cloud call with a stand-in that imitates its latency and streaming shape (see [[C3-the-harness-and-fakes]]).

## How it is measured or used in a benchmark
- **Get the framing right.** The fake microphone board must send the same frames-per-packet and packets-per-message as the real hardware, or the audio-topic message rate and every downstream per-message cost are wrong (see [[C7-how-the-bench-can-lie]]).
- **Separate per-message from per-sample cost.** Measure how each service's CPU changes when you change the framing at a fixed sample rate: the part that moves is per-message overhead, the part that does not is per-sample model work.
- **Drive the pipeline with real speech.** An event-driven service with no input costs almost nothing. To measure wake-word, ASR and speaker-id, play a scripted speech plan with actual wake phrases and utterances (see [[C2-solo-runs-and-levels]]).
- **Stub the cloud faithfully.** The stub must match the real API's streaming format and latency, or the service either fails to start or reports a false "working" (see [[C7-how-the-bench-can-lie]]).

## Common confusions
- **"The model is the cost."** For these tiny audio models, the per-message handling often costs more than the inference.
- **"Packet rate does not matter if the sample rate is right."** The sample rate fixes model work, but the packet/message framing fixes per-message overhead, and that is where a fake-hardware mismatch hides.
- **"An idle voice service with no speech is a valid measurement."** It is an idle floor; the working cost needs real speech input.
- **"The audio-topic rate is the metrics-topic rate."** Services often publish a separate low-rate metrics topic; do not mistake it for the audio stream rate.

## Why it matters for robotics workloads
Voice is the stack's purest demonstration that a benchmark measures plumbing, not just models. A tiny model behind a busy message pipe can still load a CPU core. If the fake microphone's framing is wrong, or the cloud stub is not faithful, the audio numbers are quietly biased in a way no single rate check reveals. Getting the message rate right, and separating per-message from per-sample work, is what makes voice measurable.

## Terms introduced
- **microphone-array board** — hardware that captures several audio channels and streams them as packets.
- **frame (audio)** — a small fixed group of audio samples; the unit the board packs into packets.
- **frames per packet / packets per message** — the framing that sets the message rate on the audio topic.
- **message rate** — messages per second on a topic; here set by the audio framing, not the sample rate.
- **per-message overhead** — the fixed cost of handling each message (receive, decode, deserialise, callback), independent of model work.
- **voice activity detection (VAD)** — deciding whether speech is present, to gate heavier models (Silero VAD).
- **wake-word detection** — continuously scoring for a chosen wake phrase (openWakeWord).
- **speaker identification** — identifying who is speaking from a speech embedding (ECAPA-TDNN).
- **automatic speech recognition (ASR)** — transcribing speech to text (Whisper-class).
- **text-to-speech (TTS) / speech-to-speech** — generating the robot's spoken reply, often in the cloud.
