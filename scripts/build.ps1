# 构建前端（生成 frontend/dist，后端会直接托管它）
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\common.ps1"
Set-Location (Join-Path $ProjectRoot 'frontend')

function Find-Node {
    $cmd = Get-Command node -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $bundled = 'C:\Users\Lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe'
    if (Test-Path $bundled) { return $bundled }
    return $null
}

$node = Find-Node
if (-not $node) {
    Write-Host '  [x] 没找到 Node.js，无法构建前端。' -ForegroundColor Red
    Write-Host '      安装 Node.js 18+ 后重试，或者直接找我要一份构建好的 dist。' -ForegroundColor Yellow
    exit 1
}

$vite = Join-Path $ProjectRoot 'frontend\node_modules\vite\bin\vite.js'
if (-not (Test-Path $vite)) {
    Write-Host '  [!] 前端依赖还没装，先执行 pnpm install ……' -ForegroundColor Yellow
    $install = Join-Path $PSScriptRoot 'setup.ps1'
    & $install -OnlyFrontend
}

Write-Host '  正在构建前端……' -ForegroundColor DarkGray
Push-Location (Join-Path $ProjectRoot 'frontend')
try {
    & $node $vite build
} finally {
    Pop-Location
}
if ($LASTEXITCODE -ne 0) {
    Write-Host '  [x] 构建失败，看上面的报错。' -ForegroundColor Red
    exit 1
}
Write-Host '  [√] 前端构建完成：frontend/dist' -ForegroundColor Green
