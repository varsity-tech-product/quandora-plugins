[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$CodeBuddyBin,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ConfigDirectory,

    [string]$StateDirectory,

    [switch]$Worker
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$mcpName = 'quandora'
$pluginSelector = 'quandora@quandora'
$oauthPort = 64361
$expectedAuthorizationPrefix = 'https://mcp.quandora.ai/oauth/authorize?'
$expectedRedirect = 'redirect_uri=http%3A%2F%2F127.0.0.1%3A64361%2Fmcp%2Foauth%2Fcallback'
$utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)

if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    throw 'This helper supports Windows only.'
}

$resolvedCodeBuddy = (Resolve-Path -LiteralPath $CodeBuddyBin -ErrorAction Stop).ProviderPath
if (-not (Test-Path -LiteralPath $resolvedCodeBuddy -PathType Leaf)) {
    throw 'The resolved WorkBuddy CLI does not exist.'
}
if ([IO.Path]::GetExtension($resolvedCodeBuddy).ToLowerInvariant() -ne '.exe') {
    throw 'The resolved WorkBuddy CLI must be the official native codebuddy.exe.'
}

$resolvedConfig = (Resolve-Path -LiteralPath $ConfigDirectory -ErrorAction Stop).ProviderPath
if (-not (Test-Path -LiteralPath $resolvedConfig -PathType Container)) {
    throw 'The WorkBuddy configuration directory is invalid.'
}

$systemPowerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
if (-not (Test-Path -LiteralPath $systemPowerShell -PathType Leaf)) {
    throw 'Windows PowerShell 5.1 is unavailable.'
}

if (-not $Worker) {
    $newStateDirectory = Join-Path ([IO.Path]::GetTempPath()) ("quandora-workbuddy-oauth-{0}" -f [Guid]::NewGuid().ToString('N'))
    $null = New-Item -ItemType Directory -Path $newStateDirectory -ErrorAction Stop
    $childScript = @'
$ErrorActionPreference = 'Stop'
& $env:QUANDORA_WORKBUDDY_HELPER -CodeBuddyBin $env:QUANDORA_WORKBUDDY_CLI -ConfigDirectory $env:QUANDORA_WORKBUDDY_CONFIG -StateDirectory $env:QUANDORA_WORKBUDDY_STATE -Worker
exit $LASTEXITCODE
'@
    $encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($childScript))
    $previousValues = @{
        Helper = [Environment]::GetEnvironmentVariable('QUANDORA_WORKBUDDY_HELPER', 'Process')
        Cli = [Environment]::GetEnvironmentVariable('QUANDORA_WORKBUDDY_CLI', 'Process')
        Config = [Environment]::GetEnvironmentVariable('QUANDORA_WORKBUDDY_CONFIG', 'Process')
        State = [Environment]::GetEnvironmentVariable('QUANDORA_WORKBUDDY_STATE', 'Process')
    }
    try {
        [Environment]::SetEnvironmentVariable('QUANDORA_WORKBUDDY_HELPER', $PSCommandPath, 'Process')
        [Environment]::SetEnvironmentVariable('QUANDORA_WORKBUDDY_CLI', $resolvedCodeBuddy, 'Process')
        [Environment]::SetEnvironmentVariable('QUANDORA_WORKBUDDY_CONFIG', $resolvedConfig, 'Process')
        [Environment]::SetEnvironmentVariable('QUANDORA_WORKBUDDY_STATE', $newStateDirectory, 'Process')
        $childProcess = Start-Process -FilePath $systemPowerShell -ArgumentList @('-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-EncodedCommand', $encodedCommand) -WindowStyle Hidden -PassThru
    }
    finally {
        [Environment]::SetEnvironmentVariable('QUANDORA_WORKBUDDY_HELPER', $previousValues.Helper, 'Process')
        [Environment]::SetEnvironmentVariable('QUANDORA_WORKBUDDY_CLI', $previousValues.Cli, 'Process')
        [Environment]::SetEnvironmentVariable('QUANDORA_WORKBUDDY_CONFIG', $previousValues.Config, 'Process')
        [Environment]::SetEnvironmentVariable('QUANDORA_WORKBUDDY_STATE', $previousValues.State, 'Process')
    }

    [ordered]@{
        processId = $childProcess.Id
        stateDirectory = $newStateDirectory
        statusFile = Join-Path $newStateDirectory 'status.json'
    } | ConvertTo-Json -Compress
    exit 0
}

