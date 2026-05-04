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
    If omitted, detects when run from repo scripts\ folder; otherwise prompts.

.PARAMETER SkipPrerequisites
    Skip winget installs for Git, Python, Node.js, uv.

.PARAMETER SkipBinaries
    Skip downloading ffmpeg.exe, avifenc.exe, avifdec.exe.

.PARAMETER SkipExtensionSymlinks
    Skip Notes Explorer symlink creation.

.PARAMETER Force
    Re-download binaries even if they already exist in project root.

.PARAMETER NoPauseOnError
    Do not wait for Enter before exiting after an error (for automation).
#>
[CmdletBinding()]
param(
    [string] $InstallRoot,
    [switch] $SkipPrerequisites,
    [switch] $SkipBinaries,
    [switch] $SkipExtensionSymlinks,
    [switch] $Force,
    [switch] $NoPauseOnError
)

$ErrorActionPreference = "Stop"

# GitHub API and Invoke-WebRequest on older Windows PowerShell
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
}
catch { }

$GitHubUa = "Harrix-Swiss-Knife-Deploy/1.0 (PowerShell)"

function Write-Step {
    param([string] $Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Refresh-PathFromEnvironment {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

function Test-CommandExists {
    param([string] $Name)
    return [bool](Get-Command -Name $Name -ErrorAction SilentlyContinue)
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
    Refresh-PathFromEnvironment
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

function Select-InstallRootInteractive {
    param([string] $DefaultPath = "D:\GitHub")

    if (-not (Test-Path -LiteralPath $DefaultPath)) {
        $DefaultPath = [Environment]::GetFolderPath("UserProfile")
    }

    # Offer common install roots before opening the folder picker.
    $candidates = @()
    if (Test-Path -LiteralPath "D:\GitHub") { $candidates += "D:\GitHub" }
    if (Test-Path -LiteralPath "C:\GitHub") { $candidates += "C:\GitHub" }
    if ($candidates.Count -gt 0) {
        try {
            $choices = @()
            foreach ($c in $candidates) {
                $target = Join-Path $c "harrix-swiss-knife"
                $choices += New-Object System.Management.Automation.Host.ChoiceDescription "&$target", "Clone repos as siblings under $c"
            }
            $choices += New-Object System.Management.Automation.Host.ChoiceDescription "&Browse", "Choose another folder"
            $choiceIndex = $Host.UI.PromptForChoice(
                "Select install root",
                "Pick a parent folder for sibling clones (harrix-pylib, harrix-pyssg, harrix-swiss-knife).",
                $choices,
                0
            )
            if ($choiceIndex -ge 0 -and $choiceIndex -lt $candidates.Count) {
                return $candidates[$choiceIndex]
            }
        }
        catch {
            # Non-interactive host or restricted UI; fall back to folder dialog / Read-Host.
        }
    }

    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop | Out-Null
        $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
        $dialog.Description = "Select parent folder for clones (harrix-pylib, harrix-pyssg, harrix-swiss-knife side by side)"
        $dialog.SelectedPath = $DefaultPath
        $dialog.ShowNewFolderButton = $true
        if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            return $dialog.SelectedPath
        }
    }
    catch {
        Write-Host "Folder dialog unavailable: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    $typed = Read-Host "Install root path [default: $DefaultPath]"
    if ([string]::IsNullOrWhiteSpace($typed)) {
        return $DefaultPath
    }
    return $typed.Trim()
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
            if ((Test-Path (Join-Path $destDir $exe)) -and -not $ForceBins) {
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
        if ((Test-Path (Join-Path $destDir "ffmpeg.exe")) -and -not $ForceBins) {
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

try {
    if (-not $SkipPrerequisites) {
        Write-Step "Prerequisites (winget)"
        Refresh-PathFromEnvironment
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
            Refresh-PathFromEnvironment
        }
        if (-not (Test-CommandExists "python")) {
            try {
                Invoke-WingetInstall -PackageId "Python.Python.3.13"
            }
            catch {
                Write-Host "    Python.Python.3.13 failed; trying Python.Python.3.12..." -ForegroundColor Yellow
                Invoke-WingetInstall -PackageId "Python.Python.3.12"
            }
            Refresh-PathFromEnvironment
        }
        if (-not (Test-CommandExists "node")) {
            Invoke-WingetInstall -PackageId "OpenJS.NodeJS.LTS"
            Refresh-PathFromEnvironment
        }
        if (-not (Test-CommandExists "uv")) {
            try {
                Invoke-WingetInstall -PackageId "astral-sh.uv"
            }
            catch {
                Write-Host "    winget uv failed; trying official install script..." -ForegroundColor Yellow
                & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
            }
            Refresh-PathFromEnvironment
        }
        Refresh-PathFromEnvironment
    }

    $resolvedRoot = $InstallRoot
    if ([string]::IsNullOrWhiteSpace($resolvedRoot)) {
        $fromRepo = Get-InstallRootFromClonedHsk
        if ($fromRepo) {
            $resolvedRoot = $fromRepo
            Write-Host "Detected harrix-swiss-knife clone; using install root: $resolvedRoot" -ForegroundColor Green
        }
        else {
            $resolvedRoot = Select-InstallRootInteractive -DefaultPath "D:\GitHub"
        }
    }

    $resolvedRoot = $resolvedRoot.Trim()
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
    }
    finally {
        Pop-Location
    }

    Write-Step "uv sync (harrix-pyssg)"
    Push-Location $pyssg
    try {
        uv sync
    }
    finally {
        Pop-Location
    }

    Write-Step "uv sync + npm (harrix-swiss-knife)"
    Push-Location $hsk
    try {
        uv sync
        npm install
    }
    finally {
        Pop-Location
    }

    if (-not (Test-CommandExists "prettier")) {
        Write-Step "npm install -g prettier"
        npm install -g prettier
    }
    else {
        Write-Host "    prettier already on PATH; skip global install" -ForegroundColor DarkGray
    }

    if (-not $SkipBinaries) {
        try {
            Install-OptimizeBinaries -ProjectRoot $hsk -ForceBins:$Force
        }
        catch {
            Write-Warning "Binary download failed: $($_.Exception.Message). Set GITHUB_TOKEN or install manually."
        }
    }

    Write-Step "uv tool install -e (CLI on PATH)"
    Push-Location $resolvedRoot
    try {
        $toolList = & uv tool list 2>&1 | Out-String
        if ($toolList -match "harrix-swiss-knife") {
            & uv tool install --reinstall -e $hsk
        }
        else {
            & uv tool install -e $hsk
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

    Write-Step "Done"
    $pyw = Join-Path $hsk ".venv\Scripts\pythonw.exe"
    $mainPy = Join-Path $hsk "src\harrix_swiss_knife\main.py"
    Write-Host ""
    Write-Host "Install root:    $resolvedRoot" -ForegroundColor Green
    Write-Host "Run tray app:    `"$pyw`" `"$mainPy`""
    Write-Host "CLI examples:    harrix-swiss-knife-cli markdown --help"
    Write-Host "Restart VS Code / Cursor if you linked the extension."
}
catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ScriptStackTrace) {
        Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
    }
    Invoke-DeployPauseBeforeExit
    exit 1
}
