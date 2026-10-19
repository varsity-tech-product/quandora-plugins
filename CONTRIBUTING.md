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
runtime documentation, per-Skill bundled-version copy, retired tool names, and mandatory version
probes in normal entry paths.

The public package retains the two fixed-purpose Claude authorization launchers and the five
reviewed production WorkBuddy installation/authorization scripts. These are explicitly allowlisted;
other plugin-root scripts remain rejected. WorkBuddy component hashes and the bootstrap hash in
the installation guide must be updated together when their contents change.

The check is database-free and must remain suitable for pull-request CI.

All seven Skills share `plugins/quandora/references/connection-and-security.md`.
The checks enforce automatic recovery first, bounded read retries, uncertain-mutation safety,
installed-metadata version diagnostics on demand, and no user-facing token refresh boilerplate.
Regression tests mutate disposable package copies and require no database or credentials.

Production publication promotes the reviewed seven-Skill payload from the staging repository while
preserving the production package identity, MCP/OAuth endpoint, and supported host installation
guides. Update every manifest version together. Publish and verify the package before advancing
the production MCP recommended-version label. Existing hosts must update/reload their package;
publication does not replace local caches. Rollback restores the previous package and matching label.
