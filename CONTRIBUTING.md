# Contributing

Before requesting review for a production Plugin change, run the database-free package check:

```bash
python3 scripts/check-production-plugin.py
python3 scripts/test_production_plugin.py
```

The check verifies the declared Quandora version across supported host manifests, the
public package allowlist, required Skill metadata and assets, bounded Codex entry examples,
portable Agent-facing instructions, explicit routing boundaries, user-language output policy, and
search/pagination guidance. It also rejects orphaned Skill scripts, release-process history in
runtime documentation, per-Skill bundled-version copy, retired tool names, and repeated blocking version
probes in normal entry paths.

The public package retains the two fixed-purpose Claude authorization launchers and the five
reviewed production WorkBuddy installation/authorization scripts. These are explicitly allowlisted;
other plugin-root scripts remain rejected. WorkBuddy component hashes and the bootstrap hash in
the installation guide must be updated together when their contents change.

The check is database-free and must remain suitable for pull-request CI.

All eight Skills share `plugins/quandora/references/connection-and-security.md`.
The checks enforce automatic recovery first for incidental failures, bounded read retries, uncertain-mutation safety,
once-per-session installed-metadata release checks, and no user-facing token refresh boilerplate.
Regression tests mutate disposable package copies and require no database or credentials.
The bundled Codex recovery guide must preserve same-host/production-target checks, the
`plugin_not_found` capability fallback, user-only consent and post-login read verification.
Static policy tests do not prove client OAuth recovery: record the actual host scenarios from
`agent-install-guide/verification.md`, and leave unexecuted scenarios explicitly pending.

Account Connection intentionally has no authenticated MCP dependency so it loads before
login, and no research-workflow prerequisite. Deploy Auth's additive `get_quandora_account`
tool before recommending this package; its problem reports also need Auth's
`submit_feedback_report` (contract revision `2026-10-23.feedback-reports`) in the same
environment before publication. Follow
`plugins/quandora/references/account-connection-verification.md` for current-account,
explicit reauthorization, two-account switching, cancellation and host-adoption checks.

Production publication promotes the reviewed eight-Skill payload from the staging repository while
preserving the production package identity, MCP/OAuth endpoint, and supported host installation
guides. Update every manifest version together. Publish and verify the package before advancing
the production MCP recommended-version label. Existing hosts must update/reload their package;
publication does not replace local caches. Rollback restores the previous package and matching label.

Release discovery changes must preserve legacy version API semantics and publish backend support
before recommending the new package. Validate an installed old marketplace snapshot upgrading
through host-managed commands. Record installation and loaded-state evidence separately; host
checks unavailable on the test machine remain explicit acceptance gaps. A package content change
requires a fresh version, never rewriting a previously installed release.
