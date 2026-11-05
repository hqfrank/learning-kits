# learn-diagram — how to turn a mechanism into a picture

## When a diagram beats prose

Use a diagram when the idea is about *structure* (what shares what), *flow* (what happens in what order), *position* (where a workload sits relative to a limit), or *comparison across a grid* (who affects whom). Do not diagram a single number or a definition; that is a sentence.

## Diagram types and when to use each

| Idea shape | Diagram | Notes |
|---|---|---|
| Components sharing a resource | Block diagram | One box per component, one box per shared resource, edges = paths. Label edges with the measured rate if known. |
| Ordered phases with cost | Pipeline / swimlane | One lane per actor; annotate each arrow with bytes/ms/count and its source. |
| Workload vs limits | Roofline or bounds chart | Log–log; roofs as labelled lines with their measured value; workloads as dots with names. |
| Threshold behaviour | Annotated curve | Mark the knee/cliff with the value and the mechanism name. |
| Pairwise effects | Heat map / matrix | Victim rows, aggressor columns, cell = effect size; mark cells that are lower bounds or unverified. |
| Alternatives ranked | Ladder / staircase | One step per option, height = the metric, cost of each step written on it. |
| Decision | Flowchart | Only when the source actually gives decision rules. |

## Spec first (write this before drawing)

```
Diagram: <name>
Teaches: <the one sentence the viewer should take away>
Type: <from the table>
Elements: <list, each with its label and the source of any number on it>
Reference lines / thresholds: <value + source>
What is deliberately left out: <...>
Colour semantics: <e.g. red = measured, grey = datasheet, dashed = predicted>
```

Show the spec to the user in the response before drawing unless they have asked you to proceed without review.

## Conventions

- Measured values in one colour, datasheet/advertised in another, predictions dashed. State the legend on the canvas.
- Every number on the canvas carries a short source tag in a footnote block on the canvas itself (e.g. `[A.6 Table A.6.2]`), so the exported image stands alone.
- Title states the finding, not the subject: "Thor's L2 is 8× larger; L2 latency did not change" rather than "Memory hierarchy".
- One idea per diagram. If a second idea appears, make a second page.
- Keep text ≥ 11 pt at export scale; prefer fewer, larger elements.
- Accessible colour choices (avoid red/green as the only distinction; use shape or dash as well).

## Tools

- Primary: the drawio MCP (`start_session`, `create_new_diagram` or `add_page`, `edit_diagram`, `export_diagram`). Keep elements within the viewport constraints the tool states; use explicit exit/entry points on edges.
- Save `.drawio` and export `.svg` and `.png` into `learning/<topic>/diagrams/`. Name files `<nn>-<slug>.drawio|svg|png`.
- Mermaid is acceptable for a quick flowchart or sequence inside a note, not for the deliverable images.
- After export, read the PNG back and check it: labels legible, nothing clipped, legend present. Fix and re-export before declaring done.

## Output

- The diagram files.
- A `diagrams/INDEX.md` with one row per diagram: file, the "teaches" sentence, sources used.
- Append a line to `SOURCES.md` listing which sections were used.
