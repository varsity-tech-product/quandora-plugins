# Versioned Optimizer Source

Load this reference only when the user explicitly asks for a base/pro optimizer, an
optimizer-ready Paper source, or a versioned Strategy definition operation. Analytical
optimization of an existing result belongs to `$strategy-analysis`.

Before the first source mutation, read `operation.strategy.version.manage` through
`get_quandora_guidance`. Unknown or contradictory guidance fails closed.

Select 1–20 exact admitted rows from `list_eligible_strategy_factors`. Copy only each row's exact
`admission.factor_id`, `admission.factor_version_id`, and `admission.job_id` into
`factor_references`. Stop when any triple is absent.

Build one closed cross-sectional specification:

- strategy kind `cs`;
- optional equal/custom weighting aligned with the Factor references;
- required top/bottom N or percentage ranking;
- optional long-only, short-only, or neutral direction;
- optional rebalance bars;
- `portfolio_optimizer` containing exactly version `base` or `pro` and complete `policy_yaml`.

The YAML is one UTF-8 mapping no larger than 65536 bytes and is capital-independent. It must not
contain `portfolio_value`, secrets, provider/account identity, internal URLs, paths, or
environment-specific values. Use only complete user-supplied policy or authoritative supported
guidance; do not invent provider keys.

Show exact Factors, specification, optimizer version, and policy text, then obtain confirmation.
Use `create_strategy` for a new definition or read the exact base with `get_strategy` and
`get_strategy_version` before `revise_strategy`. A new version is immutable; reads expose only safe
optimizer classification, never raw YAML.

Definition and backtest are separate mutations with separate confirmations. Before
`submit_strategy_backtest`, confirm the exact StrategyVersion, decimal-string `initial_cash`, dates,
and optional fee strings. Capital belongs to the run and never creates a new StrategyVersion or
enters policy YAML.

Monitor the returned owner-local source only with `get_paper_trade_source`. Optimizer
classification alone is not Paper eligibility. Require caller-sourced optimizer configuration and
exact source capital; missing, default, invalid, or unknown evidence fails closed. This source path
does not use the ordinary Strategy Result Bundle workflow. A later Paper start is a new
`$paper-trading` workflow with separate confirmation.
