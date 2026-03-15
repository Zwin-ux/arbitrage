[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
$releaseLogPath = "$repoRoot\.tmp\build-windows-release.log"
New-Item -ItemType Directory -Path (Split-Path -Parent $releaseLogPath) -Force | Out-Null
if (Test-Path $releaseLogPath) {
    Remove-Item $releaseLogPath -Force
}

function Write-ReleaseLog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    Add-Content -Path $releaseLogPath -Value "$timestamp $Message"
}

function Write-ReleaseStage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host ""
    Write-Host "==> $Message"
    Write-ReleaseLog "STAGE $Message"
}

function Invoke-NativeStep {
    param(
        [Parameter(Mandatory = $true)]
        [string]$StageName,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-ReleaseStage $StageName
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$StageName failed with exit code $LASTEXITCODE"
    }
}

function Invoke-ExecutableAndWait {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,
        [Parameter(Mandatory = $true)]
        [string]$StageName
    )

    Write-ReleaseStage $StageName
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
        if (Test-Path $DestinationPath) {
            Remove-Item $DestinationPath -Force -ErrorAction SilentlyContinue
        }
        Copy-Item $SourcePath $DestinationPath -Force
    }
    catch {
        Write-Warning "Unable to copy $SourcePath to $DestinationPath. Stage artifact remains available."
    }
}

function Write-ReleaseChecksums {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$AssetPaths,
        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    $lines = @()
    foreach ($assetPath in $AssetPaths) {
        if (-not (Test-Path $assetPath)) {
            throw "Checksum generation failed because $assetPath does not exist."
        }
        $hash = Get-FileHash -Path $assetPath -Algorithm SHA256
        $lines += "{0} *{1}" -f $hash.Hash.ToLowerInvariant(), (Split-Path $assetPath -Leaf)
    }
    Set-Content -Path $OutputPath -Value $lines -Encoding ascii
}

function Test-InstallerSmoke {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallerPath
    )

    $installRoot = Join-Path $env:TEMP "SuperiorSmokeInstall"
    $installLog = Join-Path $env:TEMP "superior-installer-smoke.log"
    cmd.exe /c "rmdir /s /q ""$installRoot"" >nul 2>nul"
    if (Test-Path $installLog) {
        Remove-Item $installLog -Force -ErrorAction SilentlyContinue
    }

    Invoke-ExecutableAndWait -FilePath $InstallerPath -ArgumentList @(
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/DIR=$installRoot",
        "/LOG=$installLog"
    ) -StageName "Installer smoke install"

    $appExe = Get-InstalledExecutablePath -InstallRoot $installRoot -InstallLog $installLog
    if ($null -eq $appExe) {
        throw "Installer smoke failed. Installed executable was not found. Checked install root $installRoot and install log $installLog."
    }

    $smokeExe = Get-InstalledSmokeExecutablePath -InstallRoot $installRoot
    if ($null -eq $smokeExe) {
        throw "Installer smoke failed. Installed smoke executable was not found under $installRoot."
    }

    Invoke-NativeStep -StageName "Installed app smoke" -Command {
        python "$repoRoot\scripts\smoke-test-windows-release.py" --bundle-exe $smokeExe
    }

    $uninstaller = Join-Path (Split-Path -Parent $appExe) "unins000.exe"
    if (Test-Path $uninstaller) {
        Invoke-ExecutableAndWait -FilePath $uninstaller -ArgumentList @(
            "/VERYSILENT",
            "/SUPPRESSMSGBOXES",
            "/NORESTART"
        ) -StageName "Installer smoke uninstall"
    }
    cmd.exe /c "rmdir /s /q ""$installRoot"" >nul 2>nul"
}

