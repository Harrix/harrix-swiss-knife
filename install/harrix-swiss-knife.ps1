#Requires -Version 5.1
<#
.SYNOPSIS
    Deploy harrix-swiss-knife and dependencies on a fresh Windows machine.

.DESCRIPTION
    Installs prerequisites (winget), clones sibling repos under InstallRoot,
    runs uv sync, npm, downloads ffmpeg/avif tools, uv tool install -e, and
    optional Notes Explorer symlinks.

.PARAMETER InstallRoot
    Parent folder for harrix-pylib, harrix-pyssg, harrix-swiss-knife (siblings).
    If omitted, uses the repo parent when run from a clone; otherwise picks automatically:
    D:\GitHub, C:\GitHub, Documents\GitHub (GitHub Desktop default), or creates %USERPROFILE%\harrix-swiss-knife.

.PARAMETER SkipPrerequisites
    Skip winget installs for Git, Python, Node.js, uv.

.PARAMETER SkipBinaries
    Skip downloading ffmpeg.exe, avifenc.exe, avifdec.exe.

.PARAMETER SkipExtensionSymlinks
    Skip Notes Explorer symlink creation.

.PARAMETER Force
    Re-download binaries even if they already exist in project root. Alias: -ForceBinaries.

.PARAMETER NoPauseOnError
    Do not wait for Enter before exiting after an error (for automation).
#>
[CmdletBinding()]
param(
    [Parameter()]
    [ValidateScript({
        if ($null -eq $_) { return $true }
        if ([string]::IsNullOrWhiteSpace($_)) {
            throw "InstallRoot cannot be empty or whitespace when specified."
        }
        return $true
    })]
    [string] $InstallRoot,
    [switch] $SkipPrerequisites,
    [switch] $SkipBinaries,
    [switch] $SkipExtensionSymlinks,
    [Alias("ForceBinaries")]
    [switch] $Force,
    [switch] $NoPauseOnError
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# GitHub API and Invoke-WebRequest on older Windows PowerShell
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
}
catch { }

$GitHubUa = "Harrix-Swiss-Knife-Deploy/1.0 (PowerShell)"
$script:DeployStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

$script:Already = New-Object System.Collections.Generic.List[string]
$script:Skipped = New-Object System.Collections.Generic.List[string]
$script:Installed = New-Object System.Collections.Generic.List[string]

function Add-Outcome {
    param(
        [ValidateSet("already", "skipped", "installed")]
        [string] $Category,
        [string] $Message
    )
    if ([string]::IsNullOrWhiteSpace($Message)) {
        return
    }
    switch ($Category) {
        "already" { $script:Already.Add($Message) | Out-Null }
        "skipped" { $script:Skipped.Add($Message) | Out-Null }
        "installed" { $script:Installed.Add($Message) | Out-Null }
    }
}

function Set-JsonBoolProperty {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,
        [Parameter(Mandatory = $true)]
        [string] $PropertyName,
        [Parameter(Mandatory = $true)]
        [bool] $Value
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return $false
    }
    try {
        $raw = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
        $obj = $raw | ConvertFrom-Json -ErrorAction Stop
        if ($null -eq $obj.PSObject.Properties[$PropertyName]) {
            return $false
        }
        $obj.$PropertyName = $Value
        $json = $obj | ConvertTo-Json -Depth 30
        # Keep UTF-8 for non-ASCII paths.
        $json | Set-Content -LiteralPath $Path -Encoding utf8 -ErrorAction Stop
        return $true
    }
    catch {
        Write-Warning "Could not update JSON '$Path': $($_.Exception.Message)"
        return $false
    }
}

function Write-Step {
    param([string] $Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Format-Elapsed {
    param([TimeSpan] $Elapsed)
    $parts = @()
    if ($Elapsed.Days -gt 0) { $parts += ("{0}d" -f $Elapsed.Days) }
    if ($Elapsed.Hours -gt 0) { $parts += ("{0}h" -f $Elapsed.Hours) }
    if ($Elapsed.Minutes -gt 0) { $parts += ("{0}m" -f $Elapsed.Minutes) }
    $parts += ("{0}s" -f [math]::Floor($Elapsed.TotalSeconds % 60))
    return ($parts -join " ")
}

function Write-ElapsedSummary {
    if ($null -eq $script:DeployStopwatch) {
        return
    }
    if ($script:DeployStopwatch.IsRunning) {
        $script:DeployStopwatch.Stop()
    }
    $elapsed = $script:DeployStopwatch.Elapsed
    Write-Host ""
    Write-Host ("Total time: {0}" -f (Format-Elapsed -Elapsed $elapsed)) -ForegroundColor Green
}

function Update-PathFromEnvironment {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

function Test-CommandExists {
    param([string] $Name)
    return [bool](Get-Command -Name $Name -ErrorAction SilentlyContinue)
}

function Test-AnyCodeEditorExists {
    <#
    .NOTES
        Detect a GUI editor (Cursor / VS Code / VS Code Insiders).
        We try command existence first; then typical install locations.
    #>
    if (Test-CommandExists "cursor") { return $true }
    if (Test-CommandExists "code") { return $true }
    if (Test-CommandExists "code-insiders") { return $true }

    $candidates = @(
        (Join-Path $env:LOCALAPPDATA "Programs\cursor\Cursor.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Microsoft VS Code\Code.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Microsoft VS Code Insiders\Code - Insiders.exe"),
        (Join-Path $env:ProgramFiles "Microsoft VS Code\Code.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Microsoft VS Code\Code.exe")
    )
    foreach ($p in $candidates) {
        if ($p -and (Test-Path -LiteralPath $p)) {
            return $true
        }
    }
    return $false
}

function Get-NpmExecutable {
    <#
    .NOTES
        In Windows PowerShell, `npm` may resolve to npm.ps1. Default ExecutionPolicy often blocks
        .ps1, so `npm` fails with PSSecurityException. npm.cmd is not a script and always runs.
    #>
    $cmd = Get-Command -Name "npm.cmd" -CommandType Application -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) {
        return $cmd.Source
    }
    $npm = Get-Command -Name "npm" -ErrorAction SilentlyContinue
    if ($npm -and $npm.CommandType -eq "Application" -and $npm.Source) {
        return $npm.Source
    }
    return $null
}

function Get-DependenciesDir {
    # install\harrix-swiss-knife.ps1 -> install\dependencies
    return (Join-Path $PSScriptRoot "dependencies")
}

function Get-LocalDependency {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string] $Pattern
    )
    $deps = Get-DependenciesDir
    if (-not (Test-Path -LiteralPath $deps)) {
        return $null
    }
    $foundItems = @(Get-ChildItem -LiteralPath $deps -Filter $Pattern -File -ErrorAction SilentlyContinue)
    if ($foundItems.Count -eq 1) {
        return $foundItems[0].FullName
    }
    if ($foundItems.Count -gt 1) {
        Write-Warning "Multiple matches for $Pattern in $deps; using the newest by LastWriteTime."
        return ($foundItems | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
    }
    return $null
}

function Install-LocalSetup {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,
        [string[]] $InstallerArgs = @()
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Installer not found: $Path"
    }
    $ext = [IO.Path]::GetExtension($Path).ToLowerInvariant()
    if ($ext -eq ".msi") {
        $msiArgs = @("/i", $Path, "/qn", "/norestart") + $InstallerArgs
        $p = Start-Process -FilePath "msiexec.exe" -ArgumentList $msiArgs -Wait -PassThru
        return ($p.ExitCode -eq 0)
    }
    elseif ($ext -eq ".exe") {
        $p = Start-Process -FilePath $Path -ArgumentList $InstallerArgs -Wait -PassThru
        return ($p.ExitCode -eq 0)
    }
    else {
        throw "Unsupported installer extension: $ext ($Path)"
    }
}

