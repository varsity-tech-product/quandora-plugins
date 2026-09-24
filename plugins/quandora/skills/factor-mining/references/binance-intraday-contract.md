# 86-Field Research Contract Consumption

Load this reference after obtaining the scoped Factor Plugin Contract for source construction, or
when the user asks how a supported input should be interpreted. The live response from
`fm_get_contract` is the machine authority. Do not keep a separate 86-field name, cast,
expression, definition, normalization, or Paper-readiness table in this Skill.

## Consume Field And Cross-Field Semantics

For every selected column, use the returned `python_kwarg`, `csharp_bar_field`,
`csharp_expression`, `csharp_type`, cast rule, `csharp_double_expression`, and extra-buffer
snippets exactly as published. Interpret the research input from its returned `data_source`,
`description`, `unit`, `cross_sectional_comparability`, `normalization_guidance`,
`missing_value_behavior`, `research_caution`, and `upstream_pipeline_version`.

Consume `runtime_rules.research_guidance` directly. In particular:

- normalize amount and quantity with the economically matched same-side turnover or volume;
- define pressure as `(buy - sell) / (buy + sell)` with denominator guards;
- express aggressive fill-price means as `price / close - 1` and standard deviations as
  `std / close`; they are not bid/ask quotes or a bid-ask spread;
- normalize counts by side shares or the asset's own historical activity;
- do not treat a logarithm alone as removal of cross-asset scale exposure;
- use native Binance Premium Index values directly because they are dimensionless; do not divide
  them by price;
- compare noisy daily statistics with 3-day and 7-day smoothing while retaining one-day shock
  features as daily values;
- preserve the calendar index and original NaNs before rolling; never drop missing rows to
  compress a window;
- avoid exact redundancies and use the published structural redundancy notes instead of inventing
  a second formula list;
- treat the exact 12 bucket fields in `default_paper_excluded_columns` as excluded from default
  Paper-ready recommendations. `trade_vol_max_b` and `trade_vol_max_s` are not excluded.

Large trades are not automatically informed or smart-money flow. Apply each returned field rule
instead of using generic labels as economic interpretation. The stable Task label `Auction`
means funding, Premium Index dislocation, open interest, liquidations, and positioning crowding;
it does not mean a closing-auction session.

Do not compare a `normalize_first` field across assets before applying its returned normalization.
Treat `direct` fields according to their returned caution instead of assuming equal robustness.
Preserve missing values as unavailable; never replace them with zero unless the exact factor
thesis and contract explicitly define zero as a real observation. A missing required upstream
column is an execution failure to report, not permission to emit an all-NaN factor silently.

## Preserve Point-in-Time Semantics

For selected `binance_intraday` fields, consume
`runtime_rules.data_availability.binance_intraday` directly. Its current invariant is:

- `source_date = D` describes the feature window `D 00:00-24:00 UTC`, built from 96 15-minute bars;
- `as_of_date = D + 1`, with `source_date == as_of_date - 1 day`;
- the D feature row aligns to the D daily bar and is unavailable during D intraday;
- the documented publication SLA is before D+1 00:02 UTC, but it is not a historical-fetch or
  realtime-arrival guarantee;
- the earliest safe use is the first evaluation after the row has actually arrived.

Keep historical alignment on `source_date`. Do not align on `as_of_date`, use the row during D,
or shift an already D-aligned value a second time. If actual arrival is uncertain, preserve that
uncertainty instead of assuming the SLA was met.

## Keep Product Boundaries Closed

Use only fields allowed by the selected task or session. Validate the exact final source after
every edit and proceed only when validation succeeds. The public contract may describe source
semantics; it must not expose or accept internal provider directory names, endpoints, credentials,
or submission-routing details.

Default Paper exclusions are authoring recommendations, not permission for Paper to shrink the
runtime universe. Paper required-history validation occurs before Lean and missing required values
retry or fail according to the runtime deadline.
