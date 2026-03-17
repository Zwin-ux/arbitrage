[CmdletBinding()]
param(
    [switch]$IncludeSite,
    [switch]$IncludePackaging,
    [string]$QAWorkspace = "",
    [string]$QAOutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

$logPath = "$repoRoot\.tmp\validate-superior.log"
$summaryPath = "$repoRoot\.tmp\validate-superior-summary.json"
New-Item -ItemType Directory -Path (Split-Path -Parent $logPath) -Force | Out-Null
if (Test-Path $logPath) {
    Remove-Item $logPath -Force
}

function Write-ValidationLog {
    param([Parameter(Mandatory = $true)][string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    Add-Content -Path $logPath -Value "$timestamp $Message"
}

function Write-ValidationStage {
    param([Parameter(Mandatory = $true)][string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
    Write-ValidationLog "STAGE $Message"
}

function Invoke-ValidationStep {
    param(
        [Parameter(Mandatory = $true)][string]$StageName,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )

    Write-ValidationStage $StageName
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$StageName failed with exit code $LASTEXITCODE"
    }
}

try {
    if ([string]::IsNullOrWhiteSpace($QAWorkspace)) {
        $QAWorkspace = "$repoRoot\.tmp\qa-release"
    }
    if ([string]::IsNullOrWhiteSpace($QAOutputPath)) {
        $QAOutputPath = "$QAWorkspace\report.json"
    }

    Invoke-ValidationStep -StageName "Run pytest" -Command {
        python -m pytest -q
    }

    Invoke-ValidationStep -StageName "Run mypy" -Command {
        python -m mypy src tests
    }

    Invoke-ValidationStep -StageName "Run QA client" -Command {
        python -m market_data_recorder_desktop.qa_client --headless --workspace $QAWorkspace --output $QAOutputPath
    }

    if ($IncludeSite) {
        Invoke-ValidationStep -StageName "Build site" -Command {
            npm.cmd --prefix site run build
        }
        Invoke-ValidationStep -StageName "Run browser smoke tests" -Command {
            npm.cmd --prefix site run test:browser
        }
    }

    if ($IncludePackaging) {
        Invoke-ValidationStep -StageName "Build Windows release" -Command {
            powershell -ExecutionPolicy Bypass -File "$repoRoot\scripts\build-windows-release.ps1"
        }
    }

    $summary = @{
        generated_at = (Get-Date).ToString("o")
        qa_workspace = (Resolve-Path $QAWorkspace).Path
        qa_report = (Resolve-Path $QAOutputPath).Path
        include_site = [bool]$IncludeSite
        include_packaging = [bool]$IncludePackaging
        log_path = $logPath
    }
    Set-Content -Path $summaryPath -Value ($summary | ConvertTo-Json -Depth 4) -Encoding utf8
    Write-ValidationStage "Validation complete"
    Write-Host "Summary: $summaryPath"
    Write-Host "Log:     $logPath"
    Write-Host "QA:      $QAOutputPath"
}
finally {
    Pop-Location
}

exit 0
