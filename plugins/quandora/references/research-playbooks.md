# Research call orders and similarity decisions

Use the matching order for a research goal, across the builder and analysis Skills. Bare lists,
explicit analysis-only requests and exact supplied definitions retain their scope. Read tool
schemas for `nearest_factors` and `similar_thread`; absent or `pending` means not yet measured,
and `incomplete` is partial coverage, not proof of novelty. A Factor card's `nearest_factors` is
its version's novelty at first submission, the same snapshot for every run of that version. Use
only statistics with status `ok`.
Similarity tools require completed attempt-1 runs; preserve failed or unsupported runs as evidence
gaps rather than retrying an ineligible comparison.
Follow [Research notebook](research-notebook.md) for notes, conclusions and typed `references`.

## Reference thresholds

Use the absolute mean daily Spearman correlation of Factor values (`value_abs`), which treats a
reversal as the same signal. Long-short return sign is reserved for hedge reasoning.

| Reference | Value | Interpretation |
| --- | --- | --- |
| Same signal | absolute value correlation >= 0.9 | Repeated signal |
| Related | 0.7 <= absolute value correlation < 0.9 | Related signal |
| Distinct | absolute value correlation < 0.7 | Distinct signal |
| Strategy grouping cut | `max_distance: 0.3` with `metric: "value_abs"` | At most one selected Factor per cluster |

These reference values come from one staging owner's 780 pairs with every statistic `ok`: 606
pairs had absolute value correlation below 0.3, only 13 were between 0.5 and 0.8, and 83 were at
least 0.8 (63 at least 0.9). Among the last 63, absolute IC-curve correlation had median 0.97 and
minimum 0.83. These are research defaults, not server admission rules. If another threshold fits
the goal better, state its value and reason in the decision's note.

The same reference values apply to a comparison with an official Factor. They were measured on
owned pairs only, so say so when an official comparison decides something.

A submission's nearest correlation is the larger of its nearest owned and its nearest official
absolute value correlation.
Within one task, after three consecutive Factor submissions whose nearest correlation meets the
same-signal cut, stop that direction. When an official Factor meets the cut, tell the user that
the official library already offers this signal and name that official Factor. Change direction or end the Factor search and report the
three runs and their nearest evidence. Missing or incomplete evidence cannot reset the count or
establish novelty; resolve it or report the unresolved comparison and stop the bounded search.

## New Factor direction

1. Call `get_research_context` with `stage: "factor"`. Treat threads whose `similar_thread.value_abs`
   meets the same-signal cut as one idea. Skip ideas already rejected by their conclusions unless
   the proposed change addresses the recorded reason.
2. Choose an uncovered idea; read its scoped contract through `$factor-mining`, then call
   `submit_factor_research` with `relation: "new_direction"`. In `research_note.references`, name
   the exact versions and runs read from those threads, not a thread ID typed as a version.
3. Call `wait_for_runs`, then `get_factor_backtest_window_cards` for the exact terminal run.
   Call `list_research_notes` with `subject: {type: "factor_version", id: <submitted factor_id>}`;
   it returns every note on that version. Select the hypothesis card, and read its `run_id` and
   `shown_run` to see which run it is about and which run's results it shows.
4. Read that card's `nearest_factors`, using absolute `value_mean` for its ranked rows.
   When the card or snapshot is absent, `pending` or `incomplete`, call
   `rank_similar_factors` with `order_by: "value_abs"` and page with the same selectors and returned
   token until `complete`; retain coverage. If it remains unavailable, report that gap.
   Then call `rank_similar_official_factors` for the same run with `order_by: "value_abs"` and
   page with the same candidate and returned token until `complete`; retain its coverage too.
5. Call `record_research_conclusion` with the nearest Factor and its absolute value correlation,
   or the measured empty-neighbor result or evidence gap, and the nearest official Factor
   (`official_factor_id`, name and absolute value correlation) or its gap. Its `references`
   include the analyzed run and exact neighbor runs/versions used; never invent a neighbor for
   an empty result.
6. Improve a novel, promising Factor or change direction, applying the consecutive-repeat stop
   rule above. Carry the comparison evidence into the next decision's `references`.

