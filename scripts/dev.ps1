# 开发模式：后端热重载（8000） + Vite 前端（5173）
# 改前端代码会即时刷新；改后端代码会自动重启。
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\common.ps1"
Set-Location $ProjectRoot

$python = Find-DSQPython
if (-not $python) {
    Write-Host '[x] 没找到 Python' -ForegroundColor Red
    exit 1
}

$node = (Get-Command node -ErrorAction SilentlyContinue).Source
if (-not $node) {
    $bundled = 'C:\Users\Lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe'
    if (Test-Path $bundled) { $node = $bundled }
}
if (-not $node) {
    Write-Host '[x] 没找到 Node.js' -ForegroundColor Red
    exit 1
}

Write-Host '后端：http://127.0.0.1:8000（--reload）' -ForegroundColor Cyan
Write-Host '前端：http://127.0.0.1:5173' -ForegroundColor Cyan
Write-Host ''

$backend = Start-Process -FilePath $python `
    -ArgumentList @('backend\run.py', '--no-browser', '--reload') `
    -WorkingDirectory $ProjectRoot -PassThru -WindowStyle Normal

Start-Sleep -Seconds 2

Push-Location (Join-Path $ProjectRoot 'frontend')
try {
    & $node (Join-Path $ProjectRoot 'frontend\node_modules\vite\bin\vite.js') --host 127.0.0.1
} finally {
    Pop-Location
    if (-not $backend.HasExited) { Stop-Process -Id $backend.Id -Force }
}
