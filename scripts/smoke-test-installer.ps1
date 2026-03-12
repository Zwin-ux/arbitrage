[CmdletBinding()]
param(
    [string]$InstallerPath = (Join-Path (Split-Path -Parent $PSScriptRoot) "dist\market-data-recorder-setup.exe"),
    [string]$InstallDir = (Join-Path $env:TEMP "SuperiorSmokeInstall"),
    [switch]$KeepInstallDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$installer = (Resolve-Path $InstallerPath).Path
$installRoot = [System.IO.Path]::GetFullPath($InstallDir)
$installLog = Join-Path $env:TEMP "superior-installer-smoke.log"

if (Test-Path $installRoot) {
    Remove-Item $installRoot -Recurse -Force
}

Write-Host "Installing $installer to $installRoot"
& $installer /VERYSILENT /SUPPRESSMSGBOXES /NORESTART "/DIR=$installRoot" "/LOG=$installLog"

$appExe = Join-Path $installRoot "market-data-recorder-app.exe"
if (-not (Test-Path $appExe)) {
    throw "Installer smoke test failed. Installed app executable was not found at $appExe"
}

python "$repoRoot\scripts\smoke-test-windows-release.py" --bundle-exe $appExe

$uninstaller = Join-Path $installRoot "unins000.exe"
if (Test-Path $uninstaller) {
    Write-Host "Running silent uninstall"
    & $uninstaller /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
}

if ((-not $KeepInstallDir) -and (Test-Path $installRoot)) {
    Remove-Item $installRoot -Recurse -Force
}

Write-Host "Installer smoke test passed. Log: $installLog"