## Improve an existing Factor

1. Call `get_research_context` with `stage: "factor"`; select the thread's `best_version_id` as
   parent. Read `get_factor_family_history` to resolve its exact completed run at its default
   horizon and read its card with `get_factor_backtest_window_cards`.
2. Through `$factor-mining`, call `submit_factor_research` with `relation: "improvement"`, the
   exact parent and `references` to the parent run/version and motivating evidence. Change the
   object and keep the parent's horizon. State the expected metric change before submitting. To
   test only another horizon, rerun the parent with `run_factor_version` instead; it is not an
   improvement. If `run_factor_version` is not in the tool list, report the horizon test as
   unavailable.
3. Call `wait_for_runs` and read the new card with `get_factor_backtest_window_cards`, then call
   `compare_factor_runs` against the parent run only to obtain the monthly breakdown. Compare
   headline metrics only when both runs use the same horizon; otherwise state the difference
   instead of ranking them. Also apply the new-direction order's notebook-card,
   nearest-neighbor and official-Factor reads so the task's repeat count uses the nearest.
4. Call `record_research_conclusion` with both runs in `references`. If value correlation meets
   the same-signal cut and headline metrics barely moved against the stated expected effect,
   say the change did not alter the signal. Apply the repeat stop rule before another submission.

## Build a multi-factor Strategy from owned Factors

1. Call `get_research_context` with `stage: "strategy"`, then `cluster_owned_factors` with
   `metric: "value_abs"` and the Strategy grouping cut. Retain coverage and truncation evidence.
2. Call `list_eligible_strategy_factors` and, when needed, `get_eligible_strategy_factor`. Select
   at most one eligible Factor per cluster using its IS card evidence. Each unclustered Factor
   is its own group; each official Factor starts as its own group until step 3 measures it.
3. Call `compare_factor_runs` on the selected owned runs, covering every pair, and verify each
   is below the distinct-signal cut. Never send official Factors to this owner-only tool. For
   selected official Factors, call `compare_with_official_factors` once per selected owned run
   (`factor_run_id`) with the selected `official_factor_ids`, and once per selected official
   Factor (`official_factor_id`) with the other selected official Factors, so every
   owned-to-official and official-to-official pair is measured against the same cut. Replace a
   redundant selection from the returned candidates, or record a justified threshold exception.
   A missing pair or a statistic whose status is not `ok` remains unknown; do not claim distinct
   signals without the comparison.
4. Call `create_strategy_family`, or `create_strategy` for an existing Family, through
   `$strategy-building`. The note lists groups, pairwise values including the official ones, and
   any comparison that stayed unknown; its `references` list the exact compared runs and
   selection evidence, and the note text names each compared official Factor.
5. Call `submit_strategy_backtest`, then `wait_for_runs`; read `get_strategy_backtest` and analyze
   through `$strategy-analysis`. Call `record_research_conclusion` with the Strategy run and
   relied-on Factor runs in `references`.
6. Run one control per member, each removing that member with `create_strategy` and
   `relation: "control"`, then `submit_strategy_backtest` and `wait_for_runs`. Keep other rules
   and the window fixed; record any required weight renormalization. Read and compare results
   through `$strategy-analysis`; each note/conclusion references the baseline and compared runs.

## File the Factor library

1. At a Factor round's end, or after finding unfiled owned Factors through
   `list_library_folder_items`, call `cluster_owned_factors` with `metric: "value_abs"` and the
   grouping cut. Use the measured groups and state incomplete coverage.
2. Follow [Factor similarity](../skills/factor-analysis/references/factor-similarity.md): read all
   `list_library_corrections` pages first, then `list_library_folder_items` and
   `list_library_folders` for a fresh revision. Preserve corrected and user-managed placements.
3. Call `replace_factor_library_classification` with `expected_revision` and the complete agent
   placement list; use its placement notes for the grouping reasons. Read folders and items back.
   In the Factor round's `record_research_conclusion`, include the grouping decision and exact
   compared Factor runs in `references`; filing itself has no `research_note` input.
