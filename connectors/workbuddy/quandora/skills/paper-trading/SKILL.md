---
name: paper-trading
description: Use when the user asks to start, inspect, monitor, or stop simulated Paper trading on Quandora, including current Paper assets/PnL, positions, equity, fills, funding, code, or Paper execution from a completed Strategy Portfolio backtest. Do not use to create or backtest Strategies or Strategy Portfolios.
---

# Quandora Paper Trading

Bundled plugin version: 3.0-preview

Use this skill through the authenticated `quandora` MCP connection. It owns simulated
execution only: eligible-source discovery, Paper start, lifecycle monitoring, execution data, and
terminal stop. It is simulation-only and never represents live-money trading.

`paper_trading:sources.read` is discovery-only. Both single-Strategy Paper and Strategy Portfolio
Paper use `paper_trading:runs.read`, `paper_trading:runs.create`, or
`paper_trading:runs.stop`; the execution shape does not move Portfolio
definitions or backtests into the Paper namespace. A single Strategy can be understood as one
execution sleeve, but it does not become a Strategy Portfolio research object.

Route single-Strategy authoring/backtests to `$strategy-building`. Route multi-Strategy Portfolio
composition, revision, aggregate backtests, and aggregate result reads to `$strategy-portfolio`.
Route deep diagnosis of a completed single-Strategy result to `$strategy-analysis`. If no eligible
source exists, hand off and stop before any Paper mutation.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask the user to paste
API keys, bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens,
provider credentials, or account credentials.

## Tools

Use only the minimum relevant subset:

- Source discovery: `list_paper_trade_sources`, `get_paper_trade_source`.
- Single Paper lifecycle: `list_paper_trades`, `get_paper_trade`, `start_paper_trade`,
  `stop_paper_trade`.
- Single Paper data: `refresh_paper_trade_account_snapshot`,
  `list_closed_paper_trade_positions`, `get_paper_trade_equity_curve`,
  `list_paper_trade_fills`, `list_paper_trade_funding`, `get_paper_trade_strategy_code`.
- Portfolio Paper lifecycle: `start_strategy_portfolio_paper_trade`,
  `get_strategy_portfolio_paper_trade`, `stop_strategy_portfolio_paper_trade`.
- Authoritative Paper guidance when needed: `get_quandora_guidance` with
  `operation.paper_trade.submit`, without `sections`.

Never call Strategy or Strategy Portfolio definition/backtest tools here. In particular, do not call
`create_strategy`, `revise_strategy`, `submit_strategy_backtest`,
`create_strategy_portfolio`, `revise_strategy_portfolio`, or
`submit_strategy_portfolio_backtest`.

Some hosts display a server-qualified current name such as
`quandora__start_paper_trade`. This is the canonical tool, not a compatibility alias. The
retired abbreviated names are not valid fallbacks. If a canonical tool is unavailable, report the
state and use only the host-native update/reconnect/browser-consent flow. Never bypass MCP with raw
HTTP or pasted credentials.

## Safety and Data Model

- Treat StrategyRun, PaperTradeRun, PortfolioRun, PortfolioPaperRun, child Paper handles, and
  cursors as opaque owner-scoped identifiers. Never substitute one type for another or probe a
  guessed handle.
- Money, leverage, component weights, and allocated cash are canonical decimal strings. Never pass
  them through binary floating point or send them as JSON numbers.
- Never send `symbols`, `universe`, or `universe_policy`, even as null or empty values. The Paper
  universe is selected and frozen downstream.
- A mutation timeout or ambiguous response is not proof of failure. Do not retry with a fresh or
  changed request. Reconcile only through an exact returned handle; otherwise report the ambiguity
  and stop for user direction.
- Never automatically stop, restart, resubmit, revise a Strategy, change capital, mine a factor, or
  trigger another workflow because of PnL or losses.
- Stop is terminal, not pause. There is no Paper resume, archive/unarchive, parent aggregate
  position, parent net position, or parent Portfolio Paper equity capability.

## Single-Strategy Paper

### Select an Eligible Source

Paper starts from one exact existing completed StrategyRun returned by
`list_paper_trade_sources` or supplied by the user. This skill must not create or revise the source.
If the user did not provide the handle, list one bounded page and show the returned safe Strategy
label/version, lifecycle and submit state, source capital, optimizer classification, eligibility,
and closed `eligibility_reasons`. Ask the user to select one exact source.

