# Factor Similarity and LibraryFolder Filing

Three read-only tools compare the caller's own Factors using correlations the server computes.
The server sorts and groups, but it never sets a threshold or delivers a verdict. A label such as
"duplicate", "redundant" or "hedge" is your inference: state the statistic, its value and its
`status` next to it.

Use [Research playbooks](../../../references/research-playbooks.md) for when to call these tools,
reference thresholds and the consecutive-repeat stop rule.

## Inputs

- A candidate is one completed attempt-1 FactorRun of a caller-owned Factor, passed as
  `factor_run_id`. Take it from `get_factor_family_history` with `view: "runs"` (the row's
  `factor_run_id`, which equals its `job_id`) or from a returned backtest `run.run_id`.
- A retest run, another owner's run, a shared run or an official Factor makes the whole call fail
  with `not_found`. A candidate that is not done fails with `conflict`. Official Factors cannot be
  compared.
- Rows identify Factors as `{factor_family_id, factor_id, factor_run_id, primary_horizon}`.
  `factor_id` is the immutable Factor.

## Which tool

- `rank_similar_factors`: "which of my Factors is this most like?" It compares the candidate with
  each other owned Factor version through that version's representative run: its latest completed
  run at the version's default horizon, else its latest completed run. A rerun at another horizon
  does not replace it. Read each row's `factor_run_id` and `primary_horizon` to see which run was
  compared. It sorts by `order_by`:
  - `value_abs` (default): |mean daily Spearman of the two factor values|. Use it for "is this the
    same signal"; a reversed Factor counts as the same signal flipped. Factor values do not depend
    on the horizon, so this ordering holds across horizons.
  - `ic_abs`: |Pearson of the two daily Rank IC curves|. Use it for "does it predict at the same
    times". When the two runs' horizons differ, the curves use `ret_1d` (see `ic_curve.label`).
  - `long_short`: signed Pearson of the two long-short daily returns. A negative value means the two
    portfolios hedge each other. These returns depend on each run's horizon: do not rank rows
    whose `primary_horizon` differs from the candidate's; state the difference instead.

  Archived Families are left out unless `include_archived` is true. While `complete` is false, the
  rows cover only `coverage.compared` of `coverage.eligible` Factors. Call again with the same
  `factor_run_id` and `include_archived` and the returned `next_page_token` (byte-for-byte as
  `page_token`) until `complete` is true before saying which Factor is most similar. `excluded`
  counts Factors left out by status.
- `compare_factor_runs`: compares the candidate with chosen runs (`other_factor_run_ids`, 1–50) or
  pages through `all_owned`, which uses the same representative-run targets. With exactly one explicit
  target, `monthly` adds a 24-month IS breakdown; use it to tell a stable relation from one that
  holds only in some months.
- `cluster_owned_factors`: groups every owned Factor from stored pairs at a `max_distance` that you
  choose and explain. The distance is 1 − |correlation|, or 1 − correlation for `long_short`. Every
  two members of a cluster are within the cut; for example, `value_abs` with 0.3 means every pair
  has |value correlation| ≥ 0.7. Report `coverage.pairs_present` against `pairs_needed`, because a
  missing pair keeps two Factors apart. Also report `truncated` and `unclustered`. The `medoid` is
  the most central member by distance, not the best performer.

## Reading a pair

Each statistic has its own `status`. Use a statistic only when it is `ok`, and keep `null` as
unavailable.

| Statistic | Meaning |
| --- | --- |
| `value` | Mean (`mean`) and spread (`std`) of the daily Spearman between the two factor values on common symbols, with `days` and `mean_common_symbols` |
| `ic_curve` | Pearson of the two daily Rank IC series. `label` is `primary_horizon` when both runs share it, otherwise `ret_1d` |
| `long_short` | Pearson of the two long-short daily returns, each oriented by its own IS direction |

| Status | Meaning |
| --- | --- |
| `ok` | The statistic is present |
| `insufficient_overlap` | Fewer than 120 common valid days, or a constant series |
| `source_unavailable` | A source artifact could not be read; a later call may succeed |
| `run_not_completed` | The explicit target run is not done |

- An exact reverse gives `value` ≈ −1 and `ic_curve` ≈ −1, but `long_short` ≈ +1.
- `same_factor_family` and `direct_lineage` (`parent` or `child`) say whether the pair is related
  lineage rather than an independent idea.
- All statistics use the IS window (2022-01-01 to 2023-12-31). They say nothing about OOS behavior.

## Filing groups into factor LibraryFolders

File when the research needs it; choose groups from the research context and returned evidence.

1. Propose the folders: a name, a one-line description, and the members of each, plus the metric,
   the cut, each cluster's `max_internal_distance`, and its medoid.
2. Read every `list_library_corrections` page with `scope: "factors"`. Treat each correction as a
   constraint, and never move a corrected Factor back.
3. Read `list_library_folder_items` with `scope: "factors"` to see current placements and their
   provenance. Then read `list_library_folders` with `scope: "factors"` for a fresh `revision`.
4. Call `replace_factor_library_classification` once with `scope: "factors"`, `expected_revision`,
   the complete agent-managed `folders`, and every agent placement that should exist afterwards.
   Each placement is `{item_id, folder_name, note}`, where `item_id` is the member's `factor_id` and
   the note explains why it belongs there. The call replaces the whole agent classification: agent
   placements left out return to unfiled, so keep the existing ones you want.
5. User-managed folders and user placements never change. Works the user placed come back in
   `skipped`; report them. Set `override_user_placements` only if the user explicitly asked to
   reclassify everything, and report `overridden`. At most 20 folders fit, user-managed ones
   included.
6. On a revision conflict, reread `list_library_folders` once and retry once. Then read the
   folders and items back and report what changed.
