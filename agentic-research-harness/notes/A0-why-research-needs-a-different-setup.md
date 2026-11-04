# A0 — Why research with agents needs a different setup than coding with agents

**Source:** generalised from internal methodology notes of an agentic optimization campaign, 2026 (§1 "the method in one paragraph"); Goodhart 1975 and Strathern 1997 (`pub_goodhart_year`, `pub_strathern_year`); Yao et al. 2022 (`pub_react_year`). · **Status:** concept note, no measured numbers.

## In one sentence
When an AI agent writes code, a test suite tells it whether the code is right; when an agent does optimization research, nothing tells it whether a faster number is real, so the setup must supply a judge the agent cannot touch, a record for every claim, and a memory that keeps what failed.

## What it is
This kit describes a method for running **optimization research** with AI agents. Optimization research here means a search for a change that makes one measured quantity better (lower latency, shorter end-to-end time) while the system stays correct.

An **agent** is a language model that runs in a loop: it reasons, calls a tool (read a file, run a command, submit a result), reads the tool's output, and decides the next step. ReAct (Yao et al., `pub_react_year`) named this reason–act–observe loop; the sibling kit explains it in [[../agentic-device-control/notes/06-the-react-loop|the ReAct loop note]].

Coding with agents and research with agents fail in different ways.

- **Coding.** The goal is a behaviour. A test suite, a type checker or a reviewer checks the behaviour. A wrong result usually fails a test.
- **Research.** The goal is a number. The number can be wrong in a way that no test catches: the benchmark skipped work, the output drifted, the machine was faster today. A wrong result often looks like success.

## How it works
Three failure modes make research with agents unsafe without extra structure.

1. **Claims drift.** An agent writes "the attention layer is bandwidth-bound" in its report. A second agent reads the report and builds on it. Nobody measured it. After a few sessions the shared belief has no evidence under it.
2. **Fast but wrong.** The quickest way to make a model faster is to make it do less: fewer denoising steps, a cached output, a skipped chain. Each of these is fast, plausible and wrong.
3. **Goodhart.** Goodhart (`pub_goodhart_year`) observed that a statistical regularity tends to collapse once it is used for control. Strathern (`pub_strathern_year`) restated it: "When a measure becomes a target, it ceases to be a good measure." An agent that is rewarded for a lower number optimizes the number, not the thing the number stands for.

The method answers each failure mode with one mechanism.

| Failure mode | Mechanism | Note |
|---|---|---|
| Claims drift | Every number cites an evidence record; reports are rebuilt from the records | [[B4-evidence-records]] |
| Fast but wrong | A frozen evaluator with a correctness gate, held-out inputs and negative controls | [[B2-the-frozen-evaluator]], [[B3-negative-controls]] |
| Goodhart | Agents cannot edit the evaluator; held-out inputs they cannot read; promotion by a conservative mechanical rule | [[B2-the-frozen-evaluator]], [[B7-agents-and-the-loop]] |

**The method in one paragraph.** Build a reproducible baseline and a trusted reference first. Freeze an evaluator that humans own and agents cannot change. The evaluator decides correctness against the reference, on held-out inputs, with limits calibrated from legitimate runs. It measures speed against a baseline run in the same machine state. Agents propose small candidates, each linked to a parent. The evaluator writes one evidence record per run, and nothing counts unless it cites a record. Two memories persist across rounds: a fast log of every attempt and a short curated lessons file that a planner rewrites every round, negative results included. Humans run the first rounds by hand until the evaluator has survived real candidates. Only then is the loop automated. A weekly report is built from the records and includes the spend.

Analogy: a sealed-envelope contest. The referee cannot be bribed, the test papers stay sealed until marking, decoy entries must lose, and every claim in the logbook has a page number.

## How it is used in a campaign
A **campaign** is one run of this method on one research question. The method has been used twice, and this kit uses both as examples.

- **The first campaign:** a robot foundation model (GR00T, a public NVIDIA model) ported to a cloud inference accelerator. Its results are internal; this kit keeps only the shape of its story, with illustrative numbers.
- **The scheduling topic:** a scheduler for a simulated heterogeneous robot computer. The simulator was built for a demonstration, so its numbers appear here, labelled illustrative (see [[C2-the-scheduling-topic]]).

## Common confusions
- **"A good prompt is enough."** A prompt tells an agent the rules. Only a mechanism the agent cannot change enforces them. In the first campaign an agent could argue in its report that the evaluator was wrong, but it could never edit the evaluator; a human decided.
- **"More agents find more."** More agents find more candidates. Without a judge, they also find more ways to fake a number.
- **"The method is about agents."** Most of the method would apply to a team of human researchers. The agents make it urgent, because they produce candidates faster than a human can check them.

## Why it matters
An agent can try dozens of ideas per day. Without a frozen judge and a record for every claim, it can also produce dozens of confident wrong results per day. The method turns the agent's speed into evidence a reader can trust without re-running it.

## Terms introduced
- **optimization research** — a search for a change that improves one measured quantity while the system stays correct.
- **agent** — a language model running a reason–act–observe loop with tools.
- **campaign** — one run of the method on one research question.
- **Goodhart's law** — a measure used as a target stops being a good measure (Goodhart 1975; Strathern 1997).
- **claims drift** — the growth of unmeasured beliefs as agents build on one another's reports.
- **fast but wrong** — a result that improves the metric by doing less or different work.
