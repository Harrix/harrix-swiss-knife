#Requires -Version 5.1
# Install api-keys secrets and fitness_img from a personal private-data ZIP.
[CmdletBinding()]
param(
    [string] $ZipPath = "",
    [string] $FitnessImgDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression.FileSystem

$installDir = $PSScriptRoot
$repoRoot = Split-Path -Parent $installDir

if ([string]::IsNullOrWhiteSpace($ZipPath)) {
    $ZipPath = Join-Path $installDir "private-data-harrix-swiss-knife.zip"
}
else {
    $ZipPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ZipPath)
}

function Get-JsonStringProperty {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,
        [Parameter(Mandatory = $true)]
        [string] $PropertyName
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    try {
        $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 -ErrorAction Stop
        $obj = $raw | ConvertFrom-Json -ErrorAction Stop
        if ($null -eq $obj.PSObject.Properties[$PropertyName]) {
            return $null
        }
        $val = $obj.$PropertyName
        if ($null -eq $val) {
            return $null
        }
        return [string]$val
    }
    catch {
        throw ("Could not read JSON property '{0}' from '{1}': {2}" -f $PropertyName, $Path, $_.Exception.Message)
    }
}

function Test-PlaceholderPath([string] $Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $true
    }
    return ($Value -match '<YOUR_')
}

function Resolve-FitnessImgDestination {
    [CmdletBinding()]
    param(
        [string] $ExplicitDir,
        [string] $RepoRoot
    )

    if (-not [string]::IsNullOrWhiteSpace($ExplicitDir)) {
        return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ExplicitDir)
    }

    $configPath = Join-Path $RepoRoot "config\config.json"
    if (-not (Test-Path -LiteralPath $configPath)) {
        throw @(
            "config\config.json not found. Set sqlite_fitness there, or pass -FitnessImgDir.",
            ("  Expected: {0}" -f $configPath)
        ) -join [Environment]::NewLine
    }

    $sqliteFitness = Get-JsonStringProperty -Path $configPath -PropertyName "sqlite_fitness"
    if (Test-PlaceholderPath $sqliteFitness) {
        throw @(
            "config\config.json must set a real sqlite_fitness path (not a <YOUR_...> placeholder),",
            "or pass -FitnessImgDir to choose the fitness_img destination.",
            ("  Config: {0}" -f $configPath),
            "  Images go to {parent(sqlite_fitness)}\fitness_img"
        ) -join [Environment]::NewLine
    }

    $parent = Split-Path -Parent $sqliteFitness
    if ([string]::IsNullOrWhiteSpace($parent)) {
        throw ("sqlite_fitness has no parent directory: {0}" -f $sqliteFitness)
    }

    return (Join-Path $parent "fitness_img")
}

Write-Host ""
Write-Host "Install private data (api-keys + fitness_img)" -ForegroundColor Cyan
Write-Host ("  Repo: {0}" -f $repoRoot) -ForegroundColor DarkGray
Write-Host ("  Zip:  {0}" -f $ZipPath) -ForegroundColor DarkGray
Write-Host ""

if (-not (Test-Path -LiteralPath $ZipPath -PathType Leaf)) {
    throw ("ZIP not found: {0}" -f $ZipPath)
}

$destFitnessImg = Resolve-FitnessImgDestination -ExplicitDir $FitnessImgDir -RepoRoot $repoRoot
$destApiKeys = Join-Path $repoRoot "api-keys"

Write-Host ("  api-keys -> {0}" -f $destApiKeys) -ForegroundColor DarkGray
Write-Host ("  fitness_img -> {0}" -f $destFitnessImg) -ForegroundColor DarkGray
Write-Host ""

$stageBase = Join-Path $env:TEMP ("hsk-private-data-install-" + [guid]::NewGuid().ToString("N"))

