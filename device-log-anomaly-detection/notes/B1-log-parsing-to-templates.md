# B1 — Log parsing: from raw lines to templates and parameters

**Source:** He, Zhu, Zheng, Lyu, "Drain: An Online Log Parsing Approach with Fixed Depth Tree", ICWS 2017 (https://jiemingzhu.github.io/pub/pjhe_icws2017.pdf); Du & Li, "Spell: Streaming Parsing of System Event Logs", ICDM 2016; generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer.

## In one sentence
Log parsing maps each raw message to the print statement that produced it — a **template** of constant words with `<*>` slots — plus the list of values in the slots, and the choice between mining templates from data and extracting them from source code is a trade between automation and completeness.

## What it is
A **template** (also called a log event or log key) is the constant part of a message, with each parameter position replaced by a wildcard `<*>`. Example:

```
raw:       CTRL-EVENT-DISCONNECTED bssid=aa:bb:cc:dd:ee:ff reason=3 locally_generated=1
template:  CTRL-EVENT-DISCONNECTED bssid=<*> reason=<*> locally_generated=<*>
params:    [aa:bb:cc:dd:ee:ff, 3, 1]
```

Each template gets a stable **template ID**. After parsing, a log is a sequence of template IDs with parameter lists. This shrinks the vocabulary the later models see from millions of distinct strings to a few hundred templates (an illustrative 400 for one set of Wi-Fi components).

## How it works
**Two template sources.**

- **Data-driven mining** discovers templates from sample logs. Drain and Spell are the standard online parsers. Drain (He et al. 2017) preprocesses each message with simple regular expressions for known variables (IP addresses, numbers), then walks a **parse tree of fixed depth**: the first layer splits by message length in tokens, the next layers by the first few tokens, and a leaf holds candidate log groups. It picks the group whose token-by-token similarity is highest and accepts it only if the similarity reaches a threshold *st*; otherwise it creates a new group. Spell (Du & Li 2016) instead matches each message to existing templates by longest common subsequence.
- **Source-code extraction** reads the print statements directly. Format specifiers such as `%d` and `%s` become `<*>`. The result is the complete set of templates the code can produce, including ones never seen in the field.

**Why mining misses the important templates.** A miner can only discover templates that appear in its sample. Error and warning paths are rare in normal logs, so they are the templates a miner most often misses. In an illustrative component with 100 print statements, about half on error or warning paths, a miner run on normal logs might find an illustrative 20. Those missing error templates are exactly the ones anomaly detection needs. (The direction is the lesson; the numbers are illustrative.)

**Two failure modes of parsing.**

- **One-to-many** — one print statement yields several templates. A miner that sees `pingTest target=GATEWAY` and `pingTest target=LOCALHOST` often enough may keep the value as a constant and create two templates. False diversity follows.
- **Many-to-one** — different print statements collapse into one template, because long parameter values make their messages look alike. Signal is lost.

**A matcher for fixed templates.** If templates come from source code, inference is a lookup, not a discovery. A naive matcher tests each message against every template's regular expression: cost grows with (messages × templates). A **parse-tree matcher** borrows Drain's index idea: layer 1 is the component, layer 2 the token count, then one layer per token, and the leaf stores the template ID. A lookup visits only the templates with the same component and length.

Three differences from Drain make the matcher fit fleet analysis (generalised from the internal design):

1. **Training is separate from inference.** The template set is fixed when the tree is built, so the feature space for the models stays stable ([[B2-windows-and-count-vectors]]).
2. **Partial-token wildcards.** `event=<*>` and `error=<*>` stay two templates. A whole-token wildcard would merge them into `<*>`.
3. **An unmatched bucket.** Messages that match no template are kept for engineers to review; new templates are added and the tree is rebuilt ([[C2-template-engineering]]).

## How it is measured or used
- **Parsing accuracy** is the fraction of messages assigned to the correct template. It needs ground-truth templates — which is the thing being built. Data-driven parsers tune *st* and depth against such ground truth, a chicken-and-egg problem when none exists.
- **Speed.** Drain reports a 51.85 %–81.47 % running-time improvement over the best online parser of its time on five real data sets with more than 10 million messages (He et al. 2017, abstract). A tree matcher's advantage over regular-expression matching grows as the template count grows.
- **Coverage.** The share of messages that match any template; a falling share signals new code ([[C2-template-engineering]]).

## Common confusions
- **"More templates is better."** Duplicates from one-to-many parsing inflate the feature space and split one behaviour across several columns.
- **"Drain finds all the templates."** It finds the ones in the sample. Rare paths stay invisible.
- **"Source-code extraction is free."** It needs source access, a person or tool to read print statements, and an update whenever the code changes.
- **"Parameters are noise."** Parameters carry the reason codes, latencies, and signal levels that explain a fault. Parsing keeps them; later stages may use them ([[B5-from-anomaly-to-root-cause]]).

## Why it matters for fleet operations
Every later stage works on template IDs. A parser that splits one behaviour into many templates, or merges many into one, damages every feature, model, and report built on top of it, and no later stage can repair it.

## Terms introduced
- **template (log event, log key)** — the constant part of a message with parameter positions replaced by `<*>`.
- **template ID** — a stable identifier for one template.
- **log parsing** — mapping each raw message to a template ID plus its parameter list.
- **data-driven mining** — discovering templates from sample logs (Drain, Spell).
- **source-code extraction** — building templates from the print statements in the code.
- **parse tree (fixed depth)** — Drain's index: length, then leading tokens, then candidate groups at the leaves.
- **similarity threshold (st)** — Drain's minimum token similarity for a message to join an existing group.
- **one-to-many / many-to-one parsing** — one statement split into several templates / several statements merged into one.
- **partial-token wildcard** — a wildcard inside a token (`event=<*>`), keeping the constant prefix distinct.
- **unmatched bucket** — the store of messages no template matched, reviewed to extend the template set.
