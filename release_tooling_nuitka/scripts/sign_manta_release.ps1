Param(
    [string]$SigntoolPath = "",
    [string]$CertificateSubject = "",
    [string]$TimestampUrl = "http://time.certum.pl",
    [string]$OutputRoot = "",
    [switch]$SignAppFolder,
    [switch]$VerifyOnly,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReleaseRoot = Resolve-Path (Join-Path $ScriptDir "..")
$RepoRoot = Resolve-Path (Join-Path $ReleaseRoot "..")

if (-not $OutputRoot) {
    $OutputRoot = Join-Path $RepoRoot "Output"
}

$AppExePath = Join-Path $OutputRoot "MantaAirfoilTools\MantaAirfoilTools.exe"
$InstallerPath = Join-Path $OutputRoot "MantaAirfoilToolsInstaller.exe"

function Resolve-Signtool {
    param([string]$ExplicitPath)

    if ($ExplicitPath) {
        if (Test-Path $ExplicitPath) {
            return (Resolve-Path $ExplicitPath).Path
        }
        throw "signtool.exe not found at explicit path: $ExplicitPath"
    }

    $cmd = Get-Command signtool.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $kitRoots = @(
        "${env:ProgramFiles(x86)}\Windows Kits\10\bin",
        "${env:ProgramFiles}\Windows Kits\10\bin"
    )
    foreach ($root in $kitRoots) {
        if (-not (Test-Path $root)) {
            continue
        }
        $candidate = Get-ChildItem -Path $root -Filter signtool.exe -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match "\\x64\\signtool\.exe$" } |
            Sort-Object FullName -Descending |
            Select-Object -First 1
        if ($candidate) {
            return $candidate.FullName
        }
    }

    throw "signtool.exe not found. Install Windows SDK or pass -SigntoolPath."
}

function Invoke-Signtool {
    param(
        [string[]]$Arguments,
        [string]$StepName
    )

    Write-Host "[sign] $StepName"
    Write-Host "       signtool $($Arguments -join ' ')"
    if ($WhatIf) {
        return
    }
    & $script:ResolvedSigntool @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$StepName failed with exit code $LASTEXITCODE."
    }
}

function Sign-File {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        throw "File to sign not found: $Path"
    }

    $args = @("sign", "/fd", "SHA256", "/tr", $TimestampUrl, "/td", "SHA256", "/v")
    if ($CertificateSubject) {
        $args += @("/n", $CertificateSubject)
    }
    else {
        $args += @("/a")
    }
    $args += $Path
    Invoke-Signtool -Arguments $args -StepName "Signing $Path"
}

function Verify-File {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        throw "File to verify not found: $Path"
    }

    Invoke-Signtool -Arguments @("verify", "/pa", "/v", $Path) -StepName "Verifying $Path"
}

$script:ResolvedSigntool = Resolve-Signtool -ExplicitPath $SigntoolPath
Write-Host "[sign] signtool: $script:ResolvedSigntool"
Write-Host "[sign] output root: $OutputRoot"
Write-Host "[sign] certificate selector: $(if ($CertificateSubject) { $CertificateSubject } else { 'auto (/a)' })"
Write-Host "[sign] timestamp: $TimestampUrl"

$files = New-Object System.Collections.Generic.List[string]

if ($SignAppFolder) {
    if (-not (Test-Path (Split-Path -Parent $AppExePath))) {
        throw "App folder not found: $(Split-Path -Parent $AppExePath)"
    }
    Get-ChildItem -LiteralPath (Split-Path -Parent $AppExePath) -Recurse -File |
        Where-Object { $_.Extension -in @(".exe", ".dll", ".pyd") } |
        ForEach-Object { $files.Add($_.FullName) }
}
else {
    $files.Add($AppExePath)
}

if (Test-Path $InstallerPath) {
    $files.Add($InstallerPath)
}
else {
    Write-Warning "Installer not found, skipping: $InstallerPath"
}

if ($VerifyOnly) {
    foreach ($file in $files) {
        Verify-File -Path $file
    }
    Write-Host "[sign] verification done"
    exit 0
}

foreach ($file in $files) {
    Sign-File -Path $file
    Verify-File -Path $file
}

Write-Host "[sign] done"
