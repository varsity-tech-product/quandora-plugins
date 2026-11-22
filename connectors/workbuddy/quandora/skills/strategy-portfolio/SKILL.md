---
name: strategy-portfolio
description: Use when the user asks to combine two or more exact Quandora StrategyVersions with target weights, create or revise a Strategy Portfolio, run its aggregate backtest, or read its aggregate result. Do not use for single-Strategy construction or any Paper-trading execution.
---

# Quandora Strategy Portfolio

Bundled plugin version: 3.0-preview

Use this skill through the authenticated `quandora` MCP connection. It owns Strategy
Portfolio research: immutable multi-Strategy composition, versioning, aggregate backtests, and
aggregate result reads. It never starts, monitors, or stops Paper trading.

Portfolio definitions use `strategy:portfolios.read` or `strategy:portfolios.write`, and aggregate
Portfolio research runs use `strategy:portfolio_backtests.read` or
`strategy:portfolio_backtests.create`. These are research capabilities even when a
completed PortfolioRun is later selected for Paper; the later execution uses the separate
`paper_trading:runs.read`, `paper_trading:runs.create`, or `paper_trading:runs.stop` boundary.

Route single-Strategy factor selection, Strategy/StrategyVersion authoring, optimizer policy, and
single-Strategy backtests to `$strategy-building`. Route simulated execution from a completed
PortfolioRun to `$paper-trading`. A one-component request remains a Strategy workflow; do not create
a Strategy Portfolio to represent it.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask the user to paste
API keys, bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens, or
account credentials.

## Tools

Use only the minimum relevant subset:

- Discovery: `list_strategy_portfolios`.
- Definition/version reads: `get_strategy_portfolio`, `get_strategy_portfolio_version`.
- Definition mutations: `create_strategy_portfolio`, `revise_strategy_portfolio`.
- Backtests: `submit_strategy_portfolio_backtest`, `get_strategy_portfolio_backtest`,
  `get_strategy_portfolio_backtest_result`.
- Authoritative guidance when a mutation is needed: `get_quandora_guidance` with
  `operation.strategy.portfolio.manage`, without `sections`.

Never call `start_strategy_portfolio_paper_trade`, `get_strategy_portfolio_paper_trade`, or
`stop_strategy_portfolio_paper_trade` in this skill. Never call a single-Strategy submit, rerun, or
Paper tool as an implicit prerequisite.

Some hosts display a server-qualified current name such as
`quandora__create_strategy_portfolio`. This is the same canonical tool, not a compatibility
alias. The retired abbreviated names are not valid fallbacks. If a canonical tool is unavailable,
report that exact state and use only the host-native reconnect/update flow; do not bypass MCP with
raw HTTP or pasted credentials.

## Portfolio Model

- A Strategy Portfolio contains at least two distinct exact `strategy_version_id` values.
- Every `target_weight` is a positive canonical decimal string, and the exact decimal sum is `1`.
- A PortfolioVersion is immutable. A changed component or weight creates a new version.
- Components are independent capital sleeves. There is no signal fusion, shared margin, capital
  transfer, periodic rebalance, provider-order netting, or execution-level position netting.
- A Portfolio backtest allocates `total_initial_cash` by component weight and creates independent
  child StrategyRuns. The aggregate result is research evidence; it is not a live or Paper account.
- Treat Portfolio, PortfolioVersion, PortfolioRun, StrategyVersion, and child StrategyRun handles as
  opaque owner-scoped identifiers. Never substitute one identifier type for another.

## Workflow

### Discover or Select

When the user has not supplied an exact Portfolio handle, call `list_strategy_portfolios` once with
a bounded `page_size` and default `include_archived=false`. Show only returned names, status,
latest-version metadata, version number, and archive state. Preserve `next_page_token` byte-for-byte
and use it only when the user asks for another page. Use `include_archived=true` only when explicitly
requested.

If the user wants a new composition, require two or more exact StrategyVersion handles. Do not
guess handles or select versions merely because names look similar. If exact versions are not yet
available, hand off to `$strategy-building` and stop before a Portfolio mutation.

### Create or Revise

Before the first create or revise mutation in the request, read the authoritative Portfolio guidance.
Fail closed if its revision or constraints contradict this bundled workflow.

Validate components with exact decimal arithmetic. Before `create_strategy_portfolio`, show the
name, every exact StrategyVersion, every weight, and the independent-sleeve semantics, then obtain
explicit confirmation. Before `revise_strategy_portfolio`, first read the selected Portfolio and
base PortfolioVersion, show the complete replacement composition, and obtain a separate explicit
confirmation. Send only fields declared by the canonical tool schema.

A timeout or ambiguous mutation response is not proof of failure. Do not submit a changed request
or create a replacement Portfolio. Reconcile only with an exact returned handle; otherwise report
the ambiguity and stop for user direction.

### Backtest and Result

Before `submit_strategy_portfolio_backtest`, display and confirm the exact PortfolioVersion,
`total_initial_cash`, date range, and any fee strings. Money, fees, and weights remain canonical
decimal strings; never pass them through binary floating point. Portfolio definition and Portfolio
backtest are separate mutations and require separate confirmations.

Use the submit response as the first PortfolioRun snapshot. Observe only that exact run with
`get_strategy_portfolio_backtest`; keep any polling bounded and user-visible. After completion, use
`get_strategy_portfolio_backtest_result` for the aggregate evidence. Present aggregate metrics and
ordered child outcomes without claiming shared execution, net positions, or a live account.

There is no separate Portfolio-analysis skill in this release. Aggregate Portfolio result reading
stays here. Do not route it to `$strategy-analysis`, which owns completed single-Strategy evidence.

### Handoff to Paper

If the user explicitly wants simulated execution after a completed PortfolioRun exists, stop this
workflow and hand the exact completed PortfolioRun handle to `$paper-trading`. Paper start is a new
mutation with its own confirmation. Never start it merely because the backtest completed.

## Final Response

State whether the outcome was a Portfolio definition/version, a PortfolioRun, or an aggregate
result. Summarize the exact user-visible composition and independent-sleeve model. When handing off
to Paper, state that no Paper run has been started yet. Do not expose credentials, provider
identifiers, internal topology, or raw downstream payloads.
