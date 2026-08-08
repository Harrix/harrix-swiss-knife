#Requires -Version 5.1
# Pack api-keys secrets and fitness_img into one personal ZIP (not for public install bundles).
[CmdletBinding()]
param(
    [string] $OutputZip = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression.FileSystem

$installDir = $PSScriptRoot
$repoRoot = Split-Path -Parent $installDir

if ([string]::IsNullOrWhiteSpace($OutputZip)) {
    $OutputZip = Join-Path $installDir "private-data-harrix-swiss-knife.zip"
}
else {
    $OutputZip = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputZip)
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

Write-Host ""
Write-Host "Pack private data (api-keys + fitness_img)" -ForegroundColor Cyan
Write-Host ("  Repo: {0}" -f $repoRoot) -ForegroundColor DarkGray
Write-Host ("  Out:  {0}" -f $OutputZip) -ForegroundColor DarkGray
Write-Host ""

$apiKeysDir = Join-Path $repoRoot "api-keys"
if (-not (Test-Path -LiteralPath $apiKeysDir)) {
    throw ("api-keys folder not found: {0}" -f $apiKeysDir)
}

$keyFiles = @(
    Get-ChildItem -LiteralPath $apiKeysDir -File -Filter "*.txt" -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notlike "*.example.txt" }
)
if ($keyFiles.Count -eq 0) {
    throw ("No secret *.txt files found in {0} (excluding *.example.txt)." -f $apiKeysDir)
}

$configPath = Join-Path $repoRoot "config\config.json"
$sqliteFitness = Get-JsonStringProperty -Path $configPath -PropertyName "sqlite_fitness"
if (Test-PlaceholderPath $sqliteFitness) {
    throw @(
        "config\config.json must set a real sqlite_fitness path (not a <YOUR_...> placeholder).",
        ("  Config: {0}" -f $configPath),
        "  Fitness images are expected at {parent(sqlite_fitness)}\fitness_img"
    ) -join [Environment]::NewLine
}

$fitnessImgDir = Join-Path (Split-Path -Parent $sqliteFitness) "fitness_img"
if (-not (Test-Path -LiteralPath $fitnessImgDir -PathType Container)) {
    throw ("fitness_img folder not found: {0}" -f $fitnessImgDir)
}

$fitnessFiles = @(Get-ChildItem -LiteralPath $fitnessImgDir -File -Recurse -Force -ErrorAction SilentlyContinue)
if ($fitnessFiles.Count -eq 0) {
    throw ("fitness_img folder is empty: {0}" -f $fitnessImgDir)
}

$stageBase = Join-Path $env:TEMP ("hsk-private-data-" + [guid]::NewGuid().ToString("N"))
$stageRoot = Join-Path $stageBase "root"

try {
    New-Item -ItemType Directory -Path $stageRoot -Force | Out-Null

    $stageApiKeys = Join-Path $stageRoot "api-keys"
    New-Item -ItemType Directory -Path $stageApiKeys -Force | Out-Null
    foreach ($f in $keyFiles) {
        Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $stageApiKeys $f.Name) -Force
        Write-Host ("  + api-keys\{0}" -f $f.Name) -ForegroundColor DarkGray
    }

    $stageFitness = Join-Path $stageRoot "fitness_img"
    New-Item -ItemType Directory -Path $stageFitness -Force | Out-Null
    foreach ($f in $fitnessFiles) {
        $rel = $f.FullName.Substring($fitnessImgDir.Length).TrimStart("\", "/")
        $target = Join-Path $stageFitness $rel
        $targetParent = Split-Path -Parent $target
        if (-not (Test-Path -LiteralPath $targetParent)) {
            New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
        }
        Copy-Item -LiteralPath $f.FullName -Destination $target -Force
    }
    Write-Host ("  + fitness_img\ ({0} file(s) from {1})" -f $fitnessFiles.Count, $fitnessImgDir) -ForegroundColor DarkGray

    $manifest = [ordered]@{
        created_utc         = [DateTime]::UtcNow.ToString("o")
        source_machine      = $env:COMPUTERNAME
        fitness_img_source  = $fitnessImgDir
        api_keys_count      = $keyFiles.Count
        fitness_img_count   = $fitnessFiles.Count
        api_key_files       = @($keyFiles | ForEach-Object { $_.Name })
    }
    $manifestPath = Join-Path $stageRoot "manifest.json"
    $manifestJson = ($manifest | ConvertTo-Json -Depth 5)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($manifestPath, $manifestJson, $utf8NoBom)

    $outParent = Split-Path -Parent $OutputZip
    if (-not [string]::IsNullOrWhiteSpace($outParent) -and -not (Test-Path -LiteralPath $outParent)) {
        New-Item -ItemType Directory -Path $outParent -Force | Out-Null
    }
    if (Test-Path -LiteralPath $OutputZip) {
        Remove-Item -LiteralPath $OutputZip -Force
    }

    [System.IO.Compression.ZipFile]::CreateFromDirectory(
        $stageRoot,
        $OutputZip,
        [System.IO.Compression.CompressionLevel]::Optimal,
        $false
    )
    if (-not (Test-Path -LiteralPath $OutputZip)) {
        throw ("Zip was not created: {0}" -f $OutputZip)
    }

    $zipInfo = Get-Item -LiteralPath $OutputZip
    Write-Host ""
    Write-Host ("Done. Packed {0} api-key file(s) and {1} fitness_img file(s)." -f $keyFiles.Count, $fitnessFiles.Count) -ForegroundColor Green
    Write-Host ("  ZIP:  {0}" -f $zipInfo.FullName) -ForegroundColor Green
    Write-Host ("  Size: {0:N1} MB" -f ($zipInfo.Length / 1MB)) -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $stageBase) {
        Remove-Item -LiteralPath $stageBase -Recurse -Force -ErrorAction SilentlyContinue
    }
}
