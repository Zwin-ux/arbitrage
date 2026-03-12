[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    $isccPath = & "$repoRoot\scripts\bootstrap-iscc.ps1"
    Write-Host "Using ISCC at $isccPath"

    python -m pytest -q
    python -m mypy src tests

    if (Test-Path "$repoRoot\dist") {
        Remove-Item "$repoRoot\dist" -Recurse -Force
    }

    if (Test-Path "$repoRoot\.tmp\build-release") {
        Remove-Item "$repoRoot\.tmp\build-release" -Recurse -Force
    }

    python -m PyInstaller --noconfirm --distpath dist --workpath .tmp\build-release packaging\windows\market_data_recorder_app.spec

    $portableZip = "$repoRoot\dist\market-data-recorder-app-portable.zip"
    if (Test-Path $portableZip) {
        Remove-Item $portableZip -Force
    }
    Compress-Archive -Path "$repoRoot\dist\market-data-recorder-app" -DestinationPath $portableZip -Force

    & $isccPath "$repoRoot\packaging\windows\installer.iss"

    $installerBuilt = "$repoRoot\dist\installer\market-data-recorder-setup.exe"
    $installerFinal = "$repoRoot\dist\market-data-recorder-setup.exe"
    Copy-Item $installerBuilt $installerFinal -Force

    Write-Host "Release assets ready:"
    Write-Host "  Bundle folder: $repoRoot\dist\market-data-recorder-app"
    Write-Host "  Portable zip:  $portableZip"
    Write-Host "  Installer:     $installerFinal"
}
finally {
    Pop-Location
}
