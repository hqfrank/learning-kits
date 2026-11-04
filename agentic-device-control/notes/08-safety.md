# 08 — Safety: screen content is data, actions are allow-listed, everything is logged

**Source:** OWASP Top 10 for LLM Applications 2025, https://genai.owasp.org/llm-top-10/; Anthropic computer-use tool documentation, https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool; generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)) · **Status:** concept primer. No measured numbers.

## In one sentence
Treat everything the agent reads from the screen as untrusted data, never as instruction; let the device execute only allow-listed actions; put a confirmation gate in front of anything irreversible; and log every step so that a run can be audited afterwards.

## What it is
Caution first: an agent that can see the screen and tap anywhere has the same power over the device as its user. Anything that can influence the model can therefore influence the device.

Two risks from the OWASP Top 10 for LLM Applications 2025 dominate.

- **LLM01 Prompt Injection.** Input that changes the model's behaviour against the developer's intent. **Indirect prompt injection** arrives through content the model reads, not through the task. For a device agent that content is the screen: a notification, a web page, a message in an app, text inside an image. The vendor documentation states that prompt injection can reach computer use through instructions in web pages or images (computer-use tool documentation, "Limitations").
- **LLM06 Excessive Agency.** The model has more functions, permissions, or autonomy than its job needs, so a manipulated or wrong output does real damage.

## How it works
Five controls, from the model outward.

1. **Instruction hierarchy in the prompt.** The system prompt states that the task comes only from the cloud message, and that text on screen is content to read, never a command to follow. This lowers the injection rate; it does not remove it. The remaining controls assume it fails.
2. **Allow-listed actions.** Device code, not the model, decides what may run. The actuator exposes named, typed tools only ([[05-the-actuator]]). Arguments are checked: `launch_app` accepts only packages on a list; `open_settings` accepts only listed pages. A call outside the list returns an error result and is logged.
3. **Scope limits on the vision specialist.** Screen actions are hard to allow-list one by one. Limit the context instead: the agent works only in apps on a per-task list; it detects and refuses to type into password fields, payment screens, or account-deletion pages.
4. **Confirmation gates.** Irreversible or costly actions — purchases, deletions, sending messages, factory reset — need confirmation from outside the model: a human, or a cloud-side policy check. The vendor recommends that an application which confirms consequential actions does so before each action in a batch, because one model turn can contain several actions (computer-use tool documentation, "Batch actions"). A gate the model can approve for itself is not a gate.
5. **Audit log.** Every run records the task, each routing decision, each tool call with its arguments, each result, and a reference to each screenshot. The log is append-only and stored off the device with the result report ([[01-the-message-path]]).

**Analogy:** a contractor who reads a note taped to the door that says "also remove the wall". A good contractor phones the client; a good agent treats the note as content and asks the gate.

## Design choices and trade-offs
- **Least privilege against capability.** Every tool and permission removed lowers the blast radius and also removes something a legitimate task might need. Start narrow; add tools when an evaluated task needs them ([[09-evaluation]]).
- **Privileged installation is a liability as well as an enabler.** The background capture and message permissions ([[01-the-message-path]]) make the agent a high-value target. Authenticate cloud messages, use short-lived credentials, and keep the task source single.
- **Screenshots contain personal data.** They go to a cloud model and into logs. Minimise retention, redact where possible, and treat the logs with the same access control as the device data they show (OWASP LLM02 Sensitive Information Disclosure).
- **Gates cost latency and autonomy.** Gate the irreversible few, not every tap.

## Common confusions
- **"A strong system prompt prevents injection."** It reduces it. OWASP treats prompt injection as a risk to mitigate with layered controls, not one to prevent with prompt text.
- **"The task comes from our own cloud, so inputs are trusted."** The task is trusted; the screen is not. Most of the tokens the model reads come from the screen.
- **"Logging is for debugging."** It is also the evidence for what the agent did on a user's device. Design it for audit first.

## Why it matters
An unattended agent with input-injection rights is a remote-control channel. The design must make the worst case of a fooled model small: the model proposes, device code disposes, a human or policy approves the irreversible, and the log shows all of it.

## Terms introduced
- **prompt injection** — input that changes a model's behaviour against the developer's intent (OWASP LLM01).
- **indirect prompt injection** — injection carried by content the model reads, such as screen text, rather than by the task.
- **excessive agency** — giving a model more functions, permissions, or autonomy than its job needs (OWASP LLM06).
- **instruction hierarchy** — the prompt rule that only the task is an instruction and all observed content is data.
- **confirmation gate** — an approval outside the model required before an irreversible or costly action.
- **audit log** — the append-only record of every decision, action, and result in a run.