`eligible` is a conservative Product Backend preflight; final submit authority remains downstream.
`provider_validation_required` is not proof of eligibility. Unknown, missing, contradictory, or
unsupported evidence fails closed. For an optimizer source, require returned
`optimizer_execution.version` of `base` or `pro`, `config_source=caller`, and exact positive source
capital. Never request raw policy YAML or provider state to repair a source.

When `source_strategy_no_result` is present, the completed source produced zero orders and is
ineligible for Paper. Do not submit or retry it, reinterpret it as a failure, or try to manufacture
performance evidence. Offer a handoff to `$strategy-analysis` or, after explicit confirmation, a
new controlled Strategy experiment through `$strategy-building`.

### Confirm and Start

Before `start_paper_trade`, show the exact selected source, safe label/version, optional ISO
`start_date`, optional exact leverage, and the chosen balance semantics, then obtain explicit
confirmation.

For an optimizer source, read authoritative Paper-submit guidance, show the locked StrategyRun
capital, omit `initial_balance`, and do not offer a Paper-time override. Capital changes require a
new StrategyRun through `$strategy-building` and a new Paper confirmation. For an ordinary source,
send optional `initial_balance` only when the user chose it. Omit every optional field the user did
not choose.

### Monitor and Read Data

Use the start response as the first snapshot. Use `get_paper_trade` for lifecycle monitoring; keep
polling bounded and user-visible, and stop on a terminal state. Do not poll the account-snapshot
refresh tool.

Use each read for its exact meaning:

- `refresh_paper_trade_account_snapshot`: one current assets/PnL collection. Report freshness,
  stale state, and retry delay. It consumes the per-run manual refresh gate even when the
  downstream attempt fails, so never loop it.
- `list_closed_paper_trade_positions`: closed net-position lifecycle history only. Open and
  partially closed nonzero positions remain visible only in the current account snapshot.
- `get_paper_trade_equity_curve`: choose exactly one declared lookback, bounded-sampling, or legacy
  mode; never mix their parameters. Label synthetic pre-live padding from `live_start_index` as
  synthetic, not observed performance.
- `list_paper_trade_fills` and `list_paper_trade_funding`: execution records and funding cash flows;
  do not derive closed-position semantics from them.
- `get_paper_trade_strategy_code`: use only when explicitly requested and present only bounded
  public text/content type.

Preserve opaque cursors byte-for-byte. Reuse only safe names returned in the current workflow;
never infer a Strategy name from PnL, time, direction, code, or neighboring records.

### Stop

Before `stop_paper_trade`, show the exact run and current known state, explain that stop is
terminal, and obtain explicit confirmation. Call stop once, then reconcile with
`get_paper_trade`. Never retry automatically or offer resume.

## Strategy Portfolio Paper

Portfolio Paper starts only from one exact completed PortfolioRun produced by
`$strategy-portfolio`. This skill does not create, revise, or backtest the Portfolio. If no completed
PortfolioRun exists, hand off and stop.

Before `start_strategy_portfolio_paper_trade`, show the source PortfolioRun, total/source capital,
start date, leverage, and the fact that each component runs as an independent static sleeve. Do not
offer a Paper-time capital override. To change capital, complete a new Portfolio backtest through
`$strategy-portfolio`, then obtain a new Paper confirmation.

Use `get_strategy_portfolio_paper_trade` for the parent lifecycle and ordered child handles/states.
Label every child as an independent sleeve. Never claim shared margin, capital transfer, signal
fusion, order netting, parent aggregate positions, parent real-time PnL, or a parent equity curve.

Before `stop_strategy_portfolio_paper_trade`, show the exact parent handle, explain that terminal
stop fans out to children, and obtain explicit confirmation. Call stop once, then reconcile with
`get_strategy_portfolio_paper_trade`; never retry automatically or offer resume.

## Final Response

State whether the result concerns one Paper trade or Portfolio Paper, its safe lifecycle state, and
the exact user-visible freshness or data semantics relevant to the request. If a handoff is needed,
state that no Paper mutation was performed. Never expose run handles in a general user-facing
summary unless the user needs the exact selected handle to continue, and never expose credentials,
provider identifiers, internal topology, or raw downstream payloads.
