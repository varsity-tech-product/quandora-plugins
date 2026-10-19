#!/usr/bin/env node
"use strict";

const crypto = require("node:crypto");
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const CONFIG_ID = "custom-mcp:quandora";
const MCP_URL = "https://mcp.quandora.ai/quant";
const AUTHORIZATION_SERVER = "https://mcp.quandora.ai";
const PROTOCOL_VERSION = "2025-06-18";
const CALLBACK_TIMEOUT_MS = 5 * 60 * 1000;
const REQUEST_TIMEOUT_MS = 30 * 1000;

class SafeError extends Error {
  constructor(message, code = "authorization_failed") {
    super(message);
    this.code = code;
  }
}
class AuthenticationRequiredError extends SafeError {}

function suppressRuntimeConsole() {
  // WorkBuddy's bundled modules log startup diagnostics when required. Keep
  // stdout machine-readable and OAuth runtime details out of Agent transcripts.
  console.debug = () => {};
  console.error = () => {};
  console.info = () => {};
  console.log = () => {};
  console.warn = () => {};
}

function fail(message, code) {
  throw new SafeError(message, code);
}

function emitProgress(step) {
  process.stderr.write(`${JSON.stringify({ status: "progress", step })}\n`);
}

function boundedFetch(input, init = {}) {
  const timeoutSignal = AbortSignal.timeout(REQUEST_TIMEOUT_MS);
  const signal = init.signal
    ? AbortSignal.any([init.signal, timeoutSignal])
    : timeoutSignal;
  return fetch(input, { ...init, signal });
}

function readJson(filePath, label) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    fail(`${label} is missing or invalid.`);
  }
}

function requireString(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    fail(`${label} is missing.`);
  }
  return value.trim();
}

function verifyPlugin(pluginRoot) {
  const manifest = readJson(
    path.join(pluginRoot, ".codebuddy-plugin", "plugin.json"),
    "Quandora plugin manifest",
  );
  if (manifest.name !== "quandora") {
    fail("The installed plugin identity does not match Quandora.");
  }

  const mcp = readJson(
    path.join(pluginRoot, "mcp.json"),
    "Quandora MCP manifest",
  );
  const server = mcp?.mcpServers?.["quandora"];
  if (server?.type !== "http" || server?.url !== MCP_URL) {
    fail("The installed plugin MCP declaration does not match Quandora.");
  }
}

function resolveActiveUserId(configRoot) {
  const snapshot = readJson(
    path.join(configRoot, "storage", "skeleton", "account-snapshot.json"),
    "WorkBuddy account snapshot",
  );
  const userId = requireString(snapshot?.primary?.uid, "WorkBuddy user identity");
  if (!/^[A-Za-z0-9_-]{8,160}$/.test(userId)) {
    fail("The active WorkBuddy user identity has an unsupported format.");
  }
  return userId;
}

function parseRpcPayload(responseText, contentType) {
  if (!responseText.trim()) return null;

  if (contentType.toLowerCase().includes("text/event-stream")) {
    const messages = [];
    for (const line of responseText.split(/\r?\n/)) {
      if (!line.startsWith("data:")) continue;
      const data = line.slice(5).trim();
      if (!data || data === "[DONE]") continue;
      try {
        messages.push(JSON.parse(data));
      } catch {
        fail("Quandora returned an invalid MCP event payload.");
      }
    }
    return messages.at(-1) ?? null;
  }

  try {
    return JSON.parse(responseText);
  } catch {
    fail("Quandora returned an invalid MCP response.");
  }
}