try {
    Write-ReleaseStage "Locate ISCC"
    $isccPath = & "$repoRoot\scripts\bootstrap-iscc.ps1"
    Write-Host "Using ISCC at $isccPath"
    Write-ReleaseLog "Using ISCC at $isccPath"

    Write-ReleaseStage "Clean running app processes"
    cmd.exe /c "taskkill /F /IM market-data-recorder-app.exe /T >nul 2>nul"
    Get-Process market-data-recorder-app -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Milliseconds 500

    Invoke-NativeStep -StageName "Run pytest" -Command {
        python -m pytest -q
    }
    Invoke-NativeStep -StageName "Run mypy" -Command {
        python -m mypy src tests
    }

    $stageRoot = "$repoRoot\.tmp\release-stage"
    $stageDist = "$stageRoot\dist"
    $stageWork = "$stageRoot\build-work"
    $stageSmokeDist = "$stageRoot\smoke-dist"
    $stageSmokeWork = "$stageRoot\smoke-build-work"
    $stageInstallerDir = "$stageRoot\installer"
    $finalDist = "$repoRoot\dist"
    Write-ReleaseStage "Prepare release staging"
    if (Test-Path "$repoRoot\.tmp\build-release") {
        Remove-Item "$repoRoot\.tmp\build-release" -Recurse -Force
    }
    if (Test-Path $stageRoot) {
        Remove-Item $stageRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Path $stageRoot | Out-Null

    Invoke-NativeStep -StageName "Build PyInstaller bundle" -Command {
        python -m PyInstaller --noconfirm --distpath $stageDist --workpath $stageWork packaging\windows\market_data_recorder_app.spec
    }

    Invoke-NativeStep -StageName "Build packaged smoke companion" -Command {
        python -m PyInstaller --noconfirm --distpath $stageSmokeDist --workpath $stageSmokeWork packaging\windows\market_data_recorder_smoke.spec
    }

    $bundleDir = "$stageDist\market-data-recorder-app"
    $smokeBundleDir = "$stageSmokeDist\market-data-recorder-smoke"
    $smokeExe = "$smokeBundleDir\market-data-recorder-smoke.exe"
    $portableZip = "$stageRoot\market-data-recorder-app-portable.zip"
    Write-ReleaseStage "Build portable zip"
    if (Test-Path $portableZip) {
        Remove-Item $portableZip -Force
    }
    Compress-Archive -Path $bundleDir -DestinationPath $portableZip -Force

    Invoke-NativeStep -StageName "Smoke test staged bundle" -Command {
        python "$repoRoot\scripts\smoke-test-windows-release.py" --bundle-exe $smokeExe
    }

    Invoke-NativeStep -StageName "Compile installer" -Command {
        & $isccPath "/DSourceBundleDir=$bundleDir" "/DSourceSmokeDir=$smokeBundleDir" "/DOutputDirPath=$stageInstallerDir" "$repoRoot\packaging\windows\installer.iss"
    }

    $installerBuilt = "$stageInstallerDir\market-data-recorder-setup.exe"
    $installerFinal = "$finalDist\market-data-recorder-setup.exe"

    Write-ReleaseStage "Smoke test installer"
    Test-InstallerSmoke -InstallerPath $installerBuilt

    Write-ReleaseStage "Copy final release assets"
    Copy-ReleaseAsset -SourcePath $portableZip -DestinationPath "$finalDist\market-data-recorder-app-portable.zip"
    Copy-ReleaseAsset -SourcePath $installerBuilt -DestinationPath $installerFinal

    Write-ReleaseStage "Write SHA256 manifest"
    Write-ReleaseChecksums -AssetPaths @(
        "$finalDist\market-data-recorder-setup.exe",
        "$finalDist\market-data-recorder-app-portable.zip"
    ) -OutputPath "$finalDist\SHA256SUMS.txt"

    Write-ReleaseStage "Release assets ready"
    Write-Host "Release assets ready:"
    Write-Host "  Bundle folder: $bundleDir"
    Write-Host "  Portable zip:  $portableZip"
    Write-Host "  Installer:     $installerBuilt"
    Write-Host "  Checksums:     $finalDist\SHA256SUMS.txt"
    Write-ReleaseLog "Release assets ready."
}
finally {
    Pop-Location
}

exit 0
