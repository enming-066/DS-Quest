# 一次性安装脚本：装后端依赖 + 前端依赖 + 构建前端
# 用法：双击 setup.bat，或者 powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
param([switch]$OnlyFrontend)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\common.ps1"
Set-Location $ProjectRoot

Write-Host ''
Write-Host '  DS Quest · 安装依赖' -ForegroundColor Magenta
Write-Host '  -----------------------------' -ForegroundColor DarkGray

# ---------------------------------------------------------------- 后端
if (-not $OnlyFrontend) {
    $python = Find-DSQPython
    if (-not $python) {
        Write-Host '  [x] 没找到 Python 3.10+。请先安装 Python 并勾选 Add to PATH。' -ForegroundColor Red
        Read-Host '按回车退出'
        exit 1
    }
    Write-Host "  Python : $python" -ForegroundColor DarkGray
    Set-Content -Path (Join-Path $ProjectRoot 'backend\.python-path') -Value $python -Encoding utf8

    Write-Host '  [1/3] 安装后端依赖到 backend/vendor ……' -ForegroundColor Cyan
    $pipArgs = @('-m', 'pip', 'install', '--target', (Join-Path $ProjectRoot 'backend\vendor'),
                 '--disable-pip-version-check', '--no-input', '-r',
                 (Join-Path $ProjectRoot 'backend\requirements.txt'))
    & $python @pipArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host '  [x] 后端依赖安装失败，检查网络或代理。' -ForegroundColor Red
        Read-Host '按回车退出'
        exit 1
    }
    Write-Host '  [√] 后端依赖就绪' -ForegroundColor Green
} else {
    Write-Host '  [1/3] 跳过后端依赖' -ForegroundColor DarkGray
}

# ---------------------------------------------------------------- 前端
function Find-Node {
    $cmd = Get-Command node -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $bundled = 'C:\Users\Lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe'
    if (Test-Path $bundled) { return $bundled }
    return $null
}

$node = Find-Node
if (-not $node) {
    Write-Host '  [x] 没找到 Node.js，无法安装/构建前端。' -ForegroundColor Red
    Write-Host '      安装 Node.js 18+（https://nodejs.org）后重试。' -ForegroundColor Yellow
    Read-Host '按回车退出'
    exit 1
}

$pnpmCmd = Get-Command pnpm -ErrorAction SilentlyContinue
$pnpmMjs = 'C:\Users\Lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\pnpm\bin\pnpm.mjs'
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue

$pmExe = $null
$pmArgs = @()
if ($pnpmCmd) {
    $pmExe = $pnpmCmd.Source
} elseif (Test-Path $pnpmMjs) {
    $pmExe = $node
    $pmArgs = @($pnpmMjs)
} elseif ($npmCmd) {
    $pmExe = $npmCmd.Source
} else {
    Write-Host '  [x] 没找到 pnpm / npm。' -ForegroundColor Red
    Read-Host '按回车退出'
    exit 1
}

Push-Location (Join-Path $ProjectRoot 'frontend')
try {
    Write-Host '  [2/3] 安装前端依赖 ……' -ForegroundColor Cyan
    & $pmExe @pmArgs install --store-dir (Join-Path $ProjectRoot '.tmp\pnpm-store')
    if ($LASTEXITCODE -ne 0) {
        # pnpm 对 esbuild 的构建脚本有拦截提示，但通常不影响构建
        Write-Host '  [!] 安装过程有警告，继续尝试构建' -ForegroundColor Yellow
    }

    Write-Host '  [3/3] 构建前端 ……' -ForegroundColor Cyan
    $vite = Join-Path $ProjectRoot 'frontend\node_modules\vite\bin\vite.js'
    & $node $vite build
    if ($LASTEXITCODE -ne 0) {
        Write-Host '  [x] 前端构建失败。' -ForegroundColor Red
        Read-Host '按回车退出'
        exit 1
    }
} finally {
    Pop-Location
}

Write-Host ''
Write-Host '  [√] 全部就绪。现在双击 start.bat 就能用。' -ForegroundColor Green
Write-Host ''
Read-Host '按回车退出'
