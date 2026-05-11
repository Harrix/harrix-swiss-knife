#Requires -Version 5.1
# Build online/offline distributable zip archives (moved from 05_build-install-zips.bat).
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression.FileSystem

Set-Location -LiteralPath $PSScriptRoot

$root = (Resolve-Path -LiteralPath (Get-Location)).Path
$deps = Join-Path $root "dependencies"
$outOnline = Join-Path $root "install-harrix-swiss-knife.zip"
$outOffline = Join-Path $root "install-offline-harrix-swiss-knife.zip"

Write-Host ""
Write-Host "Building:" -ForegroundColor Cyan
Write-Host ("  {0}" -f $outOnline) -ForegroundColor DarkGray
Write-Host ("  {0}" -f $outOffline) -ForegroundColor DarkGray
Write-Host ""

function New-CleanDir([string] $p) {
    if (Test-Path -LiteralPath $p) {
        Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Path $p -Force | Out-Null
}

function Copy-IfExists([string] $src, [string] $dstDir) {
    if (Test-Path -LiteralPath $src) {
        Copy-Item -LiteralPath $src -Destination (Join-Path $dstDir (Split-Path -Leaf $src)) -Force
    }
    else {
        throw ("Not found: " + $src)
    }
}

function Get-RedundantMediaZipNames([string] $depsDir) {
    # When loose tools are already in dependencies, omit matching fallback zips from distributables (saves space).
    $names = [System.Collections.Generic.List[string]]::new()
    if (-not (Test-Path -LiteralPath $depsDir)) {
        return @()
    }
    if ((Test-Path -LiteralPath (Join-Path $depsDir "avifenc.exe")) -and (Test-Path -LiteralPath (Join-Path $depsDir "avifdec.exe"))) {
        if (Test-Path -LiteralPath (Join-Path $depsDir "windows-artifacts.zip")) {
            $names.Add("windows-artifacts.zip") | Out-Null
        }
    }
    if (Test-Path -LiteralPath (Join-Path $depsDir "ffmpeg.exe")) {
        $ffZip = Join-Path $depsDir "ffmpeg-master-latest-win64-gpl.zip"
        if (Test-Path -LiteralPath $ffZip) {
            $names.Add("ffmpeg-master-latest-win64-gpl.zip") | Out-Null
        }
    }
    return [string[]]$names.ToArray()
}

function Copy-Deps([string] $srcDeps, [string] $dstDeps, [string[]] $excludeDirs, [string[]] $excludeFiles) {
    if (-not (Test-Path -LiteralPath $srcDeps)) {
        throw ("Not found: " + $srcDeps)
    }
    New-Item -ItemType Directory -Path $dstDeps -Force | Out-Null

    Get-ChildItem -LiteralPath $srcDeps -Force | ForEach-Object {
        if ($_.PSIsContainer) {
            if ($excludeDirs -contains $_.Name) { return }
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dstDeps $_.Name) -Recurse -Force
        }
        else {
            if ($_.Name -like "*.log") { return }
            if ($excludeFiles -and ($excludeFiles -contains $_.Name)) { return }
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dstDeps $_.Name) -Force
        }
    }
}

function Zip-Dir([string] $dir, [string] $zip) {
    if (Test-Path -LiteralPath $zip) {
        Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue
    }
    [System.IO.Compression.ZipFile]::CreateFromDirectory(
        $dir,
        $zip,
        [System.IO.Compression.CompressionLevel]::Optimal,
        $false
    )
    if (-not (Test-Path -LiteralPath $zip)) {
        throw ("Zip was not created: " + $zip)
    }
}

$stageBase = Join-Path $env:TEMP ("hsk-install-zip-" + [guid]::NewGuid().ToString("N"))
$stageOnline = Join-Path $stageBase "online"
$stageOffline = Join-Path $stageBase "offline"

try {
    New-CleanDir $stageOnline
    New-CleanDir $stageOffline

    $omitZips = @(Get-RedundantMediaZipNames $deps)

    Copy-IfExists (Join-Path $root "harrix-swiss-knife.ps1") $stageOnline
    Copy-IfExists (Join-Path $root "install.bat") $stageOnline
    Copy-IfExists (Join-Path $root "install-with-log.ps1") $stageOnline
    Copy-Deps $deps (Join-Path $stageOnline "dependencies") @("repos", "uv-cache") $omitZips
    Zip-Dir $stageOnline $outOnline

    Copy-IfExists (Join-Path $root "harrix-swiss-knife.ps1") $stageOffline
    Copy-IfExists (Join-Path $root "install-all-offline.bat") $stageOffline
    Copy-IfExists (Join-Path $root "install-all-offline-with-log.ps1") $stageOffline
    $offlineFileExcludes = @("ffmpeg.exe", "avifenc.exe", "avifdec.exe") + $omitZips
    Copy-Deps $deps (Join-Path $stageOffline "dependencies") @() $offlineFileExcludes
    Zip-Dir $stageOffline $outOffline

    Write-Host ("Created: {0}" -f $outOnline) -ForegroundColor Green
    Write-Host ("Created: {0}" -f $outOffline) -ForegroundColor Green
    Write-Host "OK" -ForegroundColor Green
}
finally {
    Remove-Item -LiteralPath $stageBase -Recurse -Force -ErrorAction SilentlyContinue
}
