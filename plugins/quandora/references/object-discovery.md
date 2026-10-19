# Find a named object

When the user identifies an existing object by name, first use
`search_quandora_objects(query=..., types=...)`. Omit `types` when the user's
wording could mean research or an account. Supported kinds are `factor`,
`strategy`, `portfolio`, `simulation_account`, and `live_account`.

Search normalizes case and whitespace (`Alpha03` and `Alpha 03`) and filters the
full authorized inventory before paging. Follow `next_cursor` unchanged while
keeping query and types unchanged. Results are candidates, not an automatic
selection: preserve object type, current name, exact `object_id`, `family_id`,
source, status, root context and match reason. Multiple immutable versions remain
separate. Never equate an account name with a Strategy name or silently use the
latest version. Use existing context to distinguish candidates; ask a short
clarification only when the intended target remains ambiguous.

Continue with the returned `read_tool` and `read_arguments`. In particular, owned
Factor history uses the family as `factor_id` and the immutable object as
`version_id`; copy the supplied selector pair instead of swapping IDs. Official
Factors use their advertised selector. Shared children remain in their root
Publication/Share read context and are not Mine assets or independently reusable
Factor/Strategy inputs. Search does not grant source-code access or execution
permission. Missing grants may restrict `searched_types`.

For questions about execution of a Strategy or Portfolio, pass its exact
`strategy_id` or `portfolio_id` to `list_simulation_accounts`,
`list_portfolio_trading_runs`, `list_live_accounts` or `list_live_account_runs`.
The backend checks immutable Portfolio composition. Combined filters intersect.
Account source matching defaults to current runs; set `include_history=true` only
when prior account sources matter. Run lists keep history by default;
`current_only=true` narrows to current execution. A matched account may also have
unrelated historical runs: preserve the same source filters when listing its runs.
For Simulation/Monitoring facts, use the exact returned run ID. For Live facts,
use the exact owned account and run IDs. All Live operations remain read-only.

Use `get_quandora_guidance(guide_id="operation.objects.search")` for uncertainty
about this workflow, not as a mandatory probe. An unavailable or failed search is
not evidence that the object does not exist; follow the connection recovery
policy and report the limitation rather than guessing an ID.
