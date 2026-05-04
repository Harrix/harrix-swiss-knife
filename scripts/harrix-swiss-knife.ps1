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
    D:\GitHub, C:\GitHub, Documents\GitHub (GitHub Desktop default), or creates %ProgramFiles%\harrix-swiss-knife.

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

function Invoke-NpmWithRetries {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $NpmArgs,

        [int] $MaxAttempts = 3,
        [int] $SleepSeconds = 10,

        # See: https://docs.npmjs.com/cli/v10/using-npm/config#fetch-timeout
        [int] $FetchTimeoutMs = 300000,
        [int] $FetchRetries = 5,
        [int] $FetchRetryMinTimeoutMs = 20000,
        [int] $FetchRetryMaxTimeoutMs = 120000
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

        for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
            $joined = ($NpmArgs -join " ")
            Write-Host "    & `"$npmExe`" $joined (attempt $attempt/$MaxAttempts)" -ForegroundColor DarkGray

            & $npmExe @NpmArgs
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
        If none exist, use %ProgramFiles%\harrix-swiss-knife (may require an elevated shell).
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

    $bundle = Join-Path $env:ProgramFiles "harrix-swiss-knife"
    if (-not (Test-Path -LiteralPath $bundle)) {
        Write-Host "    No GitHub folder found; creating install folder: $bundle" -ForegroundColor DarkGray
        try {
            New-Item -ItemType Directory -Path $bundle -Force -ErrorAction Stop | Out-Null
        }
        catch {
            throw "Could not create $bundle. Creating under Program Files usually requires Administrator; re-run this script elevated or pass -InstallRoot."
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
    # Explicit -InstallRoot: allow ...\GitHub, or the bundled Program Files layout ...\harrix-swiss-knife
    if ($leaf -ieq "GitHub" -or ($leaf -ieq "harrix-swiss-knife" -and $p.StartsWith($env:ProgramFiles, [System.StringComparison]::OrdinalIgnoreCase))) {
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
        return
    }

    $tmpRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("hsk-bins-" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmpRoot -Force | Out-Null
    try {
        Write-Step "Download libavif windows-artifacts (avifenc, avifdec)"
        $rel = Get-GitHubReleaseLatest -Owner "AOMediaCodec" -Repo "libavif"
        $url = Get-AssetDownloadUrl -Release $rel -ExactName "windows-artifacts.zip"
        $zipLib = Join-Path $tmpRoot "libavif.zip"
        Invoke-WebRequest -Uri $url -OutFile $zipLib -Headers @{ "User-Agent" = $GitHubUa } -UseBasicParsing
        foreach ($exe in @("avifenc.exe", "avifdec.exe")) {
            if ((Test-Path -LiteralPath (Join-Path $destDir $exe)) -and -not $ForceBins) {
                Write-Host "    Skip $exe (exists)"
                continue
            }
            $p = Expand-ExeFromZip -ZipPath $zipLib -DestDir $destDir -ExeName $exe
            if ($p) {
                Write-Host "    Extracted $exe -> $p"
            }
            else {
                Write-Warning "    $exe not found in windows-artifacts.zip"
            }
        }

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
        if ((Test-Path -LiteralPath (Join-Path $destDir "ffmpeg.exe")) -and -not $ForceBins) {
            Write-Host "    Skip ffmpeg.exe (exists)"
        }
        else {
            $p = Expand-ExeFromZip -ZipPath $zipFf -DestDir $destDir -ExeName "ffmpeg.exe"
            if ($p) {
                Write-Host "    Extracted ffmpeg.exe -> $p"
            }
            else {
                Write-Warning "    ffmpeg.exe not found in archive"
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
        return
    }

    $pyw = Join-Path $ProjectRoot ".venv\Scripts\pythonw.exe"
    $mainPy = Join-Path $ProjectRoot "src\harrix_swiss_knife\main.py"
    if (-not (Test-Path -LiteralPath $pyw)) {
        Write-Host "    pythonw.exe not found ($pyw); skip shortcut" -ForegroundColor Yellow
        return
    }
    if (-not (Test-Path -LiteralPath $mainPy)) {
        Write-Host "    main.py not found ($mainPy); skip shortcut" -ForegroundColor Yellow
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
        $lnk.Save()
        Write-Host "    Shortcut created: $lnkPath"
    }
    catch {
        Write-Warning "    Could not create desktop shortcut: $($_.Exception.Message)"
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
            Invoke-WingetInstall -PackageId "Git.Git"
            Update-PathFromEnvironment
        }
        if (-not (Test-CommandExists "python")) {
            try {
                Invoke-WingetInstall -PackageId "Python.Python.3.13"
            }
            catch {
                Write-Host "    Python.Python.3.13 failed; trying Python.Python.3.12..." -ForegroundColor Yellow
                Invoke-WingetInstall -PackageId "Python.Python.3.12"
            }
            Update-PathFromEnvironment
        }
        if (-not (Test-CommandExists "node")) {
            Invoke-WingetInstall -PackageId "OpenJS.NodeJS.LTS"
            Update-PathFromEnvironment
        }
        if (-not (Test-CommandExists "uv")) {
            try {
                Invoke-WingetInstall -PackageId "astral-sh.uv"
            }
            catch {
                Write-Host "    winget uv failed; trying official install script..." -ForegroundColor Yellow
                & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
            }
            Update-PathFromEnvironment
        }
        Update-PathFromEnvironment
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
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Host "    harrix-pylib already present"
    }
    if (-not (Test-Path -LiteralPath $pyssg)) {
        Push-Location $resolvedRoot
        try {
            git clone "https://github.com/Harrix/harrix-pyssg.git"
            if ($LASTEXITCODE -ne 0) { throw "git clone harrix-pyssg failed (exit $LASTEXITCODE)" }
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Host "    harrix-pyssg already present"
    }
    if (-not (Test-Path -LiteralPath $hsk)) {
        Push-Location $resolvedRoot
        try {
            git clone "https://github.com/Harrix/harrix-swiss-knife.git"
            if ($LASTEXITCODE -ne 0) { throw "git clone harrix-swiss-knife failed (exit $LASTEXITCODE)" }
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Host "    harrix-swiss-knife already present"
    }

    Write-Step "uv sync (harrix-pylib)"
    Push-Location $pylib
    try {
        uv sync
        if ($LASTEXITCODE -ne 0) { throw "uv sync failed in harrix-pylib (exit $LASTEXITCODE)" }
    }
    finally {
        Pop-Location
    }

    Write-Step "uv sync (harrix-pyssg)"
    Push-Location $pyssg
    try {
        uv sync
        if ($LASTEXITCODE -ne 0) { throw "uv sync failed in harrix-pyssg (exit $LASTEXITCODE)" }
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
        $npmOk = Invoke-NpmWithRetries -NpmArgs @("install")
        if (-not $npmOk) {
            Write-Warning "npm install did not complete (registry timeout or PowerShell blocked npm.ps1 due to ExecutionPolicy)."
            Write-Warning "Installation will continue. From repo folder run: npm.cmd install (or open cmd.exe and run npm install)."
        }
    }
    finally {
        Pop-Location
    }

    if (-not (Test-CommandExists "prettier")) {
        if (-not $npmOk) {
            Write-Warning "Skipping prettier global install because npm install already failed (network or npm.ps1 blocked by ExecutionPolicy)."
            Write-Warning "This is optional. Later: npm.cmd install -g prettier (or cmd.exe: npm install -g prettier)."
        }
        else {
            Write-Step "npm install -g prettier"
            $prettierOk = Invoke-NpmWithRetries -NpmArgs @("install", "-g", "prettier") -MaxAttempts 3 -SleepSeconds 15
            if (-not $prettierOk) {
                Write-Warning "Could not install prettier globally (network timeout or npm.ps1 blocked by ExecutionPolicy)."
                Write-Warning "This is optional. Later: npm.cmd install -g prettier (or cmd.exe: npm install -g prettier)."
            }
        }
    }
    else {
        Write-Host "    prettier already on PATH; skip global install" -ForegroundColor DarkGray
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
            }
        }
        catch {
            Write-Warning "uv tool install failed: $($_.Exception.Message). Installation continues; fix CLI later: uv tool install -e `"$hsk`""
        }
    }
    finally {
        Pop-Location
    }

    if (-not $SkipExtensionSymlinks) {
        Write-Step "Notes Explorer symlinks"
        $extSrc = Join-Path $hsk "vscode\harrix-notes-explorer"
        New-NotesExplorerSymlinks -ExtensionSource $extSrc
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
        }
    }

    Write-Step "Done"
    $pyw = Join-Path $hsk ".venv\Scripts\pythonw.exe"
    $mainPy = Join-Path $hsk "src\harrix_swiss_knife\main.py"
    Write-Host ""
    Write-Host "Install root:    $resolvedRoot" -ForegroundColor Green
    Write-Host "Run tray app:    `"$pyw`" `"$mainPy`""
    Write-Host "CLI examples:    harrix-swiss-knife-cli markdown --help"
    Write-Host "Restart VS Code / Cursor if you linked the extension."

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
