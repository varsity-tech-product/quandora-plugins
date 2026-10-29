# Immutable Definition Changes

The only hierarchy is StrategyFamily → immutable Strategy → StrategyRun. Use each returned
`strategy_family_id`, `strategy_id`, and `strategy_run_id` only for its matching resource.

Read an existing definition with `get_strategy(strategy_id=...)`. Its persisted `specification`
and ordered `factor_references` establish the base. Do not reconstruct them from names, a latest
Run, or missing metadata. An incomplete historical definition stays readable; do not invent
missing Factor lineage for a new execution.

For a changed specification, call `create_strategy` with the exact `strategy_family_id`,
`base_strategy_id`, complete non-optimizer specification, and exact admitted Factor references.
This creates a new immutable Strategy in that Family. It never edits the base or previous Runs.
A plain rerun uses `submit_strategy_backtest` on the existing Strategy with a fresh
`client_request_id`. Identical Strategy and dates can have multiple Runs. Only a retry of the
same operation reuses its ID and parameters; a timeout does not authorize a new operation.

Carry explicit authorization through definition and Run calls. Ask only for a materially new
choice or scope. Run-level dates do not override weighting, ranking, direction, or rebalance
frozen in the definition. Read failures as evidence; do not add a compatibility path when a tool
or old identifier is unavailable.

For the full selection and submission procedure, use the primary Skill's Canonical Strategy
Workflow reference. Trading preparation passes the exact Strategy to `$portfolio-building`;
Trading observations belong to `$portfolio-trading-analysis`.
