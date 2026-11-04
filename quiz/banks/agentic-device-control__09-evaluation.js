// Generated from learning/agentic-device-control/notes/09-evaluation.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "agentic-device-control",
 "topicTitle": "Agentic control of a consumer device",
 "section": "09-evaluation",
 "sectionTitle": "09 — Evaluation: success rate, steps, cost, and a failure taxonomy",
 "notePath": "../agentic-device-control/notes/09-evaluation.md",
 "knowledgePoints": {
  "suite-and-checks": {
   "title": "Evaluation suite with device-state checks",
   "summary": "Fixed tasks with start states and success checks decided in advance and read from device state, not the agent's self-report; reset before each run.",
   "source": "09-evaluation §What it is; Design choices and trade-offs"
  },
  "four-metrics": {
   "title": "Four metrics together",
   "summary": "Success rate with interval, steps per task, cost per task, failure taxonomy; any one alone hides the trade-off.",
   "source": "09-evaluation §In one sentence; What it is"
  },
  "wilson": {
   "title": "Wilson interval on success rate",
   "summary": "Behaves well at small n and near 0 or 1; illustrative 40/50 = 80 % with 95 % interval about 67–89 %; overlapping intervals do not show a difference.",
   "source": "09-evaluation §How it works"
  },
  "compounding": {
   "title": "Per-step reliability compounds",
   "summary": "Without recovery, task success is pⁿ; illustrative 0.9^5 ≈ 0.59; recovery breaks the product.",
   "source": "09-evaluation §How it works"
  },
  "failure-taxonomy": {
   "title": "Failure taxonomy",
   "summary": "Classes such as grounding miss, wrong element, wrong route, premature FINISH, stuck loop, unexpected UI, unsafe action refused, infrastructure; keep infrastructure separate.",
   "source": "09-evaluation §How it works"
  },
  "eval-practice": {
   "title": "Evaluation practice",
   "summary": "Report success against cost and pick the knee; fixed suite plus fresh tasks; never tune on the reported suite; compare with a script; benchmarks do not transfer.",
   "source": "09-evaluation §Design choices and trade-offs; Common confusions"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "suite-and-checks",
   "prompt": "Which is a valid success check for \"open the video app and search for a title\"?",
   "choices": [
    "Device state shows the video app in front with the title in its search field",
    "The agent replies \"done\"",
    "The orchestrator returned FINISH",
    "No error status was reported"
   ],
   "answer": 0,
   "explanation": "The agent's own \"done\" is the thing under test; read the outcome from device state.",
   "source": "09-evaluation §What it is; Design choices and trade-offs"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "suite-and-checks",
   "prompt": "The device should be reset to the task's start state before each run.",
   "answer": true,
   "explanation": "Otherwise runs are not comparable.",
   "source": "09-evaluation §How it works"
  },
  {
   "id": "q3",
   "type": "multi",
   "kp": "four-metrics",
   "prompt": "Which are among the four reported metrics? Select all that apply.",
   "choices": [
    "Task success rate with a confidence interval",
    "Steps per task",
    "Cost per task",
    "Lines of prompt text"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "The fourth is the failure taxonomy.",
   "source": "09-evaluation §What it is"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "four-metrics",
   "prompt": "An agent loops many times but eventually succeeds. Which metric exposes this?",
   "choices": [
    "Steps per task (its rising tail)",
    "Task success rate",
    "The Wilson interval",
    "Count of infrastructure failures"
   ],
   "answer": 0,
   "explanation": "Without steps and cost, a looping agent that eventually succeeds looks perfect.",
   "source": "09-evaluation §What it is; Common confusions"
  },
  {
   "id": "q5",
   "type": "tf",
   "kp": "four-metrics",
   "prompt": "Steps per task should be reported as a distribution, not one number.",
   "answer": true,
   "explanation": "A rising tail shows looping.",
   "source": "09-evaluation §What it is"
  },
  {
   "id": "q6",
   "type": "numeric",
   "kp": "wilson",
   "prompt": "The illustrative evaluation has 40 successes in 50 runs. What is the success rate (40 ÷ 50 × 100)?",
   "answer": 80,
   "unit": "%",
   "tolerance": 0.5,
   "explanation": "80 %, with a 95 % Wilson interval of about 67–89 % (my arithmetic).",
   "source": "09-evaluation §How it works; constants.json eval_runs_illustrative, eval_successes_illustrative"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "wilson",
   "prompt": "Why use the Wilson score interval?",
   "choices": [
    "It behaves well for small samples and for rates near 0 or 1",
    "It is always narrower than any other interval",
    "It removes the need to repeat runs",
    "It corrects for prompt injection"
   ],
   "answer": 0,
   "explanation": "Wilson 1927; suited to small n and extreme rates.",
   "source": "09-evaluation §How it works"
  },
  {
   "id": "q8",
   "type": "tf",
   "kp": "wilson",
   "prompt": "Two agents at 80 % and 84 % on 50 runs each are shown to differ.",
   "answer": false,
   "explanation": "Intervals as wide as about 67–89 % overlap heavily, so the difference is not shown.",
   "source": "09-evaluation §How it works"
  },
  {
   "id": "q9",
   "type": "numeric",
   "kp": "compounding",
   "prompt": "Each step succeeds with probability 0.9 and a task needs 5 steps with no recovery. Task success = 0.9^5 ≈ ?",
   "answer": 0.59,
   "unit": "",
   "tolerance": 0.01,
   "explanation": "My arithmetic: 0.9^5 ≈ 0.59.",
   "source": "09-evaluation §How it works; constants.json per_step_success_illustrative, steps_without_recovery_illustrative"
  },
  {
   "id": "q10",
   "type": "mcq",
   "kp": "compounding",
   "prompt": "Why does the observe-and-retry loop matter more than raw click accuracy for long tasks?",
   "choices": [
    "Recovery breaks the pⁿ product",
    "It raises p to 1",
    "It reduces the number of steps to one",
    "It removes the need for evaluation"
   ],
   "answer": 0,
   "explanation": "Without recovery, small per-step error compounds over n steps.",
   "source": "09-evaluation §How it works"
  },
  {
   "id": "q11",
   "type": "tf",
   "kp": "compounding",
   "prompt": "Without recovery, adding steps to a task lowers its success probability even if each step is very reliable.",
   "answer": true,
   "explanation": "pⁿ falls as n rises for any p below 1.",
   "source": "09-evaluation §How it works"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "failure-taxonomy",
   "prompt": "The agent identified the correct element, but its tap landed on the wrong pixel. Which class?",
   "choices": [
    "Grounding miss",
    "Wrong route",
    "Unexpected UI",
    "Infrastructure"
   ],
   "answer": 0,
   "explanation": "Right element, wrong pixel; check the scaler, use zoom.",
   "source": "09-evaluation §How it works"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "failure-taxonomy",
   "prompt": "A run fails because screen-capture consent was missing. Which class?",
   "choices": [
    "Infrastructure",
    "Grounding miss",
    "Unsafe action refused",
    "Premature FINISH"
   ],
   "answer": 0,
   "explanation": "Infrastructure covers BUSY, TIMEOUT, lost messages and missing capture consent.",
   "source": "09-evaluation §How it works"
  },
  {
   "id": "q14",
   "type": "tf",
   "kp": "failure-taxonomy",
   "prompt": "An \"unsafe action refused\" failure is an intended outcome whose fix is to review whether the task needs the tool.",
   "answer": true,
   "explanation": "The allow-list or gate worked as designed.",
   "source": "09-evaluation §How it works"
  },
  {
   "id": "q15",
   "type": "tf",
   "kp": "failure-taxonomy",
   "prompt": "Infrastructure failures should be mixed into agent failures for a simpler dashboard.",
   "answer": false,
   "explanation": "Mixing them blames the model for a lost message.",
   "source": "09-evaluation §How it works"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "eval-practice",
   "prompt": "A stronger tier raises success and doubles cost. How should you decide?",
   "choices": [
    "Plot success against cost per task and choose the knee",
    "Always take the higher success rate",
    "Always take the lower cost",
    "Run one demo of each"
   ],
   "answer": 0,
   "explanation": "Report success and cost together.",
   "source": "09-evaluation §Design choices and trade-offs"
  },
  {
   "id": "q17",
   "type": "multi",
   "kp": "eval-practice",
   "prompt": "Which are sound evaluation practices from the note? Select all that apply.",
   "choices": [
    "Use a fixed suite and fresh tasks",
    "Never tune prompts on the suite you report",
    "Compare each journey with a scripted baseline",
    "Trust public benchmark results to transfer"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Public results such as ReAct's are on their own benchmarks; measure on your own devices.",
   "source": "09-evaluation §Design choices and trade-offs; Common confusions"
  },
  {
   "id": "q18",
   "type": "tf",
   "kp": "eval-practice",
   "prompt": "If the demo worked once, the agent works.",
   "answer": false,
   "explanation": "One run is a sample of one from a random process.",
   "source": "09-evaluation §Common confusions"
  }
 ]
});
