[CmdletBinding()]
param(
    [string]$InstallerPath = "",
    [string]$InstallDir = "",
    [switch]$KeepInstallDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$defaultInstallerPath = Join-Path $repoRoot "dist\market-data-recorder-setup.exe"
if ([string]::IsNullOrWhiteSpace($InstallerPath)) {
    $InstallerPath = $defaultInstallerPath
}
if ([string]::IsNullOrWhiteSpace($InstallDir)) {
    $InstallDir = Join-Path $env:TEMP "SuperiorSmokeInstall"
}
$installer = (Resolve-Path $InstallerPath).Path
$installRoot = [System.IO.Path]::GetFullPath($InstallDir)
$installLog = Join-Path $env:TEMP "superior-installer-smoke.log"

function Invoke-ExecutableAndWait {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,
        [Parameter(Mandatory = $true)]
        [string]$StageName
    )

    Write-Host $StageName
    $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -PassThru -Wait -WindowStyle Hidden
    if ($null -eq $process) {
        throw "$StageName failed to start."
    }
    if ($process.ExitCode -ne 0) {
        throw "$StageName failed with exit code $($process.ExitCode)"
    }
}

function Wait-ForPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        if (Test-Path $Path) {
            return $true
        }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)

    return (Test-Path $Path)
}

function Get-InstalledExecutablePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallRoot,
        [Parameter(Mandatory = $true)]
        [string]$InstallLog
    )

    $candidates = @(
        (Join-Path $InstallRoot "market-data-recorder-app.exe"),
        (Join-Path $InstallRoot "market-data-recorder-app\market-data-recorder-app.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Superior\market-data-recorder-app.exe")
    )

    if (Test-Path $InstallLog) {
        $logMatch = Select-String -Path $InstallLog -Pattern 'Dest filename:\s+(.*market-data-recorder-app\.exe)$' | Select-Object -Last 1
        if ($null -ne $logMatch) {
            $logPath = $logMatch.Matches[0].Groups[1].Value.Trim()
            if (-not [string]::IsNullOrWhiteSpace($logPath)) {
                $candidates = @($logPath) + $candidates
            }
        }
    }

    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if ([string]::IsNullOrWhiteSpace($candidate)) {
            continue
        }
        if (Wait-ForPath -Path $candidate -TimeoutSeconds 20) {
            return $candidate
        }
    }

    return $null
}

function Get-InstalledSmokeExecutablePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallRoot
    )

    $candidates = @(
        (Join-Path $InstallRoot "market-data-recorder-smoke\market-data-recorder-smoke.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Superior\market-data-recorder-smoke\market-data-recorder-smoke.exe")
    )

    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if ([string]::IsNullOrWhiteSpace($candidate)) {
            continue
        }
        if (Wait-ForPath -Path $candidate -TimeoutSeconds 20) {
            return $candidate
        }
    }

    return $null
}

if (Test-Path $installRoot) {
    Remove-Item $installRoot -Recurse -Force
}
if (Test-Path $installLog) {
    Remove-Item $installLog -Force -ErrorAction SilentlyContinue
}

Write-Host "Installing $installer to $installRoot"
Invoke-ExecutableAndWait -FilePath $installer -ArgumentList @(
    "/VERYSILENT",
    "/SUPPRESSMSGBOXES",
    "/NORESTART",
    "/DIR=$installRoot",
    "/LOG=$installLog"
) -StageName "Installer smoke install"

$appExe = Get-InstalledExecutablePath -InstallRoot $installRoot -InstallLog $installLog
if ($null -eq $appExe) {
    throw "Installer smoke test failed. Installed app executable was not found. Checked install root $installRoot and install log $installLog."
}

$smokeExe = Get-InstalledSmokeExecutablePath -InstallRoot $installRoot
if ($null -eq $smokeExe) {
    throw "Installer smoke test failed. Installed smoke executable was not found under $installRoot."
}

python "$repoRoot\scripts\smoke-test-windows-release.py" --bundle-exe $smokeExe
if ($LASTEXITCODE -ne 0) {
    throw "Installer smoke test failed while launching the installed app. Exit code: $LASTEXITCODE"
}

$uninstaller = Join-Path (Split-Path -Parent $appExe) "unins000.exe"
if (Test-Path $uninstaller) {
    Write-Host "Running silent uninstall"
    try {
        Invoke-ExecutableAndWait -FilePath $uninstaller -ArgumentList @(
            "/VERYSILENT",
            "/SUPPRESSMSGBOXES",
            "/NORESTART"
        ) -StageName "Installer smoke uninstall"
    }
    catch {
        Write-Warning "Silent uninstall failed. Leaving install directory for inspection. $($_.Exception.Message)"
    }
}

if ((-not $KeepInstallDir) -and (Test-Path $installRoot)) {
    Remove-Item $installRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Installer smoke test passed. Log: $installLog"
$global:LASTEXITCODE = 0
exit 0
