#Requires -Version 5.1
<#
.SYNOPSIS
    Download (pack) global NPM packages into install\dependencies\npm-packages for offline installs.

.DESCRIPTION
    Reads npm package names from repo config/config.json key "npm_packages".
    For each entry without a version suffix, resolves the version from the
    globally installed package (npm list -g). Optional pinned entries
    (name@version or @scope/name@version) use the version from config.
    Then runs:
      npm.cmd pack <name>@<version> --pack-destination <depsDir>
    and stores resulting .tgz files in install\dependencies\npm-packages.

    This is analogous to the uv-cache warmup step, but uses tarballs (npm pack)
    because it is more portable than relying on npm cache format.

.PARAMETER RepoRoot
    Path to the harrix-swiss-knife repository root. If omitted, auto-detected
    as the parent folder of this script's directory (install\..).

.PARAMETER Force
    Re-pack even if a matching .tgz already exists in install\dependencies\npm-packages.
#>
[CmdletBinding()]
param(
    [string] $RepoRoot,
    [switch] $Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
        return (Resolve-Path -LiteralPath $RepoRoot).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}

function Get-NpmExecutable {
    # In Windows PowerShell, `npm` may resolve to npm.ps1 and fail under restrictive ExecutionPolicy.
    # npm.cmd is not a PowerShell script and always runs.
    # Get-Command may return multiple Application matches; always pick one path as a single [string].
    $cmds = @(Get-Command -Name "npm.cmd" -CommandType Application -ErrorAction SilentlyContinue)
    foreach ($c in $cmds) {
        if ($null -ne $c.Source -and -not [string]::IsNullOrWhiteSpace([string]$c.Source)) {
            return [string]$c.Source
        }
    }
    $npms = @(Get-Command -Name "npm" -ErrorAction SilentlyContinue | Where-Object { $_.CommandType -eq "Application" })
    foreach ($c in $npms) {
        if ($null -ne $c.Source -and -not [string]::IsNullOrWhiteSpace([string]$c.Source)) {
            return [string]$c.Source
        }
    }
    return $null
}

function Read-JsonFile([string] $Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "JSON file not found: $Path"
    }
    $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 -ErrorAction Stop
    return ($raw | ConvertFrom-Json -ErrorAction Stop)
}

function Normalize-NpmPackageName([string] $PackageName) {
    # npm pack output uses name normalization:
    #   @scope/name -> scope-name
    #   name -> name
    $n = ""
    if ($null -ne $PackageName) {
        $n = $PackageName.Trim()
    }
    if ($n.StartsWith("@")) { $n = $n.Substring(1) }
    $n = $n -replace "/", "-"
    return $n
}

function Split-NpmPackageEntry([string] $Spec) {
    $s = ""
    if ($null -ne $Spec) {
        $s = $Spec.Trim()
    }
    if ([string]::IsNullOrWhiteSpace($s)) {
        throw "Empty npm spec in config (npm_packages)."
    }
    $lastAt = $s.LastIndexOf("@")
    if ($lastAt -le 0) {
        return [pscustomobject]@{ Name = $s; VersionFromConfig = $null }
    }
    $suffix = $s.Substring($lastAt + 1)
    if ($suffix -match '^\d' -or $suffix -match '^[\^~]') {
        $name = $s.Substring(0, $lastAt)
        if ([string]::IsNullOrWhiteSpace($name)) {
            throw "Invalid npm spec: '$s'"
        }
        return [pscustomobject]@{ Name = $name; VersionFromConfig = $suffix }
    }
    return [pscustomobject]@{ Name = $s; VersionFromConfig = $null }
}

