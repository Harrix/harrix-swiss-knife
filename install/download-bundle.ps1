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

.PARAMETER SkipUvCache
    Skip populating install\dependencies\uv-cache\ via uv sync for sibling repos.

.PARAMETER OnlyUvCache
    Only populate install\dependencies\uv-cache\ and skip downloading installers/binaries.

.PARAMETER SkipRepos
    Skip snapshotting working trees of sibling repos to install\dependencies\repos\.

.PARAMETER OnlyRepos
    Only snapshot working trees of sibling repos to install\dependencies\repos\ and
    skip downloading installers/binaries and uv cache.

.PARAMETER SkipBinaries
    Skip copying/downloading media binaries (ffmpeg.exe, avifenc.exe, avifdec.exe) and related fallback zip archives.

.PARAMETER OnlyBinaries
    Only copy/download media binaries (ffmpeg.exe, avifenc.exe, avifdec.exe) and related fallback zip archives,
    and skip installers downloads, repos snapshots, and uv cache.
#>
[CmdletBinding()]
param(
    [string] $RepoRoot,
    [switch] $Force,
    [switch] $SkipUvCache,
    [switch] $OnlyUvCache,
    [switch] $SkipRepos,
    [switch] $OnlyRepos,
    [switch] $SkipBinaries,
    [switch] $OnlyBinaries
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
    Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing -TimeoutSec 1800 -Headers @{ "User-Agent" = "Harrix-Swiss-Knife-Bundle/1.0" }
}

