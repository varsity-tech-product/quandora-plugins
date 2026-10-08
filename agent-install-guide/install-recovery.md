# Shared installation and recovery policy

Read this policy together with the selected platform guide. That guide owns the
supported host, commands, minimum capabilities, and OAuth mechanism. This policy
never expands WorkBuddy China beyond its supported local macOS Agent workflow.

## Act, verify, and resume

The user's installation request authorizes ordinary environment checks and the
requested plugin installation within existing permissions. Explain the scope
briefly, then perform the work; do not ask for confirmation before every step.
Use the client's approval mechanism when required. Additional system-component
or standalone CLI installation/update requires a concise explanation and approval
unless that exact change was already authorized. Never require global Auto accept.
Never bypass an explicit security denial with another shell, script, permission
mode, or user-run workaround.

Track completed stages in the conversation: environment, dependencies, marketplace,
plugin, OAuth, tools, protected probe. After user action, recheck the blocked stage
and continue. Do not reinstall completed stages or restart the entire workflow.
Present one actionable step at a time, in the user's language. Do not claim to have
inspected the user's computer from a web/cloud session.

## Public repository access

The production repository is public:
`https://github.com/varsity-tech-product/quandora-plugins.git` at `main`.
GitHub registration, GitHub login, personal access tokens, and SSH keys are not
installation prerequisites. Do not confuse repository authentication failures
with Quandora OAuth failures. Use the exact HTTPS source, never an SSH substitute.

When a Git-backed marketplace operation fails, first identify the failing command
and stage. Use a bounded, non-interactive read-only check such as
`git ls-remote https://github.com/varsity-tech-product/quandora-plugins.git refs/heads/main`
with terminal credential prompting disabled for that process and a short tool timeout.
Inspect only relevant URL rewrites/proxy configuration when needed; redact embedded
credentials and never dump credential helpers' stored secrets or all environment variables.
A public HTTPS page being reachable does not prove Git transport works.

Do not run `gh auth login`, request a token, generate SSH keys, clear stored
credentials, disable TLS verification, or change global Git/proxy configuration
as a default fix. Correct a mistyped invocation directly. If an existing global
rewrite or managed proxy is the cause, explain the exact conflict; any persistent
change needs specific authorization. Do not silently switch marketplaces or
invent a ZIP/cache-copy installation fallback.

## Minimal dependencies (ChatGPT/Codex and Claude only)

First use the platform guide's supported installed/bundled executable. Resolve its
absolute path and test the required commands, not just a version string. After an
approved installation, test the installed path directly: the current shell may
still have an old PATH. Do not install a runtime merely because it is absent.

For Git failures, first run `git --version`. On macOS, if the error mentions
`xcrun`, `xcode-select`, or developer tools, inspect `xcode-select -p` and available
Git executables. If Command Line Tools are actually missing, explain that this
small system component is needed for Git; after approval initiate
`xcode-select --install` once. The user completes the system dialog. Verify Git
again before resuming. Do not install full Xcode, accept licenses on the user's
behalf, or reset the developer directory as a generic repair.

On Windows, first look for an existing Git for Windows installation. If absent
and the chosen marketplace operation needs Git, use the official installer at
https://git-scm.com/downloads/win after the required approval. Do not install WSL
or a package manager just for this task. Let the user complete any mandatory
installer/UAC prompt, then resolve Git and recheck once.

For Codex, prefer the desktop application's existing executable. If it is missing
or incompatible, first use the official desktop update/restart route. If that
still leaves no supported executable, consult the current official Codex install
instructions at https://developers.openai.com/codex/quickstart before proposing
one platform-supported install method. Use an existing npm only when available;
if npm is absent, do not blindly run npm or install a chain of runtimes. Explain
and request approval for any necessary additional component, verify its official
source and the actual host support, then perform the supported installation.
If no supported route can be established, report that specific blocker.

Claude uses the native installation route in its guide; npm is not required.
WorkBuddy uses its bundled runtime and reviewed bootstrap only: do not apply the
Git, CLI, or runtime installation remedies above to WorkBuddy.

## Bounded recovery and user communication

Classify failures before asking the user to troubleshoot:

| Stage | Agent action | Human action only when needed |
| --- | --- | --- |
| Missing host/local capability | Give official download and exact local-session handoff | Install/open host and sign in |
| Missing/incompatible dependency | Locate existing tool, establish minimal supported remedy, recheck | Approve added component/system dialog |
| Repository authentication/network | Verify public HTTPS source and diagnose Git/network separately | Resolve managed restriction or approve a specific configuration repair |
| Marketplace source conflict | Report expected vs actual source safely; preserve existing entry | Decide which source should be used |
| OAuth | Keep one native flow active and observe its result | Login, MFA, consent |
| Tools unavailable in current session | Preserve installation; request a fresh local session | Open the new session |

For one transient network/timeout failure, permit at most one identical retry
unless the platform guide is stricter. For a diagnosed recoverable environment
problem, apply one targeted remedy and recheck once; if the same failure remains,
report the blocker. Never loop on source conflicts, integrity errors, denied
permissions, or OAuth failures. A failed login must end before another starts.

Prefer short messages such as "Checking installation requirements", "Please
confirm the system installation dialog", and "Please sign in to Quandora; I will
verify the connection afterward". On failure provide the stage, completed steps,
safe error category and one next action. Strip tokens, cookies, authorization URLs,
callback codes, and sensitive local paths from diagnostics. Do not call a local
installation failure a server outage.

## Authorization and completion

Use the platform's native OAuth mechanism and its exit result/status file.
Do not inspect credentials or automate consent. The client chooses the browser;
embedded browsing is not promised. Do not ask the user to paste callback URLs or
codes, or routinely to say "done" when a machine-readable outcome is available.
Keep the agent turn/process available until success, bounded timeout, cancellation,
or a genuine required user action. Honor platform-specific manual-terminal fallbacks.

After successful authorization, discover tools through the host and call the
protected, read-only `fm_status` tool. Confirm that it returns authenticated
account status, not an authentication challenge or an error. Do not print account
identifiers unnecessarily. If discovery needs a fresh session, report verification
pending and resume discovery/probe there without reinstalling. Do not submit a
factor, strategy, backtest, or trade as an installation probe.

Installation, OAuth, tool discovery, and the protected probe are separate outcomes.
Only report complete when all pass. Connected alone is not proof of authorization.

## Release discipline

Refresh the marketplace and compare its version with the installed version. Plugin
payload changes must bump the version consistently in manifests/marketplaces and
bundled version declarations; do not publish different plugin payloads under the
same version. Guide-only changes outside the plugin payload do not require a
plugin reinstall. If the supported inventory exposes a source revision, compare
it too; do not invent CLI flags or edit caches when revision metadata is unavailable.
