// Generated from learning/agentic-device-control/notes/07-cost-and-latency.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "agentic-device-control",
 "topicTitle": "Agentic control of a consumer device",
 "section": "07-cost-and-latency",
 "sectionTitle": "07 — Cost and latency: prompt caching, model tiers, tokens per step",
 "notePath": "../agentic-device-control/notes/07-cost-and-latency.md",
 "knowledgePoints": {
  "cost-drivers": {
   "title": "Calls × tokens",
   "summary": "Cost and latency are set by model calls times tokens per call; in the illustrative 20 s, 5-call task model calls take about 15 s, so fewer calls beats faster calls.",
   "source": "07-cost-and-latency §In one sentence; How it works"
  },
  "cache-rules": {
   "title": "Prompt-caching rules",
   "summary": "Prefix order tools → system → messages; up to 4 breakpoints; 5 min default lifetime refreshed on use, 1 h optional; any change at or before a breakpoint misses.",
   "source": "07-cost-and-latency §What it is"
  },
  "cache-prices": {
   "title": "Cache price multipliers",
   "summary": "On base input price: 5 min write 1.25×, 1 h write 2×, read 0.1×; the first call pays the write, caching pays back from the second.",
   "source": "07-cost-and-latency §What it is; How it works"
  },
  "breakpoints-pruning": {
   "title": "Breakpoint placement and batch pruning",
   "summary": "One breakpoint after tools and system, up to three on the latest tool results; pruning changes an early block, so keep the last 3 screenshots and prune every 25 turns.",
   "source": "07-cost-and-latency §How it works"
  },
  "caching-arithmetic": {
   "title": "Caching arithmetic for one call",
   "summary": "Illustrative 7 000-token vision call: reads at 0.1× plus new screenshot written at 1.25× ≈ 35 % of uncached cost.",
   "source": "07-cost-and-latency §How it works (caching arithmetic)"
  },
  "model-tiers": {
   "title": "Model tiers and input dominance",
   "summary": "Strong tier on the orchestrator, fast tier on specialists; one public pair is $1 vs $3 per million input tokens; output is 5× input but few, so input dominates.",
   "source": "07-cost-and-latency §How it works (model tiers)"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "cost-drivers",
   "prompt": "In the illustrative budget, where does most of the ~20 s go?",
   "choices": [
    "Model calls (about 15 s)",
    "Screen capture and settle (about 15 s)",
    "Receive, validate, lock",
    "Cache writes"
   ],
   "answer": 0,
   "explanation": "Model calls take about 15 s of 20 s (my arithmetic), so latency work starts with fewer calls.",
   "source": "07-cost-and-latency §How it works (task budget)"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "cost-drivers",
   "prompt": "Cost is a fixed number per task.",
   "answer": false,
   "explanation": "Cost is per call and calls per task vary from run to run; report the distribution.",
   "source": "07-cost-and-latency §Common confusions"
  },
  {
   "id": "q3",
   "type": "numeric",
   "kp": "cost-drivers",
   "prompt": "How many model calls does the illustrative simple-task budget contain?",
   "answer": 5,
   "unit": "calls",
   "tolerance": 0,
   "explanation": "Two orchestrator calls plus three vision calls (illustrative).",
   "source": "07-cost-and-latency §How it works (task budget); constants.json task_model_calls_illustrative"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "cost-drivers",
   "prompt": "Which change most reduces latency for \"open the video app\"?",
   "choices": [
    "Route it to the actuator's single OS call",
    "Use the strong tier on the vision specialist",
    "Raise the reply-token cap",
    "Lengthen the settle delay"
   ],
   "answer": 0,
   "explanation": "Fewer calls beats faster calls; one OS call replaces a screenshot-tap-confirm cycle.",
   "source": "07-cost-and-latency §Design choices and trade-offs"
  },
  {
   "id": "q5",
   "type": "numeric",
   "kp": "cache-rules",
   "prompt": "How many cache breakpoints can one request use (public)?",
   "answer": 4,
   "unit": "breakpoints",
   "tolerance": 0,
   "explanation": "Up to 4 per request.",
   "source": "07-cost-and-latency §What it is; constants.json cache_max_breakpoints"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "cache-rules",
   "prompt": "In what order is the cacheable prefix built?",
   "choices": [
    "Tools → system prompt → messages",
    "Messages → system prompt → tools",
    "System prompt → messages → tools",
    "Any order; the API sorts it"
   ],
   "answer": 0,
   "explanation": "The fixed order means stable content (tools, system) is always earliest.",
   "source": "07-cost-and-latency §What it is"
  },
  {
   "id": "q7",
   "type": "tf",
   "kp": "cache-rules",
   "prompt": "Editing the system prompt mid-task invalidates the cache for every later block.",
   "answer": true,
   "explanation": "Changing any block at or before a breakpoint changes the prefix, so the next request misses.",
   "source": "07-cost-and-latency §What it is"
  },
  {
   "id": "q8",
   "type": "numeric",
   "kp": "cache-rules",
   "prompt": "What is the default cache lifetime in minutes (public)?",
   "answer": 5,
   "unit": "min",
   "tolerance": 0,
   "explanation": "Each use refreshes it at no extra cost; a 1 h lifetime is optional.",
   "source": "07-cost-and-latency §What it is; constants.json cache_ttl_default"
  },
  {
   "id": "q9",
   "type": "tf",
   "kp": "cache-rules",
   "prompt": "Caching changes the model's answer because it sees a compressed prompt.",
   "answer": false,
   "explanation": "Caching re-uses processed input; the model sees the same prompt.",
   "source": "07-cost-and-latency §Common confusions"
  },
  {
   "id": "q10",
   "type": "numeric",
   "kp": "cache-prices",
   "prompt": "What multiplier on base input price does a cache **read** cost (public, most models)?",
   "answer": 0.1,
   "unit": "×",
   "tolerance": 0.01,
   "explanation": "Reads cost 0.1×, which is where the savings come from.",
   "source": "07-cost-and-latency §What it is; constants.json cache_read_multiplier"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "cache-prices",
   "prompt": "Which costs the most per token?",
   "choices": [
    "A 1 h cache write",
    "A 5 min cache write",
    "A cache read",
    "An uncached input token"
   ],
   "answer": 0,
   "explanation": "1 h write is 2×, 5 min write 1.25×, uncached 1×, read 0.1×.",
   "source": "07-cost-and-latency §What it is; constants.json cache_write_1h_multiplier"
  },
  {
   "id": "q12",
   "type": "tf",
   "kp": "cache-prices",
   "prompt": "Caching saves money from the very first call of a task.",
   "answer": false,
   "explanation": "The first call pays the 1.25× write on the whole prefix; caching pays back from the second call on.",
   "source": "07-cost-and-latency §How it works (caching arithmetic)"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "cache-prices",
   "prompt": "Tasks recur only a few times a day. Is the 1 h lifetime worth it?",
   "choices": [
    "Probably not: it costs more per write and pays only if tasks recur within the hour",
    "Yes: it is always cheaper",
    "Yes: reads become free",
    "It makes no difference"
   ],
   "answer": 0,
   "explanation": "Choose cache lifetime against how often tasks recur.",
   "source": "07-cost-and-latency §Design choices and trade-offs"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "breakpoints-pruning",
   "prompt": "Why does the vendor suggest pruning screenshots in batches rather than every turn?",
   "choices": [
    "Dropping the oldest screenshot changes an early block, so everything after it misses the cache",
    "Pruning is rate-limited by the API",
    "Batches use fewer breakpoints",
    "Old screenshots improve grounding"
   ],
   "answer": 0,
   "explanation": "Batch pruning keeps the prefix byte-identical between prunes.",
   "source": "07-cost-and-latency §How it works"
  },
  {
   "id": "q15",
   "type": "numeric",
   "kp": "breakpoints-pruning",
   "prompt": "Every how many turns does the vendor suggest pruning screenshot history (public)?",
   "answer": 25,
   "unit": "turns",
   "tolerance": 0,
   "explanation": "Keep the last 3 screenshots and prune every 25 turns.",
   "source": "07-cost-and-latency §How it works; constants.json cu_prune_interval"
  },
  {
   "id": "q16",
   "type": "tf",
   "kp": "breakpoints-pruning",
   "prompt": "The recommended placement is one breakpoint after the system prompt and tools, and up to three more on the latest tool results, advanced each turn.",
   "answer": true,
   "explanation": "The stable part always hits and most of the history hits too.",
   "source": "07-cost-and-latency §How it works"
  },
  {
   "id": "q17",
   "type": "numeric",
   "kp": "caching-arithmetic",
   "prompt": "A vision call has 5 500 tokens read from cache at 0.1× and 1 500 new tokens written at 1.25×. Cost in base-input-token units = 5 500×0.1 + 1 500×1.25?",
   "answer": 2425,
   "unit": "token units",
   "tolerance": 10,
   "explanation": "My arithmetic: 550 + 1875 = 2425, against 7 000 uncached.",
   "source": "07-cost-and-latency §How it works (caching arithmetic); constants.json vision_call_tokens_illustrative, cache_read_multiplier, cache_write_5m_multiplier"
  },
  {
   "id": "q18",
   "type": "numeric",
   "kp": "caching-arithmetic",
   "prompt": "Using 2425 cached units against 7 000 uncached, what percentage of the uncached cost is the cached call (2425 ÷ 7000 × 100)?",
   "answer": 35,
   "unit": "%",
   "tolerance": 1,
   "explanation": "About 35 % (my arithmetic).",
   "source": "07-cost-and-latency §How it works (caching arithmetic)"
  },
  {
   "id": "q19",
   "type": "tf",
   "kp": "caching-arithmetic",
   "prompt": "Every call in a task hits the cache.",
   "answer": false,
   "explanation": "The first call writes, early-block edits miss, and an idle gap longer than the lifetime misses.",
   "source": "07-cost-and-latency §Common confusions"
  },
  {
   "id": "q20",
   "type": "mcq",
   "kp": "model-tiers",
   "prompt": "Why does prompt caching matter more than reply length for this workload?",
   "choices": [
    "Output tokens are few (short tool calls), so input tokens dominate cost",
    "Output tokens are free",
    "Caching also shortens replies",
    "Replies are cached too"
   ],
   "answer": 0,
   "explanation": "Output costs 5× input per token, but there are far fewer output tokens.",
   "source": "07-cost-and-latency §How it works (model tiers)"
  },
  {
   "id": "q21",
   "type": "numeric",
   "kp": "model-tiers",
   "prompt": "On every model in the public price table, output price ÷ input price is…",
   "answer": 5,
   "unit": "×",
   "tolerance": 0,
   "explanation": "A constant 5× ratio (public price table).",
   "source": "07-cost-and-latency §How it works (model tiers); constants.json price_output_to_input_ratio"
  },
  {
   "id": "q22",
   "type": "mcq",
   "kp": "model-tiers",
   "prompt": "Using the strong tier on every node would…",
   "choices": [
    "Give fewer wrong routes but multiply the cost of the many specialist calls",
    "Lower cost because fewer calls are needed",
    "Make caching unnecessary",
    "Have no effect on cost"
   ],
   "answer": 0,
   "explanation": "Measure both success and cost per task before choosing (see 09).",
   "source": "07-cost-and-latency §Design choices and trade-offs"
  }
 ]
});