async function mcpRequest(token, sessionId, payload, allowEmpty = false) {
  const headers = {
    Accept: "application/json, text/event-stream",
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    "MCP-Protocol-Version": PROTOCOL_VERSION,
  };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;

  const response = await fetch(MCP_URL, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (response.status === 401 || response.status === 403) {
    await response.body?.cancel();
    throw new AuthenticationRequiredError("Quandora authorization is required.");
  }
  if (!response.ok) {
    await response.body?.cancel();
    fail(`Quandora MCP verification failed with HTTP ${response.status}.`);
  }

  const text = await response.text();
  const rpc = parseRpcPayload(text, response.headers.get("content-type") || "");
  if (!allowEmpty && !rpc) fail("Quandora returned an empty MCP response.");
  if (rpc?.error) fail("Quandora returned an MCP verification error.");
  return {
    rpc,
    sessionId: response.headers.get("mcp-session-id") || sessionId,
  };
}

async function verifyProtectedTool(tokens) {
  emitProgress("protected_probe_started");
  const accessToken = requireString(tokens?.access_token, "Quandora access token");
  let sessionId;
  try {
    const initialized = await mcpRequest(accessToken, null, {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: PROTOCOL_VERSION,
        capabilities: {},
        clientInfo: {
          name: "quandora-workbuddy-cn-installer",
          version: "1.0.0",
        },
      },
    });
    sessionId = initialized.sessionId;
    if (!initialized.rpc?.result || !sessionId) {
      fail("Quandora MCP initialization did not establish a session.");
    }

    await mcpRequest(
      accessToken,
      sessionId,
      {
        jsonrpc: "2.0",
        method: "notifications/initialized",
      },
      true,
    );

    const listed = await mcpRequest(accessToken, sessionId, {
      jsonrpc: "2.0",
      id: 2,
      method: "tools/list",
      params: {},
    });
    const tools = listed.rpc?.result?.tools;
    if (!Array.isArray(tools) || !tools.some((tool) => tool?.name === "get_factor_mining_status")) {
      fail("The authenticated Quandora MCP server does not expose get_factor_mining_status.");
    }

    const called = await mcpRequest(accessToken, sessionId, {
      jsonrpc: "2.0",
      id: 3,
      method: "tools/call",
      params: { name: "get_factor_mining_status", arguments: {} },
    });
    if (!called.rpc?.result || called.rpc.result.isError === true) {
      fail("The protected Quandora get_factor_mining_status verification call failed.");
    }
    emitProgress("protected_probe_completed");
    return tools.length;
  } finally {
    if (sessionId) {
      fetch(MCP_URL, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "MCP-Protocol-Version": PROTOCOL_VERSION,
          "Mcp-Session-Id": sessionId,
        },
        signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
      }).catch(() => {});
    }
  }
}

async function discoverOAuth(auth) {
  emitProgress("oauth_discovery_started");
  const resourceMetadata = await auth.discoverOAuthProtectedResourceMetadata(
    new URL(MCP_URL),
    { protocolVersion: PROTOCOL_VERSION },
    boundedFetch,
  );
  if (resourceMetadata.resource !== MCP_URL) {
    fail("Quandora OAuth resource metadata does not match the plugin endpoint.");
  }
  if (
    !Array.isArray(resourceMetadata.authorization_servers) ||
    resourceMetadata.authorization_servers.length !== 1 ||
    resourceMetadata.authorization_servers[0] !== AUTHORIZATION_SERVER
  ) {
    fail("Quandora OAuth authorization-server metadata is unexpected.");
  }

  const authorizationServerUrl = new URL(AUTHORIZATION_SERVER);
  const authorizationMetadata =
    await auth.discoverAuthorizationServerMetadata(authorizationServerUrl, {
      protocolVersion: PROTOCOL_VERSION,
      fetchFn: boundedFetch,
    });
  if (
    authorizationMetadata?.issuer !== AUTHORIZATION_SERVER ||
    authorizationMetadata.authorization_endpoint !==
      `${AUTHORIZATION_SERVER}/oauth/authorize` ||
    authorizationMetadata.token_endpoint !== `${AUTHORIZATION_SERVER}/oauth/token` ||
    authorizationMetadata.registration_endpoint !==
      `${AUTHORIZATION_SERVER}/oauth/register`
  ) {
    fail("Quandora OAuth server endpoints are unexpected.");
  }

  const scopes = resourceMetadata.scopes_supported;
  if (!Array.isArray(scopes) || scopes.length === 0) {
    fail("Quandora OAuth scopes are unavailable.");
  }
  emitProgress("oauth_discovery_completed");
  return {
    authorizationMetadata,
    authorizationServerUrl,
    resource: new URL(resourceMetadata.resource),
    scope: scopes.join(" "),
  };
}

