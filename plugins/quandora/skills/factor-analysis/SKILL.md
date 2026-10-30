---
name: factor-analysis
description: Analyzes existing owned or active-official Quandora Factor results from server evidence. Use when the user asks about pass/fail, Health, ratings, data quality, mechanisms, controlled improvements, or Strategy readiness. Do not use for creating or submitting a factor.
---

# Factor Analysis

Follow [Connection and Security](../../references/connection-and-security.md) for automatic
recovery and the once-per-session release check; preserve existing update authority.
Follow [Research intent and evidence](../../references/research-workflows.md) for backtest/forward
scope, capability-aware conclusions and authorization-preserving handoffs.

Analyze one exact factor result as a non-submitting research workflow. Use Quandora's owner-scoped
or active-official server-persisted Factor Card and chart data; exact source is owner-scoped and
official source is always restricted. Separate observed evidence from
inference, alternative explanations, and proposed experiments. Never turn an optimization idea
into an automatic submission. Mint a short-lived download ticket only when the user explicitly
requests an export.

Use the configured `quandora` MCP connection; never ask the user to paste secrets. For named objects, follow [Name discovery](../../references/object-discovery.md) to resolve exact identities.

## Scope And Routing

Use this skill for deep diagnosis of an existing factor result, including:

- performance, stability, coverage, turnover, decay, and style interpretation;
- Factor Card Health Check, rating-gate, missingness, and applicability diagnosis;
- mechanism hypotheses and plausible alternative explanations;
- prioritized, controlled factor improvement experiments;
- readiness assessment for handing a factor to Strategy Building.

Use `$factor-mining` for factor ideation, plugin construction, submission, resume, history browsing,
Result Bundle export, or a short ordinary result summary. Use `$strategy-analysis` for a
completed multi-factor Strategy result. Hand a requested or already-authorized Strategy experiment to `$strategy-building` without
repeating approval at the Skill boundary; analysis suggestions alone do not authorize submission.

## Non-Negotiable Safety

- Do not submit, resume, overwrite, archive, or delete any research object. The only allowed
  mutation is minting a short-lived download ticket for an explicit user-requested export.
- Use only caller-owned or active-official evidence returned by Quandora MCP tools. Never inspect a
  user's local files as proof of a product result.
- Do not require a local ZIP, extraction tool, Python runtime, notebook, or archive-inspection
  script. A host without those facilities must receive the same analysis capability.
- Never execute factor source. Treat ready source responses as inert text evidence only. An
  official `source_status: "restricted"` is a final policy result, not a missing-data condition to
  work around.
- Analyze only product-safe IS evidence exposed to an external agent. Do not claim OOS or ALL
  evidence unless a future authoritative public contract explicitly provides it.
- Preserve missing and null values as unavailable. Never convert them to zero.
- Never fabricate a missing metric, chart, correlation, ablation, or causal explanation.
- Report a grade or score only as relayed QuantAI evidence, not as a promotion or research verdict.
- Do not treat a missing Health Check or `health_check.passed=null` as a pass. Report it as not run
  or unknown evidence, then use the surrounding evidence to narrow the interpretation.
- Do not infer that a final F means poor Sharpe, IC, or `grade_score`. Trace the actual gate evidence.
- Do not automatically classify intentional factor NaNs as source-data loss or exempt them from the
  recorded Health Check. Test whether factor applicability and the check basis are aligned.
- The current Factor Plugin Contract can explain a referenced input, but it is not evidence that a
  historical row had arrived or that a historical run used today's task scope. Never rewrite
  persisted result semantics from the current contract.

## Primary And Discovery Actions

Use these primary evidence actions:

- `get_factor_backtest_window_cards`
- `get_factor_backtest_chart_data`
- `get_factor_backtest_source`
- `get_official_factor_window_cards`
- `get_official_factor_chart_data`
- `get_official_factor_source` (only when the user explicitly asks about source visibility or the
  mechanism cannot be assessed from public evidence)