try {
    New-Item -ItemType Directory -Path $stageBase -Force | Out-Null
    [System.IO.Compression.ZipFile]::ExtractToDirectory($ZipPath, $stageBase)

    $stageApiKeys = Join-Path $stageBase "api-keys"
    $stageFitness = Join-Path $stageBase "fitness_img"
    $manifestPath = Join-Path $stageBase "manifest.json"

    if (-not (Test-Path -LiteralPath $stageApiKeys -PathType Container)) {
        throw ("ZIP is missing api-keys\: {0}" -f $ZipPath)
    }
    if (-not (Test-Path -LiteralPath $stageFitness -PathType Container)) {
        throw ("ZIP is missing fitness_img\: {0}" -f $ZipPath)
    }

    if (Test-Path -LiteralPath $manifestPath) {
        try {
            $manifest = (Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8) | ConvertFrom-Json
            Write-Host "  Manifest:" -ForegroundColor DarkGray
            if ($manifest.created_utc) { Write-Host ("    created_utc: {0}" -f $manifest.created_utc) -ForegroundColor DarkGray }
            if ($manifest.source_machine) { Write-Host ("    source_machine: {0}" -f $manifest.source_machine) -ForegroundColor DarkGray }
            if ($manifest.fitness_img_source) { Write-Host ("    fitness_img_source: {0}" -f $manifest.fitness_img_source) -ForegroundColor DarkGray }
            if ($null -ne $manifest.api_keys_count) { Write-Host ("    api_keys_count: {0}" -f $manifest.api_keys_count) -ForegroundColor DarkGray }
            if ($null -ne $manifest.fitness_img_count) { Write-Host ("    fitness_img_count: {0}" -f $manifest.fitness_img_count) -ForegroundColor DarkGray }
            Write-Host ""
        }
        catch {
            Write-Warning ("Could not parse manifest.json: {0}" -f $_.Exception.Message)
        }
    }

    if (-not (Test-Path -LiteralPath $destApiKeys)) {
        New-Item -ItemType Directory -Path $destApiKeys -Force | Out-Null
    }

    $keyFiles = @(Get-ChildItem -LiteralPath $stageApiKeys -File -Filter "*.txt" -Force -ErrorAction SilentlyContinue)
    if ($keyFiles.Count -eq 0) {
        throw ("ZIP api-keys\ has no *.txt files: {0}" -f $ZipPath)
    }
    foreach ($f in $keyFiles) {
        Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $destApiKeys $f.Name) -Force
        Write-Host ("  -> api-keys\{0}" -f $f.Name) -ForegroundColor DarkGray
    }

    if (-not (Test-Path -LiteralPath $destFitnessImg)) {
        New-Item -ItemType Directory -Path $destFitnessImg -Force | Out-Null
    }

    $fitnessFiles = @(Get-ChildItem -LiteralPath $stageFitness -File -Recurse -Force -ErrorAction SilentlyContinue)
    if ($fitnessFiles.Count -eq 0) {
        throw ("ZIP fitness_img\ is empty: {0}" -f $ZipPath)
    }

    # Copy files over existing ones; do not delete extras already on the target machine.
    $fitnessCopied = 0
    foreach ($f in $fitnessFiles) {
        $rel = $f.FullName.Substring($stageFitness.Length).TrimStart("\", "/")
        $target = Join-Path $destFitnessImg $rel
        $targetParent = Split-Path -Parent $target
        if (-not (Test-Path -LiteralPath $targetParent)) {
            New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
        }
        Copy-Item -LiteralPath $f.FullName -Destination $target -Force
        $fitnessCopied++
    }
    Write-Host ("  -> fitness_img\ ({0} file(s))" -f $fitnessCopied) -ForegroundColor DarkGray

    Write-Host ""
    Write-Host ("Done. Installed {0} api-key file(s) and {1} fitness_img file(s)." -f $keyFiles.Count, $fitnessCopied) -ForegroundColor Green
    Write-Host ("  api-keys:    {0}" -f $destApiKeys) -ForegroundColor Green
    Write-Host ("  fitness_img: {0}" -f $destFitnessImg) -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $stageBase) {
        Remove-Item -LiteralPath $stageBase -Recurse -Force -ErrorAction SilentlyContinue
    }
}