if ([string]::IsNullOrWhiteSpace($StateDirectory)) {
    throw 'The state directory is required for the worker process.'
}
$stateDirectory = (Resolve-Path -LiteralPath $StateDirectory -ErrorAction Stop).ProviderPath
if (-not (Test-Path -LiteralPath $stateDirectory -PathType Container)) {
    throw 'The state directory is invalid.'
}
$statusFile = Join-Path $stateDirectory 'status.json'
$hostLog = Join-Path $stateDirectory 'host.log'
$hostErrorLog = Join-Path $stateDirectory 'host-error.log'
$hostProcess = $null

function Write-State {
    param(
        [Parameter(Mandatory = $true)][string]$Status,
        [AllowNull()][object]$ToolsCount,
        [AllowNull()][object]$NeedsAuth,
        [AllowNull()][object]$ExitCode
    )

    $temporaryFile = Join-Path $stateDirectory (".status-{0}.json" -f [Guid]::NewGuid().ToString('N'))
    $payload = [ordered]@{
        status = $Status
        processId = $PID
        hostProcessId = if ($null -eq $hostProcess) { $null } else { $hostProcess.Id }
        port = $oauthPort
        toolsCount = $ToolsCount
        needsAuth = $NeedsAuth
        exitCode = $ExitCode
    }
    [IO.File]::WriteAllText($temporaryFile, ($payload | ConvertTo-Json -Compress), $utf8WithoutBom)
    Move-Item -LiteralPath $temporaryFile -Destination $statusFile -Force
}

function Invoke-NativeMcp {
    param([Parameter(Mandatory = $true)][string]$Path)

    $headers = @{ 'x-codebuddy-request' = '1' }
    $body = @{ name = $mcpName } | ConvertTo-Json -Compress
    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:$oauthPort$Path" -Headers $headers -ContentType 'application/json' -Body $body -TimeoutSec 10
}

function Get-McpState {
    $status = Invoke-NativeMcp -Path '/internal/mcp/status'
    $tools = @(Invoke-NativeMcp -Path '/internal/mcp/listTools')
    [ordered]@{
        name = [string]$status.name
        status = [string]$status.status
        needsAuth = [bool]$status.needsAuth
        toolsCount = $tools.Count
    }
}