function Get-GlobalNpmPackageVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string] $NpmExe,
        [Parameter(Mandatory = $true)]
        [string] $PackageName
    )
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $raw = & $NpmExe "list" "-g" $PackageName "--depth=0" "--json" 2>&1
    }
    finally {
        $ErrorActionPreference = $prevEap
    }
    $jsonText = ($raw | ForEach-Object { "$_" }) -join "`n"
    try {
        $j = $jsonText | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $null
    }
    if (-not $j -or -not $j.dependencies) {
        return $null
    }
    $deps = $j.dependencies
    if ($deps.PSObject.Properties[$PackageName]) {
        $node = $deps.$PackageName
        if ($node -and $node.version) {
            return [string]$node.version
        }
    }
    foreach ($p in $deps.PSObject.Properties) {
        if ($p.Name -eq $PackageName -and $p.Value.version) {
            return [string]$p.Value.version
        }
    }
    return $null
}

$repo = Resolve-RepoRoot
$depsRoot = Join-Path $repo "install\dependencies"
$depsNpm = Join-Path $depsRoot "npm-packages"
$configPath = Join-Path $repo "config\config.json"

New-Item -ItemType Directory -Path $depsNpm -Force | Out-Null

Write-Host ""
Write-Host ("Repo root:   {0}" -f $repo) -ForegroundColor Green
Write-Host ("Config:      {0}" -f $configPath) -ForegroundColor DarkGray
Write-Host ("NPM bundle:  {0}" -f $depsNpm) -ForegroundColor Green

$npmExe = Get-NpmExecutable
if (-not $npmExe) {
    throw "npm is not available on PATH (looked for npm.cmd / npm). Install Node.js first."
}

$cfg = Read-JsonFile -Path $configPath
$list = @($cfg.npm_packages)
if (-not $list -or $list.Count -eq 0) {
    Write-Host ""
    Write-Host "No npm_packages configured; nothing to download." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Packing npm packages:" -ForegroundColor Cyan

foreach ($item in $list) {
    $entry = Split-NpmPackageEntry -Spec ([string]$item)
    $pkgName = $entry.Name
    $version = $entry.VersionFromConfig
    if (-not $version) {
        $version = Get-GlobalNpmPackageVersion -NpmExe $npmExe -PackageName $pkgName
        if (-not $version) {
            throw (
                "Package '$pkgName' is not installed globally (npm list -g). " +
                "Install it first, e.g. npm.cmd i -g $pkgName, then re-run this script."
            )
        }
        Write-Host ("  - Resolved version from global install: {0}@{1}" -f $pkgName, $version) -ForegroundColor DarkGray
    }
    else {
        Write-Host ("  - Using version from config: {0}@{1}" -f $pkgName, $version) -ForegroundColor DarkGray
    }

    $packSpec = "{0}@{1}" -f $pkgName, $version
    $normName = Normalize-NpmPackageName -PackageName $pkgName
    $expected = Join-Path $depsNpm ("{0}-{1}.tgz" -f $normName, $version)

    if ((-not $Force) -and (Test-Path -LiteralPath $expected)) {
        Write-Host ("  - Skip (exists): {0}" -f $expected) -ForegroundColor DarkGray
        continue
    }

    Write-Host ("  - npm pack {0}" -f $packSpec) -ForegroundColor DarkGray
    & $npmExe "pack" $packSpec "--pack-destination" $depsNpm
    if ($LASTEXITCODE -ne 0) {
        throw ("npm pack failed for '{0}' (exit {1})" -f $packSpec, $LASTEXITCODE)
    }

    if (-not (Test-Path -LiteralPath $expected)) {
        $actual = @(Get-ChildItem -LiteralPath $depsNpm -Filter ("{0}-*.tgz" -f $normName) -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1)
        if ($actual.Count -gt 0) {
            throw ("Expected '{0}' but got '{1}'. Check npm pack naming or spec: {2}" -f $expected, $actual[0].FullName, $packSpec)
        }
        throw ("Expected tarball was not created: {0}" -f $expected)
    }

    Write-Host ("    OK: {0}" -f $expected) -ForegroundColor Green
}

Write-Host ""
Write-Host "Done" -ForegroundColor Green
