#Requires -Version 5.1
# Remove Python/tool junk under repo root; remove *.log in install\ and install\dependencies\.
[CmdletBinding()]
param(
    [string] $RepoRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}
else {
    $RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
}

$gitRegex = '(\\|/)\.git(\\|/|$)'
$junkDirNames = @(
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".hypothesis",
    "htmlcov"
)

Write-Host ""
Write-Host ("Repo root: {0}" -f $RepoRoot) -ForegroundColor Green

$removedDirs = 0
$removedFiles = 0

$dirs = @(Get-ChildItem -LiteralPath $RepoRoot -Recurse -Directory -Force -ErrorAction SilentlyContinue |
        Where-Object { ($junkDirNames -contains $_.Name) -and ($_.FullName -notmatch $gitRegex) } |
        Sort-Object { $_.FullName.Length } -Descending)

foreach ($d in $dirs) {
    Remove-Item -LiteralPath $d.FullName -Recurse -Force -ErrorAction Stop
    $removedDirs++
    Write-Host ("    Removed dir:  {0}" -f $d.FullName) -ForegroundColor DarkGray
}

$files = @(Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object {
            ($_.Extension -in @(".pyc", ".pyo")) -and ($_.FullName -notmatch $gitRegex)
        })

foreach ($f in $files) {
    Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
    $removedFiles++
    Write-Host ("    Removed file: {0}" -f $f.FullName) -ForegroundColor DarkGray
}

$ds = @(Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -Force -Filter ".DS_Store" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch $gitRegex })
foreach ($f in $ds) {
    Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
    $removedFiles++
    Write-Host ("    Removed file: {0}" -f $f.FullName) -ForegroundColor DarkGray
}

$installDir = $PSScriptRoot
foreach ($logRoot in @($installDir, (Join-Path $installDir "dependencies"))) {
    if (-not (Test-Path -LiteralPath $logRoot)) { continue }
    foreach ($log in @(Get-ChildItem -LiteralPath $logRoot -File -Filter "*.log" -Force -ErrorAction SilentlyContinue)) {
        Remove-Item -LiteralPath $log.FullName -Force -ErrorAction Stop
        $removedFiles++
        Write-Host ("    Removed file: {0}" -f $log.FullName) -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host ("Done. Removed {0} dirs, {1} files." -f $removedDirs, $removedFiles) -ForegroundColor Green
