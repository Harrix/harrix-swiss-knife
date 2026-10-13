# Upload deploy/harrix-stack to the VPS and run install.sh.
# Usage from the repo root:
#   powershell -File deploy/harrix-stack/scripts/push-stack.ps1
param(
    [string]$HostAlias = "harrix-vps",
    [string]$RemoteDir = "/opt/harrix-stack"
)

$ErrorActionPreference = "Stop"
$LocalStack = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Upload = "/tmp/harrix-stack-upload"

# PowerShell appends CRLF to piped text, so the remote side strips `\r` before bash runs it.
function Invoke-Remote([string]$Script) {
    $Script | ssh -o BatchMode=yes $HostAlias "tr -d '\r' | bash -s"
    if ($LASTEXITCODE -ne 0) { throw "Remote command failed on $HostAlias" }
}

Invoke-Remote "rm -rf $Upload && mkdir -p $Upload $RemoteDir"

$items = @("docker-compose.yml", "Caddyfile", ".env.example", "README.md", "api", "git", "host", "scripts", "www-seed")
foreach ($item in $items) {
    scp -r -q (Join-Path $LocalStack $item) "${HostAlias}:$Upload/"
    if ($LASTEXITCODE -ne 0) { throw "Upload of $item failed" }
}

Invoke-Remote @"
set -e
find $Upload -name __pycache__ -type d -prune -exec rm -rf {} +
cp -a $Upload/. $RemoteDir/
find $RemoteDir -type f \( -name '*.sh' -o -name post-receive -o -name Caddyfile -o -name '*.yml' -o -name .env.example -o -name '*.service' -o -name '*.example' \) -exec sed -i 's/\r`$//' {} +
chmod +x $RemoteDir/scripts/*.sh $RemoteDir/git/post-receive $RemoteDir/host/login-alert/*.sh
STACK_DIR=$RemoteDir bash $RemoteDir/scripts/install.sh </dev/null
bash $RemoteDir/host/login-alert/install.sh </dev/null
"@
