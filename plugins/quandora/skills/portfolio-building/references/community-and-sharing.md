# Community discovery and Portfolio sharing

Load only for discovery, favorites, sharing, or contextual research reads. Sharing an existing
Portfolio does not authorize changing its definition or submitting another backtest.

## Community and Contextual Research

Use `list_community_portfolios` with optional `query`, `page_size`, and unchanged `page_token`
to discover currently visible publications. Read `get_community_portfolio` with its exact
`publication_id` for author, intro, readiness, favorite state and trading eligibility.
Read `get_community_portfolio_research` for retained results and exact composition; follow
`get_community_strategy_research` and `get_community_factor_research` with that same Publication
and the returned exact Strategy or Factor/FactorRun identities. Pending delivery is not empty
successful research. Never pass these IDs to owner tools or copy them into Mine to bypass access.

Use `read_community_research_artifact` for an artifact name returned by contextual research.
Supply either `strategy_id` or both `factor_id` and `factor_run_id`. Decode the returned base64;
continue with `next_offset` and the same `expected_sha256`. Every chunk rechecks current access
and exact lineage. A changed digest requires a fresh read, never combining snapshots.
These projections exclude private source, credentials and internal storage URLs.

Portfolio stars use `set_portfolio_favorite` with `publication_id` and explicit `favorite` and
`list_favorite_portfolios`. Explicit true/false is idempotent. Portfolio favorites are separate
from Factor/Strategy LibraryFolder metadata; no Portfolio LibraryFolder is introduced.

## Portfolio Sharing

Read `get_portfolio_sharing` before managing an owned exact `portfolio_id`. Proceed within the
user's sharing authorization; obtain any missing audience or inclusive UTC `valid_through_date`.
There is no permanent/default expiry. Only public and specified-user sharing are supported.
Do not create or redeem invitation codes, including through cached tool names.

Use `publish_portfolio_to_community` for public sharing: PB atomically manages the public Share
and Community Publication. Use `search_portfolio_share_recipients` to resolve an intended user,
then `share_portfolio_with_user` with their exact `recipient_username`. Each recipient has its
own grant and expiry. `create_portfolio_share` is a compatibility entry for these same public
or direct operations. Do not publish publicly when only a specified recipient was authorized.

While any grant is active, public and direct channels are mutually exclusive. Grants cannot
be revoked, shortened, removed or switched to another channel. Use `extend_portfolio_share`
with the original `share_id`, its `expected_expires_at`, and a later valid-through date to extend
that same active grant. Expired grants cannot be revived by extension. Use
`update_portfolio_share_intro` with the aggregate `expected_updated_at` to edit the introduction.
A conflict requires rereading current sharing; do not overwrite or create a substitute grant.
These edits do not create a research version or rerun a backtest.

For retained authorized Shares use `list_portfolio_shares`, `get_portfolio_share`,
`get_portfolio_share_research`, and `download_result_bundle` with `kind: "portfolio_share"` and the exact authorized share ID.
The returned download is a retained source-free ZIP; preserve its status, size and digest.
Retained Share research may remain readable after expiry, while current Community discovery and
trading authorization follow PB's current visibility and grant rules. Preserve `status`,
`trading_allowed` and `cross_owner_trading_supported`; never infer permission from a date alone.

Hand a currently authorized `publication_id` or `share_id` to `$portfolio-trading-analysis` for an explicit
Simulation request. Use the recipient's own account and PB authorization; never use the owner
Portfolio ID as a bypass, impersonate its owner or claim a frozen historical snapshot unless
the returned evidence establishes it.
