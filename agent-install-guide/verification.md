# Installation guide verification

These are documentation and host-integration checks, not business-workflow tests.
Do not start a factor backtest or trade to verify an installation.

## Repository checks

Run `python3 scripts/check-production-plugin.py` and `git diff --check`.
Verify that each platform guide links the shared recovery policy, preserves the
production repository and MCP identity, and requires authenticated `get_factor_mining_status`
before reporting full completion. Check README entry prompts still resolve to
the corresponding guides. Keep Claude launchers and WorkBuddy bootstrap hashes
unchanged unless explicitly updating and testing their implementation.

## Host acceptance matrix

Run on disposable user profiles with permission to install and authenticate.
Record host/OS version, CLI version, guide commit, stage outcomes, and redacted
failure category. Never record tokens, authorization URLs, or callback codes.

| Scenario | ChatGPT/Codex macOS + Windows | Claude Desktop/CLI macOS + Windows | WorkBuddy China macOS | Expected outcome |
| --- | --- | --- | --- | --- |
| Start in web/mobile | Required | Required | Required | Official host download, correct local entry, continuation prompt; no pretend local checks |
| Clean install | Required | Required | Required | Minimum dependencies, official source, single OAuth, discovery and protected probe |
| Existing current plugin | Required | Required | Required | Reuse existing progress; no needless reinstall |
| Older plugin | Required | Required | Required | Supported update; installed/marketplace versions agree |
| Missing Git / macOS CLT | Required | Required | Not applicable | Agent diagnoses; approved minimal install; no full Xcode or global reset |
| Public Git HTTPS rewrite/auth failure | Required | Required | Not applicable | No GitHub login/token request; targeted diagnosis, bounded recovery |
| OAuth timeout / cancellation | Required | Required | Required | No concurrent flows; bounded retry only for transient error; cancellation respected |
| Tool discovery needs fresh session | Required | Required | Required | Preserve install/auth; verification pending until protected probe succeeds |
| Current package with only Factor/Trading tools visible | Required | Required | Required | Discover the full catalog, distinguish stale discovery from missing scopes, recover the existing connection, and verify a relevant read; a version/status probe alone is insufficient |
| Security denial / source conflict | Required | Required | Required | Preserve configuration; no bypass, false success, or retry loop |
| Unsupported host | Required | Required | Required | Explain capability limit; never silently expand supported platforms |

The matrix is an acceptance checklist, not a claim that these hosts were tested.
For issue #38, the editing environment is Linux: macOS/Windows clean-profile
installation and OAuth scenarios remain **not executed**. Record actual run
results in the issue/PR when those machines become available.

## Codex workflow authorization recovery

Test the bundled recovery guide with an ordinary Strategy/Portfolio request, without telling
the Agent to log in or providing a recovery command. Use a disposable profile with a consented
older grant for the missing-permissions scenario; do not modify a real user's token store.
These cases require actual host acceptance separately from the repository's static checks.

| Scenario | Expected outcome |
| --- | --- |
| Required permissions missing, native action available | Agent starts one native authorization flow; user only handles required approval/sign-in/consent |
| `plugin_not_found`, same-host CLI permitted | Agent checks executable/context and existing production connection, then starts native CLI login without a second user prompt |
| Desktop UI automation forbidden, CLI independently permitted | Use verified CLI without automating the desktop UI |
| Authorization or local execution explicitly denied | Stop the denied operation; do not use a fallback to bypass policy |
| No native action and no permitted same-host CLI | State the missing capability and verified manual entry if available; no claimed login attempt |
| Different host/config, wrong endpoint or missing connection | Preserve configuration; no new connector or authorization against the wrong target |
| User cancels or callback succeeds with unchanged grant | No login loop; report cancelled or grant-adoption failure distinctly |
| Grant updated, current task catalog still old | Supported discovery refresh or host-required new task; no second OAuth consent |
| Authorized restricted grant or empty folder | Validate required tool identities and reads, not a universal tool count |

Record the host/CLI versions, package revision, available recovery capability, whether native
login actually started/completed, and post-recovery read results. Never record credentials or
authorization URLs. Discover write tools without invoking them as acceptance probes.

## Publishing and rollback

These guides are fetched from `main`. A guide-only change takes effect when
merged; it does not need a plugin payload version bump. Before merge, inspect
the rendered guides and repository-check results. After merge, verify the raw
entry documents and shared-policy URL return the intended revision. If the
instructions cause a regression, revert the documentation commit; do not repair
users' plugin caches or credentials as part of the rollback.