function Invoke-NpmWithRetries {
    <#
    .NOTES
        Slow or unstable links to registry.npmjs.org can raise EIDLETIMEOUT (idle socket / no data).
        We set high fetch timeouts and both env + CLI flags so npm honors limits on all versions.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $NpmArgs,

        [int] $MaxAttempts = 5,
        [int] $SleepSeconds = 20,

        # See: https://docs.npmjs.com/cli/v10/using-npm/config#fetch-timeout
        [int] $FetchTimeoutMs = 600000,
        [int] $FetchRetries = 8,
        [int] $FetchRetryMinTimeoutMs = 20000,
        [int] $FetchRetryMaxTimeoutMs = 180000
    )

    $npmExe = Get-NpmExecutable
    if (-not $npmExe) {
        throw "npm is not available on PATH (looked for npm.cmd / npm)."
    }

    $prev = [ordered]@{
        npm_config_fetch_timeout           = $env:npm_config_fetch_timeout
        npm_config_fetch_retries           = $env:npm_config_fetch_retries
        npm_config_fetch_retry_mintimeout  = $env:npm_config_fetch_retry_mintimeout
        npm_config_fetch_retry_maxtimeout  = $env:npm_config_fetch_retry_maxtimeout
        npm_config_fund                    = $env:npm_config_fund
        npm_config_audit                   = $env:npm_config_audit
    }

    try {
        # Make npm more tolerant on slow/unstable networks (process-local via env vars).
        $env:npm_config_fetch_timeout = "$FetchTimeoutMs"
        $env:npm_config_fetch_retries = "$FetchRetries"
        $env:npm_config_fetch_retry_mintimeout = "$FetchRetryMinTimeoutMs"
        $env:npm_config_fetch_retry_maxtimeout = "$FetchRetryMaxTimeoutMs"
        # Reduce extra network calls; deploy should not depend on audit/fund checks.
        $env:npm_config_fund = "false"
        $env:npm_config_audit = "false"

        $cliFlags = @(
            "--fetch-timeout=$FetchTimeoutMs",
            "--fetch-retries=$FetchRetries",
            "--fetch-retry-mintimeout=$FetchRetryMinTimeoutMs",
            "--fetch-retry-maxtimeout=$FetchRetryMaxTimeoutMs"
        )
        $fullArgs = $cliFlags + $NpmArgs

        for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
            $joined = ($fullArgs -join " ")
            Write-Host "    & `"$npmExe`" $joined (attempt $attempt/$MaxAttempts)" -ForegroundColor DarkGray

            & $npmExe @fullArgs
            $code = $LASTEXITCODE
            if ($code -eq 0) {
                return $true
            }

            if ($attempt -lt $MaxAttempts) {
                Write-Host "    npm failed (exit $code). Retrying in $SleepSeconds s..." -ForegroundColor Yellow
                Start-Sleep -Seconds $SleepSeconds
            }
            else {
                Write-Host "    npm failed (exit $code). Giving up." -ForegroundColor Yellow
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

function Invoke-DeployPauseBeforeExit {
    if ($NoPauseOnError -or $env:CI -eq "true") {
        return
    }
    if ($Host.Name -eq "ConsoleHost" -and [Environment]::UserInteractive) {
        Write-Host ""
        Read-Host "Press Enter to close this window"
    }
}

function Get-WingetExePath {
    Update-PathFromEnvironment
    $cmd = Get-Command -Name "winget" -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) {
        return $cmd.Source
    }
    $pf86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
    $candidates = @( (Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\winget.exe") )
    if ($pf86) {
        $candidates += (Join-Path $pf86 "Microsoft\WindowsApps\winget.exe")
    }
    foreach ($c in $candidates) {
        if ($c -and (Test-Path -LiteralPath $c)) {
            return $c
        }
    }
    try {
        $whereLine = & where.exe winget 2>$null | Select-Object -First 1
        if ($whereLine) {
            return $whereLine.Trim()
        }
    }
    catch {
        # where.exe missing on some minimal Windows images
    }
    return $null
}

function Get-InstallRootFromClonedHsk {
    $repoRoot = Split-Path -Parent $PSScriptRoot
    $pp = Join-Path $repoRoot "pyproject.toml"
    if (-not (Test-Path -LiteralPath $pp)) {
        return $null
    }
    $head = Get-Content -LiteralPath $pp -TotalCount 30 -ErrorAction SilentlyContinue
    if (-not ($head -match 'name\s*=\s*"harrix-swiss-knife"')) {
        return $null
    }
    return (Split-Path -Parent $repoRoot)
}

function Get-AutomaticInstallRootParent {
    <#
    .NOTES
        Prefer existing Git locations: D:\GitHub, C:\GitHub, then Documents\GitHub (GitHub Desktop default on Windows).
        If none exist, create %USERPROFILE%\harrix-swiss-knife (writable without elevation).
    #>
    $candidates = @(
        "D:\GitHub",
        "C:\GitHub",
        (Join-Path ([Environment]::GetFolderPath("MyDocuments")) "GitHub")
    )
    foreach ($dir in $candidates) {
        if (-not $dir) { continue }
        if (Test-Path -LiteralPath $dir) {
            try {
                $item = Get-Item -LiteralPath $dir -ErrorAction Stop
                if ($item.PSIsContainer) {
                    return $item.FullName
                }
            }
            catch {
                continue
            }
        }
    }

    $bundle = Join-Path $env:USERPROFILE "harrix-swiss-knife"
    if (-not (Test-Path -LiteralPath $bundle)) {
        Write-Host "    No GitHub folder found; creating install folder: $bundle" -ForegroundColor DarkGray
        try {
            New-Item -ItemType Directory -Path $bundle -Force -ErrorAction Stop | Out-Null
        }
        catch {
            throw "Could not create $bundle. Pass -InstallRoot to use another parent folder."
        }
    }
    return (Resolve-Path -LiteralPath $bundle).Path
}

function Initialize-GitHubRoot {
    param([string] $SelectedPath)

    $p = $SelectedPath.Trim().TrimEnd("\").TrimEnd("/")
    if ([string]::IsNullOrWhiteSpace($p)) {
        throw "Selected install path is empty."
    }

    $leaf = Split-Path -Leaf $p
    # Explicit -InstallRoot: allow ...\GitHub, or a dedicated ...\harrix-swiss-knife parent (user profile or Program Files).
    $underPf = $p.StartsWith($env:ProgramFiles, [System.StringComparison]::OrdinalIgnoreCase)
    $underUser = $p.StartsWith($env:USERPROFILE, [System.StringComparison]::OrdinalIgnoreCase)
    if ($leaf -ieq "GitHub" -or ($leaf -ieq "harrix-swiss-knife" -and ($underPf -or $underUser))) {
        return $p
    }

    # Legacy: other folders get a GitHub subfolder for sibling clones
    $gh = Join-Path $p "GitHub"
    if (-not (Test-Path -LiteralPath $gh)) {
        Write-Host "    Creating folder: $gh" -ForegroundColor DarkGray
        New-Item -ItemType Directory -Path $gh -Force | Out-Null
    }
    return $gh
}

function Update-GitRepoIfPossible {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string] $RepoPath,
        [Parameter(Mandatory = $true)]
        [string] $Label
    )

    if (-not (Test-CommandExists "git")) {
        Write-Warning "    git not available; cannot update $Label"
        Add-Outcome -Category "skipped" -Message "$Label not updated (git not available)"
        return
    }
    if (-not (Test-Path -LiteralPath $RepoPath)) {
        return
    }
    $gitDir = Join-Path $RepoPath ".git"
    if (-not (Test-Path -LiteralPath $gitDir)) {
        Write-Warning "    $Label exists but is not a git repository: $RepoPath"
        Add-Outcome -Category "skipped" -Message "$Label not updated (no .git folder)"
        return
    }

    Write-Host "    Updating $Label..." -ForegroundColor DarkGray
    Push-Location $RepoPath
    try {
        # If there are local changes, do not auto-pull to avoid conflicts.
        $status = (& git status --porcelain 2>$null) | Out-String
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "    git status failed in $Label; skip update"
            Add-Outcome -Category "skipped" -Message "$Label not updated (git status failed)"
            return
        }
        if (-not [string]::IsNullOrWhiteSpace($status)) {
            Write-Warning "    $Label has local changes; skip git pull"
            Add-Outcome -Category "skipped" -Message "$Label not updated (local changes present)"
            return
        }

        & git fetch --prune
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "    git fetch failed in $Label; skip pull"
            Add-Outcome -Category "skipped" -Message "$Label not updated (git fetch failed)"
            return
        }
        & git pull --ff-only
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "    git pull --ff-only failed in $Label; skip"
            Add-Outcome -Category "skipped" -Message "$Label not updated (git pull failed)"
            return
        }
        Add-Outcome -Category "installed" -Message "Updated $Label (git pull)"
    }
    finally {
        Pop-Location
    }
}

function Invoke-WingetInstall {
    param([string] $PackageId)

    if (-not $script:WingetExe -or -not (Test-Path -LiteralPath $script:WingetExe)) {
        throw "winget executable path is not set or missing. Re-run prerequisite detection."
    }

    Write-Host "    winget install --id $PackageId"
    # Avoid Microsoft Store source issues (TLS interception / cert mismatch) by forcing the community repo source.
    $output = (& $script:WingetExe install -e --id $PackageId --source winget --accept-package-agreements --accept-source-agreements --silent 2>&1) | Out-String
    $output | Out-Host
    if ($LASTEXITCODE -eq 0) {
        return
    }
    if ($output -match "already installed|No available upgrade|No newer package|successfully installed|Nothing to do") {
        Write-Host "    (winget: package already satisfied or no upgrade)" -ForegroundColor DarkGray
        return
    }
    if ($output -match "0x8a15005e|server certificate did not match any of the expected values|Failed when searching source: msstore") {
        Write-Host "    winget Store source certificate error detected." -ForegroundColor Yellow
        Write-Host "    Tip: this script uses --source winget for installs, but your system may still have broken sources." -ForegroundColor Yellow
        Write-Host "    You can try (in an elevated PowerShell): winget source reset --force ; winget source update" -ForegroundColor Yellow
    }
    $listOut = (& $script:WingetExe list -e --id $PackageId 2>&1) | Out-String
    if ($LASTEXITCODE -eq 0 -and ($listOut -match [regex]::Escape($PackageId))) {
        Write-Host "    (already installed)" -ForegroundColor DarkGray
        return
    }
    throw "winget install --id $PackageId failed (exit $LASTEXITCODE)"
}

function Get-GitHubReleaseLatest {
    param(
        [string] $Owner,
        [string] $Repo
    )

    $uri = "https://api.github.com/repos/$Owner/$Repo/releases/latest"
    $headers = @{
        Accept               = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
        "User-Agent"         = $GitHubUa
    }
    if ($env:GITHUB_TOKEN) {
        $headers["Authorization"] = "Bearer $($env:GITHUB_TOKEN)"
    }
    return Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
}

function Get-AssetDownloadUrl {
    <#
    .NOTES
        When matching via -NameContains, asset filenames containing "shared" are skipped on purpose
        (e.g. FFmpeg shared builds ship extra DLLs; this deploy expects single-file static executables).
        For a release that only publishes shared artifacts, use -ExactName or extend this function.
    #>
    param(
        [object] $Release,
        [string] $ExactName = $null,
        [string[]] $NameContains = @()
    )

    $assets = @($Release.assets)
    if ($ExactName) {
        foreach ($a in $assets) {
            if ($a.name -eq $ExactName) {
                return [string] $a.browser_download_url
            }
        }
        throw "Asset '$ExactName' not found in release $($Release.tag_name)"
    }
    foreach ($a in $assets) {
        $n = [string] $a.name
        if (-not $n) { continue }
        $ok = $true
        foreach ($part in $NameContains) {
            if ($n -notlike "*$part*") {
                $ok = $false
                break
            }
        }
        if (-not $ok) { continue }
        if ($n.ToLower().Contains("shared")) { continue }
        if (-not $n.EndsWith(".zip")) { continue }
        return [string] $a.browser_download_url
    }
    throw "No matching zip asset in release $($Release.tag_name)"
}

function Expand-ExeFromZip {
    param(
        [string] $ZipPath,
        [string] $DestDir,
        [string] $ExeName
    )

    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("hsk-deploy-" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    try {
        Expand-Archive -LiteralPath $ZipPath -DestinationPath $tmp -Force
        $found = Get-ChildItem -Path $tmp -Recurse -Filter $ExeName -File -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if (-not $found) {
            return $null
        }
        $target = Join-Path $DestDir $ExeName
        Copy-Item -LiteralPath $found.FullName -Destination $target -Force
        return $target
    }
    finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Install-OptimizeBinaries {
    param(
        [string] $ProjectRoot,
        [switch] $ForceBins
    )

    $destDir = $ProjectRoot
    $need = @("ffmpeg.exe", "avifenc.exe", "avifdec.exe")
    $allExist = $true
    foreach ($n in $need) {
        if (-not (Test-Path -LiteralPath (Join-Path $destDir $n))) {
            $allExist = $false
            break
        }
    }
    if ($allExist -and -not $ForceBins) {
        Write-Host "    Binaries already present; skip (use -Force to re-download)" -ForegroundColor DarkGray
        Add-Outcome -Category "already" -Message "Optimize binaries already present (ffmpeg.exe, avifenc.exe, avifdec.exe)"
        return
    }

    # Prefer offline bundle files in install\dependencies.
    $deps = Get-DependenciesDir
    foreach ($exe in @("avifenc.exe", "avifdec.exe", "ffmpeg.exe")) {
        $srcExe = Join-Path $deps $exe
        if ((-not (Test-Path -LiteralPath (Join-Path $destDir $exe))) -or $ForceBins) {
            if (Test-Path -LiteralPath $srcExe) {
                Copy-Item -LiteralPath $srcExe -Destination (Join-Path $destDir $exe) -Force
                Add-Outcome -Category "installed" -Message "Copied $exe from offline bundle"
            }
        }
    }

    $zipLib = Get-LocalDependency -Pattern "windows-artifacts.zip"
    $zipFf = $null
    if (-not $zipLib) {
        $zipLib = Get-LocalDependency -Pattern "libavif*.zip"
    }
    $zipFf = Get-LocalDependency -Pattern "ffmpeg*-win64*gpl*.zip"
    if (-not $zipFf) {
        $zipFf = Get-LocalDependency -Pattern "ffmpeg-master-latest-win64-gpl.zip"
    }

    $tmpRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("hsk-bins-" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmpRoot -Force | Out-Null
    try {
        if (-not $zipLib) {
            Write-Step "Download libavif windows-artifacts (avifenc, avifdec)"
            $rel = Get-GitHubReleaseLatest -Owner "AOMediaCodec" -Repo "libavif"
            $url = Get-AssetDownloadUrl -Release $rel -ExactName "windows-artifacts.zip"
            $zipLib = Join-Path $tmpRoot "libavif.zip"
            Invoke-WebRequest -Uri $url -OutFile $zipLib -Headers @{ "User-Agent" = $GitHubUa } -UseBasicParsing
        }
        foreach ($exe in @("avifenc.exe", "avifdec.exe")) {
            if ((Test-Path -LiteralPath (Join-Path $destDir $exe)) -and -not $ForceBins) {
                Write-Host "    Skip $exe (exists)"
                continue
            }
            $p = Expand-ExeFromZip -ZipPath $zipLib -DestDir $destDir -ExeName $exe
            if ($p) {
                Write-Host "    Extracted $exe -> $p"
                if ($zipLib -like "*\\dependencies\\*") {
                    Add-Outcome -Category "installed" -Message "Extracted $exe from offline bundle zip"
                }
                else {
                    Add-Outcome -Category "installed" -Message "Downloaded $exe"
                }
            }
            else {
                Write-Warning "    $exe not found in windows-artifacts.zip"
                Add-Outcome -Category "skipped" -Message "$exe not found in libavif archive (download skipped)"
            }
        }

        if (-not $zipFf) {
            Write-Step "Download FFmpeg (ffmpeg.exe)"
            $relF = Get-GitHubReleaseLatest -Owner "BtbN" -Repo "FFmpeg-Builds"
            try {
                $urlF = Get-AssetDownloadUrl -Release $relF -ExactName "ffmpeg-master-latest-win64-gpl.zip"
            }
            catch {
                $urlF = Get-AssetDownloadUrl -Release $relF -NameContains @("win64", "gpl")
            }
            $zipFf = Join-Path $tmpRoot "ffmpeg.zip"
            Invoke-WebRequest -Uri $urlF -OutFile $zipFf -Headers @{ "User-Agent" = $GitHubUa } -UseBasicParsing
        }
        if ((Test-Path -LiteralPath (Join-Path $destDir "ffmpeg.exe")) -and -not $ForceBins) {
            Write-Host "    Skip ffmpeg.exe (exists)"
            Add-Outcome -Category "already" -Message "ffmpeg.exe already present"
        }
        else {
            $p = Expand-ExeFromZip -ZipPath $zipFf -DestDir $destDir -ExeName "ffmpeg.exe"
            if ($p) {
                Write-Host "    Extracted ffmpeg.exe -> $p"
                if ($zipFf -like "*\\dependencies\\*") {
                    Add-Outcome -Category "installed" -Message "Extracted ffmpeg.exe from offline bundle zip"
                }
                else {
                    Add-Outcome -Category "installed" -Message "Downloaded ffmpeg.exe"
                }
            }
            else {
                Write-Warning "    ffmpeg.exe not found in archive"
                Add-Outcome -Category "skipped" -Message "ffmpeg.exe not found in FFmpeg archive (download skipped)"
            }
        }
    }
    finally {
        Remove-Item -LiteralPath $tmpRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function New-NotesExplorerSymlinks {
    param([string] $ExtensionSource)

    if (-not (Test-Path -LiteralPath $ExtensionSource)) {
        Write-Warning "Extension folder not found: $ExtensionSource"
        return
    }

    $src = (Resolve-Path -LiteralPath $ExtensionSource).Path
    $pairs = @(
        @("VS Code", (Join-Path $env:USERPROFILE ".vscode\extensions")),
        @("VS Code Insiders", (Join-Path $env:USERPROFILE ".vscode-insiders\extensions")),
        @("Cursor", (Join-Path $env:USERPROFILE ".cursor\extensions"))
    )

    foreach ($item in $pairs) {
        $label = $item[0]
        $extRoot = $item[1]
        $linkPath = Join-Path $extRoot "notes-explorer"
        if (-not (Test-Path -LiteralPath $extRoot)) {
            Write-Host "    Skip ${label}: extensions folder not found ($extRoot)" -ForegroundColor DarkGray
            continue
        }
        if (Test-Path -LiteralPath $linkPath) {
            try {
                $itemLink = Get-Item -LiteralPath $linkPath -Force -ErrorAction Stop
                if ($itemLink.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                    $target = $itemLink.Target
                    if ($target -is [array]) {
                        $target = $target[0]
                    }
                    if ($target -and ([IO.Path]::GetFullPath($target) -ieq [IO.Path]::GetFullPath($src))) {
                        Write-Host "    Skip ${label}: symlink already points to repo" -ForegroundColor DarkGray
                        continue
                    }
                }
            }
            catch { }
            Write-Host "    Skip ${label}: path exists ($linkPath); remove manually or run elevated to replace" -ForegroundColor Yellow
            continue
        }
        try {
            New-Item -ItemType SymbolicLink -LiteralPath $linkPath -Target $src -Force | Out-Null
            Write-Host "    Linked ${label}: $linkPath -> $src"
        }
        catch {
            Write-Warning "    ${label}: could not create symlink ($($_.Exception.Message)). Enable Windows Developer Mode or run PowerShell elevated, then re-run with -SkipPrerequisites or only symlink step."
        }
    }
}

function New-DesktopShortcut {
    param(
        [string] $ProjectRoot
    )

    $desktop = [Environment]::GetFolderPath("Desktop")
    if (-not $desktop -or -not (Test-Path -LiteralPath $desktop)) {
        Write-Host "    Desktop folder not found; skip shortcut" -ForegroundColor DarkGray
        Add-Outcome -Category "skipped" -Message "Desktop shortcut skipped (Desktop folder not found)"
        return
    }

    $pyw = Join-Path $ProjectRoot ".venv\Scripts\pythonw.exe"
    $mainPy = Join-Path $ProjectRoot "src\harrix_swiss_knife\main.py"
    if (-not (Test-Path -LiteralPath $pyw)) {
        Write-Host "    pythonw.exe not found ($pyw); skip shortcut" -ForegroundColor Yellow
        Add-Outcome -Category "skipped" -Message "Desktop shortcut skipped (pythonw.exe not found)"
        return
    }
    if (-not (Test-Path -LiteralPath $mainPy)) {
        Write-Host "    main.py not found ($mainPy); skip shortcut" -ForegroundColor Yellow
        Add-Outcome -Category "skipped" -Message "Desktop shortcut skipped (main.py not found)"
        return
    }

    try {
        $lnkPath = Join-Path $desktop "Harrix Swiss Knife.lnk"
        $wsh = New-Object -ComObject WScript.Shell
        $lnk = $wsh.CreateShortcut($lnkPath)
        $lnk.TargetPath = $pyw
        $lnk.Arguments = "`"$mainPy`""
        $lnk.WorkingDirectory = $ProjectRoot
        $lnk.WindowStyle = 1
        $lnk.Description = "Harrix Swiss Knife"
        # Prefer repo-root img\icon.ico; optional fallback for older layouts.
        $iconCandidates = @(
            (Join-Path $ProjectRoot "img\icon.ico"),
            (Join-Path $ProjectRoot "src\harrix_swiss_knife\assets\app.ico")
        )
        foreach ($iconPath in $iconCandidates) {
            if ($iconPath -and (Test-Path -LiteralPath $iconPath)) {
                $lnk.IconLocation = "$iconPath,0"
                break
            }
        }
        $lnk.Save()
        Write-Host "    Shortcut created: $lnkPath"
        Add-Outcome -Category "installed" -Message "Desktop shortcut created ($lnkPath)"
    }
    catch {
        Write-Warning "    Could not create desktop shortcut: $($_.Exception.Message)"
        Add-Outcome -Category "skipped" -Message "Desktop shortcut failed: $($_.Exception.Message)"
    }
}

