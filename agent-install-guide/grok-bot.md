# Install and authenticate Quandora in Grok Bot / Cursor

Also read the [shared installation and recovery policy](https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/install-recovery.md). This guide describes the procedure; it does not grant permission by itself. Use the host's supported approval flow for installation changes, and leave browser sign-in, MFA, and consent to the user.

Explain that installation adds the third-party Quandora connector and skills to the current user's host. Reuse completed installation and authorization stages. Never request or handle API keys, OAuth tokens, cookies, callback codes, or authorization URLs.

The canonical agent-readable copy is <https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/agent-install-guide/grok-bot.md>.

## Identify the host

For Cursor Desktop, use the existing native plugin route from the public README:

```text
/add-plugin quandora@https://github.com/varsity-tech-product/quandora-plugins
```

Use Cursor's supported plugin installation surface, authenticate the plugin-provided `quandora` Remote MCP server in the browser, then start a new Agent chat if required to load its tools and skills. Do not add a second connector or copy skills separately when the plugin already provides them. Continue with the verification section below.

For Grok Bot, discover the available connector and skill-management capabilities before continuing. The procedure below requires the host's connector inventory, installation, authorization, and skill-library operations. Names such as `GetMcpServerStatus`, `SearchPlugins`, `InstallPlugin`, `AddMcpServer`, `AuthenticateMcpServer`, and `UpdateSkill` refer to host operations when available; use the actual discovered schema. If the host lacks a required capability, report that stage as unavailable rather than inventing a command or substituting another host's CLI.

## Production identities

- MCP server name: `quandora`
- Remote Streamable HTTP endpoint with OAuth: `https://mcp.quandora.ai/quant`
- Public repository: `https://github.com/varsity-tech-product/quandora-plugins.git`, branch `main`
- Skill directory: `plugins/quandora/skills/`
- Expected skills: `account-connection`, `factor-mining`, `factor-analysis`, `strategy-building`, `strategy-analysis`, `portfolio-building`, `portfolio-analysis`, and `portfolio-trading-analysis`

## 1. Check the existing connection

Inspect the host's installed connectors. Reuse an existing `quandora` server only when its endpoint is exactly the production URL above. If that name points elsewhere, report the conflict and preserve the existing configuration. A connected indicator alone does not prove authenticated tool access.

Search the host's plugin catalog for Quandora. Prefer installing its supported plugin when available, using the required native approval. A plugin that provides both the connector and skills owns those resources; do not duplicate them. Otherwise, use the host's supported remote MCP operation to add the exact server name and URL, without custom authentication headers or an API key, after the required approval.

## 2. Authorize through the host

Use the host's native connector authorization card for the installed server. The user completes browser sign-in, MFA, and consent. Keep one authorization flow active at a time. Retry a completed timeout or transient error once; respect cancellation and security denials. Do not repair OAuth by reinstalling a working plugin or creating another connector.

## 3. Load the skills

If the installed plugin already exposes all eight skills, use those managed copies. For a Grok Bot host that stores each skill as a single `SKILL.md`, use its supported skill-library operation and a retained local copy of the public repository so relative references remain available.

Before cloning or updating, explain the local directory change and use any required host approval. The source is public; GitHub sign-in, a personal access token, or an SSH key is not a prerequisite. Use an existing Git installation and the exact HTTPS source.

Use a dedicated directory such as `~/quandora-plugins`. If it already exists, verify that it is a Git checkout of the exact repository above and that its working tree is clean before a fast-forward-only update of `main`. Preserve and report a conflicting source, branch, or local changes. If it is absent, clone `main` from the exact repository. Do not overwrite an unrelated directory.

For each expected skill, read `plugins/quandora/skills/<name>/SKILL.md`. When the host stores only that file, resolve relative Markdown link targets against the original skill directory and replace them with absolute paths into the retained checkout. Preserve HTTP(S), mailto, and fragment-only links, and retain frontmatter and all other content. Save through the host's skill-library operation. Skip an existing identical copy. Repeating this step after an approved repository update refreshes the saved skill while keeping referenced files available.

If the host exposes newly installed skills only after another message or session, report loading as pending and continue there. Do not claim a skill is loaded merely because it was saved.

## 4. Verify completion

Verify connector installation, authorization, skill availability, and tool access separately:

1. The connector or plugin uses the exact production identity above.
2. All eight expected skills are available through the host's supported discovery; load one to confirm.
3. OAuth has completed and supported tool discovery exposes Quandora tools.
4. The protected read-only `get_factor_mining_status` call succeeds with authenticated account access.

Do not submit a factor, strategy, backtest, or trade as an installation test. If tools require a fresh session, preserve completed installation and authorization and report verification as pending until the protected read succeeds. Describe the observed stage and any non-sensitive error; say complete only after all four checks pass.
