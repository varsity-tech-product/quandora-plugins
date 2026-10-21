#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");

const BUNDLE_ID = "com.tencent.workbuddy.mac";
const URL_SCHEME = "workbuddy";
const MARKETPLACE_REPOSITORY = "varsity-tech-product/quandora-plugins";
const MARKETPLACE_NAME = "quandora";
const PLUGIN_ID = "quandora@quandora";
const PLUGIN_NAME = "quandora";
const MCP_URL = "https://mcp.quandora.ai/quant";
const CLI_HEALTH_TIMEOUT_MS = 45 * 1000;
const CLI_TIMEOUT_MS = 2 * 60 * 1000;
const OAUTH_TIMEOUT_MS = 7 * 60 * 1000;
const INSTALL_TIMEOUT_MS = 9 * 60 * 1000 + 30 * 1000;
const OUTPUT_LIMIT_BYTES = 1024 * 1024;
const DEFAULT_REMEDIATION = "Stop without retrying and report this safe failure.";
const CLI_REMEDIATION =
  "Close this failed task, restart WorkBuddy, and paste the same installation prompt once in a new local Agent task. If it repeats, update WorkBuddy from Personal Center first.";
const AGENT_ROUTING_ENV_KEYS = [
  "CODEBUDDY_SESSION_ID",
  "CODEBUDDY_TOOL_CALL_ID",
  "CODEBUDDY_CONVERSATION_REQUEST_ID",
  "CODEBUDDY_MCP_CONFIG",
  "CODEBUDDY_SERVICE_PROXY_URL",
  "CODEBUDDY_PROJECT_DIR",
  "CODEBUDDY_CURRENT_MODEL_ID",
  "CLAUDE_SESSION_ID",
  "CLAUDE_PROJECT_DIR",
  "SERVER__HOST",
  "SERVER__PORT",
];
const EXPECTED_SKILLS = [
  "account-connection",
  "factor-mining",
  "factor-analysis",
  "strategy-building",
  "strategy-analysis",
  "portfolio-building",
  "portfolio-analysis",
  "portfolio-trading-analysis",
];
const OAUTH_PROGRESS_STEPS = new Set([
  "oauth_runtime_ready",
  "protected_probe_started",
  "protected_probe_completed",
  "oauth_discovery_started",
  "oauth_discovery_completed",
  "callback_listener_ready",
  "browser_opened",
  "callback_received",
  "token_exchange_started",
  "token_exchange_completed",
  "authorization_saved",
  "workbuddy_notified",
]);

class SafeError extends Error {
  constructor(message, code = "installation_failed", remediation = DEFAULT_REMEDIATION) {
    super(message);
    this.code = code;
    this.remediation = remediation;
  }
}

function fail(message, code, remediation) {
  throw new SafeError(message, code, remediation);
}

function requireString(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    fail(`${label} is missing.`);
  }
  return value.trim();
}

function readJson(filePath, label) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    fail(`${label} is missing or invalid.`);
  }
}

function realpath(filePath, label) {
  try {
    return fs.realpathSync(filePath);
  } catch {
    fail(`${label} is missing.`);
  }
}

function isInside(parent, child) {
  const relative = path.relative(parent, child);
  return relative !== "" && relative !== ".." && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative);
}

function emit(payload) {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
}

function resolveBootstrapOAuthHelper(helperPath, installerPath) {
  const reviewedHelperPath = realpath(helperPath, "Reviewed Quandora OAuth helper");
  if (
    path.basename(reviewedHelperPath) !== "workbuddy-cn-oauth-macos.js" ||
    path.dirname(reviewedHelperPath) !== path.dirname(installerPath)
  ) {
    fail("The reviewed Quandora OAuth helper is missing or invalid.");
  }
  return reviewedHelperPath;
}

function createCliEnv(configRoot) {
  const env = { ...process.env };
  for (const key of AGENT_ROUTING_ENV_KEYS) delete env[key];
  env.CODEBUDDY_CONFIG_DIR = configRoot;
  env.NO_COLOR = "1";
  return env;
}

function pluginArgs(...args) {
  return ["plugin", ...args, "--", "--print"];
}

function remainingTimeout(startedAt, maximumMs, label) {
  const remaining = INSTALL_TIMEOUT_MS - (Date.now() - startedAt);
  if (remaining <= 0) fail(`${label} could not start before the installer deadline.`);
  return Math.min(maximumMs, remaining);
}

