# 05 — The actuator: system actions that bypass the UI

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Android `AccessibilityService.performGlobalAction`, https://developer.android.com/reference/android/accessibilityservice/AccessibilityService; Android intents guide, https://developer.android.com/guide/components/intents-filters; Toolformer, Schick et al. 2023, https://arxiv.org/abs/2302.04761 · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
The actuator performs actions through OS interfaces instead of through the screen — launch an app, open a settings page, change a device state — because one direct call is faster, cheaper, and more reliable than several taps.

## What it is
The actuator is the second specialist node ([[02-the-agent-graph]]). Its tools are ordinary **function-calling tools**: each tool has a name, a description, and a typed input schema, and the model returns a call that names a tool and fills in the inputs (Anthropic tool-use documentation, https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview). Toolformer (Schick et al. 2023) showed that a language model can learn when to call an external tool and what to pass to it; vendor function-calling APIs make the same idea a request format.

Typical actuator tools:

| Tool | OS mechanism (Android-type device) |
|---|---|
| `launch_app(package)` | an explicit launch intent (intents guide) |
| `open_settings(page)` | a settings intent for that page |
| `go_home()`, `go_back()` | `performGlobalAction` with the home or back action |
| `set_volume(level)`, `set_wifi(on)` | the matching system service, where the app has permission |
| `get_device_state()` | read-only queries: foreground app, battery, connectivity |

## How it works
1. The orchestrator routes to the actuator with an instruction such as `"launch the video app"`.
2. The actuator model chooses a tool and its arguments.
3. Device code checks the call against an allow-list ([[08-safety]]) and runs it.
4. The tool returns a structured result: success or an error message.
5. The actuator writes a one-line summary to the shared state and returns to the orchestrator.

The actuator usually needs a short inner loop only: one or two tool calls, then a summary ([[06-the-react-loop]]).

## Design choices and trade-offs
**Why bypass the UI.** Compare two routes to "open the video app" on an illustrative tablet:

- *Through the screen:* screenshot, find the icon, tap, settle, screenshot, confirm. That is an illustrative 2 model calls and about 10 s.
- *Through the OS:* one launch call. That is an illustrative 1 model call and about 2 s, and no grounding error is possible.

The OS route also works when the target is off-screen, hidden in a folder, or behind a dialog.

**Why keep the vision route at all.** System interfaces cover the OS, not the inside of apps. Searching for a title inside a video app has no OS call; it needs the screen. The two specialists are therefore complementary, and the orchestrator's prompt says "prefer the actuator when it can do the job" ([[03-the-orchestrator]]).

**The cost of power.** Every actuator tool is a capability that a manipulated model could misuse. The tool list is short, each tool is narrow, and state-changing tools are allow-listed and logged ([[08-safety]]).

**Verification.** A system call can succeed and still not give the visible result (an app can crash on start). The orchestrator therefore often sends the vision specialist to confirm the screen after an actuator step.

## Common confusions
- **"The actuator runs shell commands."** A safe actuator exposes named, typed operations only. A generic "run this command" tool removes every guard.
- **"System actions do not need checking."** They return an API result, not the user-visible outcome. Confirm on screen when the outcome matters.
- **"Function calling and the computer-use tool are different mechanisms."** Both are tool calls in the same protocol. The computer-use tool has a vendor-defined schema; actuator tools have your own schemas.

## Why it matters
The cheapest model call is the one you do not make. Every task step that has a direct OS route should take it; the screen is the fallback for the parts of a task that only the screen can reach.

## Terms introduced
- **actuator** — the specialist that performs system-level actions through OS interfaces, not through the screen.
- **function-calling tool** — a tool defined by name, description, and input schema, which the model invokes with a structured call.
- **intent** — an Android-type OS message that asks the system to start an app or open a page.
- **global action** — an accessibility-service action that acts on the whole system, such as home or back.
- **allow-list** — the explicit list of tools and arguments the device will execute; everything else is refused.
