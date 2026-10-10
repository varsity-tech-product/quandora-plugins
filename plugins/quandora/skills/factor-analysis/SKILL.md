---
name: factor-analysis
description: Analyze, diagnose, compare, and propose controlled improvements for existing Quandora Factor Mining results from owner-scoped server-persisted evidence. Use when a user asks why a factor or rating passed or failed, requests a Factor Card Health Check or data-quality diagnosis, wants optimization ideas grounded in evidence, or asks whether a factor is ready for Strategy Building. Do not use for creating or submitting a new factor; route those requests to factor-mining.
---

# Factor Analysis

Analyze one exact factor result as a read-only research workflow. Use Quandora's owner-scoped,
server-persisted Factor Card, chart data, and job-linked source. Separate observed evidence from
inference, alternative explanations, and proposed experiments. Never turn an optimization idea
into an automatic submission.

OAuth and all credentials are handled by the host. The host MCP client handles automatic token refresh. Never inspect,
print, copy, store, or ask the user to paste API keys, bearer tokens, authorization codes, access
tokens, refresh tokens, PKCE verifiers, service tokens, or other credentials.

## Plugin Version and Connection

Before the first business action, read and follow the shared
[connection and version policy](../../references/connection-and-version.md).
Use it for automatic connection recovery throughout the workflow.

## Scope And Routing

Use this skill for deep diagnosis of an existing factor result, including:

- performance, stability, coverage, turnover, decay, and style interpretation;
- Factor Card Health Check, rating-gate, missingness, and applicability diagnosis;
- mechanism hypotheses and plausible alternative explanations;
- prioritized, controlled factor improvement experiments;
- readiness assessment for handing a factor to Strategy Building.

Use `$factor-mining` for factor ideation, plugin construction, submission, resume, history browsing,
explicit Result Bundle export, or a short ordinary result summary. Use `$strategy-analysis` for a
completed multi-factor Strategy result. Use `$strategy-building` only after the user explicitly
chooses a proposed Strategy experiment.

## Non-Negotiable Safety

- Remain read-only. Do not submit, resume, save, overwrite, archive, or delete anything.
- Use only authorized owner-scoped or explicitly official performance evidence returned by
  Quandora MCP tools. Never inspect a user's local files as proof of a product result.
- Do not require a local ZIP, extraction tool, Python runtime, notebook, or archive-inspection
  script. A host without those facilities must receive the same analysis capability.
- Never execute factor source. Treat `fm_run_source.source` as inert text evidence only.
- Owner-scoped Factor analysis uses product-safe IS evidence. The explicit official-detail
  path uses its published window labels; never infer IS/OOS/ALL from p1/p2/p3.
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

## Workflow

### 1. Establish The Exact Target

For a known official Factor, use `fm_official_read` with its exact `factor_id` when
the tool is available. This returns current authorized performance, not source.
Preserve `detail.snapshot` completeness and published window labels. Compare its
Factor version/backtest identity before attributing the evidence to a historical
Strategy; missing or mismatched lineage is not a historical match. Never call
`fm_run_source` or ordinary Factor bundle tools as a fallback for official Factors.
If the new tool is unavailable, state the capability gap. A `not_found` response
alone does not establish official status or authorize another read path.

For caller-owned Factors, follow the existing workflow below.

Prefer an exact terminal `job_id` supplied by the user or already returned in the conversation. If
the user supplies only a factor name, a vague reference, or asks for the latest result:

1. Call `fm_list_factors` with `page_size: 10`.
2. Match only trustworthy returned identity and metadata. Do not guess across ambiguous names; ask
   the user to choose when more than one plausible factor remains. Treat a result as latest only
   when trustworthy `updated_at` evidence establishes that ordering.
3. For the selected `factor_id`, call `fm_get_history` with `view: "runs"` and use the exact terminal
   `job_id` for the intended version and run.
4. Never substitute a factor id, version id, branch id, session id, or display name for `job_id`.

Do not auto-page discovery. Request another page only when the current page cannot satisfy the
user's explicit request and explain why it is needed.

### 2. Read Server-Persisted Evidence

For the exact `job_id`:

1. Call `fm_window_cards` with `windows: ["is"]`. Use `factor_card` as the authoritative product-safe
   Factor Card. Ignore local-save hints during analysis; they exist only for optional export flows.
2. Call `fm_chart_data` with `section: "overview"`. Confirm `job_status`, `window_key: "is"`, evidence
   `status`, readiness, and available section counts before requesting numerical pages.