function createCallbackServer() {
  let resolveCallback;
  let rejectCallback;
  let callbackResponse;
  let timer;
  const callback = new Promise((resolve, reject) => {
    resolveCallback = resolve;
    rejectCallback = reject;
  });

  const server = http.createServer((request, response) => {
    try {
      const requestUrl = new URL(request.url || "/", "http://127.0.0.1");
      const address = server.address();
      const port = address && typeof address !== "string" ? address.port : 0;
      const host = request.headers.host;
      const origin = request.headers.origin;
      const allowedHost = host === `127.0.0.1:${port}` || host === `localhost:${port}`;
      let allowedOrigin = origin === undefined;
      if (origin !== undefined) {
        try {
          const parsedOrigin = new URL(origin);
          allowedOrigin =
            parsedOrigin.protocol === "http:" &&
            ["127.0.0.1", "localhost", "::1"].includes(parsedOrigin.hostname) &&
            Number(parsedOrigin.port) === port;
        } catch {
          allowedOrigin = false;
        }
      }
      if (request.method !== "GET" || !allowedHost || !allowedOrigin) {
        response.writeHead(403, { "Content-Type": "text/plain; charset=utf-8" });
        response.end("Forbidden.\n");
        return;
      }
      if (requestUrl.pathname !== "/oauth/callback") {
        response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
        response.end("Not found.\n");
        return;
      }
      if (callbackResponse) {
        response.writeHead(409, { "Content-Type": "text/plain; charset=utf-8" });
        response.end("Authorization callback already received.\n");
        return;
      }
      callbackResponse = response;
      resolveCallback(requestUrl);
    } catch (error) {
      if (!response.headersSent) {
        response.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" });
      }
      response.end("Invalid authorization callback.\n");
      rejectCallback(error);
    }
  });

  server.on("error", rejectCallback);

  return {
    server,
    callback,
    async listen() {
      await new Promise((resolve, reject) => {
        server.once("error", reject);
        server.listen(0, "127.0.0.1", () => {
          server.off("error", reject);
          resolve();
        });
      });
      const address = server.address();
      if (!address || typeof address === "string") {
        fail("The local OAuth callback listener did not start.");
      }
      timer = setTimeout(() => {
        if (callbackResponse && !callbackResponse.writableEnded) {
          callbackResponse.shouldKeepAlive = false;
          callbackResponse.writeHead(408, {
            "Content-Type": "text/plain; charset=utf-8",
            "Cache-Control": "no-store",
            Connection: "close",
          });
          callbackResponse.end("Quandora authorization timed out. Return to WorkBuddy.\n");
        }
        rejectCallback(new Error("Quandora authorization timed out."));
        server.close();
      }, CALLBACK_TIMEOUT_MS);
      return new URL(`http://127.0.0.1:${address.port}/oauth/callback`);
    },
    respond(success) {
      if (!callbackResponse || callbackResponse.writableEnded) return;
      callbackResponse.shouldKeepAlive = false;
      callbackResponse.writeHead(success ? 200 : 400, {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-store",
        Connection: "close",
      });
      callbackResponse.end(
        success
          ? "<!doctype html><meta charset=utf-8><title>Quandora authorized</title>" +
              "<p>Quandora authorization completed. You can return to WorkBuddy.</p>"
          : "<!doctype html><meta charset=utf-8><title>Quandora authorization failed</title>" +
              "<p>Quandora could not complete authorization. Return to WorkBuddy.</p>",
      );
    },
    close() {
      if (timer) clearTimeout(timer);
      server.close();
      server.closeAllConnections?.();
    },
  };
}

