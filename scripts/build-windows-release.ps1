[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

function Copy-ReleaseAsset {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourcePath,
        [Parameter(Mandatory = $true)]
        [string]$DestinationPath
    )

    try {
        $destinationDir = Split-Path -Parent $DestinationPath
        if (-not (Test-Path $destinationDir)) {
            New-Item -ItemType Directory -Path $destinationDir | Out-Null
        }
        Copy-Item $SourcePath $DestinationPath -Force
    }
    catch {
        Write-Warning "Unable to copy $SourcePath to $DestinationPath. Stage artifact remains available."
    }
}

try {
    $isccPath = & "$repoRoot\scripts\bootstrap-iscc.ps1"
    Write-Host "Using ISCC at $isccPath"

    cmd.exe /c "taskkill /F /IM market-data-recorder-app.exe /T >nul 2>nul"
    Get-Process market-data-recorder-app -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Milliseconds 500

    python -m pytest -q
    python -m mypy src tests

    $stageRoot = "$repoRoot\.tmp\release-stage"
    $stageDist = "$stageRoot\dist"
    $stageWork = "$stageRoot\build-work"
    $stageInstallerDir = "$stageRoot\installer"
    $finalDist = "$repoRoot\dist"
    if (Test-Path "$repoRoot\.tmp\build-release") {
        Remove-Item "$repoRoot\.tmp\build-release" -Recurse -Force
    }
    if (Test-Path $stageRoot) {
        Remove-Item $stageRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Path $stageRoot | Out-Null

    python -m PyInstaller --noconfirm --distpath $stageDist --workpath $stageWork packaging\windows\market_data_recorder_app.spec

    $bundleDir = "$stageDist\market-data-recorder-app"
    $portableZip = "$stageRoot\market-data-recorder-app-portable.zip"
    if (Test-Path $portableZip) {
        Remove-Item $portableZip -Force
    }
    Compress-Archive -Path $bundleDir -DestinationPath $portableZip -Force

    python "$repoRoot\scripts\smoke-test-windows-release.py" --bundle-exe "$bundleDir\market-data-recorder-app.exe"

    & $isccPath "/DSourceBundleDir=$bundleDir" "/DOutputDirPath=$stageInstallerDir" "$repoRoot\packaging\windows\installer.iss"

    $installerBuilt = "$stageInstallerDir\market-data-recorder-setup.exe"
    $installerFinal = "$finalDist\market-data-recorder-setup.exe"

    & "$repoRoot\scripts\smoke-test-installer.ps1" -InstallerPath $installerBuilt

    Copy-ReleaseAsset -SourcePath $portableZip -DestinationPath "$finalDist\market-data-recorder-app-portable.zip"
    Copy-ReleaseAsset -SourcePath $installerBuilt -DestinationPath $installerFinal

    Write-Host "Release assets ready:"
    Write-Host "  Bundle folder: $bundleDir"
    Write-Host "  Portable zip:  $portableZip"
    Write-Host "  Installer:     $installerBuilt"
}
finally {
    Pop-Location
}
