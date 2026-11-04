// Generated from learning/agentic-device-control/notes/04-the-vision-specialist.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "agentic-device-control",
 "topicTitle": "Agentic control of a consumer device",
 "section": "04-the-vision-specialist",
 "sectionTitle": "04 — The vision specialist: see the screen, then tap, type, scroll",
 "notePath": "../agentic-device-control/notes/04-the-vision-specialist.md",
 "knowledgePoints": {
  "action-cycle": {
   "title": "Five-step action cycle",
   "summary": "Capture → scale down to the reference frame → model decides in frame pixels → scale up → inject through the accessibility service.",
   "source": "04-the-vision-specialist §How it works"
  },
  "computer-use-tool": {
   "title": "The computer-use tool",
   "summary": "A vendor-defined tool (screenshot, left_click, type, key, scroll, drag, wait, zoom) that the model calls and the application executes.",
   "source": "04-the-vision-specialist §What it is"
  },
  "reference-frame": {
   "title": "Reference frame size",
   "summary": "Recommended 1280×800, avoid above 1920×1080; smaller costs fewer image tokens, `zoom` recovers small text.",
   "source": "04-the-vision-specialist §How it works; Design choices and trade-offs"
  },
  "coordinate-scaling": {
   "title": "Coordinate scaling and aspect ratio",
   "summary": "Keep the scale factors and apply their inverse to every coordinate; different aspect ratios give different x/y scales, so preserve the aspect ratio.",
   "source": "04-the-vision-specialist §How it works (worked scaling example)"
  },
  "grounding-errors": {
   "title": "Diagnosing grounding errors",
   "summary": "A consistent offset in one direction is a scaling bug; near-misses on small targets come from lost detail — use zoom or crop.",
   "source": "04-the-vision-specialist §Common confusions"
  },
  "settle-history": {
   "title": "Settle delay and screenshot history",
   "summary": "Wait an illustrative 1 s after acting; each screenshot costs 1000–1800 input tokens, so keep only the last 3 and prune in batches.",
   "source": "04-the-vision-specialist §Design choices and trade-offs"
  },
  "capture-and-inject": {
   "title": "Capture and injection services",
   "summary": "The screen-capture API (MediaProjection) needs user consent; the accessibility service injects gestures and is the OS's supported route, which is also why it is a security concern.",
   "source": "04-the-vision-specialist §How it works; Common confusions"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "action-cycle",
   "prompt": "Which step comes immediately after the model returns an action in reference-frame pixels?",
   "choices": [
    "Scale the coordinates up to device pixels",
    "Capture a new screenshot",
    "Resize the screenshot down",
    "Return FINISH to the orchestrator"
   ],
   "answer": 0,
   "explanation": "Scale up, then act through the accessibility service.",
   "source": "04-the-vision-specialist §How it works"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "action-cycle",
   "prompt": "The vendor executes each computer-use action on the device.",
   "answer": false,
   "explanation": "The application, not the vendor, executes each action and returns the result.",
   "source": "04-the-vision-specialist §What it is"
  },
  {
   "id": "q3",
   "type": "multi",
   "kp": "computer-use-tool",
   "prompt": "Which are computer-use tool actions listed in the note? Select all that apply.",
   "choices": [
    "`left_click`",
    "`zoom`",
    "`scroll`",
    "`launch_app`"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "`launch_app` is an actuator function-calling tool, not a computer-use action.",
   "source": "04-the-vision-specialist §What it is"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "computer-use-tool",
   "prompt": "Who defines the schema of the computer-use tool?",
   "choices": [
    "The model vendor",
    "The device's accessibility service",
    "The orchestrator prompt",
    "The cloud message channel"
   ],
   "answer": 0,
   "explanation": "It is vendor-defined; actuator tools have your own schemas (see 05).",
   "source": "04-the-vision-specialist §What it is; Terms introduced"
  },
  {
   "id": "q5",
   "type": "tf",
   "kp": "computer-use-tool",
   "prompt": "Coordinates returned by the model are expressed in the reference frame's pixels, not the device's native pixels.",
   "answer": true,
   "explanation": "That is why the scaler must map them back.",
   "source": "04-the-vision-specialist §How it works"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "reference-frame",
   "prompt": "What reference-frame size does the vendor recommend for web-style applications (public)?",
   "choices": [
    "1280×800",
    "1920×1080",
    "2400×1600",
    "640×400"
   ],
   "answer": 0,
   "explanation": "The vendor recommends 1280×800 and advises against sizes above 1920×1080.",
   "source": "04-the-vision-specialist §How it works; constants.json cu_reference_frame_recommended"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "reference-frame",
   "prompt": "Small text is unreadable at the reference frame. What does the note recommend first?",
   "choices": [
    "Use the `zoom` action on that region",
    "Raise the frame above 1920×1080",
    "Add more prompt text",
    "Increase the settle delay"
   ],
   "answer": 0,
   "explanation": "`zoom` inspects one region at full resolution without paying for a large full-screen image every call.",
   "source": "04-the-vision-specialist §Design choices and trade-offs"
  },
  {
   "id": "q8",
   "type": "tf",
   "kp": "reference-frame",
   "prompt": "A smaller reference frame costs fewer image tokens and gives a faster reply.",
   "answer": true,
   "explanation": "The trade is readability of small text, recovered with `zoom`.",
   "source": "04-the-vision-specialist §Design choices and trade-offs"
  },
  {
   "id": "q9",
   "type": "numeric",
   "kp": "coordinate-scaling",
   "prompt": "Device native size is 2400×1600 (illustrative), reference frame 1280×800. The model taps x = 200. Compute the device x as 200 × 2400 ÷ 1280.",
   "answer": 375,
   "unit": "px",
   "tolerance": 2,
   "explanation": "x scale is 1280÷2400; dividing by it gives 375 px.",
   "source": "04-the-vision-specialist §How it works (worked scaling example); my arithmetic on constants.json device_native_resolution_illustrative, model_click_illustrative"
  },
  {
   "id": "q10",
   "type": "numeric",
   "kp": "coordinate-scaling",
   "prompt": "Same setup: the model taps y = 560. Compute the device y as 560 × 1600 ÷ 800.",
   "answer": 1120,
   "unit": "px",
   "tolerance": 2,
   "explanation": "y scale is 800÷1600 = 0.5, so the device y is 1120 px.",
   "source": "04-the-vision-specialist §How it works (worked scaling example); my arithmetic"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "coordinate-scaling",
   "prompt": "Why do the x and y scale factors differ in the worked example?",
   "choices": [
    "The device and the reference frame have different aspect ratios",
    "The model rounds coordinates",
    "The settle delay shifts the image",
    "The accessibility service rescales y"
   ],
   "answer": 0,
   "explanation": "3:2 against 16:10; a plain resize stretches the image, so the vendor advises preserving aspect ratio.",
   "source": "04-the-vision-specialist §How it works (worked scaling example)"
  },
  {
   "id": "q12",
   "type": "tf",
   "kp": "coordinate-scaling",
   "prompt": "With one uniform scale of min(x scale, y scale), the resized image is padded to fill the reference frame.",
   "answer": true,
   "explanation": "In the example the uniform scale is 0.5, giving a 1200×800 image padded to 1280×800 (my arithmetic).",
   "source": "04-the-vision-specialist §How it works (worked scaling example)"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "grounding-errors",
   "prompt": "Every tap lands about 40 px to the left of its target. What is the most likely cause?",
   "choices": [
    "A scaling bug in the coordinate scaler",
    "The model's temperature is too high",
    "The settle delay is too short",
    "Prompt injection"
   ],
   "answer": 0,
   "explanation": "A consistent offset in one direction is almost always a scaling bug; check the scaler before the prompt.",
   "source": "04-the-vision-specialist §Common confusions"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "grounding-errors",
   "prompt": "Taps land near, but not on, small icons with no consistent direction. What helps most?",
   "choices": [
    "Use `zoom` or crop the region",
    "Add more prompt text",
    "Lower the reference frame further",
    "Switch the orchestrator tier"
   ],
   "answer": 0,
   "explanation": "Near-misses on small targets come from detail lost in down-scaling.",
   "source": "04-the-vision-specialist §Common confusions"
  },
  {
   "id": "q15",
   "type": "tf",
   "kp": "grounding-errors",
   "prompt": "**Coordinate grounding** is the main source of wrong actions in the vision specialist.",
   "answer": true,
   "explanation": "Mapping \"the video app icon\" to a pixel is where most wrong actions start.",
   "source": "04-the-vision-specialist §How it works"
  },
  {
   "id": "q16",
   "type": "numeric",
   "kp": "settle-history",
   "prompt": "How many recent screenshots does the vendor suggest keeping (public)?",
   "answer": 3,
   "unit": "screenshots",
   "tolerance": 0,
   "explanation": "Keep the last 3 and prune in batches so the cached prefix stays unchanged between prunes.",
   "source": "04-the-vision-specialist §Design choices and trade-offs; constants.json cu_screenshots_kept"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "settle-history",
   "prompt": "The settle delay is too short. What typically happens?",
   "choices": [
    "The model sees a half-drawn screen and repeats the action",
    "The cache expires",
    "Coordinates shift by a constant offset",
    "The watchdog fires immediately"
   ],
   "answer": 0,
   "explanation": "Too short: repeats; too long: every step pays the wait.",
   "source": "04-the-vision-specialist §Design choices and trade-offs"
  },
  {
   "id": "q18",
   "type": "tf",
   "kp": "settle-history",
   "prompt": "Putting the target description **before** the screenshot in the message improved click accuracy, per the vendor.",
   "answer": true,
   "explanation": "Instruction before image is a vendor prompting recommendation.",
   "source": "04-the-vision-specialist §Design choices and trade-offs"
  },
  {
   "id": "q19",
   "type": "mcq",
   "kp": "capture-and-inject",
   "prompt": "Why can the vision specialist not use a debug-cable screenshot?",
   "choices": [
    "There is no cable in a cloud-initiated design",
    "Cable screenshots are too large",
    "The model rejects them",
    "They bypass user consent"
   ],
   "answer": 0,
   "explanation": "The device must capture itself through the screen-capture API.",
   "source": "04-the-vision-specialist §How it works"
  },
  {
   "id": "q20",
   "type": "tf",
   "kp": "capture-and-inject",
   "prompt": "Accessibility services are only meant for assistive apps, so using them for gestures is an unsupported hack.",
   "answer": false,
   "explanation": "They are the OS's general, supported route for programmatic gestures and global actions; that power is also a security concern.",
   "source": "04-the-vision-specialist §Common confusions"
  },
  {
   "id": "q21",
   "type": "tf",
   "kp": "capture-and-inject",
   "prompt": "The screen-capture API (MediaProjection) asks the user for consent before capture starts.",
   "answer": true,
   "explanation": "Consent is required; a missing consent is an infrastructure failure in 09's taxonomy.",
   "source": "04-the-vision-specialist §How it works"
  }
 ]
});