async function authenticate(auth, store, oauth) {
  const listener = createCallbackServer();
  const redirectUrl = await listener.listen();
  emitProgress("callback_listener_ready");
  let callbackReceived = false;
  try {
    const clientMetadata = {
      client_name: "Quandora for WorkBuddy",
      redirect_uris: [redirectUrl.href],
      token_endpoint_auth_method: "none",
      grant_types: ["authorization_code", "refresh_token"],
      response_types: ["code"],
    };
    const clientInformation = await auth.registerClient(
      oauth.authorizationServerUrl,
      {
        metadata: oauth.authorizationMetadata,
        clientMetadata,
        scope: oauth.scope,
        fetchFn: boundedFetch,
      },
    );
    const state = crypto.randomBytes(32).toString("base64url");
    const authorization = await auth.startAuthorization(
      oauth.authorizationServerUrl,
      {
        metadata: oauth.authorizationMetadata,
        clientInformation,
        redirectUrl,
        scope: oauth.scope,
        state,
        resource: oauth.resource,
      },
    );

    const opened = spawnSync("/usr/bin/open", [authorization.authorizationUrl.href], {
      stdio: "ignore",
    });
    if (opened.status !== 0) fail("WorkBuddy could not open the authorization page.");
    emitProgress("browser_opened");

    const callbackUrl = await listener.callback;
    callbackReceived = true;
    emitProgress("callback_received");
    if (callbackUrl.searchParams.get("state") !== state) {
      fail("The OAuth callback state did not match.");
    }
    const oauthError = callbackUrl.searchParams.get("error");
    if (oauthError) fail("Quandora authorization was declined or failed.");
    const code = requireString(
      callbackUrl.searchParams.get("code"),
      "OAuth authorization code",
    );

    emitProgress("token_exchange_started");
    const tokens = await auth.exchangeAuthorization(
      oauth.authorizationServerUrl,
      {
        metadata: oauth.authorizationMetadata,
        clientInformation,
        authorizationCode: code,
        codeVerifier: authorization.codeVerifier,
        redirectUri: redirectUrl,
        resource: oauth.resource,
        fetchFn: boundedFetch,
      },
    );
    emitProgress("token_exchange_completed");
    if (!store.saveClientInfo(CONFIG_ID, MCP_URL, clientInformation)) {
      fail("WorkBuddy refused to save the Quandora OAuth client.");
    }
    if (!store.saveTokens(CONFIG_ID, MCP_URL, tokens)) {
      fail("WorkBuddy refused to save Quandora authorization.");
    }
    emitProgress("authorization_saved");
    listener.respond(true);
    return tokens;
  } catch (error) {
    if (callbackReceived) listener.respond(false);
    throw error;
  } finally {
    listener.close();
  }
}

async function refreshStoredTokens(auth, store, oauth, tokens) {
  if (!tokens?.refresh_token) return null;
  const clientInformation = store.loadClientInfo(CONFIG_ID, MCP_URL);
  if (!clientInformation) return null;
  try {
    const refreshed = await auth.refreshAuthorization(oauth.authorizationServerUrl, {
      metadata: oauth.authorizationMetadata,
      clientInformation,
      refreshToken: tokens.refresh_token,
      resource: oauth.resource,
      fetchFn: boundedFetch,
    });
    if (!store.saveTokens(CONFIG_ID, MCP_URL, refreshed)) return null;
    return refreshed;
  } catch {
    return null;
  }
}

function notifyWorkBuddy(configRoot) {
  const registry = path.join(configRoot, "plugins", "installed_plugins.json");
  if (!fs.existsSync(registry)) fail("WorkBuddy plugin registry is missing.");
  const now = new Date();
  fs.utimesSync(registry, now, now);
}

