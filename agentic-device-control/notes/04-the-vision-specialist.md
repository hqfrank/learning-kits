# 04 — The vision specialist: see the screen, then tap, type, scroll

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Anthropic computer-use tool documentation, https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool; Android MediaProjection guide, https://developer.android.com/media/grow/media-projection; Android `AccessibilityService.dispatchGesture`, https://developer.android.com/reference/android/accessibilityservice/AccessibilityService · **Status:** concept primer. Numbers are public (cited) or labelled illustrative.

## In one sentence
The vision specialist captures the screen, shrinks it to the model's reference frame, lets the model name an action in that frame's pixel coordinates, scales the coordinates back to the device's pixels, and injects the gesture through the OS accessibility service.

## What it is
The vision specialist is a graph node ([[02-the-agent-graph]]) whose only tools are screen actions. It uses the vendor's **computer-use tool**: a tool built into the model whose actions include `screenshot`, `left_click`, `type`, `key`, `scroll`, `left_click_drag`, `wait`, and `zoom` (computer-use tool documentation, "Available actions"). The application, not the vendor, executes each action and returns the result (same source, "The computing environment").

## How it works
One action cycle has five steps.

1. **Capture.** The device captures its own screen with the OS screen-capture API (MediaProjection on Android-type devices; MediaProjection guide). A debug-cable screenshot is not an option, because there is no cable ([[00-why-cloud-initiated-device-agents]]). The platform asks the user for consent before capture starts (MediaProjection guide).
2. **Scale down.** The screenshot is resized to the **reference frame**, the image size the model sees. The vendor recommends 1280×800 for web-style applications and advises against sizes above 1920×1080 (computer-use tool documentation, "Size screenshots to fit image limits").
3. **Decide.** The screenshot is added to the conversation as an image. The model returns an action with coordinates in the reference frame's pixels.
4. **Scale up.** A coordinate scaler maps the point to the device's native pixels.
5. **Act.** The accessibility service injects the gesture. On Android-type devices `AccessibilityService.dispatchGesture` performs taps and swipes, and the service can also set text in a focused field.

**Coordinate grounding** is the model's mapping from "the video app icon" to a pixel. It is the main source of wrong actions.

**Worked scaling example.** Caution: the device size here is illustrative. Take an illustrative native screen of 2400×1600 and the public 1280×800 reference frame.

| Quantity | Value | Source |
|---|---|---|
| x scale, reference ÷ native | 1280 ÷ 2400 ≈ 0.533 | my arithmetic |
| y scale, reference ÷ native | 800 ÷ 1600 = 0.5 | my arithmetic |
| Model asks to tap at | (200, 560) | illustrative |
| Device taps at | (200 ÷ 0.533, 560 ÷ 0.5) = (375, 1120) | my arithmetic |

The two scales differ because the two aspect ratios differ (3:2 against 16:10). A plain resize therefore stretches the image. The vendor advises to preserve the aspect ratio when resizing (computer-use tool documentation, "Diagnose click issues"). The alternative is one uniform scale, here min(0.533, 0.5) = 0.5 (my arithmetic), giving a 1200×800 image padded to 1280×800. Either way, keep the scale factors and apply their inverse to every returned coordinate.

## Design choices and trade-offs
- **Reference frame size.** A smaller frame costs fewer image tokens and gives a faster reply. A larger frame keeps small text readable. The `zoom` action lets the model inspect one region at full resolution without paying for a large full-screen image (computer-use tool documentation, "Available actions").
- **Settle delay.** After an action the UI animates. The specialist waits an illustrative 1 s before the next screenshot. Too short, and the model sees a half-drawn screen and repeats the action. Too long, and every step pays the wait.
- **Screenshot history.** Each screenshot costs roughly 1 000–1 800 input tokens (computer-use tool documentation, "Manage screenshot history"). The specialist keeps only the most recent few. The vendor suggests keeping the last three and pruning in batches so that the cached prompt prefix stays unchanged between prunes (same section; see [[07-cost-and-latency]]).
- **Instruction before image.** The vendor reports better click accuracy when the target description comes before the screenshot in the message (computer-use tool documentation, "Optimize model performance with prompting").

## Common confusions
- **"A consistent click offset is a model error."** A consistent offset in one direction is almost always a scaling bug: coordinates applied to a display of a different size (computer-use tool documentation, "Diagnose click issues"). Check the scaler before the prompt.
- **"Clicks near the target mean the model is nearly right."** Near-misses on small targets usually come from detail lost in down-scaling. Use `zoom`, or crop, rather than more prompt text (same section).
- **"Accessibility services are only for assistive apps."** They are the OS's general, supported route for programmatic gestures and global actions. Their power is also why they are a security concern ([[08-safety]]).

## Why it matters
The vision specialist is what makes the agent work on any app, including apps with no test hooks. Its reliability depends less on the model than on plumbing: a correct scaler, a sensible reference frame, a settle delay, and a bounded screenshot history.

## Terms introduced
- **computer-use tool** — a vendor-defined tool with screen actions (screenshot, click, type, key, scroll, zoom) that the model calls and the application executes.
- **reference frame** — the pixel size of the screenshot the model sees; all model coordinates are in this frame.
- **coordinate scaler** — the code that maps points between the reference frame and the device's native pixels, in both directions.
- **coordinate grounding** — the model's mapping from a described element to a pixel coordinate.
- **settle delay** — the wait after an action before the next screenshot, so that the UI has finished changing.
- **screen-capture API** — the OS service that lets an app capture the display (MediaProjection on Android-type devices); it needs user consent.
- **accessibility service** — the OS service that can read the UI and inject gestures and global actions.
