# Account connection acceptance

The Auth service must expose `get_quandora_account({}) -> {id, email}` before this
plugin version is recommended. It must resolve only the active token's Auth user,
with no account selector and no extra research/trading scope. Keep OAuth and issuer
validation host-owned; this Skill does not repair an OAuth protocol incompatibility.

For Codex, select **Quandora Account** from the Skill picker or explicitly reference
`$account-connection`, followed by "show my current account", "open authorization",
"reauthorize Quandora", or "switch to my other account". Natural language requests
have the same intent routing. The installed package must be reloaded before use.

Record host/app and bundled CLI versions, package version, scenario, observed launch
count, completion state and whether identity changed. Do not save token values,
authorization URLs, callback codes, or personal account emails in public evidence.

| Scenario | Required observation |
| --- | --- |
| Fresh install, no credentials or MCP tools | Skill can load and initiates one native flow; no business failure is required. |
| Connected user requests status | Fresh current identity; no interactive login. |
| Connected user explicitly requests authorization again | One new native flow starts even though the existing grant is valid. |
| Connected user requests account switch | Business calls pause; a fresh post-login profile has a different stable ID and matches any requested email. |
| Browser reuses old account | Switch is reported incomplete; no business call and no automatic second login. |
| Old identity unknown | Returned identity is shown; target is confirmed before business calls resume. |
| User cancels or flow times out | Flow stops; no repeated login; remaining account is verified or marked unknown. |
| Callback succeeds but host retains old grant | Switch remains incomplete; only a verified supported reload step is suggested. |
| Native action absent / plugin lookup fails | Verified same-host CLI fallback starts, if permitted; no duplicate connection. |
| Host explicitly denies authorization | Stop; no fallback to bypass the denial. |
| Identity endpoint unavailable / network fails | Verification remains pending; no false success or inferred logout. |
| Issuer validation fails | Preserve validation; report the failure and versions, not a successful connection or reinstall fix. |

Static package and API tests cover packaging and the identity contract. All browser
and host scenarios above remain pending until executed on the supported host with
user-controlled test accounts. Two-account acceptance requires two distinct accounts.
After release, rollback uses the previous plugin package and recommended-version
label; do not erase user credentials. Auth's additive identity endpoint can remain.
