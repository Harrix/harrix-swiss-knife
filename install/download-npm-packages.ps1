#Requires -Version 5.1
<#
.SYNOPSIS
    Download (pack) global NPM packages into install\dependencies\npm-packages for offline installs.

.DESCRIPTION
    Reads npm package names from repo config/config.json key "npm_packages".
    For each entry without a version suffix, resolves the version from the
    globally installed package (npm list -g). Optional pinned entries
    (name@version or @scope/name@version) use the version from config.
    Prefers packing from the global install folder (npm root -g) so no registry
    fetch is needed when versions match. Falls back to:
      npm.cmd pack <name>@<version> --pack-destination <depsDir>
    with long timeouts and retries when the global folder cannot be used.

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

function Get-NpmGlobalNodeModulesRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string] $NpmExe
    )
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $raw = @(& $NpmExe "root" "-g" 2>&1 | ForEach-Object { "$_" })
    }
    finally {
        $ErrorActionPreference = $prevEap
    }
    $candidates = New-Object System.Collections.Generic.List[string]
    foreach ($line in $raw) {
        $t = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($t)) { continue }
        if (Test-Path -LiteralPath $t) {
            try {
                $item = Get-Item -LiteralPath $t -ErrorAction Stop
                if ($item.PSIsContainer) {
                    $candidates.Add($item.FullName) | Out-Null
                }
            }
            catch { }
        }
    }
    if ($candidates.Count -eq 0) {
        return $null
    }
    return [string]$candidates[$candidates.Count - 1]
}

function Get-GlobalNpmPackageFolder {
    param(
        [Parameter(Mandatory = $true)]
        [string] $NpmExe,
        [Parameter(Mandatory = $true)]
        [string] $PackageName
    )
    $root = Get-NpmGlobalNodeModulesRoot -NpmExe $NpmExe
    if (-not $root) {
        return $null
    }
    $name = $PackageName.Trim()
    if ($name.StartsWith("@")) {
        $slash = $name.IndexOf("/", 1, [System.StringComparison]::Ordinal)
        if ($slash -lt 0) {
            return $null
        }
        $scope = $name.Substring(0, $slash)
        $leaf = $name.Substring($slash + 1)
        $p = Join-Path (Join-Path $root $scope) $leaf
    }
    else {
        $p = Join-Path $root $name
    }
    if (Test-Path -LiteralPath $p) {
        return (Resolve-Path -LiteralPath $p).Path
    }
    return $null
}

function Get-PackageJsonVersion {
    param([Parameter(Mandatory = $true)] [string] $PackageFolder)
    $pj = Join-Path $PackageFolder "package.json"
    if (-not (Test-Path -LiteralPath $pj)) {
        return $null
    }
    try {
        $raw = Get-Content -LiteralPath $pj -Raw -Encoding UTF8 -ErrorAction Stop
        $j = $raw | ConvertFrom-Json -ErrorAction Stop
        if ($j.version) {
            return [string]$j.version
        }
    }
    catch { }
    return $null
}

function Invoke-NpmPackWithNetworkRetries {
    param(
        [Parameter(Mandatory = $true)]
        [string] $NpmExe,
        [Parameter(Mandatory = $true)]
        [string[]] $PackArgs,
        [int] $MaxAttempts = 5,
        [int] $SleepSeconds = 20,
        [int] $FetchTimeoutMs = 600000,
        [int] $FetchRetries = 8,
        [int] $FetchRetryMinTimeoutMs = 20000,
        [int] $FetchRetryMaxTimeoutMs = 180000
    )
    $prev = [ordered]@{
        npm_config_fetch_timeout           = $env:npm_config_fetch_timeout
        npm_config_fetch_retries           = $env:npm_config_fetch_retries
        npm_config_fetch_retry_mintimeout  = $env:npm_config_fetch_retry_mintimeout
        npm_config_fetch_retry_maxtimeout  = $env:npm_config_fetch_retry_maxtimeout
        npm_config_fund                    = $env:npm_config_fund
        npm_config_audit                   = $env:npm_config_audit
    }
    try {
        $env:npm_config_fetch_timeout = "$FetchTimeoutMs"
        $env:npm_config_fetch_retries = "$FetchRetries"
        $env:npm_config_fetch_retry_mintimeout = "$FetchRetryMinTimeoutMs"
        $env:npm_config_fetch_retry_maxtimeout = "$FetchRetryMaxTimeoutMs"
        $env:npm_config_fund = "false"
        $env:npm_config_audit = "false"
        $cliFlags = @(
            "--fetch-timeout=$FetchTimeoutMs",
            "--fetch-retries=$FetchRetries",
            "--fetch-retry-mintimeout=$FetchRetryMinTimeoutMs",
            "--fetch-retry-maxtimeout=$FetchRetryMaxTimeoutMs"
        )
        $fullArgs = $cliFlags + $PackArgs
        for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
            Write-Host ("    npm {0} (attempt {1}/{2})" -f (($fullArgs -join " ")), $attempt, $MaxAttempts) -ForegroundColor DarkGray
            & $NpmExe @fullArgs
            if ($LASTEXITCODE -eq 0) {
                return $true
            }
            if ($attempt -lt $MaxAttempts) {
                Write-Host ("    npm pack failed (exit {0}). Retrying in {1} s..." -f $LASTEXITCODE, $SleepSeconds) -ForegroundColor Yellow
                Start-Sleep -Seconds $SleepSeconds
            }
        }
        return $false
    }
    finally {
        foreach ($k in $prev.Keys) {
            if ($null -eq $prev[$k]) {
                Remove-Item "Env:$k" -ErrorAction SilentlyContinue
            }
            else {
                Set-Item "Env:$k" -Value $prev[$k]
            }
        }
    }
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

    $globalFolder = Get-GlobalNpmPackageFolder -NpmExe $npmExe -PackageName $pkgName
    $useLocalFolder = $false
    $tarballVersion = $version
    $pj = if ($globalFolder) { Join-Path $globalFolder "package.json" } else { $null }
    if ($globalFolder -and $pj -and (Test-Path -LiteralPath $pj)) {
        $diskVer = Get-PackageJsonVersion -PackageFolder $globalFolder
        if (-not $entry.VersionFromConfig) {
            if ($diskVer) {
                $useLocalFolder = $true
                $tarballVersion = $diskVer
            }
        }
        elseif ($diskVer -and ($diskVer -eq $version)) {
            $useLocalFolder = $true
            $tarballVersion = $diskVer
        }
    }

    $expected = Join-Path $depsNpm ("{0}-{1}.tgz" -f $normName, $tarballVersion)

    if ((-not $Force) -and (Test-Path -LiteralPath $expected)) {
        Write-Host ("  - Skip (exists): {0}" -f $expected) -ForegroundColor DarkGray
        continue
    }

    if ($useLocalFolder) {
        Write-Host ("  - npm pack (from global install folder, no registry) {0}" -f $globalFolder) -ForegroundColor DarkGray
        & $npmExe "pack" $globalFolder "--pack-destination" $depsNpm
        if ($LASTEXITCODE -ne 0) {
            throw ("npm pack failed for folder '{0}' (exit {1})" -f $globalFolder, $LASTEXITCODE)
        }
    }
    else {
        Write-Host ("  - npm pack {0} (registry)" -f $packSpec) -ForegroundColor DarkGray
        $ok = Invoke-NpmPackWithNetworkRetries -NpmExe $npmExe -PackArgs @("pack", $packSpec, "--pack-destination", $depsNpm)
        if (-not $ok) {
            throw ("npm pack failed for '{0}' after retries" -f $packSpec)
        }
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
