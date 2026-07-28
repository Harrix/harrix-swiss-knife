#Requires -Version 5.1
# Optional Android toolchain for harrix-swiss-knife\android (not part of zip pipeline 01-07).
[CmdletBinding()]
param(
    [switch]$SkipAndroidStudio,
    [switch]$InstallAndroidStudio
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$installDir = $PSScriptRoot
$repoRoot = Split-Path -Parent $installDir
$androidDir = Join-Path $repoRoot "android"
$sdkRoot = Join-Path $env:LOCALAPPDATA "Android\Sdk"
$jdkPortableRoot = Join-Path $env:LOCALAPPDATA "Java"
$jdkPortableDir = Join-Path $jdkPortableRoot "jdk-17.0.14+7"
$cmdToolsZip = Join-Path $env:TEMP "commandlinetools-win-hsk.zip"
$cmdToolsUrl = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
$temurinZipUrl = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.14%2B7/OpenJDK17U-jdk_x64_windows_hotspot_17.0.14_7.zip"
$temurinZip = Join-Path $env:TEMP "OpenJDK17U-jdk_x64_windows_hotspot_17.0.14_7.zip"

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host $Message -ForegroundColor Cyan
}

function Test-Java17 {
    param([string]$JavaHomeCandidate)
    $javaExe = if ($JavaHomeCandidate) {
        Join-Path $JavaHomeCandidate "bin\java.exe"
    } else {
        $null
    }
    if ($javaExe -and (Test-Path -LiteralPath $javaExe)) {
        $verOut = & $javaExe -version 2>&1 | Out-String
        if ($verOut -match 'version "17(\.|")') {
            return (Split-Path (Split-Path $javaExe -Parent) -Parent)
        }
    }
    $which = Get-Command java -ErrorAction SilentlyContinue
    if ($which) {
        $verOut = & java -version 2>&1 | Out-String
        if ($verOut -match 'version "17(\.|")') {
            $javaPath = $which.Source
            return (Split-Path (Split-Path $javaPath -Parent) -Parent)
        }
    }
    return $null
}

function Add-UserPathEntry([string]$Entry) {
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    if ([string]::IsNullOrEmpty($userPath)) {
        [System.Environment]::SetEnvironmentVariable("Path", $Entry, "User")
        return
    }
    $parts = $userPath -split ";" | Where-Object { $_ -ne "" }
    if ($parts -contains $Entry) {
        return
    }
    [System.Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(";") + ";" + $Entry), "User")
}

Write-Host ("Repo root: {0}" -f $repoRoot) -ForegroundColor Green
if (-not (Test-Path -LiteralPath $androidDir)) {
    throw "android\ folder not found at $androidDir"
}

# --- JDK 17 ---
Write-Step "1/6 JDK 17"
$javaHome = Test-Java17 -JavaHomeCandidate $env:JAVA_HOME
if (-not $javaHome) {
    $javaHome = Test-Java17 -JavaHomeCandidate $jdkPortableDir
}
if (-not $javaHome) {
    $msJdk = "C:\Program Files\Microsoft\jdk-17*"
    $msMatch = Get-ChildItem "C:\Program Files\Microsoft" -Directory -Filter "jdk-17*" -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending |
        Select-Object -First 1
    if ($msMatch) {
        $javaHome = Test-Java17 -JavaHomeCandidate $msMatch.FullName
    }
}

if (-not $javaHome) {
    Write-Host "Installing Microsoft OpenJDK 17 via winget..."
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        & winget install --id Microsoft.OpenJDK.17 --accept-package-agreements --accept-source-agreements --disable-interactivity
        $msMatch = Get-ChildItem "C:\Program Files\Microsoft" -Directory -Filter "jdk-17*" -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            Select-Object -First 1
        if ($msMatch) {
            $javaHome = Test-Java17 -JavaHomeCandidate $msMatch.FullName
        }
    }
}

if (-not $javaHome) {
    Write-Host "Falling back to portable Temurin JDK 17..."
    New-Item -ItemType Directory -Force -Path $jdkPortableRoot | Out-Null
    if (-not (Test-Path -LiteralPath (Join-Path $jdkPortableDir "bin\java.exe"))) {
        Invoke-WebRequest -Uri $temurinZipUrl -OutFile $temurinZip -UseBasicParsing
        Expand-Archive -Path $temurinZip -DestinationPath $jdkPortableRoot -Force
    }
    $javaHome = Test-Java17 -JavaHomeCandidate $jdkPortableDir
}

if (-not $javaHome) {
    throw "JDK 17 not available after install attempts."
}
Write-Host ("JAVA_HOME: {0}" -f $javaHome) -ForegroundColor Green
$env:JAVA_HOME = $javaHome
$env:Path = "$(Join-Path $javaHome 'bin');$env:Path"

