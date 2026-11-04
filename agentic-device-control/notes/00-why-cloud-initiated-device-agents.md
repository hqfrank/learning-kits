# 00 — Why cloud-initiated device agents

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); ReAct, Yao et al. 2022, https://arxiv.org/abs/2210.03629; Anthropic computer-use tool documentation, https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool · **Status:** concept primer. Every number is public (cited) or labelled illustrative.

## In one sentence
A cloud-initiated device agent lets a server send a plain-language task such as "open the video app and search for a title" to a consumer device, and the device completes the task by looking at its own screen and acting, with no person and no cable involved.

## What it is
The system has three parts.

- **The cloud side** decides that a task must run on a specific device and sends it as a message.
- **The device side** receives the message, runs the task, and reports the result.
- **The agent** is the software on the device that turns the task into actions. It calls a large multimodal model in the cloud to decide each action. The model sees screenshots and returns actions such as "tap here" or "type this".

The device in this kit is a tablet that runs a mobile OS of the Android type. The ideas apply to any consumer device with a screen and an OS that permits programmatic input.

## How it works
Three use cases drive the design.

1. **Automated testing.** A test asks for a user journey ("sign in, play a video, pause it") and checks the outcome. The test runs on many devices at the same time.
2. **Remote support.** A support process asks the device to change a setting or collect a state on the user's behalf.
3. **Fleet automation.** A fleet operator runs the same chore on many devices, for example to put each device into a known state before an experiment.

The old method for each case is a **scripted automation**: a fixed sequence of commands sent over a debug cable (the Android Debug Bridge, ADB, https://developer.android.com/tools/adb) or a UI test framework such as UI Automator (https://developer.android.com/training/testing/other-components/ui-automator). A script names each element by its identifier or its screen position.

An agent replaces the fixed sequence with a loop: look at the screen, decide the next action, act, look again. This is the ReAct pattern (reason, act, observe) from Yao et al. 2022; see [[06-the-react-loop]].

## Design choices and trade-offs
"Agentic" adds three things over a script.

- **Robustness to UI change.** A script breaks when a button moves or a dialog appears. An agent sees the new screen and adapts.
- **Natural-language tasks.** The task author does not need to know the element identifiers.
- **Recovery.** An agent can notice a wrong result and try another action.

The agent pays for these with three costs.

- **Latency.** Each decision is a model call over the network. An illustrative simple task takes about 20 s end to end ([[07-cost-and-latency]]). A script does the same task in well under a second.
- **Money.** Each model call consumes tokens. An illustrative simple task consumes about 30 000 tokens.
- **Non-determinism.** The same task can take a different path on two runs. Evaluation must therefore count success over many runs ([[09-evaluation]]).

Caution: the vendor documentation itself says that computer-use latency can be too slow for interactive use, and recommends background tasks such as automated software testing (computer-use tool documentation, "Limitations").

**Why cloud-initiated and not cable-initiated.** A cable needs a host computer next to each device. A cloud message reaches every device in a fleet. The cost is that the device must do on its own everything the host computer used to do: capture the screen, inject input, and keep credentials.

## Common confusions
- **"The model runs on the device."** In this design the model runs in the cloud. The device captures screenshots, sends them, and executes the returned actions.
- **"An agent is a better script."** An agent is a different trade: it buys robustness with latency, cost, and variance. A stable journey that runs thousands of times a day is often cheaper as a script.
- **"The cloud controls the device directly."** The cloud sends only a task. All actions are decided by the agent loop and executed by the device's own input services.

## Why it matters
An engineer who must automate a fleet of devices has a new option between "write and maintain scripts" and "send a person". The rest of this kit explains how to build that option so that it is reliable ([[01-the-message-path]]), structured ([[02-the-agent-graph]]), affordable ([[07-cost-and-latency]]), safe ([[08-safety]]), and measurable ([[09-evaluation]]).

## Terms introduced
- **cloud-initiated device agent** — software on a device that receives a natural-language task from a server and completes it by acting on the device.
- **large multimodal model** — a model that accepts text and images and returns text or tool calls.
- **scripted automation** — a fixed sequence of commands that names each UI element in advance.
- **ADB (Android Debug Bridge)** — the cable- or network-attached command-line tool for controlling an Android-type device from a host computer.
- **agentic** — describes software that chooses its next action from what it observes, in a loop, instead of following a fixed sequence.
