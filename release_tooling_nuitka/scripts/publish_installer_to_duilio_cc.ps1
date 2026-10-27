param(
    [string]$InstallerPath = "",
    [string]$SiteRepoRoot = "",
    [string]$RemoteSubdir = "",
    [string]$RemoteBaseUrl = "",
    [string]$LocalConfigPath = "",
    [switch]$SkipUpload
)

$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Resolve-WinScpPath {
    $candidates = @(
        $env:WINSCP_PATH,
        "C:\Program Files\WinSCP\WinSCP.com",
        "C:\Program Files (x86)\WinSCP\WinSCP.com"
    ) | Where-Object { $_ }

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }

    throw "WinSCP.com not found. Install WinSCP or set WINSCP_PATH."
}

function Invoke-WinScpUpload {
    param(
        [string]$WinScpPath,
        [string]$SessionName,
        [string]$RemoteDir,
        [string]$InstallerLocalPath,
        [string]$ManifestLocalPath
    )

    $tempScript = [System.IO.Path]::GetTempFileName()
    try {
        $scriptLines = @(
            "option batch abort",
            "option confirm off",
            ('open "{0}"' -f $SessionName.Replace('"', '""')),
            ('put "{0}" "{1}/"' -f $InstallerLocalPath.Replace('"', '""'), $RemoteDir),
            ('put "{0}" "{1}/"' -f $ManifestLocalPath.Replace('"', '""'), $RemoteDir),
            "exit"
        )
        [System.IO.File]::WriteAllLines($tempScript, $scriptLines, [System.Text.UTF8Encoding]::new($false))

        & $WinScpPath "/script=$tempScript"
        if ($LASTEXITCODE -ne 0) {
            throw "WinSCP upload failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Remove-Item -LiteralPath $tempScript -Force -ErrorAction SilentlyContinue
    }
}

$repoRoot = Get-RepoRoot
if (-not $InstallerPath) {
    $InstallerPath = Join-Path $repoRoot "Output\MantaAirfoilToolsInstaller.exe"
}

if (-not $SiteRepoRoot) {
    throw "Missing SiteRepoRoot. Run python .\Action\release_manta_airlab.py or pass -SiteRepoRoot explicitly."
}

if (-not $RemoteSubdir) {
    throw "Missing RemoteSubdir. Run python .\Action\release_manta_airlab.py or pass -RemoteSubdir explicitly."
}

if (-not $RemoteBaseUrl) {
    throw "Missing RemoteBaseUrl. Run python .\Action\release_manta_airlab.py or pass -RemoteBaseUrl explicitly."
}

if (-not (Test-Path $InstallerPath)) {
    throw "Installer not found: $InstallerPath`nRun python .\Action\release_manta_airlab.py first."
}

$InstallerPath = (Resolve-Path $InstallerPath).Path

if (-not $LocalConfigPath) {
    $actionConfigPath = Join-Path $repoRoot "Action\installer_upload.local.ps1"
    $legacyConfigPath = Join-Path $SiteRepoRoot "_private\installer_upload.local.ps1"
    if (Test-Path $actionConfigPath) {
        $LocalConfigPath = $actionConfigPath
    }
    else {
        $LocalConfigPath = $legacyConfigPath
    }
}

$winscpSite = $env:DUILIO_WINSCP_SITE

if ((-not $winscpSite) -and (Test-Path $LocalConfigPath)) {
    $localConfig = . $LocalConfigPath
    if ($localConfig -is [hashtable]) {
        if (-not $winscpSite) { $winscpSite = $localConfig["DUILIO_WINSCP_SITE"] }
    }
}

if (-not $SkipUpload -and -not $winscpSite) {
    throw "Missing WinSCP site name. Set DUILIO_WINSCP_SITE or create local config: $LocalConfigPath"
}

$stagingDir = Join-Path $SiteRepoRoot "_private\release_staging\manta-airfoil-tools"
$publicMirrorDir = Join-Path $SiteRepoRoot "www\$RemoteSubdir"
New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null
New-Item -ItemType Directory -Force -Path $publicMirrorDir | Out-Null

$installerName = [IO.Path]::GetFileName($InstallerPath)
$stagedInstaller = Join-Path $stagingDir $installerName
$publicMirrorInstaller = Join-Path $publicMirrorDir $installerName

Copy-Item -LiteralPath $InstallerPath -Destination $stagedInstaller -Force
Copy-Item -LiteralPath $InstallerPath -Destination $publicMirrorInstaller -Force

$hash = (Get-FileHash -LiteralPath $InstallerPath -Algorithm SHA256).Hash.ToLowerInvariant()
$size = (Get-Item -LiteralPath $InstallerPath).Length
$releasedAt = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$versionPath = Join-Path $repoRoot "VERSION"
$version = ""
if (Test-Path $versionPath) {
    $version = ((Get-Content -LiteralPath $versionPath -Raw) -as [string]).Trim()
}

$manifest = [ordered]@{
    product = "MantaAirfoilTools"
    channel = "stable"
    version = $version
    filename = $installerName
    size_bytes = $size
    sha256 = $hash
    released_at = $releasedAt
    url = "https://duilio.cc/manta-airfoil-tools/download.php"
}

$manifestJson = $manifest | ConvertTo-Json -Depth 3
$stagedManifest = Join-Path $stagingDir "manifest.json"
$publicMirrorManifest = Join-Path $publicMirrorDir "manifest.json"
[IO.File]::WriteAllText($stagedManifest, $manifestJson + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($publicMirrorManifest, $manifestJson + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))

if (-not $SkipUpload) {
    $winscpPath = Resolve-WinScpPath
    $remoteDir = "/www/{0}" -f $RemoteSubdir.Trim("/")
    Write-Host "Upload backend: WinSCP"
    Write-Host "WinSCP site: $winscpSite"
    Invoke-WinScpUpload -WinScpPath $winscpPath -SessionName $winscpSite -RemoteDir $remoteDir -InstallerLocalPath $stagedInstaller -ManifestLocalPath $stagedManifest
}

Write-Host "Installer staged: $stagedInstaller"
Write-Host "Mirror updated: $publicMirrorInstaller"
Write-Host "Manifest: $stagedManifest"
if (-not $SkipUpload) {
    Write-Host "Remote URL: $RemoteBaseUrl/$installerName"
}