try {
    $listener = Get-NetTCPConnection -LocalPort $oauthPort -State Listen -ErrorAction SilentlyContinue
    if ($null -ne $listener) {
        Write-State -Status 'port_conflict' -ToolsCount 0 -NeedsAuth $null -ExitCode 75
        exit 75
    }

    Write-State -Status 'starting' -ToolsCount 0 -NeedsAuth $null -ExitCode $null
    $previousConfigDirectory = [Environment]::GetEnvironmentVariable('CODEBUDDY_CONFIG_DIR', 'Process')
    try {
        [Environment]::SetEnvironmentVariable('CODEBUDDY_CONFIG_DIR', $resolvedConfig, 'Process')
        $hostArguments = @(
            '--serve',
            '--no-session-persistence',
            '--setting-sources', 'user',
            '--channels', "plugin:$pluginSelector",
            '--port', [string]$oauthPort
        )
        $hostProcess = Start-Process -FilePath $resolvedCodeBuddy -ArgumentList $hostArguments -RedirectStandardOutput $hostLog -RedirectStandardError $hostErrorLog -WindowStyle Hidden -PassThru
    }
    finally {
        [Environment]::SetEnvironmentVariable('CODEBUDDY_CONFIG_DIR', $previousConfigDirectory, 'Process')
    }
    Write-State -Status 'starting' -ToolsCount 0 -NeedsAuth $null -ExitCode $null

    $ready = $false
    $alreadyAuthorized = $false
    $state = $null
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            $state = Get-McpState
            if ($state.name -eq $mcpName -and $state.status -eq 'connected' -and -not $state.needsAuth) {
                $ready = $true
                $alreadyAuthorized = $true
                break
            }
            if ($state.name -eq $mcpName -and $state.status -ne 'disconnected' -and $state.needsAuth) {
                $ready = $true
                break
            }
        }
        catch {
        }
        if ($hostProcess.HasExited) {
            Write-State -Status 'host_failed' -ToolsCount 0 -NeedsAuth $null -ExitCode 70
            exit 70
        }
        Start-Sleep -Seconds 1
    }

    if (-not $ready) {
        Write-State -Status 'incompatible' -ToolsCount 0 -NeedsAuth $null -ExitCode 69
        exit 69
    }
    if ($alreadyAuthorized) {
        Write-State -Status 'completed' -ToolsCount $state.toolsCount -NeedsAuth $false -ExitCode 0
        exit 0
    }

    Write-State -Status 'authorizing' -ToolsCount $state.toolsCount -NeedsAuth $true -ExitCode $null
    $authorization = Invoke-NativeMcp -Path '/internal/mcp/oauth/authorize'
    $authorizationError = ''
    if ($authorization.PSObject.Properties.Name -contains 'error') {
        $authorizationError = [string]$authorization.error
    }
    if ($authorizationError -eq 'No authorization URL available. Server may not require OAuth or connection attempt has not been made yet.') {
        try {
            $state = Get-McpState
            if ($state.name -eq $mcpName -and $state.status -eq 'connected' -and -not $state.needsAuth) {
                Write-State -Status 'native_ready' -ToolsCount $state.toolsCount -NeedsAuth $false -ExitCode 0
                exit 0
            }
        }
        catch {
        }
    }

    $authorizationUrl = ''
    if ($authorization.PSObject.Properties.Name -contains 'authorizationUrl') {
        $authorizationUrl = [string]$authorization.authorizationUrl
    }
    if ([string]::IsNullOrWhiteSpace($authorizationUrl) -or -not $authorizationUrl.StartsWith($expectedAuthorizationPrefix, [StringComparison]::Ordinal) -or -not $authorizationUrl.Contains($expectedRedirect)) {
        Write-State -Status 'oauth_response_invalid' -ToolsCount $state.toolsCount -NeedsAuth $true -ExitCode 65
        exit 65
    }

    try {
        Start-Process -FilePath $authorizationUrl -ErrorAction Stop
    }
    catch {
        Write-State -Status 'browser_open_failed' -ToolsCount $state.toolsCount -NeedsAuth $true -ExitCode 69
        exit 69
    }
    $authorizationUrl = $null
    $authorization = $null

    for ($attempt = 0; $attempt -lt 300; $attempt++) {
        try {
            $state = Get-McpState
            if ($state.name -eq $mcpName -and $state.status -eq 'connected' -and -not $state.needsAuth) {
                Write-State -Status 'completed' -ToolsCount $state.toolsCount -NeedsAuth $false -ExitCode 0
                exit 0
            }
        }
        catch {
        }
        if ($hostProcess.HasExited) {
            Write-State -Status 'host_failed' -ToolsCount 0 -NeedsAuth $null -ExitCode 70
            exit 70
        }
        Start-Sleep -Seconds 1
    }

    Write-State -Status 'timed_out' -ToolsCount $state.toolsCount -NeedsAuth $state.needsAuth -ExitCode 124
    exit 124
}
catch {
    Write-State -Status 'helper_failed' -ToolsCount 0 -NeedsAuth $null -ExitCode 1
    exit 1
}
finally {
    if ($null -ne $hostProcess -and -not $hostProcess.HasExited) {
        Stop-Process -Id $hostProcess.Id -ErrorAction SilentlyContinue
        $null = $hostProcess.WaitForExit(5000)
    }
}
