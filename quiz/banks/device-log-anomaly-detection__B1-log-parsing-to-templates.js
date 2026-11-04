// Generated from learning/device-log-anomaly-detection/notes/B1-log-parsing-to-templates.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "B1-log-parsing-to-templates",
 "sectionTitle": "B1 — Log parsing: from raw lines to templates and parameters",
 "notePath": "../device-log-anomaly-detection/notes/B1-log-parsing-to-templates.md",
 "knowledgePoints": {
  "template-def": {
   "title": "Template, parameters, template ID",
   "summary": "A template is the constant part of a message with each parameter replaced by `<*>`; after parsing, a log is a sequence of template IDs with parameter lists.",
   "source": "B1-log-parsing-to-templates §What it is"
  },
  "mining-vs-source": {
   "title": "Data-driven mining versus source-code extraction",
   "summary": "Mining (Drain, Spell) discovers templates from sample logs; source-code extraction reads print statements and yields the complete set, at the cost of source access and upkeep.",
   "source": "B1-log-parsing-to-templates §How it works; Common confusions"
  },
  "mining-misses-errors": {
   "title": "Miners miss the rare error templates",
   "summary": "A miner finds only templates that appear in its sample; error and warning paths are rare, so they are the ones most often missed — exactly the ones anomaly detection needs.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  "drain-tree": {
   "title": "Drain's fixed-depth parse tree",
   "summary": "Drain splits by message length, then by leading tokens; a leaf holds candidate groups and a message joins the most similar group only if similarity reaches st. Spell instead uses longest common subsequence.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  "failure-modes": {
   "title": "One-to-many and many-to-one",
   "summary": "One-to-many splits one print statement into several templates (false diversity); many-to-one merges different statements into one (signal lost).",
   "source": "B1-log-parsing-to-templates §How it works; Common confusions"
  },
  "tree-matcher": {
   "title": "A parse-tree matcher for fixed templates",
   "summary": "With source-derived templates, inference is a lookup in a tree indexed by component and token count; training is separate from inference, wildcards can be partial-token, and unmatched messages go to a bucket.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  "parse-measures": {
   "title": "Accuracy, speed, coverage",
   "summary": "Accuracy needs ground-truth templates (chicken-and-egg); Drain reports large speed gains; coverage is the share of messages matched and falls when new code ships.",
   "source": "B1-log-parsing-to-templates §How it is measured or used"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "template-def",
   "prompt": "What is the template of `CTRL-EVENT-DISCONNECTED bssid=aa:bb:cc:dd:ee:ff reason=3 locally_generated=1`?",
   "choices": [
    "`CTRL-EVENT-DISCONNECTED bssid=aa:bb:cc:dd:ee:ff reason=3 locally_generated=1`",
    "`<*> <*> <*> <*>`",
    "`CTRL-EVENT-DISCONNECTED bssid=<*> reason=<*> locally_generated=<*>`",
    "`CTRL-EVENT-DISCONNECTED bssid=<*> reason=3 locally_generated=1`"
   ],
   "answer": 2,
   "explanation": "Constant words stay; every parameter position becomes `<*>`. The values `[aa:bb:..., 3, 1]` are the parameter list.",
   "source": "B1-log-parsing-to-templates §What it is"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "template-def",
   "prompt": "After parsing, a log becomes a sequence of template IDs, each with its parameter list.",
   "answer": true,
   "explanation": "This shrinks the vocabulary from millions of strings to a few hundred templates.",
   "source": "B1-log-parsing-to-templates §What it is"
  },
  {
   "id": "q3",
   "type": "tf",
   "kp": "template-def",
   "prompt": "Parameters are noise and can be discarded once the template ID is known.",
   "answer": false,
   "explanation": "Parameters carry reason codes, latencies, and signal levels that explain a fault; later stages may use them (B5).",
   "source": "B1-log-parsing-to-templates §Common confusions"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "mining-vs-source",
   "prompt": "What is the main advantage of source-code extraction over data-driven mining?",
   "choices": [
    "It needs no source access",
    "It yields the complete template set, including templates never seen in the field",
    "It tunes itself on sample logs",
    "It never needs updating"
   ],
   "answer": 1,
   "explanation": "Reading the print statements gives every template the code can produce; mining sees only what appears in the sample.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q5",
   "type": "multi",
   "kp": "mining-vs-source",
   "prompt": "Which are costs of source-code extraction?",
   "choices": [
    "It needs access to the source",
    "Someone or something must read the print statements",
    "It must be updated whenever the code changes",
    "It misses rare error paths",
    "It needs labelled faults"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Source extraction is not free; missing rare paths is the weakness of mining, not of extraction.",
   "source": "B1-log-parsing-to-templates §Common confusions"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "mining-misses-errors",
   "prompt": "Why does a data-driven miner most often miss the templates anomaly detection needs?",
   "choices": [
    "Error templates are too long to tokenise",
    "Error and warning paths are rare in normal logs, and a miner finds only what is in its sample",
    "Miners drop error-severity lines",
    "Error templates have no parameters"
   ],
   "answer": 1,
   "explanation": "A miner can only discover templates that appear; rare paths stay invisible.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q7",
   "type": "numeric",
   "kp": "mining-misses-errors",
   "prompt": "An illustrative component has 100 print statements; a miner on normal logs finds 20 templates. What percentage of the print statements has no mined template?",
   "answer": 80,
   "unit": "%",
   "tolerance": 1,
   "explanation": "(100 − 20) ÷ 100 = 80 %. The numbers are illustrative; the direction is the lesson: the missing ones are mostly error paths.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "drain-tree",
   "prompt": "What does the first layer of Drain's parse tree split messages by?",
   "choices": [
    "The first token",
    "Message length in tokens",
    "The component tag",
    "Severity"
   ],
   "answer": 1,
   "explanation": "Drain splits by token count first, then by the first few tokens; leaves hold candidate log groups.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q9",
   "type": "mcq",
   "kp": "drain-tree",
   "prompt": "In Drain, the best candidate group's similarity is below the threshold *st*. What happens?",
   "choices": [
    "The message is discarded",
    "The message joins the group anyway",
    "A new log group is created",
    "The tree depth increases"
   ],
   "answer": 2,
   "explanation": "A message joins an existing group only if its token-by-token similarity reaches *st*; otherwise it starts a new group.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q10",
   "type": "tf",
   "kp": "drain-tree",
   "prompt": "Spell matches each message to existing templates by longest common subsequence.",
   "answer": true,
   "explanation": "That is Spell's approach (Du & Li 2016); Drain uses a fixed-depth tree and a similarity threshold.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "failure-modes",
   "prompt": "A miner creates `pingTest target=GATEWAY` and `pingTest target=LOCALHOST` as two templates from one print statement. Which failure is this?",
   "choices": [
    "Many-to-one",
    "One-to-many",
    "Unmatched bucket overflow",
    "Template drift"
   ],
   "answer": 1,
   "explanation": "One statement yields several templates because a value was kept as a constant: false diversity.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "failure-modes",
   "prompt": "What is the consequence of many-to-one parsing?",
   "choices": [
    "Duplicate columns for one behaviour",
    "Different print statements collapse into one template, so signal is lost",
    "Parsing becomes slower",
    "Parameters are kept as constants"
   ],
   "answer": 1,
   "explanation": "Long parameter values make different messages look alike and they merge; no later stage can separate them again.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q13",
   "type": "tf",
   "kp": "failure-modes",
   "prompt": "More templates is always better, because each one adds detail for the model.",
   "answer": false,
   "explanation": "Duplicates from one-to-many parsing inflate the feature space and split one behaviour across several columns.",
   "source": "B1-log-parsing-to-templates §Common confusions"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "tree-matcher",
   "prompt": "Why does the matcher use partial-token wildcards such as `event=<*>`?",
   "choices": [
    "To speed up regular expressions",
    "So `event=<*>` and `error=<*>` stay two templates instead of merging into `<*>`",
    "To mask MAC addresses",
    "To reduce tree depth"
   ],
   "answer": 1,
   "explanation": "A whole-token wildcard would merge the two; keeping the constant prefix keeps them distinct.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q15",
   "type": "multi",
   "kp": "tree-matcher",
   "prompt": "Which are differences between the fleet matcher and Drain?",
   "choices": [
    "Training is separate from inference, so the template set is fixed",
    "Partial-token wildcards",
    "An unmatched bucket for review",
    "Matching by longest common subsequence",
    "Tuning *st* online on each message"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "A fixed template set keeps the feature space stable; LCS is Spell's method and online *st* tuning is the opposite of a fixed set.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "tree-matcher",
   "prompt": "Why is the tree matcher faster than testing each message against every template's regular expression?",
   "choices": [
    "It skips error lines",
    "A lookup visits only templates with the same component and token count",
    "It caches parameters",
    "It uses fewer templates"
   ],
   "answer": 1,
   "explanation": "Naive cost grows with messages × templates; the tree prunes to one component and one length first.",
   "source": "B1-log-parsing-to-templates §How it works"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "parse-measures",
   "prompt": "Why is measuring parsing accuracy a chicken-and-egg problem?",
   "choices": [
    "Accuracy needs labelled faults",
    "It needs ground-truth templates, which is the thing being built",
    "Drain has no accuracy metric",
    "Coverage is always 100 %"
   ],
   "answer": 1,
   "explanation": "Data-driven parsers tune *st* and depth against ground-truth templates; when none exist you are stuck.",
   "source": "B1-log-parsing-to-templates §How it is measured or used"
  },
  {
   "id": "q18",
   "type": "numeric",
   "kp": "parse-measures",
   "prompt": "Drain's speed evaluation used how many real data sets?",
   "answer": 5,
   "unit": "data sets",
   "tolerance": 0,
   "explanation": "He et al. 2017 report a 51.85 %–81.47 % running-time improvement on 5 real data sets with more than 10 million messages.",
   "source": "B1-log-parsing-to-templates §How it is measured or used"
  },
  {
   "id": "q19",
   "type": "tf",
   "kp": "parse-measures",
   "prompt": "A falling share of messages that match any template signals new code.",
   "answer": true,
   "explanation": "Coverage drops when print statements change or new ones appear (C2).",
   "source": "B1-log-parsing-to-templates §How it is measured or used"
  }
 ]
});
