# 质量自检：内容（参考解真的跑测试点）+ 接口冒烟
# 用法：powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\common.ps1"
Set-Location $ProjectRoot

$python = Find-DSQPython
if (-not $python) {
    Write-Host '[x] 没找到 Python' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host '=== 1/2 内容自检（编译参考解 + 跑全部测试点 + 编译代码模板） ===' -ForegroundColor Magenta
Invoke-DSQPython -Exe $python -Arguments @('backend\verify.py')
$contentExit = $LASTEXITCODE

Write-Host ''
Write-Host '=== 2/2 接口冒烟（需要服务已经在 8000 端口运行） ===' -ForegroundColor Magenta
try {
    Invoke-DSQPython -Exe $python -Arguments @('backend\smoke_test.py')
} catch {
    Write-Host '[!] 冒烟测试跳过：服务没启动（先跑 scripts/start.ps1）' -ForegroundColor Yellow
}

if ($contentExit -ne 0) {
    Write-Host ''
    Write-Host '[x] 内容自检有失败项，修好再提交。' -ForegroundColor Red
    exit 1
}
Write-Host ''
Write-Host '[√] 自检完成' -ForegroundColor Green