function cleanupTemporaryBootstrap() {
  try {
    const installerPath = fs.realpathSync(__filename);
    const installerDirectory = path.dirname(installerPath);
    const temporaryRoot = fs.realpathSync(process.env.TMPDIR || "/tmp");
    if (
      path.basename(installerPath) !== "workbuddy-cn-install-macos.js" ||
      !/^quandora-workbuddy\.[A-Za-z0-9]{6,12}$/.test(path.basename(installerDirectory)) ||
      !isInside(temporaryRoot, installerDirectory)
    ) {
      return;
    }
    const oauthHelperPath = path.join(installerDirectory, "workbuddy-cn-oauth-macos.js");
    if (fs.existsSync(oauthHelperPath)) fs.unlinkSync(oauthHelperPath);
    fs.unlinkSync(installerPath);
    fs.rmdirSync(installerDirectory);
  } catch {
    // Cleanup is best-effort and never changes the installation result.
  }
}

async function runProcess(command, args, options) {
  const {
    label,
    timeoutMs,
    env = process.env,
    onStderrLine,
    failureCode = "process_failed",
    remediation = DEFAULT_REMEDIATION,
  } = options;
  return new Promise((resolve, reject) => {
    let settled = false;
    let timedOut = false;
    let oversized = false;
    let stdout = Buffer.alloc(0);
    let stderr = Buffer.alloc(0);
    let pendingStderr = "";
    let killTimer;
    let timeout;

    const child = spawn(command, args, {
      env,
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
    });

    const finish = (error, result) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      clearTimeout(killTimer);
      if (error) reject(error);
      else resolve(result);
    };

    const terminate = () => {
      child.kill("SIGTERM");
      if (!killTimer) {
        killTimer = setTimeout(() => child.kill("SIGKILL"), 2000);
      }
    };

    const append = (current, chunk) => {
      if (current.length + chunk.length > OUTPUT_LIMIT_BYTES) {
        oversized = true;
        terminate();
        return current;
      }
      return Buffer.concat([current, chunk]);
    };

    child.stdout.on("data", (chunk) => {
      stdout = append(stdout, chunk);
    });
    child.stderr.on("data", (chunk) => {
      stderr = append(stderr, chunk);
      if (onStderrLine) {
        pendingStderr += chunk.toString("utf8");
        let newline = pendingStderr.indexOf("\n");
        while (newline !== -1) {
          onStderrLine(pendingStderr.slice(0, newline));
          pendingStderr = pendingStderr.slice(newline + 1);
          newline = pendingStderr.indexOf("\n");
        }
      }
    });
    child.on("error", () => {
      finish(new SafeError(`${label} could not be started.`, failureCode, remediation));
    });
    child.on("close", (code, signal) => {
      if (onStderrLine && pendingStderr) onStderrLine(pendingStderr);
      if (timedOut) {
        const outputState = stdout.length === 0 && stderr.length === 0
          ? " without producing output"
          : "";
        finish(new SafeError(`${label} timed out${outputState}.`, failureCode, remediation));
        return;
      }
      if (oversized) {
        finish(new SafeError(`${label} returned too much output.`, failureCode, remediation));
        return;
      }
      finish(null, {
        code,
        signal,
        stdout: stdout.toString("utf8"),
        stderr: stderr.toString("utf8"),
      });
    });

    timeout = setTimeout(() => {
      timedOut = true;
      terminate();
    }, timeoutMs);
  });
}

function relayOAuthProgress(line) {
  let payload;
  try {
    payload = JSON.parse(line);
  } catch {
    return;
  }
  if (
    payload?.status === "progress" &&
    typeof payload.step === "string" &&
    OAUTH_PROGRESS_STEPS.has(payload.step)
  ) {
    emit({ status: "progress", step: payload.step });
  }
}

function oauthFailureRequiresHostUpdate(stderr) {
  for (const line of stderr.split(/\r?\n/).reverse()) {
    try {
      const payload = JSON.parse(line);
      if (payload?.status === "failed" && payload?.code === "host_update_required") {
        return true;
      }
    } catch {
      // Ignore non-JSON runtime diagnostics.
    }
  }
  return false;
}

async function requireSuccess(command, args, options) {
  const result = await runProcess(command, args, options);
  if (result.code !== 0) {
    fail(
      `${options.label} failed.`,
      options.exitFailureCode || "process_failed",
      options.remediation || DEFAULT_REMEDIATION,
    );
  }
  return result.stdout;
}

