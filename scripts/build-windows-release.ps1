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

function Reset-Directory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (Test-Path $Path) {
        try {
            Remove-Item $Path -Recurse -Force -ErrorAction Stop
        }
        catch {
            cmd.exe /c "rmdir /s /q ""$Path"" >nul 2>nul"
        }
    }

    if (Test-Path $Path) {
        Start-Sleep -Milliseconds 500
        if (Test-Path $Path) {
            throw "Unable to clear directory $Path before release build."
        }
    }

    New-Item -ItemType Directory -Path $Path -Force | Out-Null
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
    $appVersion = python -c "import tomllib, pathlib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['version'])"
    Write-ReleaseStage "Prepare release staging"
    if (Test-Path "$repoRoot\.tmp\build-release") {
        Remove-Item "$repoRoot\.tmp\build-release" -Recurse -Force
    }
    Reset-Directory -Path $stageRoot

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
        & $isccPath "/DAppVersion=$appVersion" "/DSourceBundleDir=$bundleDir" "/DSourceSmokeDir=$smokeBundleDir" "/DOutputDirPath=$stageInstallerDir" "$repoRoot\packaging\windows\installer.iss"
    }

    $installerBuilt = "$stageInstallerDir\market-data-recorder-setup.exe"
    $installerFinal = "$finalDist\market-data-recorder-setup.exe"

    Invoke-NativeStep -StageName "Smoke test installer" -Command {
        powershell -ExecutionPolicy Bypass -File "$repoRoot\scripts\smoke-test-installer.ps1" -InstallerPath $installerBuilt
    }

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
