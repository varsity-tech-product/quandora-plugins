---
name: paper-trading
description: Use when the user asks for simulated trading, paper trading, current Paper PnL or assets, Paper positions/fills/funding/equity/code, stopping a Paper run, or a Strategy Portfolio Paper workflow on Quandora. Use strategy-building for factor selection and Strategy creation or backtests.
---

# Quandora Paper Trading

Bundled plugin version: 3.1-preview

Use this skill through the authenticated `quandora` MCP connection. It operates only on
the current user's product-safe StrategyRun, Paper run, and Strategy Portfolio handles. It is
simulated trading and must never be described as live-money trading.

Route requests for simulated trading, paper trading, current Paper assets/PnL, Paper history,
or Portfolio Paper here directly. Factor selection, Strategy composition or revision, and Strategy
backtests always belong to `$strategy-building` and use its `sb_*` tools. If no eligible source
exists, hand off to Strategy Building; do not prepare one in this skill.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask the user to paste
API keys, bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens,
account credentials, or any other secret.

## Plugin Version Reminder

On the first entry into any Quandora skill in the current conversation, if the conversation history
does not already contain one successful `qd_plugin_ver` call and no earlier version-check
attempt has occurred, call it once before the business entry point. Pass `3.0-preview` verbatim as
`installed_version`; treat it as an opaque release label and never parse, order, or normalize it.

- If `update_available=false`, continue silently.
- If `update_available=true`, say exactly: `The latest Quandora plugin version is <latest_version>. Please update the plugin.` Then say: `A Quandora MCP access token is valid for 7 days. After 7 days, use the prompt below to ask your agent to refresh the connection; it should use automatic refresh first and CLI re-authentication only if required.` Then provide this exact copyable prompt in a fenced `text` block: `Refresh the Quandora MCP connection. If automatic refresh fails, re-authenticate it with the CLI.` Then immediately continue the original request.
- If the version tool is missing, invisible, disabled, or fails, do not retry it later in the
  conversation and do not claim the plugin is outdated. Continue the business workflow.
- Never install, update, reload, or reauthorize merely because of this reminder.
- A later entry into Factor Mining, Factor Analysis, Strategy Building, Strategy Analysis, or Paper Trading recognizes the first check
  and does not call it again.

## Tools and Routing

Route read-only diagnosis of a completed Strategy result or Paper-readiness assessment to
`$strategy-analysis`. Keep actual Paper discovery, start, monitoring, data reads, and stop here.

Use only the minimum relevant subset of these Paper tools:

- Existing-source discovery: `pt_list_sources`, `pt_get_source`.
- Single runs: `pt_list_runs`, `pt_get_run`, `pt_submit_run`, `pt_stop_run`.
- Single-run data: `pt_get_portfolio`, `pt_list_pos`, `pt_get_equity`, `pt_list_fills`,
  `pt_list_funding`, `pt_get_code`.
- Strategy Portfolio setup and backtest: `pt_sp_create`,
  `pt_sp_revise`, `pt_sp_get`,
  `pt_sp_version`, `pt_sp_bt_submit`,
  `pt_sp_bt_get`, `pt_sp_bt_result`.
- Portfolio Paper: `pt_sp_run_submit`, `pt_sp_run_get`,
  `pt_sp_run_stop`.

Some hosts prefix names with the server name, for example
`quandora__pt_get_run`; treat it as the same tool. If no `pt_*` tools are visible, use the normal
Quandora connection-recovery path. When an authoritative safe error or tool signal shows that the
token lacks the required Paper scopes, fresh Quandora consent is required because refreshed old
tokens do not gain newly granted scopes automatically. Do not loop authorization. Use only the
host-native reconnect/browser consent flow; never bypass MCP with raw HTTP, inspect credentials,
or ask for pasted tokens.

The exact Paper OAuth scope set is `paper_trading:sources.read`,
`paper_trading:sources.write`, `paper_trading:runs.read`, `paper_trading:runs.create`,
`paper_trading:runs.stop`, `paper_trading:code.read`, `paper_trading:portfolios.read`, and
`paper_trading:portfolios.write`. This skill uses source read only to discover and monitor an
existing Paper-eligible source. Tool visibility does not authorize this skill to compose, create,
revise, or backtest a Strategy. Tools remain invisible when the relevant gate is closed or the
token lacks their exact scope.

There is deliberately no Paper archive, unarchive, resume, parent Portfolio list, parent aggregate
positions, parent net position, or parent Paper equity tool. Never invent or imply these abilities.
Do not call `sb_submit_run` from this skill. Hand Strategy work to `$strategy-building`; use Paper
tools here only after an eligible source exists.