async function requireCliSuccess(command, args, options) {
  return requireSuccess(command, args, {
    ...options,
    failureCode: "cli_unhealthy",
    exitFailureCode: options.exitFailureCode || "cli_operation_failed",
    remediation: CLI_REMEDIATION,
  });
}

async function plutilValue(infoPlist, key) {
  const stdout = await requireSuccess(
    "/usr/bin/plutil",
    ["-extract", key, "raw", "-o", "-", infoPlist],
    { label: "WorkBuddy application inspection", timeoutMs: 30 * 1000 },
  );
  return stdout.trim();
}

function validateAccount(configRoot) {
  const snapshot = readJson(
    path.join(configRoot, "storage", "skeleton", "account-snapshot.json"),
    "WorkBuddy account snapshot",
  );
  const userId = requireString(snapshot?.primary?.uid, "WorkBuddy user identity");
  if (!/^[A-Za-z0-9_-]{8,160}$/.test(userId)) {
    fail("The active WorkBuddy user identity has an unsupported format.");
  }
}

function validateMarketplace(marketplace, configRoot) {
  if (
    marketplace?.type !== "github" ||
    marketplace?.source?.source !== "github" ||
    marketplace?.source?.repo !== MARKETPLACE_REPOSITORY
  ) {
    fail("The Quandora marketplace name is already assigned to another source.");
  }
  const marketplaceRoot = realpath(
    requireString(marketplace.installLocation, "Quandora marketplace path"),
    "Quandora marketplace path",
  );
  const expectedMarketplaceRoot = realpath(
    path.join(configRoot, "plugins", "marketplaces", MARKETPLACE_NAME),
    "Quandora marketplace path",
  );
  if (marketplaceRoot !== expectedMarketplaceRoot) {
    fail("The Quandora marketplace is outside WorkBuddy's managed marketplace directory.");
  }
  const manifest = readJson(
    path.join(marketplaceRoot, ".codebuddy-plugin", "marketplace.json"),
    "Quandora marketplace manifest",
  );
  const entries = manifest?.plugins;
  if (!Array.isArray(entries)) fail("The Quandora marketplace manifest is invalid.");
  const plugin = entries.find((entry) => entry?.name === PLUGIN_NAME);
  const version = requireString(plugin?.version, "Quandora marketplace version");
  if (
    manifest?.name !== MARKETPLACE_NAME ||
    manifest?.version !== version ||
    !/^[0-9A-Za-z][0-9A-Za-z.+-]{0,63}$/.test(version) ||
    plugin?.source !== "./plugins/quandora"
  ) {
    fail("The Quandora marketplace package declaration is invalid.");
  }
  return version;
}

function parsePluginList(stdout) {
  let payload;
  try {
    payload = JSON.parse(stdout);
  } catch {
    fail("WorkBuddy returned an invalid plugin inventory.");
  }
  if (!Array.isArray(payload)) fail("WorkBuddy returned an invalid plugin inventory.");
  return payload;
}

function selectUserPlugin(entries) {
  const matches = entries.filter(
    (entry) => entry?.id === PLUGIN_ID && entry?.scope === "user",
  );
  if (matches.length > 1) fail("WorkBuddy returned duplicate user-scoped Quandora plugins.");
  return matches[0];
}

function requiredRuntimeFiles(pluginRoot) {
  return [
    path.join(pluginRoot, ".codebuddy-plugin", "plugin.json"),
    path.join(pluginRoot, "mcp.json"),
    ...EXPECTED_SKILLS.map((skill) => path.join(pluginRoot, "skills", skill, "SKILL.md")),
  ];
}

function hasRequiredPackageFiles(entry, configRoot) {
  if (typeof entry?.installPath !== "string" || entry.installPath.trim() === "") return false;
  try {
    const pluginRoot = fs.realpathSync(entry.installPath);
    const pluginCache = fs.realpathSync(path.join(configRoot, "plugins", "cache"));
    if (!isInside(pluginCache, pluginRoot)) return false;
    return requiredRuntimeFiles(pluginRoot).every((filePath) => fs.statSync(filePath).isFile());
  } catch {
    return false;
  }
}