try {
    if (-not $SkipPrerequisites) {
        Write-Step "Prerequisites (winget)"
        Update-PathFromEnvironment
        $script:WingetExe = Get-WingetExePath
        if (-not $script:WingetExe) {
            Write-Host ""
            Write-Host "winget was not found (fresh Windows often has no WinGet on PATH until App Installer is installed)." -ForegroundColor Yellow
            Write-Host "Install Microsoft App Installer from Microsoft Store (search for App Installer), then sign out or reboot once." -ForegroundColor Yellow
            Write-Host "Docs: https://learn.microsoft.com/windows/package-manager/winget/" -ForegroundColor Cyan
            Write-Host "Alternatively install Git, Python, Node.js, and uv yourself, then run this script with -SkipPrerequisites." -ForegroundColor Yellow
            Invoke-DeployPauseBeforeExit
            exit 1
        }
        Write-Host "    Using winget: $script:WingetExe" -ForegroundColor DarkGray
        if (-not (Test-CommandExists "git")) {
            $gitInstaller = Get-LocalDependency -Pattern "Git-*-64-bit.exe"
            if ($gitInstaller) {
                Write-Host "    Offline Git installer found: $gitInstaller" -ForegroundColor DarkGray
                $ok = Install-LocalSetup -Path $gitInstaller -InstallerArgs @("/VERYSILENT", "/NORESTART", "/SUPPRESSMSGBOXES")
                Update-PathFromEnvironment
                if ($ok -and (Test-CommandExists "git")) {
                    Add-Outcome -Category "installed" -Message "Installed Git (offline)"
                }
                else {
                    Write-Warning "Offline Git install failed; falling back to winget."
                    Invoke-WingetInstall -PackageId "Git.Git"
                    Update-PathFromEnvironment
                    Add-Outcome -Category "installed" -Message "Installed Git"
                }
            }
            else {
                Invoke-WingetInstall -PackageId "Git.Git"
                Update-PathFromEnvironment
                Add-Outcome -Category "installed" -Message "Installed Git"
            }
        }
        else {
            Add-Outcome -Category "already" -Message "Git already installed"
        }
        if (-not (Test-CommandExists "python")) {
            $pyInstaller = Get-LocalDependency -Pattern "python-*-amd64.exe"
            if ($pyInstaller) {
                Write-Host "    Offline Python installer found: $pyInstaller" -ForegroundColor DarkGray
                $ok = Install-LocalSetup -Path $pyInstaller -InstallerArgs @("/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_launcher=1")
                Update-PathFromEnvironment
                if ($ok -and (Test-CommandExists "python")) {
                    Add-Outcome -Category "installed" -Message "Installed Python (offline)"
                }
                else {
                    Write-Warning "Offline Python install failed; falling back to winget."
                    try {
                        Invoke-WingetInstall -PackageId "Python.Python.3.13"
                    }
                    catch {
                        Write-Host "    Python.Python.3.13 failed; trying Python.Python.3.12..." -ForegroundColor Yellow
                        Invoke-WingetInstall -PackageId "Python.Python.3.12"
                    }
                    Update-PathFromEnvironment
                    Add-Outcome -Category "installed" -Message "Installed Python"
                }
            }
            else {
                try {
                    Invoke-WingetInstall -PackageId "Python.Python.3.13"
                }
                catch {
                    Write-Host "    Python.Python.3.13 failed; trying Python.Python.3.12..." -ForegroundColor Yellow
                    Invoke-WingetInstall -PackageId "Python.Python.3.12"
                }
                Update-PathFromEnvironment
                Add-Outcome -Category "installed" -Message "Installed Python"
            }
        }
        else {
            Add-Outcome -Category "already" -Message "Python already installed"
        }
        if (-not (Test-CommandExists "node")) {
            $nodeMsi = Get-LocalDependency -Pattern "node-v*-x64.msi"
            if ($nodeMsi) {
                Write-Host "    Offline Node.js installer found: $nodeMsi" -ForegroundColor DarkGray
                $ok = Install-LocalSetup -Path $nodeMsi
                Update-PathFromEnvironment
                if ($ok -and (Test-CommandExists "node")) {
                    Add-Outcome -Category "installed" -Message "Installed Node.js (offline)"
                }
                else {
                    Write-Warning "Offline Node.js install failed; falling back to winget."
                    Invoke-WingetInstall -PackageId "OpenJS.NodeJS.LTS"
                    Update-PathFromEnvironment
                    Add-Outcome -Category "installed" -Message "Installed Node.js"
                }
            }
            else {
                Invoke-WingetInstall -PackageId "OpenJS.NodeJS.LTS"
                Update-PathFromEnvironment
                Add-Outcome -Category "installed" -Message "Installed Node.js"
            }
        }
        else {
            Add-Outcome -Category "already" -Message "Node.js already installed"
        }

        if (-not (Test-AnyCodeEditorExists)) {
            $vsCode = Get-LocalDependency -Pattern "VSCode*Setup*x64*.exe"
            if ($vsCode) {
                Write-Host "    Offline VS Code installer found: $vsCode" -ForegroundColor DarkGray
                $ok = Install-LocalSetup -Path $vsCode -InstallerArgs @("/VERYSILENT", "/NORESTART", "/MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,addtopath")
                Update-PathFromEnvironment
                if ($ok -and (Test-AnyCodeEditorExists)) {
                    Add-Outcome -Category "installed" -Message "Installed VS Code (offline)"
                }
                else {
                    Write-Warning "Offline VS Code install failed; falling back to winget."
                    Invoke-WingetInstall -PackageId "Microsoft.VisualStudioCode"
                    Update-PathFromEnvironment
                    Add-Outcome -Category "installed" -Message "Installed VS Code"
                }
            }
            else {
                Invoke-WingetInstall -PackageId "Microsoft.VisualStudioCode"
                Update-PathFromEnvironment
                Add-Outcome -Category "installed" -Message "Installed VS Code"
            }
        }
        else {
            Add-Outcome -Category "already" -Message "Cursor/VS Code already installed"
        }

        if (-not (Test-CommandExists "uv")) {
            $uvZip = Get-LocalDependency -Pattern "uv-x86_64-pc-windows-msvc.zip"
            if ($uvZip) {
                Write-Host "    Offline uv zip found: $uvZip" -ForegroundColor DarkGray
                $bin = Join-Path $env:USERPROFILE ".local\\bin"
                New-Item -ItemType Directory -Path $bin -Force | Out-Null
                $tmpUv = Join-Path ([System.IO.Path]::GetTempPath()) ("uv-" + [Guid]::NewGuid().ToString("N"))
                New-Item -ItemType Directory -Path $tmpUv -Force | Out-Null
                try {
                    Expand-Archive -LiteralPath $uvZip -DestinationPath $tmpUv -Force
                    $uvExe = Get-ChildItem -Path $tmpUv -Recurse -Filter "uv.exe" -File | Select-Object -First 1
                    $uvxExe = Get-ChildItem -Path $tmpUv -Recurse -Filter "uvx.exe" -File | Select-Object -First 1
                    if ($uvExe) { Copy-Item -LiteralPath $uvExe.FullName -Destination (Join-Path $bin "uv.exe") -Force }
                    if ($uvxExe) { Copy-Item -LiteralPath $uvxExe.FullName -Destination (Join-Path $bin "uvx.exe") -Force }
                }
                finally {
                    Remove-Item -LiteralPath $tmpUv -Recurse -Force -ErrorAction SilentlyContinue
                }
                $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
                if ($userPath -notlike "*$bin*") {
                    [Environment]::SetEnvironmentVariable("Path", ($userPath + ";" + $bin), "User")
                }
                Update-PathFromEnvironment
                if (Test-CommandExists "uv") {
                    Add-Outcome -Category "installed" -Message "Installed uv (offline)"
                }
                else {
                    Write-Warning "Offline uv install did not place uv on PATH; falling back to winget."
                    try {
                        Invoke-WingetInstall -PackageId "astral-sh.uv"
                    }
                    catch {
                        Write-Host "    winget uv failed; trying official install script..." -ForegroundColor Yellow
                        & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
                    }
                    Update-PathFromEnvironment
                    Add-Outcome -Category "installed" -Message "Installed uv"
                }
            }
            else {
                try {
                    Invoke-WingetInstall -PackageId "astral-sh.uv"
                }
                catch {
                    Write-Host "    winget uv failed; trying official install script..." -ForegroundColor Yellow
                    & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
                }
                Update-PathFromEnvironment
                Add-Outcome -Category "installed" -Message "Installed uv"
            }
        }
        else {
            Add-Outcome -Category "already" -Message "uv already installed"
        }
        Update-PathFromEnvironment
    }
    else {
        Add-Outcome -Category "skipped" -Message "Prerequisites install skipped (-SkipPrerequisites)"
    }

    $resolvedRoot = $InstallRoot
    if ([string]::IsNullOrWhiteSpace($resolvedRoot)) {
        $fromRepo = Get-InstallRootFromClonedHsk
        if ($fromRepo) {
            $resolvedRoot = $fromRepo
            Write-Host "Detected harrix-swiss-knife clone; using install root: $resolvedRoot" -ForegroundColor Green
        }
        else {
            $resolvedRoot = Get-AutomaticInstallRootParent
            Write-Host "Automatic install root: $resolvedRoot" -ForegroundColor Green
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($InstallRoot)) {
        $resolvedRoot = Initialize-GitHubRoot -SelectedPath $resolvedRoot
    }
    if ([string]::IsNullOrWhiteSpace($resolvedRoot)) {
        throw "InstallRoot is empty."
    }

    Write-Step "Ensure install root exists: $resolvedRoot"
    if (-not (Test-Path -LiteralPath $resolvedRoot)) {
        New-Item -ItemType Directory -Path $resolvedRoot -Force | Out-Null
    }
    $resolvedRoot = (Resolve-Path -LiteralPath $resolvedRoot).Path

    $pylib = Join-Path $resolvedRoot "harrix-pylib"
    $pyssg = Join-Path $resolvedRoot "harrix-pyssg"
    $hsk = Join-Path $resolvedRoot "harrix-swiss-knife"

    Write-Step "Clone repositories (idempotent)"
    if (-not (Test-Path -LiteralPath $pylib)) {
        Push-Location $resolvedRoot
        try {
            git clone "https://github.com/Harrix/harrix-pylib.git"
            if ($LASTEXITCODE -ne 0) { throw "git clone harrix-pylib failed (exit $LASTEXITCODE)" }
            Add-Outcome -Category "installed" -Message "Cloned harrix-pylib"
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Host "    harrix-pylib already present"
        Add-Outcome -Category "already" -Message "harrix-pylib already present"
        Update-GitRepoIfPossible -RepoPath $pylib -Label "harrix-pylib"
    }
    if (-not (Test-Path -LiteralPath $pyssg)) {
        Push-Location $resolvedRoot
        try {
            git clone "https://github.com/Harrix/harrix-pyssg.git"
            if ($LASTEXITCODE -ne 0) { throw "git clone harrix-pyssg failed (exit $LASTEXITCODE)" }
            Add-Outcome -Category "installed" -Message "Cloned harrix-pyssg"
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Host "    harrix-pyssg already present"
        Add-Outcome -Category "already" -Message "harrix-pyssg already present"
        Update-GitRepoIfPossible -RepoPath $pyssg -Label "harrix-pyssg"
    }
    if (-not (Test-Path -LiteralPath $hsk)) {
        Push-Location $resolvedRoot
        try {
            git clone "https://github.com/Harrix/harrix-swiss-knife.git"
            if ($LASTEXITCODE -ne 0) { throw "git clone harrix-swiss-knife failed (exit $LASTEXITCODE)" }
            Add-Outcome -Category "installed" -Message "Cloned harrix-swiss-knife"
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Host "    harrix-swiss-knife already present"
        Add-Outcome -Category "already" -Message "harrix-swiss-knife already present"
        Update-GitRepoIfPossible -RepoPath $hsk -Label "harrix-swiss-knife"
    }

    Write-Step "uv sync (harrix-pylib)"
    Push-Location $pylib
    try {
        uv sync
        if ($LASTEXITCODE -ne 0) { throw "uv sync failed in harrix-pylib (exit $LASTEXITCODE)" }
        Add-Outcome -Category "installed" -Message "Synced Python deps (harrix-pylib)"
    }
    finally {
        Pop-Location
    }

    Write-Step "uv sync (harrix-pyssg)"
    Push-Location $pyssg
    try {
        uv sync
        if ($LASTEXITCODE -ne 0) { throw "uv sync failed in harrix-pyssg (exit $LASTEXITCODE)" }
        Add-Outcome -Category "installed" -Message "Synced Python deps (harrix-pyssg)"
    }
    finally {
        Pop-Location
    }

    Write-Step "uv sync + npm (harrix-swiss-knife)"
    $npmOk = $false
    Push-Location $hsk
    try {
        uv sync
        if ($LASTEXITCODE -ne 0) { throw "uv sync failed in harrix-swiss-knife (exit $LASTEXITCODE)" }
        Add-Outcome -Category "installed" -Message "Synced Python deps (harrix-swiss-knife)"
        $npmOk = Invoke-NpmWithRetries -NpmArgs @("install")
        if (-not $npmOk) {
            Write-Warning "npm install did not complete (registry timeout or PowerShell blocked npm.ps1 due to ExecutionPolicy)."
            Write-Warning "Installation will continue. From repo folder run: npm.cmd install (or open cmd.exe and run npm install)."
            Add-Outcome -Category "skipped" -Message "npm install failed (Node deps not installed)"
        }
        else {
            Add-Outcome -Category "installed" -Message "Installed Node deps (npm install)"
        }
    }
    finally {
        Pop-Location
    }

    if (-not (Test-CommandExists "prettier")) {
        if (-not $npmOk) {
            Write-Warning "Skipping prettier global install because npm install already failed (network or npm.ps1 blocked by ExecutionPolicy)."
            Write-Warning "This is optional. Later: npm.cmd install -g prettier (or cmd.exe: npm install -g prettier)."
            Add-Outcome -Category "skipped" -Message "Global prettier not installed (npm failed earlier)"
        }
        else {
            Write-Step "npm install -g prettier"
            $prettierOk = Invoke-NpmWithRetries -NpmArgs @("install", "-g", "prettier")
            if (-not $prettierOk) {
                Write-Warning "Could not install prettier globally (network timeout or npm.ps1 blocked by ExecutionPolicy)."
                Write-Warning "This is optional. Later: npm.cmd install -g prettier (or cmd.exe: npm install -g prettier)."
                Add-Outcome -Category "skipped" -Message "Global prettier not installed (npm error)"
            }
            else {
                Add-Outcome -Category "installed" -Message "Installed global prettier"
            }
        }
    }
    else {
        Write-Host "    prettier already on PATH; skip global install" -ForegroundColor DarkGray
        Add-Outcome -Category "already" -Message "prettier already on PATH"
    }

    Write-Step "uv tool install -e (CLI on PATH)"
    Push-Location $resolvedRoot
    try {
        if (-not (Test-Path -LiteralPath $hsk)) {
            throw "Project folder not found: $hsk"
        }
        $hskPyproject = Join-Path $hsk "pyproject.toml"
        if (-not (Test-Path -LiteralPath $hskPyproject)) {
            throw "pyproject.toml not found in: $hsk (expected: $hskPyproject)"
        }

        # uv may write "No tools installed" to stderr; with $ErrorActionPreference Stop that can surface as a terminating error.
        $toolList = ""
        $prevEap = $ErrorActionPreference
        try {
            $ErrorActionPreference = "Continue"
            $toolOut = & uv tool list 2>&1
            $toolExit = $LASTEXITCODE
            $toolList = ($toolOut | ForEach-Object { "$_" }) -join "`n"
            if ($toolExit -ne 0) {
                Write-Warning "uv tool list exited with code $toolExit; assuming no tools installed yet."
                $toolList = ""
            }
        }
        finally {
            $ErrorActionPreference = $prevEap
        }

        # Do not abort deploy if CLI install fails — continue to shortcut and Optimize binaries.
        try {
            $prevEap2 = $ErrorActionPreference
            try {
                $ErrorActionPreference = "Continue"
                if ($toolList -match "harrix-swiss-knife") {
                    & uv tool install --reinstall -e $hsk
                }
                else {
                    & uv tool install -e $hsk
                }
            }
            finally {
                $ErrorActionPreference = $prevEap2
            }
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "uv tool install failed (exit $LASTEXITCODE). Tray app and downloads will still run; fix CLI later: uv tool install -e `"$hsk`""
                Add-Outcome -Category "skipped" -Message "CLI not installed (uv tool install failed)"
            }
            else {
                Add-Outcome -Category "installed" -Message "Installed CLI (uv tool install -e)"
            }
        }
        catch {
            Write-Warning "uv tool install failed: $($_.Exception.Message). Installation continues; fix CLI later: uv tool install -e `"$hsk`""
            Add-Outcome -Category "skipped" -Message "CLI not installed (uv tool install error)"
        }
    }
    finally {
        Pop-Location
    }

    if (-not $SkipExtensionSymlinks) {
        Write-Step "Notes Explorer symlinks"
        $extSrc = Join-Path $hsk "vscode\harrix-notes-explorer"
        New-NotesExplorerSymlinks -ExtensionSource $extSrc
        Add-Outcome -Category "installed" -Message "Notes Explorer symlink step attempted (see warnings above if any)"
    }
    else {
        Add-Outcome -Category "skipped" -Message "Notes Explorer symlinks skipped (-SkipExtensionSymlinks)"
    }

    Write-Step "Default config (show main window on startup)"
    $configPath = Join-Path $hsk "config\config.json"
    $updated = Set-JsonBoolProperty -Path $configPath -PropertyName "show_main_window_on_startup" -Value $true
    if ($updated) {
        Add-Outcome -Category "installed" -Message "Configured show_main_window_on_startup=true in installed config.json"
    }
    else {
        Add-Outcome -Category "skipped" -Message "Could not set show_main_window_on_startup in config.json (file missing or key not found)"
    }

    Write-Step "Desktop shortcut"
    New-DesktopShortcut -ProjectRoot $hsk

    # Download large binaries at the very end so a failure doesn't block installation.
    if (-not $SkipBinaries) {
        Write-Step "Download Optimize dependencies (ffmpeg, avifenc, avifdec)"
        try {
            Install-OptimizeBinaries -ProjectRoot $hsk -ForceBins:$Force
        }
        catch {
            Write-Warning "Could not download Optimize dependencies: $($_.Exception.Message)"
            Write-Warning "Installation will continue. You can download these later from the app: Dev → Download Optimize dependencies (ffmpeg, avifenc, avifdec)."
            Add-Outcome -Category "skipped" -Message "Optimize binaries download failed: $($_.Exception.Message)"
        }
    }
    else {
        Add-Outcome -Category "skipped" -Message "Optimize binaries download skipped (-SkipBinaries)"
    }

    Write-Step "Done"
    $pyw = Join-Path $hsk ".venv\Scripts\pythonw.exe"
    $mainPy = Join-Path $hsk "src\harrix_swiss_knife\main.py"
    Write-Host ""
    Write-Host "Install root:    $resolvedRoot" -ForegroundColor Green
    Write-Host "Run tray app:    `"$pyw`" `"$mainPy`""
    Write-Host "CLI examples:    harrix-swiss-knife-cli markdown --help"
    Write-Host "Restart VS Code / Cursor if you linked the extension."

    Write-Host ""
    Write-Host "Summary" -ForegroundColor Cyan
    if ($script:Already.Count -gt 0) {
        Write-Host ""
        Write-Host "What already existed:" -ForegroundColor Green
        foreach ($m in $script:Already) { Write-Host ("  - " + $m) }
    }
    if ($script:Skipped.Count -gt 0) {
        Write-Host ""
        Write-Host "What was skipped:" -ForegroundColor Yellow
        foreach ($m in $script:Skipped) { Write-Host ("  - " + $m) }
    }
    if ($script:Installed.Count -gt 0) {
        Write-Host ""
        Write-Host "What was installed:" -ForegroundColor Green
        foreach ($m in $script:Installed) { Write-Host ("  - " + $m) }
    }

    Write-ElapsedSummary
}
catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ScriptStackTrace) {
        Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
    }
    Write-ElapsedSummary
    Invoke-DeployPauseBeforeExit
    exit 1
}

