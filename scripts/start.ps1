# DS Quest 启动脚本
#   1. 找一个能用的 Python
#   2. 确认前端产物存在（没有就尝试构建）
#   3. 启动 FastAPI（同时托管前端页面），自动打开浏览器
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\common.ps1"
Set-Location $ProjectRoot

Write-Host ''
Write-Host '  DS Quest · 数据结构闯关' -ForegroundColor Magenta
Write-Host '  -----------------------------' -ForegroundColor DarkGray

$python = Find-DSQPython
if (-not $python) {
    Write-Host '  [x] 没找到可用的 Python 3.10+' -ForegroundColor Red
    Write-Host '      请先双击 setup.bat 安装依赖，或安装 Python 后重试。' -ForegroundColor Yellow
    Read-Host '按回车退出'
    exit 1
}
Write-Host "  Python : $python" -ForegroundColor DarkGray

# 检查依赖是否装好
$check = & $python -c "import sys;sys.path.insert(0,r'$ProjectRoot\backend\vendor');import fastapi,uvicorn;print('ok')" 2>&1
if ($check -notmatch 'ok') {
    Write-Host '  [x] 后端依赖没装好（找不到 fastapi / uvicorn）' -ForegroundColor Red
    Write-Host '      请先双击 setup.bat。' -ForegroundColor Yellow
    Read-Host '按回车退出'
    exit 1
}

# 前端产物检查
$dist = Join-Path $ProjectRoot 'frontend\dist\index.html'
if (-not (Test-Path $dist)) {
    Write-Host '  [!] 前端还没构建，正在尝试构建……' -ForegroundColor Yellow
    $buildScript = Join-Path $PSScriptRoot 'build.ps1'
    & $buildScript
    if (-not (Test-Path $dist)) {
        Write-Host '  [x] 前端构建失败。请先双击 setup.bat。' -ForegroundColor Red
        Read-Host '按回车退出'
        exit 1
    }
}

$port = 8000
if ($env:DSQ_PORT) { $port = [int]$env:DSQ_PORT }
$url = "http://127.0.0.1:$port"
Write-Host "  地址   : $url" -ForegroundColor Cyan
Write-Host '  停止   : 在这个窗口按 Ctrl + C' -ForegroundColor DarkGray
Write-Host ''

Invoke-DSQPython -Exe $python -Arguments @('backend\run.py')
