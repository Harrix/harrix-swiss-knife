<# 
.SYNOPSIS
    Download (or copy) offline installers and binaries to install\dependencies.

.DESCRIPTION
    Copies existing binaries from repo root when available (ffmpeg.exe, avifenc.exe, avifdec.exe),
    and downloads missing installers (Git/Python/Node/uv/VS Code) plus optional zip archives
    for libavif/FFmpeg as fallbacks.

.PARAMETER RepoRoot
    Path to the harrix-swiss-knife repository root. If omitted, it is auto-detected
    as the parent folder of this script's directory (install\..).

.PARAMETER Force
    Re-download / overwrite existing files in install\dependencies.
#>
[CmdletBinding()]
param(
    [string] $RepoRoot,
    [switch] $Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch { }

function Write-Step([string] $Msg) {
    Write-Host ""
    Write-Host "==> $Msg" -ForegroundColor Cyan
}

function Resolve-RepoRoot {
    if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
        return (Resolve-Path -LiteralPath $RepoRoot).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}

function New-DirIfMissing([string] $Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Copy-IfExists([string] $Src, [string] $DestDir) {
    if (-not (Test-Path -LiteralPath $Src)) { return $false }
    $name = Split-Path -Leaf $Src
    $dest = Join-Path $DestDir $name
    if ((-not $Force) -and (Test-Path -LiteralPath $dest)) { return $true }
    Copy-Item -LiteralPath $Src -Destination $dest -Force
    return $true
}

function Invoke-Download([string] $Url, [string] $OutFile) {
    if ((-not $Force) -and (Test-Path -LiteralPath $OutFile)) {
        return
    }
    Write-Host "    Download: $Url" -ForegroundColor DarkGray
    Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing -Headers @{ "User-Agent" = "Harrix-Swiss-Knife-Bundle/1.0" }
}

function Get-GitHubJson([string] $Url) {
    $headers = @{
        Accept = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
        "User-Agent" = "Harrix-Swiss-Knife-Bundle/1.0"
    }
    if ($env:GITHUB_TOKEN) {
        $headers["Authorization"] = "Bearer $($env:GITHUB_TOKEN)"
    }
    return Invoke-RestMethod -Uri $Url -Headers $headers -Method Get
}

function Get-LatestRelease([string] $Owner, [string] $Repo) {
    return Get-GitHubJson "https://api.github.com/repos/$Owner/$Repo/releases/latest"
}

function Find-AssetUrl($Release, [string] $ExactName, [string[]] $Contains = @()) {
    $assets = @($Release.assets)
    if ($ExactName) {
        foreach ($a in $assets) {
            if ($a.name -eq $ExactName) { return [string]$a.browser_download_url }
        }
        return $null
    }
    foreach ($a in $assets) {
        $n = [string]$a.name
        if (-not $n) { continue }
        $ok = $true
        foreach ($c in $Contains) {
            if ($n -notlike "*$c*") { $ok = $false; break }
        }
        if ($ok) { return [string]$a.browser_download_url }
    }
    return $null
}

$repo = Resolve-RepoRoot
$deps = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "dependencies") -ErrorAction SilentlyContinue)
if (-not $deps) {
    $deps = Join-Path $PSScriptRoot "dependencies"
}
New-DirIfMissing $deps

Write-Step "Copy binaries from repo root (if present)"
foreach ($exe in @("ffmpeg.exe", "avifenc.exe", "avifdec.exe")) {
    $src = Join-Path $repo $exe
    if (Copy-IfExists -Src $src -DestDir $deps) {
        Write-Host "    Copied $exe" -ForegroundColor Green
    }
    else {
        Write-Host "    Not found: $exe (will rely on zip fallback)" -ForegroundColor Yellow
    }
}

Write-Step "Download Git for Windows installer"
$gitRel = Get-LatestRelease "git-for-windows" "git"
$gitUrl = Find-AssetUrl -Release $gitRel -ExactName $null -Contains @("64-bit.exe")
if (-not $gitUrl) { throw "Could not find Git 64-bit installer asset." }
Invoke-Download -Url $gitUrl -OutFile (Join-Path $deps (Split-Path $gitUrl -Leaf))

Write-Step "Download Python 3.13 amd64 installer"
# Simple approach: pin to latest 3.13.x known at runtime via python.org downloads JSON not available in PS5.1 by default.
# Keep it explicit and easy to bump.
$pyVersion = "3.13.3"
$pyUrl = "https://www.python.org/ftp/python/$pyVersion/python-$pyVersion-amd64.exe"
Invoke-Download -Url $pyUrl -OutFile (Join-Path $deps ("python-$pyVersion-amd64.exe"))

Write-Step "Download Node.js LTS x64 MSI"
$nodeIndex = Invoke-RestMethod -Uri "https://nodejs.org/dist/index.json" -Method Get
$lts = $nodeIndex | Where-Object { $_.lts } | Select-Object -First 1
if (-not $lts) { throw "Could not determine Node.js LTS from index.json" }
$nodeVer = $lts.version.TrimStart("v")
$nodeUrl = "https://nodejs.org/dist/v$nodeVer/node-v$nodeVer-x64.msi"
Invoke-Download -Url $nodeUrl -OutFile (Join-Path $deps ("node-v$nodeVer-x64.msi"))

Write-Step "Download uv windows zip"
$uvRel = Get-LatestRelease "astral-sh" "uv"
$uvUrl = Find-AssetUrl -Release $uvRel -ExactName "uv-x86_64-pc-windows-msvc.zip"
if (-not $uvUrl) { throw "Could not find uv windows zip asset." }
Invoke-Download -Url $uvUrl -OutFile (Join-Path $deps "uv-x86_64-pc-windows-msvc.zip")

Write-Step "Download VS Code user installer"
$vsUrl = "https://update.code.visualstudio.com/latest/win32-x64-user/stable"
# Follow redirect to a real filename, then download.
$resp = Invoke-WebRequest -Uri $vsUrl -MaximumRedirection 5 -UseBasicParsing -Headers @{ "User-Agent" = "Harrix-Swiss-Knife-Bundle/1.0" }
$final = $resp.BaseResponse.ResponseUri.AbsoluteUri
if (-not $final) { $final = $vsUrl }
$vsName = Split-Path $final -Leaf
if ([string]::IsNullOrWhiteSpace($vsName)) { $vsName = "VSCodeUserSetup-x64-latest.exe" }
Invoke-Download -Url $final -OutFile (Join-Path $deps $vsName)

Write-Step "Download fallback zip archives (optional)"
try {
    $libRel = Get-LatestRelease "AOMediaCodec" "libavif"
    $libUrl = Find-AssetUrl -Release $libRel -ExactName "windows-artifacts.zip"
    if ($libUrl) {
        Invoke-Download -Url $libUrl -OutFile (Join-Path $deps "windows-artifacts.zip")
    }
}
catch { Write-Host "    Skip libavif zip: $($_.Exception.Message)" -ForegroundColor Yellow }

try {
    $ffRel = Get-LatestRelease "BtbN" "FFmpeg-Builds"
    $ffUrl = Find-AssetUrl -Release $ffRel -ExactName "ffmpeg-master-latest-win64-gpl.zip"
    if ($ffUrl) {
        Invoke-Download -Url $ffUrl -OutFile (Join-Path $deps "ffmpeg-master-latest-win64-gpl.zip")
    }
}
catch { Write-Host "    Skip FFmpeg zip: $($_.Exception.Message)" -ForegroundColor Yellow }

Write-Step "Done"
Write-Host "Repo root: $repo" -ForegroundColor Green
Write-Host "Bundle dir: $deps" -ForegroundColor Green