# --- cmdline-tools ---
Write-Step "2/6 Android cmdline-tools"
New-Item -ItemType Directory -Force -Path $sdkRoot | Out-Null
$latestDir = Join-Path $sdkRoot "cmdline-tools\latest"
$sdkmanager = Join-Path $latestDir "bin\sdkmanager.bat"
if (-not (Test-Path -LiteralPath $sdkmanager)) {
    Write-Host "Downloading Android cmdline-tools..."
    Invoke-WebRequest -Uri $cmdToolsUrl -OutFile $cmdToolsZip -UseBasicParsing
    $extractTmp = Join-Path $env:TEMP "android-cmdline-extract-hsk"
    if (Test-Path -LiteralPath $extractTmp) {
        Remove-Item -LiteralPath $extractTmp -Recurse -Force
    }
    Expand-Archive -Path $cmdToolsZip -DestinationPath $extractTmp -Force
    New-Item -ItemType Directory -Force -Path $latestDir | Out-Null
    Copy-Item -Path (Join-Path $extractTmp "cmdline-tools\*") -Destination $latestDir -Recurse -Force
}
if (-not (Test-Path -LiteralPath $sdkmanager)) {
    throw "sdkmanager.bat missing at $sdkmanager"
}
Write-Host ("sdkmanager: {0}" -f $sdkmanager) -ForegroundColor Green

# --- packages + licenses ---
Write-Step "3/6 SDK packages (platform-tools, android-35, build-tools 35.0.0)"
$licensesDir = Join-Path $sdkRoot "licenses"
New-Item -ItemType Directory -Force -Path $licensesDir | Out-Null
Set-Content -Path (Join-Path $licensesDir "android-sdk-license") -Value "24333f8a63b6825ea9c5514f83c2829b004d1fee" -NoNewline
Set-Content -Path (Join-Path $licensesDir "android-sdk-preview-license") -Value "84831b9409646a918e30573bab4c9c91346d8abd" -NoNewline

& $sdkmanager --sdk_root=$sdkRoot "platform-tools" "platforms;android-35" "build-tools;35.0.0"
if ($LASTEXITCODE -ne 0) {
    throw "sdkmanager failed with exit code $LASTEXITCODE"
}
Write-Host "SDK packages OK." -ForegroundColor Green

# --- user env ---
Write-Step "4/6 User environment variables"
[System.Environment]::SetEnvironmentVariable("ANDROID_HOME", $sdkRoot, "User")
[System.Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $sdkRoot, "User")
[System.Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome, "User")
Add-UserPathEntry (Join-Path $javaHome "bin")
Add-UserPathEntry (Join-Path $sdkRoot "platform-tools")
Add-UserPathEntry (Join-Path $sdkRoot "emulator")
Add-UserPathEntry (Join-Path $sdkRoot "cmdline-tools\latest\bin")
$env:ANDROID_HOME = $sdkRoot
$env:ANDROID_SDK_ROOT = $sdkRoot
Write-Host ("ANDROID_HOME: {0}" -f $sdkRoot) -ForegroundColor Green

# --- local.properties ---
Write-Step "5/6 android/local.properties"
$sdkDirEscaped = $sdkRoot.Replace("\", "\\")
$localProps = "sdk.dir=$sdkDirEscaped`n"
Set-Content -Path (Join-Path $androidDir "local.properties") -Value $localProps -Encoding ASCII -NoNewline
Write-Host ("Wrote {0}" -f (Join-Path $androidDir "local.properties")) -ForegroundColor Green

# --- Android Studio (optional) ---
Write-Step "6/6 Android Studio (optional)"
$studioInstalled = Test-Path -LiteralPath "${env:ProgramFiles}\Android\Android Studio\bin\studio64.exe"
if ($studioInstalled) {
    Write-Host "Android Studio already installed." -ForegroundColor Green
} elseif ($SkipAndroidStudio) {
    Write-Host "Skipping Android Studio (-SkipAndroidStudio)." -ForegroundColor DarkYellow
} elseif ($InstallAndroidStudio) {
    Write-Host "Installing Android Studio via winget..."
    & winget install --id Google.AndroidStudio --accept-package-agreements --accept-source-agreements --disable-interactivity
} else {
    Write-Host "Android Studio is optional (emulator / GUI). To install now:" -ForegroundColor DarkYellow
    Write-Host "  winget install Google.AndroidStudio" -ForegroundColor DarkYellow
    Write-Host "Or re-run: .\setup-android-sdk.ps1 -InstallAndroidStudio" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "Done. Open a new terminal (or restart Cursor) so ANDROID_HOME / JAVA_HOME apply." -ForegroundColor Green
Write-Host "Then: cd android && .\gradlew.bat assembleDebug" -ForegroundColor Green
