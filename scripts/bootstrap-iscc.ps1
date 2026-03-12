[CmdletBinding()]
param(
    [string]$Version = "6.7.1"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-IsccPath {
    $command = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @(
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

$existing = Get-IsccPath
if ($existing) {
    Write-Output $existing
    exit 0
}

$downloadUrl = "https://github.com/jrsoftware/issrc/releases/download/is-$($Version -replace '\.', '_')/innosetup-$Version.exe"
$installerPath = Join-Path $env:TEMP "innosetup-$Version.exe"

Write-Host "Downloading Inno Setup $Version from official release URL..."
curl.exe -L $downloadUrl -o $installerPath | Out-Null

Write-Host "Installing Inno Setup silently..."
& $installerPath /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-

$installed = Get-IsccPath
if (-not $installed) {
    throw "ISCC.exe was not found after installation."
}

Write-Output $installed
