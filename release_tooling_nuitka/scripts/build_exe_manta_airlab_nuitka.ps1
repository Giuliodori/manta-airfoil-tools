Param(
    [string]$PythonExe = "python",
    [string]$AppVersion = "0.1.0",
    [switch]$SkipInno
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReleaseRoot = Resolve-Path (Join-Path $ScriptDir "..")
$RepoRoot = Resolve-Path (Join-Path $ReleaseRoot "..")

$EntryScript = Join-Path $RepoRoot "manta_airfoil_tools.py"
$IconPath = Join-Path $RepoRoot "images\ico.ico"
$InnoScript = Join-Path $ReleaseRoot "inno\manta-airfoil-tools.iss"
$Requirements = Join-Path $ReleaseRoot "requirements-windows.txt"
$NuitkaWorkRoot = Join-Path $env:TEMP "manta_airlab_nuitka_build"
$NuitkaOutputRoot = Join-Path $NuitkaWorkRoot "out"
$RepoOutputPath = Join-Path $ReleaseRoot "output"
$RepoDistAppPath = Join-Path $RepoOutputPath "MantaAirfoilTools"
$FinalOutputPath = Join-Path $RepoRoot "Output"
$FinalDistAppPath = Join-Path $FinalOutputPath "MantaAirfoilTools"
$InstallerName = "MantaAirfoilToolsInstaller.exe"
$RepoInstallerPath = Join-Path $RepoOutputPath $InstallerName
$FinalInstallerPath = Join-Path $FinalOutputPath $InstallerName

function Copy-DirectoryContents {
    param(
        [string]$SourceDir,
        [string]$DestinationDir
    )

    if (Test-Path $DestinationDir) {
        Remove-Item -Recurse -Force $DestinationDir -ErrorAction Stop
    }

    New-Item -ItemType Directory -Path $DestinationDir -Force | Out-Null
    Copy-Item -Path (Join-Path $SourceDir '*') -Destination $DestinationDir -Recurse -Force
}

function Assert-LastExitCode {
    param([string]$StepName)

    if ($LASTEXITCODE -ne 0) {
        throw "$StepName failed with exit code $LASTEXITCODE."
    }
}

function Resolve-InnoCompiler {
    $isccCandidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
    )

    foreach ($candidate in $isccCandidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

Write-Host "[1/6] Repo root: $RepoRoot"
Write-Host "[1.1/6] Checking Python version"
& $PythonExe -c "import sys; print(sys.version); raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
Assert-LastExitCode "Python version check (>=3.11 required)"

Write-Host "[2/6] Installing build dependencies"
& $PythonExe -m pip install -r $Requirements
Assert-LastExitCode "Dependency installation"

Write-Host "[3/6] Preparing Nuitka work directory"
if (Test-Path $NuitkaWorkRoot) {
    Remove-Item -Recurse -Force $NuitkaWorkRoot -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $NuitkaOutputRoot -Force | Out-Null

Write-Host "[4/6] Building standalone executable with Nuitka"
Push-Location $RepoRoot
try {
    & $PythonExe -m nuitka `
        --assume-yes-for-downloads `
        --mode=standalone `
        --output-dir="$NuitkaOutputRoot" `
        --output-filename=MantaAirfoilTools.exe `
        --windows-console-mode=disable `
        --windows-icon-from-ico="$IconPath" `
        --company-name="Fabio Giuliodori" `
        --product-name="Manta Airfoil Tools" `
        --file-version="$AppVersion" `
        --product-version="$AppVersion" `
        --enable-plugin=tk-inter `
        --enable-plugin=matplotlib `
        --include-data-dir=images=images `
        --include-data-files=VERSION=VERSION `
        --include-data-files=LICENSE=licenses/LICENSE `
        --include-data-files=docs/THIRD_PARTY_NOTICES.md=licenses/THIRD_PARTY_NOTICES.md `
        --include-module=aero `
        --include-module=airfoil_db_sqlite `
        --include-module=airfoil_library `
        --include-module=defaults `
        --include-module=exporters `
        --include-module=geometry `
        --include-module=setup `
        --include-module=units `
        "$EntryScript"
    Assert-LastExitCode "Nuitka build"
}
finally {
    Pop-Location
}

$nuitkaDistAppPath = Join-Path $NuitkaOutputRoot "manta_airfoil_tools.dist"
if (-not (Test-Path $nuitkaDistAppPath)) {
    throw "Nuitka output not found: $nuitkaDistAppPath"
}

Write-Host "[5/6] Refreshing repo dist folder"
if (-not (Test-Path $RepoOutputPath)) {
    New-Item -ItemType Directory -Path $RepoOutputPath -Force | Out-Null
}
if (-not (Test-Path $FinalOutputPath)) {
    New-Item -ItemType Directory -Path $FinalOutputPath -Force | Out-Null
}
Copy-DirectoryContents -SourceDir $nuitkaDistAppPath -DestinationDir $RepoDistAppPath
Copy-DirectoryContents -SourceDir $nuitkaDistAppPath -DestinationDir $FinalDistAppPath

if (-not $SkipInno) {
    Write-Host "[6/6] Creating installer with Inno Setup"
    $iscc = Resolve-InnoCompiler
    if (-not $iscc) {
        throw "ISCC.exe not found. Install Inno Setup 6 or run with -SkipInno."
    }

    & $iscc "/DAppVersion=$AppVersion" "/DDistSource=$RepoDistAppPath" $InnoScript
    Assert-LastExitCode "Inno Setup compilation"
}

if (-not $SkipInno -and (Test-Path $RepoInstallerPath)) {
    Copy-Item -LiteralPath $RepoInstallerPath -Destination $FinalInstallerPath -Force
}

Write-Host "Done."
Write-Host "Nuitka output: $FinalDistAppPath"
if (-not $SkipInno) {
    Write-Host "Installer output: $FinalInstallerPath"
}
