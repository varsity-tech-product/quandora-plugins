# Installation guide verification

These are documentation and host-integration checks, not business-workflow tests.
Do not start a factor backtest or trade to verify an installation.

## Repository checks

Run `python3 scripts/check-production-plugin.py` and `git diff --check`.
Verify that each platform guide links the shared recovery policy, preserves the
production repository and MCP identity, and requires authenticated `fm_status`
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
| Security denial / source conflict | Required | Required | Required | Preserve configuration; no bypass, false success, or retry loop |
| Unsupported host | Required | Required | Required | Explain capability limit; never silently expand supported platforms |

The matrix is an acceptance checklist, not a claim that these hosts were tested.
For issue #38, the editing environment is Linux: macOS/Windows clean-profile
installation and OAuth scenarios remain **not executed**. Record actual run
results in the issue/PR when those machines become available.

## Publishing and rollback

These guides are fetched from `main`. A guide-only change takes effect when
merged; it does not need a plugin payload version bump. Before merge, inspect
the rendered guides and repository-check results. After merge, verify the raw
entry documents and shared-policy URL return the intended revision. If the
instructions cause a regression, revert the documentation commit; do not repair
users' plugin caches or credentials as part of the rollback.