async function main() {
  if (process.platform !== "darwin") fail("This helper supports macOS only.");
  const [pluginRootArgument, configRootArgument, appRootArgument] = process.argv.slice(2);
  const pluginRoot = fs.realpathSync(requireString(pluginRootArgument, "Plugin path"));
  const configRoot = fs.realpathSync(requireString(configRootArgument, "Config path"));
  const appRoot = fs.realpathSync(requireString(appRootArgument, "WorkBuddy app path"));
  const electron = fs.realpathSync(path.join(appRoot, "Contents", "MacOS", "Electron"));
  if (fs.realpathSync(process.execPath) !== electron) {
    fail("The helper is not running with the selected WorkBuddy application runtime.");
  }
  const pluginCache = fs.realpathSync(path.join(configRoot, "plugins", "cache"));
  if (!pluginRoot.startsWith(`${pluginCache}${path.sep}`)) {
    fail("The helper is not running from WorkBuddy's managed plugin cache.");
  }
  verifyPlugin(pluginRoot);

  const resources = path.join(appRoot, "Contents", "Resources");
  const tarModule = require(path.join(resources, "app.asar", "main", "tar.js"));
  const authModule = require(path.join(resources, "app.asar", "main", "auth.js"));
  const ConnectorOAuthStore = tarModule.ConnectorOAuthStore;
  const auth = authModule.auth_exports;
  if (
    typeof fetch !== "function" ||
    typeof globalThis.AbortSignal?.timeout !== "function" ||
    typeof globalThis.AbortSignal?.any !== "function" ||
    typeof ConnectorOAuthStore !== "function" ||
    !auth ||
    typeof auth.discoverOAuthProtectedResourceMetadata !== "function" ||
    typeof auth.discoverAuthorizationServerMetadata !== "function" ||
    typeof auth.registerClient !== "function" ||
    typeof auth.startAuthorization !== "function" ||
    typeof auth.exchangeAuthorization !== "function" ||
    typeof auth.refreshAuthorization !== "function"
  ) {
    fail(
      "This WorkBuddy build does not expose the required native OAuth runtime.",
      "host_update_required",
    );
  }
  emitProgress("oauth_runtime_ready");

  const store = new ConnectorOAuthStore(resolveActiveUserId(configRoot));
  let tokens = store.loadTokens(CONFIG_ID, MCP_URL);
  let toolCount;
  if (tokens?.access_token) {
    try {
      toolCount = await verifyProtectedTool(tokens);
    } catch (error) {
      if (!(error instanceof AuthenticationRequiredError)) throw error;
    }
  }

  let reusedAuthorization = toolCount !== undefined;
  if (toolCount === undefined) {
    const oauth = await discoverOAuth(auth);
    tokens = await refreshStoredTokens(auth, store, oauth, tokens);
    if (tokens?.access_token) {
      try {
        toolCount = await verifyProtectedTool(tokens);
        reusedAuthorization = true;
      } catch (error) {
        if (!(error instanceof AuthenticationRequiredError)) throw error;
      }
    }
    if (toolCount === undefined) {
      tokens = await authenticate(auth, store, oauth);
      toolCount = await verifyProtectedTool(tokens);
      reusedAuthorization = false;
    }
  }

  notifyWorkBuddy(configRoot);
  emitProgress("workbuddy_notified");
  process.stdout.write(
    `${JSON.stringify({
      status: "completed",
      authenticated: true,
      protectedProbe: "get_factor_mining_status",
      toolCount,
      browserAuthorizationOpened: !reusedAuthorization,
    })}\n`,
  );
}

if (require.main === module) {
  suppressRuntimeConsole();
  main().catch((error) => {
    process.stderr.write(
      `${JSON.stringify({
        status: "failed",
        code:
          error instanceof SafeError
            ? error.code
            : "authorization_failed",
        message:
          error instanceof SafeError
            ? error.message
            : "Quandora authorization or protected verification failed.",
      })}\n`,
    );
    process.exitCode = 1;
  });
}

module.exports = { createCallbackServer };