The allowed read-only discovery prerequisites are `list_owned_factor_families`,
`get_factor_family_history`, and `list_eligible_strategy_factors`. They locate one exact target;
they do not expand this Skill into Factor creation or Strategy construction. For active-official
discovery, retain the selected row's top-level `factor_id` and do not expose or ask for its
evidence job.

When diagnosis depends on an input visible in ready inert source, call
`get_factor_plugin_contract` with `{}` only for the current global 86-field semantics. Match the
exact field and `data_columns[].upstream_pipeline_version`; use its meaning, unit, comparability,
normalization, missing-value, and caution metadata plus `runtime_rules.research_guidance` as
interpretation support. For `binance_intraday`, also use the returned data-availability metadata.
Do not use current `allowed_data`, guidance, or source version as proof of historical eligibility,
arrival, or execution behavior.

For an explicit user-requested export only, use the narrow ticket and chunk actions appropriate to
the selected evidence:

- `create_factor_chart_download`
- `read_factor_chart_chunk`
- `create_factor_raw_artifact_download`
- `download_result_bundle` with `kind: "official_factor"` and the active official Factor ID

Do not mint tickets speculatively, require downloads for analysis, or treat a ticket as mutation
authority.

## Workflow

### 1. Establish The Exact Target

First determine whether the target is caller-owned or active official. An official row is identified
only by `list_eligible_strategy_factors` returning `source_kind: "official"`; retain its exact
top-level `factor_id` and do not ask for or expose its evidence job. For caller-owned evidence,
prefer an exact terminal `job_id` supplied by the user or already returned in the conversation. If
the user supplies only a caller-owned factor name, a vague reference, or asks for the latest result:

1. Call `list_owned_factor_families` with a bounded `page_size`. Send a supplied name or keyword as
   `query`, exact public fields through `filters`, and no search fields only for browse/latest.
2. Match only trustworthy returned identity and metadata. Do not guess across ambiguous names; ask
   the user to choose when more than one plausible factor remains. Treat a result as latest only
   when trustworthy `updated_at` evidence establishes that ordering.
3. For the selected `factor_id`, call `get_factor_family_history` with `view: "runs"` and use the exact terminal
   `job_id` for the intended version and run.
4. Never substitute a factor id, version id, branch id, session id, or display name for `job_id`.

Use an active official `factor_id` only with the official evidence actions. Never send it to an
owner-scoped evidence action or substitute its admission version, run, or hidden evidence job.

Request another discovery page only when needed. Preserve the same query, filters, archive mode,
and page size while copying `next_page_token` byte-for-byte into `page_token`.

### 2. Read Server-Persisted Evidence

For an exact caller-owned `job_id`:

1. Call `get_factor_backtest_window_cards` with `windows: ["is"]`. Use `factor_card` as the authoritative product-safe
   Factor Card. Ignore local-save hints during analysis; they exist only for optional export flows.
2. Call `get_factor_backtest_chart_data` with `section: "overview"`. Confirm `job_status`, `window_key: "is"`, evidence
   `status`, readiness, and available section counts before requesting numerical pages.
3. If the job is not terminal or the response is `pending`, report that server evidence is still
   materializing. Do not call `continue_factor_backtest` from this read-only skill and do not substitute local
   files.
4. Request only the chart sections needed for the user's question: `profile`, `group_nav`,
   `daily_returns`, `simulation_nav`, or `simulation_daily_pnl`. Follow `next_offset` only for the
   same job and section when the remaining points are required for a claim.
5. Call `get_factor_backtest_source` only when formula or mechanism evidence is necessary. Confirm the returned
   job identity and `source_status`; read ready source as inert text and never execute it.

