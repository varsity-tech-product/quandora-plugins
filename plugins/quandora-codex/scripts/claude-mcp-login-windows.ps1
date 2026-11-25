[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ClaudeBin
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$mcpIdentity = 'plugin:quandora:quandora'
$isWindows = [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT
if (-not $isWindows) {
    throw 'This helper supports Windows only.'
}

$systemPowerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
if (-not (Test-Path -LiteralPath $systemPowerShell -PathType Leaf)) {
    throw 'Windows PowerShell 5.1 is unavailable.'
}

$resolvedClaude = (Resolve-Path -LiteralPath $ClaudeBin -ErrorAction Stop).ProviderPath
if (-not (Test-Path -LiteralPath $resolvedClaude -PathType Leaf)) {
    throw 'The resolved Claude Code executable does not exist.'
}

$extension = [IO.Path]::GetExtension($resolvedClaude).ToLowerInvariant()
if ($extension -notin @('.exe', '.cmd')) {
    throw 'The resolved Claude Code path must be a real .exe or .cmd client.'
}

if ($resolvedClaude -match '\\Microsoft\\WindowsApps\\') {
    throw 'The WindowsApps Claude alias is not an acceptable Claude Code client.'
}

$stateDirectory = Join-Path ([IO.Path]::GetTempPath()) ("quandora-oauth-{0}" -f [Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $stateDirectory -ErrorAction Stop
$statusFile = Join-Path $stateDirectory 'status.json'

function Write-StateFile {
    param([Parameter(Mandatory = $true)][System.Collections.IDictionary]$Payload)

    $temporaryFile = Join-Path $stateDirectory (".status-{0}.json" -f [Guid]::NewGuid().ToString('N'))
    $json = $Payload | ConvertTo-Json -Compress
    [IO.File]::WriteAllText($temporaryFile, $json, [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporaryFile -Destination $statusFile -Force
}

Write-StateFile -Payload ([ordered]@{
    status = 'launching'
    processId = $null
    inputRedirected = $null
    outputRedirected = $null
    errorRedirected = $null
    exitCode = $null
    completedAt = $null
})

$null = & $resolvedClaude mcp help login 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-StateFile -Payload ([ordered]@{
        status = 'incompatible_cli'
        processId = $PID
        inputRedirected = [Console]::IsInputRedirected
        outputRedirected = [Console]::IsOutputRedirected
        errorRedirected = [Console]::IsErrorRedirected
        exitCode = 69
        completedAt = [DateTime]::UtcNow.ToString('o')
    })
    [ordered]@{
        processId = $PID
        stateDirectory = $stateDirectory
        statusFile = $statusFile
        mcpIdentity = $mcpIdentity
    } | ConvertTo-Json -Compress
    exit 69
}

$childScript = @'
$ErrorActionPreference = 'Stop'
$mcpIdentity = 'plugin:quandora:quandora'
$claudePath = $env:QUANDORA_CLAUDE_PATH
$statusPath = $env:QUANDORA_OAUTH_STATUS_PATH

function Write-ChildState {
    param(
        [Parameter(Mandatory = $true)][string]$Status,
        [AllowNull()][object]$ExitCode,
        [AllowNull()][object]$CompletedAt
    )

    $payload = [ordered]@{
        status = $Status
        processId = $PID
        inputRedirected = [Console]::IsInputRedirected
        outputRedirected = [Console]::IsOutputRedirected
        errorRedirected = [Console]::IsErrorRedirected
        exitCode = $ExitCode
        completedAt = $CompletedAt
    }
    $temporaryPath = "$statusPath.$PID.tmp"
    $json = $payload | ConvertTo-Json -Compress
    [IO.File]::WriteAllText($temporaryPath, $json, [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporaryPath -Destination $statusPath -Force
}

try {
    if ([Console]::IsInputRedirected -or [Console]::IsOutputRedirected -or [Console]::IsErrorRedirected) {
        Write-ChildState -Status 'no_interactive_console' -ExitCode 70 -CompletedAt ([DateTime]::UtcNow.ToString('o'))
        exit 70
    }

    Write-ChildState -Status 'running' -ExitCode $null -CompletedAt $null
    & $claudePath mcp login $mcpIdentity
    $loginExitCode = $LASTEXITCODE
    $completionStatus = if ($loginExitCode -eq 0) { 'completed' } else { 'failed' }
    Write-ChildState -Status $completionStatus -ExitCode $loginExitCode -CompletedAt ([DateTime]::UtcNow.ToString('o'))
    exit $loginExitCode
}
catch {
    Write-ChildState -Status 'failed' -ExitCode 1 -CompletedAt ([DateTime]::UtcNow.ToString('o'))
    exit 1
}
'@

$encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($childScript))
$previousClaudePath = [Environment]::GetEnvironmentVariable('QUANDORA_CLAUDE_PATH', 'Process')
$previousStatusPath = [Environment]::GetEnvironmentVariable('QUANDORA_OAUTH_STATUS_PATH', 'Process')

try {
    [Environment]::SetEnvironmentVariable('QUANDORA_CLAUDE_PATH', $resolvedClaude, 'Process')
    [Environment]::SetEnvironmentVariable('QUANDORA_OAUTH_STATUS_PATH', $statusFile, 'Process')

    $process = Start-Process `
        -FilePath $systemPowerShell `
        -ArgumentList @('-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-EncodedCommand', $encodedCommand) `
        -WindowStyle Normal `
        -PassThru
}
finally {
    [Environment]::SetEnvironmentVariable('QUANDORA_CLAUDE_PATH', $previousClaudePath, 'Process')
    [Environment]::SetEnvironmentVariable('QUANDORA_OAUTH_STATUS_PATH', $previousStatusPath, 'Process')
}

[ordered]@{
    processId = $process.Id
    stateDirectory = $stateDirectory
    statusFile = $statusFile
    mcpIdentity = $mcpIdentity
} | ConvertTo-Json -Compress
