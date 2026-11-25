# Account and individual Run metrics

Simulation and real Live share these canonical performance fields and meanings. Use the
returned `scope` and `mode`; performance `mode=live` means real Live. The legacy lifecycle
wire alias live=simulation does not apply to these performance tools.

| Question | Account fields (`scope=ACCOUNT`) | Run fields (`scope=RUN`) |
| --- | --- | --- |
| Current valuation | `account_equity_usdt` | `run_nav_usdt` |
| Change / profit | `account_equity_change_usdt` | `run_net_pnl_usdt` |
| Return | `account_roi` | `run_roi` |
| Identity | `account_id` | `run_id`, `account_id`, `portfolio_id`, `portfolio_run_id` |
| Evidence quality | `account_metric_availability` | `run_metric_unavailable_reasons` |

Account ROI uses the initial positive account equity of the first confirmed Portfolio Run:
(current equity − fixed baseline equity) / fixed baseline equity. Its basis is
`FIRST_RUN_ACCOUNT_EQUITY_CHANGE`. Baseline evidence is `account_roi_baseline_equity_usdt`,
`account_roi_baseline_at`, `account_roi_baseline_run_id`, `account_roi_baseline_source`,
`first_run_started_at` and `first_run_confirmed_at`. Preserve nullable timestamps; confirmation
time is Unix milliseconds, while the baseline/start/as-of fields are ISO timestamps.
Never replace the fixed baseline with account-creation funds, first polling observation,
current Run capital or the most recent positive balance. Changing Runs does not reset account
performance. Neither Simulation nor Live supports reset. Account ROI includes deposits,
withdrawals, transfers and other equity changes; it is not TWR or pure trading profit.
Do not infer deposits/withdrawals by subtracting Run ROI from Account ROI.

Run metrics describe one trading execution only. `run_id` is that execution; `portfolio_run_id`
is the source research backtest, not an execution selector. For Simulation, the input selector
`portfolio_trading_run_id` equals the output `run_id`. For Live, both `account_id` and `run_id`
are required and must belong together. Do not combine repeated Runs into a Portfolio ROI,
sum their percentages, substitute Account ROI, or multiply ROI by leverage.

Amounts and ROI are decimal strings. ROI is a ratio: `0.10` means 10%, `-0.05` means −5%.
Account equity change and Run net PnL remain separate USDT amounts. Preserve exact values for
calculations; round only for presentation. Historical legacy `return_rate` or other TWR fields
are not the canonical Account ROI and must not be used as a fallback.

Both objects include `as_of` (source valuation time) and `data_status`. `STALE` means the
last available observation, not current market truth. A read does not guarantee a new provider
query or fresh exchange snapshot. PB collection time must not replace source `as_of`.
A known zero (`"0"`) is distinct from null. Preserve missing reasons, including a missing first
confirmed Run baseline; an idle/new account can have known equity and null Account ROI.
Unavailable history stays unavailable. Never fabricate zero returns, baselines or timestamps.

For an answer, name the account or exact Run, report the corresponding canonical fields,
state the valuation time and meaningful missing/stale evidence. Keep research backtest ROI
separate from observed forward performance. These reads authorize no execution changes.
