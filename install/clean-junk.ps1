<#
.SYNOPSIS
    Remove common Python/tool junk under repository root (recursive).
.DESCRIPTION
    Deletes __pycache__, *.pyc / *.pyo, and typical cache folders (.pytest_cache,
    .ruff_cache, .mypy_cache, .hypothesis). Skips anything under .git.
.PARAMETER RepoRoot
    Root folder to clean. Default: parent of install\ (repository root).
#>
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

try {
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

    # macOS metadata files sometimes copied onto Windows shares
    $ds = @(Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -Force -Filter ".DS_Store" -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch $gitRegex })
    foreach ($f in $ds) {
        Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
        $removedFiles++
        Write-Host ("    Removed file: {0}" -f $f.FullName) -ForegroundColor DarkGray
    }
}
catch {
    Write-Host ("ERROR: {0}" -f $_.Exception.Message) -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host ("Done. Removed {0} dirs, {1} files." -f $removedDirs, $removedFiles) -ForegroundColor Green