Raw Factor inputs remain governed by the Factor Plugin Contract before they reach Paper Trading.
This Skill must not copy the `binance_intraday` field registry, realign the D feature row to D+1,
shift it again, backfill a missing row, or treat the pre-00:02 UTC publication SLA as an arrival
guarantee. Trading consumes the frozen Portfolio/Strategy contract and reported runtime
observations. Paper validates every required history column and bar before Lean execution; missing
required data retries or fails the run according to the runtime deadline and does not silently
filter that symbol into a smaller universe. The 12 first-seven-day bucket exclusions are default
Factor recommendation guidance, not a Paper runtime fallback; `trade_vol_max_b` and
`trade_vol_max_s` are not in that exclusion set.

## Global Safety Rules

- Never request, display, store, or infer FM/QuantAI/provider/account identifiers, raw provider
  payloads, downstream configuration, internal URLs, hostnames, ports, topology, database details,
  or credentials.
- Treat `source_strategy_run_id`, `paper_run_id`, Portfolio ids, child Paper handles, and cursors as
  opaque product handles. Return cursors byte-for-byte and never parse them.
- Never send `symbols`, `universe`, or `universe_policy`, including null or empty values. Quandora
  chooses and freezes the Paper universe downstream.
- Money, leverage, component weights, and allocated cash are exact decimal strings. Never convert
  them through a binary float or send them as JSON numbers.
- Never automatically stop, reopen, resubmit, change a strategy, change capital, mine another
  factor, or trigger another module because of losses or performance.
- A mutation timeout or ambiguous response is not proof of failure. Do not issue a fresh mutation
  or altered request. If a product handle was returned, reconcile with its get tool. If none was
  returned, report the ambiguity and stop; the user must decide after authoritative reconciliation.
- Treat Product Backend preflight as conservative guidance. FM submit remains the final eligibility
  authority, and another owner's handle must look nonexistent rather than distinguishable.

## Single-Strategy Workflow

### 1. Require an Existing Eligible Source

Paper Trading begins with an exact existing source StrategyRun supplied by the user or returned by
`pt_list_sources`. This skill must not list or choose factors, create or revise a Strategy, inspect a
prepared StrategyVersion, or submit a Strategy backtest.

If no suitable eligible source exists, or the user asks to create, change, or backtest a Strategy,
hand that work to `$strategy-building` and stop before any Paper mutation. Strategy Building uses
only its `sb_*` tools. After it produces a completed source with `paper_eligibility=eligible`,
continue only when the user still wants Paper, then select the exact source and obtain the separate
Paper confirmation below.

### 2. Select a Source

If the user did not provide an exact source StrategyRun handle, call `pt_list_sources`. Show a
compact table with source handle, lifecycle/submit state, strategy kind, initial cash, safe
strategy/version information, `paper_eligibility`, and the returned closed
`eligibility_reasons`.

Ask the user to select one exact returned source. Never probe guessed handles. Explain eligibility
without downstream internals:

- `eligible`: local and safe execution evidence passed preflight; final submit validation still
  belongs to FM.
- `provider_validation_required`: source validation could not be completed; it is not guaranteed
  eligible.
- `ineligible`: use only the returned closed reason codes, such as incomplete/unsubmitted source,
  unsupported strategy kind, or missing semantic lineage.

A source must ultimately be owner-scoped, completed, successfully submitted, cross-sectional, and
semantically reconstructable. `source_validation_unavailable` means the bounded source read failed
or exhausted its deadline. Describe validation as incomplete and retry only the read later if the
user asks. Unknown reason values fail closed; do not infer their meaning or request downstream
payloads. Missing displayed capital does not by itself make an ordinary source ineligible.

### 3. Confirm and Submit

Before `pt_submit_run`, display and obtain explicit confirmation for:

- exact source StrategyRun handle and safe strategy/version label;
- exact `initial_balance` when the user supplies one;
- optional ISO `start_date`;
- optional exact `leverage`.

Send only `source_strategy_run_id`, `start_date`, `initial_balance`, and `leverage`, omitting optional
fields the user did not choose. When the caller omits `initial_balance`, omit it from the tool call;
FM retains its existing default. Creating or revising a source, completing its backtest, and
submitting Paper are separate mutations and each requires the appropriate explicit confirmation.

### 4. Observe Lifecycle and Read Data

Use the submit response as the first snapshot. For lifecycle monitoring, call `pt_get_run`; never
poll `pt_get_portfolio`. Keep polling bounded and user-visible, and stop when terminal. If a caller
asks only for current state, make one detail call.

When presenting `pt_list_runs` or `pt_get_run`, use the returned `strategy_name` when it is present.
If it is null, reuse a safe source name already returned in
the current workflow; if the user specifically needs missing names, resolve only the distinct
returned source handles with bounded `pt_get_source` reads (at most 20 per request) and use
`source.strategy.name` when present. Otherwise label the name unavailable. Never infer a name from
submission time, PnL, ROI, direction, code, or neighboring rows, and never probe a guessed handle.

Use each data tool for its distinct meaning:

- Current assets/current PnL: call `pt_get_portfolio` once. Report `freshness.age_ms`, `stale`, and
  `retry_after_s`; explain cached or stale data without forcing refresh. This is a live manual
  collection protected by a PB 60-second per-run guard, and failed downstream attempts also consume
  that window.
- Historical positions: call `pt_list_pos`. This is a history of closed net-position lifecycles
  only: an item appears after the net position returns from nonzero to zero. Open positions and
  positions that were partially closed but remain nonzero are absent from this history and remain
  visible only through the current `pt_get_portfolio` snapshot. Honor symbol, side, open/close time
  filters, sort/order, bounded limit, and opaque cursor exactly. Closed-position realized return
  and current PnL are different semantics; never rename or derive one from the other, and never
  describe this list as arbitrary point-in-time portfolio replay.
- Execution records: use `pt_list_fills` for fills and `pt_list_funding` for funding cash flows.
  Do not infer closed-position semantics from fills.
- Strategy code: use `pt_get_code` only when asked and present only its bounded text/content type.
  Never expose a rejected internal reference.

### 5. Equity Curves

Choose exactly one mode from the user's intent and never mix their parameters:

- Legacy/full mode: omit lookback/bounds/sampling, or use only a bounded legacy `limit`.
- Bounded mode: use `max_points` and optional `started_at`/`ended_at`; do not send `limit` or
  `lookback`.
- Fixed lookback: send only one `lookback` plus `paper_run_id`.

| lookback | interval | total points |
|---|---:|---:|
| `7D` | `30m` | 336 |
| `30D` | `1.5h` | 480 |
| `90D` | `6h` | 360 |
| `180D` | `12h` | 360 |
| `1Y` | `1d` | 365 |
| `3Y` | `3d` | 365 |

Fixed windows return ROI values, `interval`, `total_points`, `live_start_index`, and `is_live` per
point. Explicitly label points before `live_start_index` as synthetic pre-live zero padding. Never
describe those zeros as observed returns or imply the strategy existed during that interval.

### 6. Stop

Before `pt_stop_run`, show the exact run handle and current known status, state that stop is terminal,
and obtain explicit confirmation. Make one stop call; do not automatically retry it. Then use
`pt_get_run` to observe authoritative state. Never call it pause and never offer resume. Running the
same strategy again requires a new user-confirmed submit and produces a new Paper run from a flat
book.

## Strategy Portfolio and Portfolio Paper

A Strategy Portfolio contains at least two exact StrategyVersion sleeves. Every weight is a
positive canonical Decimal string and the exact decimal sum must equal `1`. A version is a static
composition: no capital transfer, periodic rebalance, shared margin, signal fusion, order netting,
or execution-level netting exists.

Use `pt_sp_create` for the first exact composition and
`pt_sp_revise` only when the user explicitly changes the version. Display and
confirm every StrategyVersion handle and weight before either mutation. Read exact parent/version
state with `pt_sp_get` and `pt_sp_version`.

Before `pt_sp_bt_submit`, confirm the exact PortfolioVersion, total initial cash, dates,
and optional fee strings. The total cash is allocated exactly across sleeves; child StrategyRuns
are ordinary independent runs. Observe with `pt_sp_bt_get` and read the completed
aggregate backtest result with `pt_sp_bt_result`.

Portfolio Paper can start only from one completed PortfolioRun. Before
`pt_sp_run_submit`, display and confirm the source PortfolioRun, its exact total/source
capital, start date, leverage, and that every child is an independent static sleeve. Do not offer a
Paper-time capital override. To change total Paper capital, first complete a new PortfolioRun at
that capital.

Use `pt_sp_run_get` for the parent lifecycle and ordered child handles/status. Present child
status in component order and label every child `independent sleeve`. Do not claim parent aggregate
positions exist. Do not claim parent net positions, shared margin, or a parent real-time/equity
curve exists.

Before `pt_sp_run_stop`, show the exact parent handle, explain that stop fans out to its
children and is terminal, and obtain explicit confirmation. Call stop once, then reconcile with
`pt_sp_run_get`; never retry automatically or offer resume.

## Safe Errors

Explain safe failures as actionable product states without exposing downstream text:

- `source_strategy_ineligible`: choose another eligible completed source or complete the missing
  source prerequisite. Use only its returned closed `eligibility_reasons`.
- `paper_initial_balance_unavailable`: the requested Paper balance cannot be used safely; omit an
  override only when the user intended FM's default.
- `source_validation_unavailable`: source discovery could not complete its bounded FM validation;
  do not describe the source as eligible.
- `quantai_unavailable` or another retryable mutation error: the mutation can still be ambiguous.
  Reconcile authoritatively and never change its idempotency identity or blindly submit again.
- Authoritative authorization/scope failure: complete fresh Quandora consent for
  the minimum required Paper scopes.
- Rate/freshness response: honor returned cache, stale, and retry-after information.

If the response contains no recognized closed reason, report only the generic safe error code and
retryability. Never quote, reinterpret, or ask for a hidden provider message.