function validateInstalledPlugin(entry, configRoot, marketplaceVersion) {
  if (!entry || entry.enabled !== true) fail("Quandora is not enabled for the WorkBuddy user.");
  if (entry.version !== marketplaceVersion) {
    fail("The installed Quandora version does not match the marketplace.");
  }

  const pluginRoot = realpath(requireString(entry.installPath, "Quandora install path"), "Quandora install path");
  const pluginCache = realpath(path.join(configRoot, "plugins", "cache"), "WorkBuddy plugin cache");
  if (!isInside(pluginCache, pluginRoot)) {
    fail("Quandora is not installed inside WorkBuddy's managed plugin cache.");
  }
  for (const filePath of requiredRuntimeFiles(pluginRoot)) {
    try {
      if (!fs.statSync(filePath).isFile()) fail("The installed Quandora package is incomplete.");
    } catch (error) {
      if (error instanceof SafeError) throw error;
      fail("The installed Quandora package is incomplete.");
    }
  }

  const manifest = readJson(
    path.join(pluginRoot, ".codebuddy-plugin", "plugin.json"),
    "Installed Quandora plugin manifest",
  );
  if (manifest.name !== PLUGIN_NAME || manifest.version !== marketplaceVersion) {
    fail("The installed Quandora plugin identity is invalid.");
  }
  const mcp = readJson(path.join(pluginRoot, "mcp.json"), "Installed Quandora MCP manifest");
  if (
    mcp?.mcpServers?.quandora?.type !== "http" ||
    mcp?.mcpServers?.quandora?.url !== MCP_URL
  ) {
    fail("The installed Quandora MCP declaration is invalid.");
  }
  return pluginRoot;
}

function parseOAuthResult(stdout) {
  const lines = stdout.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  if (lines.length !== 1) fail("Quandora authorization returned an invalid result.");
  let payload;
  try {
    payload = JSON.parse(lines[0]);
  } catch {
    fail("Quandora authorization returned an invalid result.");
  }
  if (
    payload?.status !== "completed" ||
    payload?.authenticated !== true ||
    payload?.protectedProbe !== "get_factor_mining_status" ||
    !Number.isInteger(payload?.toolCount) ||
    payload.toolCount <= 0
  ) {
    fail("Quandora authorization or protected verification failed.");
  }
  return payload;
}

