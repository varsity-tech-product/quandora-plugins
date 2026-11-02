# Immutable Definition Changes

The only hierarchy is StrategyFamily → immutable Strategy → StrategyRun. Use each returned
`strategy_family_id`, `strategy_id`, and `strategy_run_id` only for its matching resource.

Read an existing definition with `get_strategy(strategy_id=...)`. Its persisted `specification`
and ordered `factor_references` establish the base. Do not reconstruct them from names, a latest
Run, or missing metadata. An incomplete historical definition stays readable; do not invent
missing Factor lineage for a new execution.

For a changed specification, call `create_strategy` with the exact `strategy_family_id`,
`base_strategy_id`, complete non-optimizer specification, exact admitted Factor references, and a
`research_note` explaining the change. Each base reference keeps its `factor_family_id`, `factor_id`
(the immutable Factor) and `factor_run_id`; copy those three, never a display name.
This creates a new immutable Strategy in that Family. It never edits the base or previous Runs.
A plain rerun uses `submit_strategy_backtest` on the existing Strategy with a fresh
`client_request_id`. Identical Strategy and dates can have multiple Runs. Only a retry of the
same operation reuses its ID and parameters; a timeout does not authorize a new operation.

Carry the research goal through definition and Run calls. Make missing choices from the research
context and returned candidates; record why in the decision's `research_note` (`hypothesis` for a
new direction, `change_summary` otherwise). Run-level dates do not override weighting, ranking,
direction, or rebalance frozen in the definition. Read failures as evidence; do not add a compatibility path when a tool
or old identifier is unavailable.

For the full selection and submission procedure, use the primary Skill's Canonical Strategy
Workflow reference. Trading preparation passes the exact Strategy to `$portfolio-building`;
Trading observations belong to `$portfolio-trading-analysis`.
