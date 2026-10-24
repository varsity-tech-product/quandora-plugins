---
name: account-connection
description: Connects, reauthorizes, switches, and verifies the current Quandora account through host-native MCP OAuth, and files problem reports with the Quandora team. Use when the user asks to log in, open authorization, reconnect, change accounts, identify the connected account, or report a problem, bug or wrong data to Quandora. Do not use for Factor, Strategy, Portfolio, or Trading operations.
---

# Quandora Account

Use the user's language. Handle account requests independently of research workflows.
This Skill intentionally has no authenticated MCP dependency: it must be loadable before
login. Problem reports are the only part that needs an active connection. Tool absence
does not prevent starting a supported native authorization flow.
Use only the existing production `quandora` connection; do not switch environments.

Read the [shared connection policy](../../references/connection-and-security.md).
For Codex, follow the [native authorization procedure](../../references/codex-authorization-recovery.md)
before launching OAuth. Other hosts may use their verified native connector action; do
not translate Codex CLI commands into guessed commands for another host.

## Choose the requested action

| Intent | Action |
| --- | --- |
| Current account / connection status | Call `get_quandora_account` with `{}` if discoverable. Do not start interactive login solely for a status request. |
| Connect / sign in / open authorization | Start one native OAuth flow, even if a connection already works. |
| Reauthorize / reconnect explicitly | Start one native OAuth flow even with a valid grant; do not substitute a health check or silently skip the request. |
| Switch account | Suspend business calls, capture the current identity if available, start one native OAuth flow, then verify the new identity. |
| Report a problem to the Quandora team | Follow [Report a problem](#report-a-problem); do not start OAuth for it while the connection works. |

Selecting this Skill without a stated action defaults to status. A previous successful
authorization does not satisfy a new explicit request. The user's request authorizes
initiating the flow; do not ask them to repeat it as another prompt. Browser sign-in,
MFA and consent remain user actions. An explicit host security denial still applies.

For incidental business-call failures, let the shared policy handle automatic refresh
first. Explicit account requests do not require a terminal failure or missing scopes.

## Launch and wait

1. Reuse a supported native authorization action if the host exposes one. Otherwise,
   in Codex, verify the official CLI belongs to the same host and configuration and
   invoke `codex mcp login quandora` as the native procedure specifies.
2. Allow only one pending flow per connection. If one is already running, observe
   that flow instead of launching another. Keep it in the foreground until completion,
   cancellation, timeout or failure; do not leave a background login waiting indefinitely.
3. Tell the user to complete the browser action. For switching, tell them to select
   the intended Quandora account; an existing browser session can select the old account.
   Do not change the browser session, sign in or approve consent on their behalf.
4. On timeout, stop the flow started by this request through the host's supported
   cancellation mechanism. Respect cancellation and do not automatically relaunch.

Do not reinstall, add a duplicate MCP entry, inspect credential stores, implement OAuth,
paste authorization URLs/codes into saved output, or revoke unrelated connections.
Do not logout first as a routine step: a failed switch must not unnecessarily discard
the existing connection. If no supported launch path is available, state the concrete
capability missing and the verified host entry the user can use; never invent a button.

## Verify the active connection

After a successful callback, rediscover if needed and make a **fresh**
`get_quandora_account({})` call through the active MCP connection. Its `{id, email}`
comes from Auth; a browser email, callback, health check, token refresh or cached
profile is not proof of the active identity. Display the returned email. Use `id`
for comparison internally; do not print identifiers or credentials as troubleshooting.

- Connect or reauthorize succeeds only when this fresh identity call succeeds.
- For switching from a known account, require a different `id`. If the user supplied
  a target email, also compare it case-insensitively to the returned email. A changed
  email with the same `id` is not an account switch.
- If the old identity was unavailable, display the returned email and ask the user
  to confirm the intended account before resuming business work, unless it matches
  their explicitly supplied target email. Do not claim that an old-to-new change
  was verified when the old identity was unknown.
- If the old account or a different target is still active, say which email is active
  and that the requested switch is incomplete. Keep business calls paused. Do not
  retry login automatically or operate on that account as if it were the target.
- If the host cannot adopt the new grant without a supported reload/new task, report
  that concrete next step. Do not treat callback success as completion.
- If the server does not expose `get_quandora_account`, report identity verification
  unavailable and keep switching incomplete. Do not use private APIs as a fallback.

On cancellation or failure, a single best-effort fresh identity read may establish
which account remains active. A missing/invalid credential means unauthenticated;
network errors, discovery gaps and timeouts mean unknown. Never infer logout from a
failed request. Report the flow outcome and verified remaining state separately.
Resume an earlier business task only after its account and required tools are verified.

## Report a problem

Call `submit_feedback_report` when the user asks to report a problem, bug or wrong data
to the Quandora team, or accepts your offer to report one. Never file a report on your own
initiative or for an error you can still recover. Before sending, show the user the
category and note in their language; an explicit request to report is already consent.

- `category` (required): `data_missing`, `wrong_numbers`, `stuck_loading`, `page_error`
  or `other`.
- `note`: what the user saw, in their words or a faithful summary, at most 2000
  characters. Never include credentials, API keys, tokens, exchange secrets, authorization
  URLs or callback codes. Images and files are not accepted; describe what they show in the note.
- `context_type` and `context_id`: when the problem concerns one object, use
  `portfolio_trading_run` with a Simulation or Monitoring Run's `portfolio_trading_run_id`,
  `portfolio_monitoring` with a `portfolio_run_id`, `portfolio_availability` with the
  downlisted Portfolio's `portfolio_id`, or `client_error` with the web error digest.
  Copy the exact ID from a tool result or the user; never guess one. Otherwise omit both
  or use `general` without `context_id`.

The result is `{report_id, reference, duplicate, idempotent_replay}`. Give the user the
`reference` to quote. `duplicate: true` means it was added to the user's report about the
same object from the last day; `idempotent_replay: true` means this invocation was already filed.
Report one problem once: do not resubmit after an uncertain result, follow the shared
uncertain-mutation rule instead. `feedback_rate_limited` means the report limit is reached;
tell the user to try later and do not retry in a loop. `invalid_feedback_report` names a
field to correct once. `idempotency_conflict` means changed content reused one invocation;
send a new call only if the user still wants the changed report.

The tool needs an active connection but no extra permission. If it is not discoverable,
follow the shared connection policy; do not request broader scopes for it, and do not
substitute email, the web frontend or private APIs.

Use the [account acceptance scenarios](../../references/account-connection-verification.md)
when changing this flow; static package checks do not prove host behavior.
