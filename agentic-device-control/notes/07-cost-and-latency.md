# 07 — Cost and latency: prompt caching, model tiers, tokens per step

**Source:** Anthropic prompt-caching documentation, https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching; Anthropic computer-use tool documentation, https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool; generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)) · **Status:** concept primer. Caution: every token count, latency, and task size below is illustrative; only the caching rules and price multipliers are public.

## In one sentence
An agent's cost and latency are set by the number of model calls times the tokens per call, and the two biggest levers are prompt caching (re-use the unchanged prefix of each request) and putting the cheap, fast model tier on every node that does not need the strong one.

## What it is
Every ReAct iteration ([[06-the-react-loop]]) is one model request. Each request re-sends the tool definitions, the system prompt, the history, and one or more screenshots. Most of that content is identical to the previous request.

**Prompt caching** lets the API re-use the processed form of an unchanged request prefix. The rules (prompt-caching documentation):

- The prefix is built in a fixed order: tools, then system prompt, then messages.
- A **cache breakpoint** marks the end of a cacheable prefix. A request can use up to 4 breakpoints.
- A cache entry lives 5 min by default, and each use refreshes it at no extra cost. A 1 h lifetime is also offered.
- Changing any block at or before a breakpoint changes the prefix, so the next request misses the cache.
- Price multipliers on the base input price: a 5 min cache write costs 1.25×, a 1 h write costs 2×, and a cache read costs 0.1× for most models (price table and its notes).

## How it works
**Where the breakpoints go.** The vendor's recommendation for computer-use loops is one breakpoint after the system prompt and tool definitions, and up to three more on the latest tool results, advanced each turn (computer-use tool documentation, "Manage screenshot history"). The stable part (tools and system) is then always a hit, and most of the history is a hit too.

**Why pruning breaks caching.** Dropping the oldest screenshot changes an early block, so everything after it misses. The vendor therefore suggests pruning in batches — keep the last three screenshots and prune every 25 turns — so that the prefix stays byte-identical between prunes (same section).

**An illustrative task budget.** Caution: all values in this table are illustrative and chosen to be self-consistent.

| Step | Calls | Input tokens per call | Wall time |
|---|---|---|---|
| Receive, validate, lock | 0 | — | 0.1 s |
| Orchestrator: route to vision | 1 | 4 000 | 2 s |
| Capture and resize screenshot | 0 | — | 2 s |
| Vision: find icon and tap | 1 | 7 000 | 5 s |
| Settle, capture | 0 | — | 1 s + 2 s |
| Vision: confirm and tap again if needed | 2 | 7 000 | 6 s |
| Orchestrator: FINISH | 1 | 4 000 | 2 s |
| **Total** | **5** | **29 000 (about 30 000)** | **about 20 s** |

Two facts follow (my arithmetic on the illustrative table). Model calls take about 15 s of the 20 s, so latency work starts with fewer calls. Screen capture and settle take about 5 s, so the device side is not free either.

**Caching arithmetic for one vision call.** Use the illustrative 7 000 input tokens: 3 000 stable prefix, 2 500 earlier history, 1 500 new screenshot (inside the public 1 000–1 800 tokens per screenshot range, computer-use tool documentation).

| Case | Cost in base-input-token units | Source |
|---|---|---|
| No caching | 7 000 | my arithmetic |
| 5 500 read at 0.1×, 1 500 written at 1.25× | 550 + 1 875 = 2 425 | my arithmetic, public multipliers |

The cached call costs about 35 % of the uncached call (my arithmetic). The first call of a task pays the 1.25× write on the whole prefix; caching pays back from the second call on.

**Model tiers per role.** The orchestrator uses the stronger tier; the vision specialist and the actuator use the fast tier ([[03-the-orchestrator]]). On the vendor's public price table the gap between tiers varies by generation; for one same-generation pair the fast tier costs $1 and the stronger tier $3 per million input tokens, and for every listed model the output price is 5× its input price (prompt-caching documentation, price table). Output tokens are few in this workload (short tool calls), so input tokens dominate cost; this is why caching matters more than reply length.

## Design choices and trade-offs
- **Fewer calls beats faster calls.** Route to the actuator when an OS call exists ([[05-the-actuator]]); one call replaces a screenshot-tap-confirm cycle.
- **Smaller screenshots.** A smaller reference frame cuts image tokens on every call; use `zoom` for small text ([[04-the-vision-specialist]]).
- **Cache lifetime against task length.** A task of an illustrative 20 s fits easily in the 5 min default lifetime. A long gap between tasks lets the cache expire; the 1 h lifetime costs more per write and pays only if tasks recur within the hour.
- **Strong tier everywhere** gives fewer wrong routes but multiplies the cost of the many specialist calls. Measure both success and cost per task before choosing ([[09-evaluation]]).

## Common confusions
- **"Caching changes the answer."** It re-uses processed input; the model sees the same prompt.
- **"Every call hits the cache."** The first call writes; edits to early blocks miss; an idle gap longer than the lifetime misses.
- **"Cost is per task."** Cost is per call, and calls per task vary from run to run. Report the distribution, not one task ([[09-evaluation]]).

## Why it matters
An agent that is correct but costs too much per task never leaves the lab. Order the prompt for caching, place breakpoints deliberately, prune in batches, and spend the strong model only where a wrong decision is expensive.

## Terms introduced
- **prompt caching** — re-use of the processed form of an unchanged request prefix across requests.
- **cache breakpoint** — a marker that ends a cacheable prefix; up to 4 per request (prompt-caching documentation).
- **cache lifetime (TTL)** — how long a cache entry lives without use: 5 min by default, 1 h optional (prompt-caching documentation).
- **cache write / cache read** — processing and storing a new prefix (charged above base price) / re-using a stored prefix (charged far below base price).
- **tokens per step** — the input and output tokens of one model call; the unit of agent cost.
