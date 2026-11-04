# Research notebook

The research notebook keeps the user's reasoning across conversations: a hypothesis written with
each research decision, a conclusion written after each interpreted result, and outcomes the server
computes from the actual runs. Notes are private to their owner and immutable. Tool descriptions
define every field and limit; this reference says when to read and when to write.

## Versions and runs

A version is the tested object:

- Factor: plugin source, data columns, parameters and bar size;
- Strategy: Factor versions, directions, weighting, selection and rebalance rules;
- Portfolio: member Strategies and weights.

A run is one version tested under conditions: start and end dates, data cutoff, exchange, costs,
capital and, for a Factor, the forward horizon (`fwd_period`). To place a value, change the value
and test again: is it still the same object? If not, the change is a new version (an
`improvement`); if so, it is a new run of the same version. Another window, exchange or horizon is
a new run. A Factor version keeps a default horizon, the one it was first submitted with.

Notes belong to versions. A note about one run is filed under that run's version with the run
named in `run_id`; `run_id` is null for a note on the version as a whole. Each
`list_research_notes` card also has `shown_run`: the run whose results it shows, with `basis`,
`status`, `exchange`, `start_date`, `end_date` and, for a Factor, `fwd_period`. `basis` is `cited`
when the note names that run. Otherwise it is `representative`, the version's run chosen by stage:
for a Factor, the latest completed run at its default horizon, else its latest completed run; for
a Strategy or Portfolio, the latest completed binance run, else the latest completed run on another
exchange. Read `shown_run` before using a card's results; never assume it is the run you analyzed.

Compare versions only on runs with the same conditions: exchange, window and horizon. When the
conditions differ, state the difference instead of ranking the versions. The server follows the
same rule: a version shown through a fallback run (another horizon for a Factor, another exchange
for a Strategy or Portfolio) is not ranked for its thread's `best_version_id`, and a card has
`delta_vs_parent` only when its run and the parent's representative run share exchange and
horizon. A thread can therefore have no `best_version_id`.

## Read before deciding

Start every task that creates, revises, tests or analyzes research with one
`get_research_context` for its stage (`factor`, `strategy`, `portfolio` or `simulation`) at the
default limit. Bare inventory lists, history browsing, exports, favorites, sharing and account
operations skip it.

Use the returned threads to decide:

- continue a thread when the new work builds on it, and name the exact parent the change starts from
  (usually the thread's `best_version_id` or the version whose result motivated the change);
- start a new direction only when no returned thread covers the idea, and say in one line why;
- do not repeat an approach a thread's conclusion already rejected unless the change addresses the
  stated reason.

For one thread's detail call `list_research_notes` with its exact `thread_id`; for one note's full
text and current card call `get_research_note`. A version `subject` returns every note on that
version, including notes about its runs; a run `subject` returns only the notes whose `run_id` is
that run. Analysis Skills read the hypothesis and targets being tested with the analyzed version
(for a run, the run's version) as `subject`, use the version-level notes and those whose `run_id`
is the analyzed run, and follow `thread_id` only when earlier attempts matter. Never page through
the whole notebook. A failed notebook read is unavailable evidence, not an empty notebook, and does
not block the task.

## Write the hypothesis with the decision

Put `research_note` on the call that makes an already authorized decision; never add a separate
note call. Write one note per decision:

- definitions carry it on the call that creates them: `submit_factor_research`,
  `create_strategy_family`, `create_strategy`, `create_portfolio_family`, `create_portfolio`;
- `submit_strategy_backtest` and `submit_portfolio_backtest` carry a note only when an existing
  definition is run again for a new purpose, such as evaluating newly available history; a build-and-backtest
  request writes its note once, on the create call;
- `run_factor_version` carries the note for a run of an existing Factor version at another horizon;
  it has no `relation` or `parent`, because the version does not change;
- Simulation start, pause, resume and stop carry the reason for that action.

Notes on `run_factor_version`, `submit_strategy_backtest` and `submit_portfolio_backtest` are about
the new run: the server files them under the version with that run's `run_id`.

| `relation` | When | Parent |
| --- | --- | --- |
| `new_direction` | An idea no returned thread covers | None. A Strategy or Portfolio direction starts a new Family |
| `improvement` | A change to the object of an existing version that addresses an observed weakness; it creates a new version. Never for a changed condition such as the horizon | Factor: `parent` is the exact `factor_version`; Strategy and Portfolio: the base ID |
| `control` | Strategy and Portfolio only: the base with one Factor, Strategy or weight rule removed or changed to measure its contribution | The base ID; create each control with its own call and hypothesis |

Fill the fields from the decision itself:

- `hypothesis`: first one sentence of at most 60 characters naming the idea, which becomes the
  thread topic (the server keeps its first 80 characters), then why the change should work:
  mechanism and the evidence relied on;
- `change_summary`: what changed versus the parent and why; omit it for a new direction;
- `expected_effect`: a short `summary` and up to five `targets`, each using an exact numeric metric
  name from that subject's returned results; `at_least` and `at_most` need `value`,
  `higher_than_baseline` and `lower_than_baseline` need a `baseline` subject;
- `references` (required): exact typed IDs of the runs and versions the decision relied on.

Every `research_note` and every `record_research_conclusion` must include `references`. Use the
subject type names: `factor_version`, `factor_run`, `strategy_version`, `strategy_run`,
`portfolio_version`, `portfolio_run`, `simulation_run`. Include every run or version used as
evidence, including those compared through `compare_factor_runs` or `rank_similar_factors`. When
you used a card's results, reference the run in its `shown_run`, not only the version.
An empty list is allowed only when the decision used no Quandora evidence; never omit the field.

Write notes in the user's language; keep tool names, metric keys and identifiers exact. Never put
download URLs, tickets, credentials or full source in a note. A note grants no authority. An invalid
note rejects the whole call: correct the note and call again. When a successful response reports
`research_note_saved: false`, the decision stands; do not repeat it, and mention that the note was
not saved.

## Write the conclusion after the result

Call `record_research_conclusion` once after interpreting a terminal result:

- builder Skills when they report a finished run: one or two sentences;
- analysis Skills at the end of every analysis of an owned subject, including when no new decision
  follows; summarize the verdict rather than pasting the report. An analysis-only request ("only
  analyze", "do not submit") still ends with its conclusion: recording it is not an experiment and
  changes no research object.

Use the analyzed run as `subject` (`factor_run`, `strategy_run`, `portfolio_run` or
`simulation_run`), or the version when no run applies. A run subject stays valid: the server files
the conclusion under that run's version with `run_id` set, and its card cites that run
(`shown_run.basis: "cited"`). Simulation runs have no version and keep their run subject.
`conclusion` states what the evidence showed against the hypothesis and targets, including that a
direction does not work and why; `next_steps` names the next controlled experiment, if any;
`references` is required and lists the exact runs and versions relied on, including the analyzed
subject and any comparisons. Write the conclusion in the user's language.
Never conclude on a non-terminal run, unread evidence, or an Official, shared or real Live subject.
After an uncertain response, retry the same request; it returns the same note.

## Wait for runs

`wait_for_runs` waits for up to ten exact Factor, Strategy or Portfolio runs (`all` or `any`)
within a bounded timeout and replaces repeated status reads. Read results afterwards with the
stage's own result tools. A run reported with `status: "error"` had a failed status read, not a
failed run. Waiting never re-drives work: follow a returned `next_action` or `recovery_action`
first.