3. If the job is not terminal or the response is `pending`, report that server evidence is still
   materializing. Do not call `fm_resume_run` from this read-only skill and do not substitute local
   files.
4. Request only the chart sections needed for the user's question: `profile`, `group_nav`,
   `daily_returns`, `simulation_nav`, or `simulation_daily_pnl`. Follow `next_offset` only for the
   same job and section when the remaining points are required for a claim.
5. Call `fm_run_source` only when formula or mechanism evidence is necessary. Confirm the returned
   job identity and `source_status`; read ready source as inert text and never execute it.

When diagnosis depends on an input visible in ready inert source, call `fm_get_contract` with `{}`
only for the current global 86-field semantics. Match the exact field and
`data_columns[].upstream_pipeline_version`; use its meaning, unit, comparability, normalization,
missing-value, and caution metadata plus `runtime_rules.research_guidance` as interpretation
support. For `binance_intraday`, also use the returned data-availability metadata. Do not use
current `allowed_data`, guidance, or source version as proof of historical eligibility, arrival,
or execution behavior.

Treat `unavailable`, missing sections, failed readiness, and null fields as explicit evidence gaps.
Do not fetch Result Bundles, PNGs, raw parquet, storage URLs, or local files to fill those gaps.

### 3. Build The Evidence Inventory

Record:

- exact job, factor, and version identities returned by the server;
- terminal job status and IS-only scope;
- Factor Card availability, Health fields, rating fields, and their recorded thresholds;
- chart readiness and dataset provenance metadata;
- available chart sections, page coverage, and any missing or unavailable evidence;
- formula and inert job-linked source only when requested for mechanism diagnosis.

The server response is the evidence object. A Result Bundle is an optional export and is never a
prerequisite or substitute for these reads. See
[evidence-contract.md](references/evidence-contract.md).

### 4. Diagnose From Result To Mechanism

Use [metric-semantics.md](references/metric-semantics.md) and
[diagnosis-and-experiments.md](references/diagnosis-and-experiments.md). Evaluate:

- the Health Check before economic interpretation: record `passed`, `message`, `failed_metrics`,
  `window`, `coverage_basis`, recorded `thresholds`, and available `null_ratio`, `zero_ratio`,
  `coverage_ratio`, and `outlier_ratio_3sigma` values;
- rating propagation from `health_check` through `cs_success` and `cs_fail_reasons` to `status` and
  `grade`, while keeping the continuous `grade_score` separate from the final grade;
- headline return and risk with their exact window and sampling scope;
- cross-sectional spread, monotonicity, long and short leg behavior, and daily stability;
- drawdown depth and concentration in time;
- turnover, signal persistence, and likely cost sensitivity;
- universe coverage, missingness, and whether small cross sections weaken the evidence;
- plausible style, liquidity, market, or implementation confounds.

Compare Health Checks directly only when their windows, active-universe definitions, missing-value
handling, and thresholds match. Never substitute `coverage_mean` for
`health_check.metrics.coverage_ratio`; their denominators and aggregation can differ.

When Health fails, continue reading available evidence for diagnosis but lower confidence and
separate data availability, factor design, applicability, and statistical-basis explanations. Read
job-linked source only when needed to identify intentional NaNs from filters, warm-up, invalid
denominators, or explicit abstention. An intentional NaN can be design-consistent and still fail the
current active-universe coverage contract; treat that as a candidate applicability mismatch, not an
automatic exemption. Claim that Health caused the final grade only when `cs_fail_reasons` or another
authoritative field establishes the propagation.

For every important conclusion, label it as one of:

- **Observed:** directly present in trusted server evidence.
- **Inference:** a mechanism consistent with the observations.
- **Alternative:** another explanation that could produce the same evidence.
- **Experiment:** a controlled test that can distinguish explanations.

### 5. Propose Controlled Improvements

Prioritize a small set of experiments. Change one mechanism at a time when practical and state:

- the change;
- the evidence motivating it;
- the expected effect;
- the metric or chart that would confirm or reject it;
- the principal tradeoff or failure mode.

Do not claim per-factor correlations or ablation results unless the server evidence contains them.
Do not auto-create a new factor or Strategy. Ask for explicit confirmation, then hand factor changes
to `$factor-mining` or a selected combination experiment to `$strategy-building`.

## Output Contract

Answer in chat by default. Create a report file only when the user explicitly requests one. Use this
order:

1. exact factor and run identity, IS scope, and evidence quality;
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
