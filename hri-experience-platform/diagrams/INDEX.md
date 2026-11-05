# Diagrams — A platform for many robot experiences (rung 2, learn-diagram)

Six diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. This is the picture layer for
the rung-1 notes: the two roles and the boundary (Part A), the kernel mechanics (Part B), and the verification
ladder (Part C). Every number on every canvas is loaded from this kit's [`../constants.json`](../constants.json)
by key and tagged on the canvas (`[In]` = illustrative design parameter, `[Pn]` = public, `[calc]` = my
arithmetic on tagged values); no number is typed into a spec. Every number on these pages is class
`illustrative`: a round design parameter, never a measurement of any system. Each canvas carries its own legend
and sources block, so the exported image stands alone. `hri-experience-platform.drawio` is the combined 6-page
document.

**Sources used:** only this kit's `notes/`, `glossary.md` and `constants.json`, plus the public references the
notes already cite (Lamport 1978, Richardson's transactional outbox, Harel 1987, Pact, North's BDD). No internal
figure was copied, traced or described; every diagram is drawn fresh from the mechanism in the notes.

**Rendering:** the same local pipeline as [`../../robot-workload-benchmarking/diagrams/`](../../robot-workload-benchmarking/diagrams/).
Each page is a cell list in `specNN.py` (palette, `V(key)` loader and `Tags()` footnotes in `_common.py`),
rendered by `.render_local.py` into an editable `.drawio` and a standalone `.svg` (rect + XHTML `foreignObject`
labels), rasterised to `.png` by headless Chrome at 2x. Every PNG was read back and checked for legibility,
clipping and overlap. To regenerate: `python3 .render_local.py specNN.py`, then
`python3 .render_local.py --combine`.

| File | Teaches (the finding in the title) | Notes and constants used |
|---|---|---|
| `01-roles-and-the-boundary` | The reasoner proposes, only the coordinator invokes: one shared kernel owns every authority, each experience owns only its story, reached through one small effect vocabulary. | A0 (kernel concerns, rejected alternatives, vocabulary shrink), A1 (ownership table, proposal path), B1, B3 (effect table), B5 (catalogs, targets), B6 (boundaries, bounded turns); `chat_turns_illustrative`, `chat_turn_budget_s_illustrative`, `chat_session_bound_s_illustrative`, `old_effect_kinds_illustrative` |
| `02-one-event-path` | One event, one path: the kernel orders, admits and intercepts every input first; the reducer sees only what is left; nothing is sent until one snapshot is committed. | B4 (queue, priority, tie-break, admission, interception, single worker, hardware stop), B3 (atomic preparation and dispatch, outbox, deterministic IDs), B5, C2; no numeric parameter |
| `03-state-ownership` | The kernel owns the envelope; each experience owns only an opaque local story inside the one shared phase 'in story'. | B2 (envelope, phases, validators, participant authority vs policy, local state contract, recovery, two profiles), B1 (wave example), B4; `gesture_wait_timeout_s_illustrative`, `cleanup_ack_timeout_ms_illustrative` |
| `04-resource-claims` | Resource claims decide what may overlap: one physical action, one gaze lease and one conversation turn together, never two physical actions. | B3 (contract kinds, claims, action slot, head vs gaze, speech vs canned TTS, first wave claims), B4 (conflict matrix), C2 (showcase order, held intervals); no numeric parameter |
| `05-cancellation-proof` | Cancelling is not releasing: claims are kept until positive quiescence proof; settle bound <= ceiling < cleanup deadline, drawn to scale. | B3 (proof, settle bound and deadline, forced cleanup, non-proof, revocations), B2 (recovery); `cancel_settle_target_ms_illustrative`, `cancel_settle_ceiling_ms_illustrative`, `cleanup_ack_timeout_ms_illustrative` |
| `06-conformance-ladder` | Every experience climbs the same ladder, and 'done' must name its milestone; simulation done authorises no physical deployment. | C2 (ladder, suites, milestones, evidence rules), C1 (what simulation cannot prove), C3 (non-blocking regeneration, comparator); no numeric parameter |

## Per-diagram specs (as built)

### 01-roles-and-the-boundary
```
Teaches: the reasoner talks and proposes typed intents; the coordinator (kernel + one experience) decides and is
         the only thing that invokes; the effect vocabulary is the experience's only way out.
Type:    Block diagram, left to right: visitor -> reasoner -> coordinator frame (kernel over experience, effect
         vocabulary between) -> primitive / input catalogs -> per-target contracts -> targets.
Numbers: chat 3 turns x 8 s = 24 s [calc] inside a 60 s session bound; old effect list ~30 kinds (all illustrative).
Colour:  purple reasoner, amber kernel, green experience, blue catalogs/targets, red never-allowed.
Left out: event ordering (02), state split (03), resource claims (04).
```

### 02-one-event-path
```
Teaches: queue -> admission -> interception -> reducer -> validate -> derive IDs -> materialise -> commit one
         snapshot -> dispatch; failure before commit leaves no command; rejection, not deferral.
Type:    Pipeline in two rows with failure semantics under the steps.
Numbers: none (B4 has none). Step numbers are a drawing order, stated on the canvas.
Left out: what each primitive claims (04).
```

### 03-state-ownership
```
Teaches: envelope (kernel) around an opaque local story (experience) that lives only in 'in story'.
Type:    Nested containment: envelope fields, the closed phase set, the wave story inside; side panels for
         participant authority vs policy, validator order, local state contract, two profile levels.
Numbers: gesture-wait timer 10 s; cleanup deadline 10 000 ms (illustrative).
Deliberately not drawn: phase transitions the notes do not state (only in story -> cleanup -> recovery are drawn).
```

### 04-resource-claims
```
Teaches: claims per contract kind decide overlap; the action slot serialises physical actions.
Type:    Matrix (contract kind x resource) + rules panel + conflict matrix + three-lane showcase timeline.
Numbers: none. Timeline bar lengths are a drawing choice (the notes give order, not durations); said on canvas.
```

### 05-cancellation-proof
```
Teaches: claims are held from cancel request until positive proof; stuck -> forced cleanup -> recovery.
Type:    Bars to scale on one axis (0.094 px/ms) + decision flow + proof / non-proof panels.
Numbers: settle bound 1500 ms, ceiling 2000 ms, cleanup deadline 10 000 ms (illustrative); the spec asserts
         settle <= ceiling < cleanup, so a changed constant that breaks the relation fails the build.
Left out: a worked clamp example (the notes give the rule, not a case).
```

### 06-conformance-ladder
```
Teaches: kernel conformance -> experience suite -> platform done -> simulation acceptance -> physical acceptance;
         milestones: simulation (offline), live-chat gate, cross-target; evidence rules.
Type:    Staircase with "what it proves" above each rung, milestone bars below.
Numbers: none.
Left out: the B5 switching cycle and the serial profile-matrix cost (illustrative in B5: 5 profiles x up to 1 200 s each, my arithmetic); that is
         explorer 2's material (brief: "Switching experiences").
```

## Files

Per diagram: `NN-slug.drawio` (editable single page), `NN-slug.svg` (vector, self-rendered), `NN-slug.png`
(2x raster). `hri-experience-platform.drawio` = all six pages. `specNN.py` = the cell list for each page;
`_common.py` = palette, constants loader and footnote tags; `.render_local.py` = the renderer.
