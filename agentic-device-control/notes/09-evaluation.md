# 09 — Evaluation: success rate, steps, cost, and a failure taxonomy

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Wilson score interval, E. B. Wilson, "Probable inference, the law of succession, and statistical inference", JASA 22 (1927), https://doi.org/10.1080/01621459.1927.10502953; ReAct, Yao et al. 2022, https://arxiv.org/abs/2210.03629 · **Status:** concept primer. Caution: every task count and rate below is illustrative.

## In one sentence
Evaluate an agent by running a fixed task suite many times and reporting four things together — success rate with a confidence interval, steps per task, cost per task, and the count of each failure class — because any one of them alone hides the trade-off.

## What it is
An **evaluation suite** is a fixed list of tasks, each with a start state and a success check. The success check is decided in advance and does not ask the agent: for example, "the foreground app is the video app and its search field contains the title", read from device state.

The four metrics:

| Metric | Definition | Why it is needed |
|---|---|---|
| Task success rate | successful runs ÷ runs, with a confidence interval | the headline, but blind to cost |
| Steps per task | model calls per run, as a distribution | drives latency and cost; a rising tail shows looping |
| Cost per task | input and output tokens per run, priced | decides whether the agent is affordable ([[07-cost-and-latency]]) |
| Failure taxonomy | count of failed runs per failure class | tells you what to fix next |

## How it works
**Run each task many times.** The agent is not deterministic ([[03-the-orchestrator]]), so one run per task says little. Reset the device to the start state before each run.

**Put an interval on the success rate.** Use the Wilson score interval (Wilson 1927); it behaves well for small samples and for rates near 0 or 1. Illustrative example: 40 successes in 50 runs is 80 %, with a 95 % Wilson interval of about 67 % to 89 % (my arithmetic). Two agents whose intervals overlap this much are not shown to differ.

**Why per-step reliability compounds.** If each step succeeds with probability p and a task needs n steps without recovery, the task succeeds with probability pⁿ. Illustrative: p = 0.9 and n = 5 gives 0.9⁵ ≈ 0.59 (my arithmetic). Recovery ([[06-the-react-loop]]) breaks this product, which is why the observe-and-retry loop matters more than raw click accuracy for long tasks.

**Classify every failure.** A generic taxonomy for device agents:

| Class | What happened | Usual fix |
|---|---|---|
| Grounding miss | right element, wrong pixel | check the scaler; use zoom ([[04-the-vision-specialist]]) |
| Wrong element | tapped a similar-looking element | more specific instruction; instruction before image |
| Wrong route | orchestrator chose the wrong specialist | prompt or tier change ([[03-the-orchestrator]]) |
| Premature FINISH | claimed success without evidence | evidence-based stop rule |
| Stuck loop | repeated action, unchanged screen | loop detection ([[06-the-react-loop]]) |
| Unexpected UI | dialog, update prompt, notification | recovery prompt; reset state |
| Unsafe action refused | allow-list or gate blocked a call | intended; review whether the task needs the tool ([[08-safety]]) |
| Infrastructure | BUSY, TIMEOUT, message lost, capture consent missing | message-path guards ([[01-the-message-path]]) |

Keep infrastructure failures separate from agent failures; mixing them blames the model for a lost message.

## Design choices and trade-offs
- **Report success and cost together.** A stronger model tier can raise the success rate and double the cost. Plot success against cost per task and choose the knee.
- **Fixed suite, then fresh tasks.** A fixed suite measures change between versions. Fresh tasks measure generality. Use both, and never tune prompts on the suite you report.
- **Device-state success checks over agent self-reports.** The agent's own "done" is the thing under test.
- **Compare with a script.** For each journey, record the scripted-automation cost and success. The agent wins where UI change breaks scripts often; the script wins where the journey is stable ([[00-why-cloud-initiated-device-agents]]).

## Common confusions
- **"The demo worked, so it works."** One run is a sample of one from a random process.
- **"Success rate is the only number."** Without steps and cost, a looping agent that eventually succeeds looks perfect.
- **"Failures are noise."** Failures are the most informative output; classify every one.
- **"Benchmark results transfer."** Public results such as ReAct's (Yao et al. 2022) are on their own benchmarks; measure on your own devices and apps.

## Why it matters
Without an evaluation suite, every prompt change is a guess. With one, each change becomes a measured move on four axes, and the failure taxonomy points at the next fix.

## Terms introduced
- **evaluation suite** — a fixed list of tasks with start states and predefined success checks.
- **task success rate** — the fraction of runs that pass the success check.
- **Wilson score interval** — a confidence interval for a proportion that stays sensible at small n and near 0 or 1.
- **steps per task** — model calls in one run; reported as a distribution.
- **cost per task** — priced tokens in one run.
- **failure taxonomy** — the fixed list of failure classes into which every failed run is sorted.
