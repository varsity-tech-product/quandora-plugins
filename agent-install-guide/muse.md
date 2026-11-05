# Install and authenticate Quandora in Muse

Read the [shared installation and recovery policy](https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/install-recovery.md) together with this guide. The user's request authorizes the requested installation within existing permissions. Use Muse's supported approvals where required; the user completes browser sign-in, MFA, and consent.

The canonical agent-readable copy is <https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/muse.md>.

Use Muse's **Custom Connector** workflow. This guide does not define a Muse CLI or assume that a connector, refresh script, or skill loader already exists. Discover the actual host capabilities and their schemas before using them. Explain the installation briefly, perform the available stages, and report any stage that needs a host capability or user action.

## Production sources

| Purpose | Official source |
| --- | --- |
| Connector name | `quandora` |
| Remote Streamable HTTP MCP endpoint | `https://mcp.quandora.ai/quant` |
| General installation documentation | <https://quandora.gitbook.io/en/start-here/installation-guide.md> |
| Public plugin repository | `https://github.com/varsity-tech-product/quandora-plugins.git`, branch `main` |
| Plugin manifest | `plugins/quandora/.claude-plugin/plugin.json` in that repository |
| Skill source | `plugins/quandora/skills/`, as declared by the current manifest |

Read the current installation documentation and manifest. Use the live server for OAuth metadata and MCP tool definitions, and the official repository for skill instructions. Do not copy a tool, scope, or skill count from an example or a previous installation.

## 1. Check and prepare the connector

Inspect Muse's available connectors and Custom Connector operations. Reuse an existing Quandora connector only when it targets the exact production endpoint above. Preserve a conflicting connector or directory and report its source; do not silently replace it. A connector that already supplies working OAuth and skill access should be verified, not rebuilt.

Use Muse's supported remote MCP integration inside the Custom Connector workflow. If Muse requires a custom implementation, inspect its current connector authoring instructions and use its supported OAuth/credential APIs. Do not invent operation names, shell commands, callback addresses, or credential-file layouts. If the host cannot support the required MCP transport or OAuth flow, report that capability as the blocker.

## 2. Discover OAuth and connect

Start discovery at `https://mcp.quandora.ai/quant`. Follow the resource metadata URL advertised by its authentication challenge; the current production discovery document is <https://mcp.quandora.ai/.well-known/oauth-protected-resource/quant>. Verify that its resource matches the endpoint and discover authorization-server metadata from the advertised issuer.

Use the currently advertised authorization, token, registration, revocation, and PKCE capabilities through Muse's supported OAuth integration. For a new public client, use the supported authorization-code flow with PKCE and registration when required. Keep client registration, redirect handling, token exchange, refresh, and storage inside the supported connector runtime and secure credential store. Do not ask the user for an API key or to paste a token, callback URL, or code into the conversation.

For the user's requested full Quandora integration, derive the requested permissions from the server's current advertised scopes and show them through the normal consent flow. The user signs in to Quandora and grants the permissions they choose. Discovering scopes does not grant them. Preserve an intentional restricted grant and report which requested capabilities remain unavailable. Newly added scopes require a supported consent update; do not silently expand an existing grant.

Keep one authorization flow active. Observe its machine-readable result and host-visible granted permissions when available, then continue verification. Do not infer the actual grant from advertised scopes or one successful read. Follow the shared policy for timeout, cancellation, and denial. A published refresh or revocation endpoint establishes server support; it does not prove the connector has implemented or tested those operations.

## 3. Load the current skills

MCP tools and Quandora skills have different sources. `tools/list` provides callable tool definitions; it does not install the repository's `SKILL.md` instructions or their references.

If a supported installation already supplies the current official skills, use those managed copies. Otherwise retain a dedicated checkout of the public repository in Muse's supported workspace. Use the exact HTTPS source and branch above. Reuse an existing checkout only after verifying its source, branch, and clean working tree; update it with a fast-forward-only operation. Preserve unrelated directories and local changes. GitHub login, a personal access token, and an SSH key are not prerequisites.

Read the plugin manifest and enumerate the actual skill directories under its declared skills path. Load each current `SKILL.md` through Muse's supported skill or connector-instruction mechanism, preserving frontmatter and relative reference access. If the host stores only the entry document, resolve its relative links against the retained skill directory so referenced files remain readable. Do not assume that cloning files registers skills in Muse.

Verify that the installed connector can discover and read the skill instructions and their referenced files when needed. Read the account-connection skill and follow its current version-check and connection policy. Continue verification of this installation's existing authorization flow; loading the skill is not a new user request to launch OAuth again. Report the version from the installed manifest, not a guessed release or the latest remote label. If Muse has no supported way to expose these instructions, report skill loading as pending and distinguish it from a successful MCP connection.

## 4. Discover tools and preserve update instructions

After OAuth completes, use MCP `tools/list` through the connector and follow every pagination cursor. Use the current schemas, descriptions, and annotations; do not generate wrappers or allowlists from an old tool-name snapshot. Check that the catalog covers the user's granted capabilities. A status/version tool alone does not demonstrate that Strategy or Portfolio tools are available. For a missing tool, distinguish stale discovery, a missing grant, account eligibility, and a capability not offered by the server before choosing recovery.

If Muse requires tool registration or an allowlist, implement it through its documented connector mechanism and verify the exposed catalog. Classify tools from their actual behavior and schema, not name alone. Newly discovered reads can be admitted after semantic review within existing permissions; mutations and ambiguous tools must follow the host's applicable review and approval rules. Remove stale entries for tools no longer advertised. Tool discovery never authorizes executing a write operation as an installation test.

When Muse supports persistent connector instructions or a session initialization hook, save the verified source references and a refresh procedure there: refresh live metadata and the complete tool catalog, update the clean official checkout, reconcile skills, and handle changed scopes through consent. Verify that the supported hook or instructions are actually registered. A prose recipe alone does not establish automatic synchronization, and this repository does not ship a Muse refresh script. If automatic synchronization is unavailable, report that updates need an explicit supported refresh.

## 5. Verify and start research

Check these outcomes separately:

1. The connector targets the exact production endpoint.
2. OAuth has completed with the intended grant, and authenticated tool discovery succeeds.
3. The current repository skills and their references are accessible through Muse's supported mechanism; load one to confirm.
4. A fresh read-only `get_quandora_account({})` call verifies the active account after OAuth, following the account-connection skill; the protected `get_factor_mining_status` call also succeeds.
5. Tools relevant to the user's intended workflow are available. When Strategy research is requested, read the current `get_strategy_capabilities` result if that tool is offered, following the applicable skill.

Do not submit a factor, strategy, backtest, or trade to test installation. If the grant lacks a required read, report the permission gap and use the supported consent update for the requested capability. If the host needs another message or session to expose newly installed tools or skills, preserve completed stages and finish verification there.

Report completion only after connector, OAuth, skill access, tool discovery, and the protected read all pass. Then proceed with the user's research request under the applicable Quandora skill. A new conversation is only necessary if Muse requires it. Product eligibility, invitations, or workflow-specific permissions are separate from installation success.

Summarize the observed stages and any remaining blocker without credentials or unnecessary account identifiers. Report refresh and revocation as tested only when those operations were actually exercised through the supported host flow. See the [Muse acceptance checklist](https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/verification.md#muse-custom-connector-acceptance) for independent clean-install and lifecycle verification.