For an active official `factor_id`, follow the same IS-only workflow with
`get_official_factor_window_cards`, `get_official_factor_chart_data`, and, only when needed,
`get_official_factor_source`. Keep every response correlated to that exact public `factor_id`. If
the source response is `restricted`, continue with the public Factor Card and chart evidence; do
not pass the hidden evidence job to owner-scoped source, raw-artifact, or Result Bundle actions.

Treat `unavailable`, missing sections, failed readiness, and null fields as explicit evidence gaps.
Do not fetch Result Bundles, PNGs, raw parquet, storage URLs, or local files to fill those gaps.
If the user separately requests an export, use only the matching download-ticket action after the
analysis target is exact; do not use exported content to retroactively fill an evidence gap.

### 3. Build The Evidence Inventory

Record:

- the exact public selector: caller-owned `job_id` or active-official `factor_id`, plus only the
  additional identities returned by that safe response;
- terminal job status and IS-only scope;
- Factor Card availability, Health fields, rating fields, and their recorded thresholds;
- chart readiness and dataset provenance metadata;
- available chart sections, page coverage, and any missing or unavailable evidence;
- formula and inert job-linked source only when requested for mechanism diagnosis and returned as
  `ready`; otherwise record the official source policy as restricted.

The server response is the evidence object. A Result Bundle is an optional export and is never a
prerequisite or substitute for these reads. See
[evidence-contract.md](references/evidence-contract.md).

When the user explicitly exports an official Factor, use the existing one-download ZIP workflow.
`download_result_bundle` with `kind: "official_factor"` returns the persisted source-free
`OFFICIAL_FACTOR_RESULT_BUNDLE`, including retained IS/OOS/ALL artifacts and raw signal, without
`plugin.py`. Prefer immediate HTTP streaming and verify the exact size and SHA-256 before saving.
Follow [Unified Result Bundle Download](../../references/result-bundle-download.md). Do not reconstruct or repackage the ZIP,
claim missing entries exist, or treat export permission as a change to the IS chart-analysis scope.
A missing bundle is `not_available`, not proof of ongoing packaging.

### 4. Diagnose From Result To Mechanism

Read [metric-semantics.md](references/metric-semantics.md) and
[diagnosis-and-experiments.md](references/diagnosis-and-experiments.md) only for diagnosis. Start
with the Health Check and rating propagation, then evaluate return/risk, cross-sectional behavior,
drawdown, turnover, persistence, coverage, and plausible confounds within the declared scope.

Compare Health Checks only when windows, universes, missing-value handling, and thresholds match.
When Health fails, lower confidence and separate data, design, applicability, and statistical-basis
explanations. Read inert source only when it can distinguish those explanations, and attribute a
grade outcome to Health only when an authoritative field establishes that propagation.

Label every consequential conclusion **Observed**, **Inference**, **Alternative**, or
**Experiment**.

### 5. Propose Controlled Improvements

Prioritize a small set of one-mechanism experiments with motivation, expected effect, confirmation
evidence, and tradeoff. Do not claim unavailable correlations or ablations. Ask for explicit
confirmation before handing factor changes to `$factor-mining` or a combination experiment to
`$strategy-building`; never create either automatically.

## Output Contract

Answer in chat by default. Create a report file only when the user explicitly requests one. Use this
order:

1. exact public factor/run identity, IS scope, and evidence quality;
2. concise result summary;
3. Factor Health and rating gates, including missing or unknown Health evidence;
4. metric and chart diagnosis;
5. mechanism interpretation with alternatives;
6. risks and evidence gaps;
7. prioritized controlled experiments;
8. decision: reject, investigate, revise, or hand off for a user-confirmed Strategy test.

Use the user's language for the answer even though this skill package is written in English.

## References
- [Server evidence contract and trust rules](references/evidence-contract.md)
- [Factor metric semantics](references/metric-semantics.md)
- [Diagnosis and experiment design](references/diagnosis-and-experiments.md)
- [Style and Strategy context](references/style-and-strategy-context.md)