function Try-Download([string] $Label, [string] $Url, [string] $OutFile) {
    try {
        Invoke-Download -Url $Url -OutFile $OutFile
        if (Test-Path -LiteralPath $OutFile) {
            Write-Host "    OK: $Label -> $OutFile" -ForegroundColor Green
            return $true
        }
        Write-Host "    FAIL: $Label (file not created)" -ForegroundColor Yellow
        return $false
    }
    catch {
        Write-Host "    FAIL: ${Label}: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    }
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
$deps = Join-Path $PSScriptRoot "dependencies"
New-DirIfMissing $deps

Write-Host ""
Write-Host ("Repo root:  {0}" -f $repo) -ForegroundColor Green
Write-Host ("Bundle dir: {0}" -f $deps) -ForegroundColor Green

$onlyCount = 0
if ($OnlyUvCache) { $onlyCount++ }
if ($OnlyRepos) { $onlyCount++ }
if ($OnlyBinaries) { $onlyCount++ }
if ($onlyCount -gt 1) {
    throw "Specify only one of -OnlyUvCache, -OnlyRepos, -OnlyBinaries."
}

if ($OnlyUvCache) {
    # When refreshing uv cache frequently, skip all other downloads/copies.
    Write-Host ""
    Write-Host "OnlyUvCache enabled: skipping installers/binaries/repos snapshot." -ForegroundColor DarkGray
    $SkipUvCache = $false
    $SkipRepos = $true
    $SkipBinaries = $true
}

if ($OnlyRepos) {
    # When refreshing repo snapshots frequently, skip all other downloads/copies.
    Write-Host ""
    Write-Host "OnlyRepos enabled: skipping installers/binaries/uv cache." -ForegroundColor DarkGray
    $SkipRepos = $false
    $SkipUvCache = $true
    $SkipBinaries = $true
}

if ($OnlyBinaries) {
    # When refreshing media binaries frequently, skip all other downloads/copies.
    Write-Host ""
    Write-Host "OnlyBinaries enabled: skipping installers/repos snapshot/uv cache." -ForegroundColor DarkGray
    $SkipBinaries = $false
    $SkipRepos = $true
    $SkipUvCache = $true
}

$SkipInstallers = $OnlyUvCache -or $OnlyRepos -or $OnlyBinaries

if ((-not $SkipBinaries) -and (-not $OnlyUvCache) -and (-not $OnlyRepos)) {
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
}

if (-not $SkipInstallers) {
    Write-Step "Download Git for Windows installer"
    try {
        $gitRel = Get-LatestRelease "git-for-windows" "git"
        $gitUrl = Find-AssetUrl -Release $gitRel -ExactName $null -Contains @("64-bit.exe")
        if (-not $gitUrl) { throw "Could not find Git 64-bit installer asset." }
        Try-Download -Label "Git installer" -Url $gitUrl -OutFile (Join-Path $deps "Git-latest-64-bit.exe") | Out-Null
    }
    catch { Write-Host "    Skip Git: $($_.Exception.Message)" -ForegroundColor Yellow }
}

if (-not $SkipInstallers) {
    Write-Step "Download Python 3.13 amd64 installer"
    try {
        # Try a few latest patch versions (python.org may already have newer/older on different days).
        $candidates = @("3.13.4", "3.13.3", "3.13.2", "3.13.1", "3.13.0")
        $downloaded = $false
        foreach ($pyVersion in $candidates) {
            $pyUrl = "https://www.python.org/ftp/python/$pyVersion/python-$pyVersion-amd64.exe"
            $out = Join-Path $deps ("python-$pyVersion-amd64.exe")
            if (Try-Download -Label ("Python " + $pyVersion) -Url $pyUrl -OutFile $out) {
                $downloaded = $true
                break
            }
        }
        if (-not $downloaded) {
            Write-Host "    Skip Python: none of the candidate versions downloaded." -ForegroundColor Yellow
        }
    }
    catch { Write-Host "    Skip Python: $($_.Exception.Message)" -ForegroundColor Yellow }
}

if (-not $SkipInstallers) {
    Write-Step "Download Node.js LTS x64 MSI"
    try {
        $nodeIndex = Invoke-RestMethod -Uri "https://nodejs.org/dist/index.json" -Method Get
        $lts = $nodeIndex | Where-Object { $_.lts } | Select-Object -First 1
        if (-not $lts) { throw "Could not determine Node.js LTS from index.json" }
        $nodeVer = $lts.version.TrimStart("v")
        $nodeUrl = "https://nodejs.org/dist/v$nodeVer/node-v$nodeVer-x64.msi"
        Try-Download -Label ("Node.js LTS " + $nodeVer) -Url $nodeUrl -OutFile (Join-Path $deps ("node-v$nodeVer-x64.msi")) | Out-Null
    }
    catch { Write-Host "    Skip Node.js: $($_.Exception.Message)" -ForegroundColor Yellow }
}

if (-not $SkipInstallers) {
    Write-Step "Download uv windows zip"
    try {
        $uvUrl = "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
        if (-not (Try-Download -Label "uv zip (latest/download)" -Url $uvUrl -OutFile (Join-Path $deps "uv-x86_64-pc-windows-msvc.zip"))) {
            # Fallback: GitHub API (may 403 if rate limited; set GITHUB_TOKEN if so)
            $uvRel = Get-LatestRelease "astral-sh" "uv"
            $uvUrl2 = Find-AssetUrl -Release $uvRel -ExactName "uv-x86_64-pc-windows-msvc.zip"
            if (-not $uvUrl2) { throw "Could not find uv windows zip asset." }
            Try-Download -Label "uv zip (api)" -Url $uvUrl2 -OutFile (Join-Path $deps "uv-x86_64-pc-windows-msvc.zip") | Out-Null
        }
    }
    catch { Write-Host "    Skip uv: $($_.Exception.Message)" -ForegroundColor Yellow }
}

if (-not $SkipInstallers) {
    Write-Step "Download VS Code user installer"
    $vsUrl = "https://update.code.visualstudio.com/latest/win32-x64-user/stable"
    # Download directly (URL redirects to actual installer).
    try {
        Try-Download -Label "VS Code installer" -Url $vsUrl -OutFile (Join-Path $deps "VSCodeSetup-x64-latest.exe") | Out-Null
    }
    catch { Write-Host "    Skip VS Code: $($_.Exception.Message)" -ForegroundColor Yellow }
}

if ((-not $SkipBinaries) -and (-not $OnlyUvCache) -and (-not $OnlyRepos)) {
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
}

if (-not $SkipRepos) {
    Write-Step "Snapshot sibling repos (git archive HEAD)"
    $reposDir = Join-Path $deps "repos"
    if ($Force -and (Test-Path -LiteralPath $reposDir)) {
        Write-Host "    -Force: removing existing $reposDir" -ForegroundColor DarkGray
        Remove-Item -LiteralPath $reposDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-DirIfMissing $reposDir

    if (-not (Get-Command -Name "git" -ErrorAction SilentlyContinue)) {
        Write-Host "    Skip repos snapshot: 'git' is not on PATH." -ForegroundColor Yellow
    }
    else {
        $repoParent = Split-Path -Parent $repo
        $repoList = @(
            @{ Path = (Join-Path $repoParent "harrix-pylib");      Name = "harrix-pylib"      },
            @{ Path = (Join-Path $repoParent "harrix-pyssg");      Name = "harrix-pyssg"      },
            @{ Path = $repo;                                       Name = "harrix-swiss-knife" }
        )
        foreach ($r in $repoList) {
            if (-not (Test-Path -LiteralPath (Join-Path $r.Path ".git"))) {
                Write-Host ("    Skip {0}: not a git repo at {1}" -f $r.Name, $r.Path) -ForegroundColor Yellow
                continue
            }
            $out = Join-Path $reposDir ("{0}.zip" -f $r.Name)
            Write-Host ("    git archive {0} -> {1}" -f $r.Name, $out) -ForegroundColor DarkGray
            Push-Location $r.Path
            try {
                $prevEap = $ErrorActionPreference
                $ErrorActionPreference = "Continue"
                # Use cmd.exe wrapper for consistent stderr handling on Windows PowerShell.
                & cmd.exe /c "git archive --format=zip --output=`"$out`" HEAD"
                $code = $LASTEXITCODE
                $ErrorActionPreference = $prevEap
                if ($code -ne 0) {
                    Write-Host ("    {0}: git archive exited with code {1}" -f $r.Name, $code) -ForegroundColor Yellow
                }
                else {
                    Write-Host ("    OK: {0}" -f $r.Name) -ForegroundColor Green
                }
            }
            finally {
                Pop-Location
            }
        }
    }
}
else {
    Write-Host ""
    Write-Host "Skip repos snapshot (-SkipRepos)" -ForegroundColor DarkGray
}

if (-not $SkipUvCache) {
    Write-Step "Populate uv cache (sibling repos)"
    $cacheDir = Join-Path $deps "uv-cache"
    if ($Force -and (Test-Path -LiteralPath $cacheDir)) {
        Write-Host "    -Force: removing existing $cacheDir" -ForegroundColor DarkGray
        Remove-Item -LiteralPath $cacheDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-DirIfMissing $cacheDir

    $uvCmd = Get-Command -Name "uv" -ErrorAction SilentlyContinue
    if (-not $uvCmd) {
        Write-Host "    Skip uv cache: 'uv' is not on PATH (install uv first or run install.bat once to provision it)." -ForegroundColor Yellow
    }
    else {
        $repoParent = Split-Path -Parent $repo
        $siblings = @(
            @{ Path = (Join-Path $repoParent "harrix-pylib");      Name = "harrix-pylib"      },
            @{ Path = (Join-Path $repoParent "harrix-pyssg");      Name = "harrix-pyssg"      },
            @{ Path = $repo;                                       Name = "harrix-swiss-knife" }
        )

        $prevCache = $env:UV_CACHE_DIR
        try {
            $env:UV_CACHE_DIR = $cacheDir
            foreach ($s in $siblings) {
                $pp = Join-Path $s.Path "pyproject.toml"
                if (-not (Test-Path -LiteralPath $pp)) {
                    Write-Host ("    Skip {0}: pyproject.toml not found at {1}" -f $s.Name, $s.Path) -ForegroundColor Yellow
                    continue
                }
                Write-Host ("    uv sync in {0} ({1})" -f $s.Name, $s.Path) -ForegroundColor DarkGray
                Push-Location $s.Path
                try {
                    $prevEap = $ErrorActionPreference
                    $ErrorActionPreference = "Continue"
                    # Use cmd.exe wrapper to avoid Windows PowerShell treating uv stderr as a terminating error record.
                    & cmd.exe /c "uv sync --reinstall"
                    $code = $LASTEXITCODE
                    $ErrorActionPreference = $prevEap
                    if ($code -ne 0) {
                        Write-Host ("    {0}: uv sync exited with code {1}" -f $s.Name, $code) -ForegroundColor Yellow
                    }
                    else {
                        Write-Host ("    OK: {0}" -f $s.Name) -ForegroundColor Green
                    }
                }
                finally {
                    Pop-Location
                }
            }
        }
        finally {
            if ($null -eq $prevCache) {
                Remove-Item Env:UV_CACHE_DIR -ErrorAction SilentlyContinue
            }
            else {
                $env:UV_CACHE_DIR = $prevCache
            }
        }
    }
}
else {
    Write-Host ""
    Write-Host "Skip uv cache population (-SkipUvCache)" -ForegroundColor DarkGray
}

Write-Step "Done"
Write-Host "Repo root: $repo" -ForegroundColor Green
Write-Host "Bundle dir: $deps" -ForegroundColor Green