async function main() {
  const startedAt = Date.now();
  if (process.platform !== "darwin") fail("This installer supports macOS only.");
  const [appRootArgument, configRootArgument] = process.argv.slice(2);
  const appRoot = realpath(
    requireString(appRootArgument, "WorkBuddy application path"),
    "WorkBuddy application",
  );
  const configRoot = realpath(
    requireString(configRootArgument, "WorkBuddy configuration path"),
    "WorkBuddy configuration directory",
  );

  const infoPlist = path.join(appRoot, "Contents", "Info.plist");
  const [bundleId, urlScheme] = await Promise.all([
    plutilValue(infoPlist, "CFBundleIdentifier"),
    plutilValue(infoPlist, "CFBundleURLTypes.0.CFBundleURLSchemes.0"),
  ]);
  if (bundleId !== BUNDLE_ID || urlScheme !== URL_SCHEME) {
    fail("The application identity is not WorkBuddy China.");
  }
  validateAccount(configRoot);
  const installerPath = realpath(__filename, "Reviewed Quandora installer");
  const oauthHelper = resolveBootstrapOAuthHelper(
    path.join(path.dirname(installerPath), "workbuddy-cn-oauth-macos.js"),
    installerPath,
  );

  const electron = realpath(
    path.join(appRoot, "Contents", "MacOS", "Electron"),
    "WorkBuddy bundled runtime",
  );
  if (realpath(process.execPath, "Active runtime") !== electron) {
    fail("The installer is not running with the selected WorkBuddy application runtime.");
  }

  const cli = realpath(
    path.join(appRoot, "Contents", "Resources", "app.asar.unpacked", "cli", "bin", "codebuddy"),
    "WorkBuddy bundled CLI",
  );
  const cliEnv = createCliEnv(configRoot);
  await requireCliSuccess(
    cli,
    pluginArgs("marketplace", "list"),
    {
      label: "WorkBuddy marketplace health check",
      timeoutMs: CLI_HEALTH_TIMEOUT_MS,
      env: cliEnv,
      exitFailureCode: "cli_unhealthy",
    },
  );
  emit({ status: "progress", step: "host_verified" });

  const knownMarketplacesPath = path.join(configRoot, "plugins", "known_marketplaces.json");
  let knownMarketplaces = readJson(knownMarketplacesPath, "WorkBuddy marketplace registry");
  const existingMarketplace = knownMarketplaces[MARKETPLACE_NAME];
  if (existingMarketplace) {
    validateMarketplace(existingMarketplace, configRoot);
    await requireCliSuccess(cli, pluginArgs("marketplace", "update", MARKETPLACE_NAME), {
      label: "Quandora marketplace refresh",
      timeoutMs: remainingTimeout(startedAt, CLI_TIMEOUT_MS, "Quandora marketplace refresh"),
      env: cliEnv,
    });
  } else {
    await requireCliSuccess(
      cli,
      pluginArgs("marketplace", "add", MARKETPLACE_REPOSITORY, "--name", MARKETPLACE_NAME),
      {
        label: "Quandora marketplace installation",
        timeoutMs: remainingTimeout(startedAt, CLI_TIMEOUT_MS, "Quandora marketplace installation"),
        env: cliEnv,
      },
    );
  }
  knownMarketplaces = readJson(knownMarketplacesPath, "WorkBuddy marketplace registry");
  const marketplaceVersion = validateMarketplace(
    knownMarketplaces[MARKETPLACE_NAME],
    configRoot,
  );
  emit({ status: "progress", step: "marketplace_ready" });

  const listPlugins = async () => parsePluginList(
    await requireCliSuccess(cli, pluginArgs("list", "--json"), {
      label: "WorkBuddy plugin inventory",
      timeoutMs: remainingTimeout(startedAt, CLI_TIMEOUT_MS, "WorkBuddy plugin inventory"),
      env: cliEnv,
    }),
  );
  let plugin = selectUserPlugin(await listPlugins());
  if (!plugin) {
    await requireCliSuccess(cli, pluginArgs("install", PLUGIN_ID, "--scope", "user"), {
      label: "Quandora plugin installation",
      timeoutMs: remainingTimeout(startedAt, CLI_TIMEOUT_MS, "Quandora plugin installation"),
      env: cliEnv,
    });
  } else if (!hasRequiredPackageFiles(plugin, configRoot)) {
    await requireCliSuccess(cli, pluginArgs("update", PLUGIN_ID, "--scope", "user"), {
      label: "Quandora plugin update",
      timeoutMs: remainingTimeout(startedAt, CLI_TIMEOUT_MS, "Quandora plugin update"),
      env: cliEnv,
    });
  }

  plugin = selectUserPlugin(await listPlugins());
  if (!plugin) fail("Quandora was not installed for the WorkBuddy user.");
  if (!hasRequiredPackageFiles(plugin, configRoot)) {
    fail("The installed preview package cannot be replaced safely while WorkBuddy is using it.");
  }
  if (plugin.enabled !== true) {
    await requireCliSuccess(cli, pluginArgs("enable", PLUGIN_ID, "--scope", "user"), {
      label: "Quandora plugin enablement",
      timeoutMs: remainingTimeout(startedAt, CLI_TIMEOUT_MS, "Quandora plugin enablement"),
      env: cliEnv,
    });
    plugin = selectUserPlugin(await listPlugins());
  }

  const pluginRoot = validateInstalledPlugin(plugin, configRoot, marketplaceVersion);
  emit({ status: "progress", step: "plugin_ready" });

  const oauth = await runProcess(
    electron,
    [
      oauthHelper,
      pluginRoot,
      configRoot,
      appRoot,
    ],
    {
      label: "Quandora authorization",
      timeoutMs: remainingTimeout(startedAt, OAUTH_TIMEOUT_MS, "Quandora authorization"),
      env: { ...cliEnv, ELECTRON_RUN_AS_NODE: "1" },
      onStderrLine: relayOAuthProgress,
    },
  );
  if (oauth.code !== 0) {
    if (oauthFailureRequiresHostUpdate(oauth.stderr)) {
      fail(
        "This WorkBuddy build does not expose the required native OAuth runtime.",
        "host_update_required",
        "Update WorkBuddy from Personal Center, restart it, and retry in a new local Agent task.",
      );
    }
    fail("Quandora authorization failed.");
  }
  const result = parseOAuthResult(oauth.stdout);
  emit({
    status: "completed",
    installed: true,
    enabled: true,
    authenticated: true,
    plugin: PLUGIN_ID,
    scope: "user",
    version: plugin.version,
    protectedProbe: result.protectedProbe,
    toolCount: result.toolCount,
    browserAuthorizationOpened: result.browserAuthorizationOpened === true,
  });
}

main().catch((error) => {
  const failure = error instanceof SafeError
    ? error
    : new SafeError("The WorkBuddy China installation failed safely.");
  process.stderr.write(
    `${JSON.stringify({
      status: "failed",
      code: failure.code,
      message: failure.message,
      remediation: failure.remediation,
    })}\n`,
  );
  process.exitCode = 69;
}).finally(cleanupTemporaryBootstrap);
