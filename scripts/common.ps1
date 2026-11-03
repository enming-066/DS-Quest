# 在项目目录里找到并验证一个可用的 Python 解释器，结果写进 backend/.python-path
# 被 start.ps1 / setup.ps1 / verify.ps1 共用（dot-source 引入）

$script:ProjectRoot = Split-Path -Parent $PSScriptRoot

function Test-PythonCandidate {
    param([string]$Exe, [string[]]$PrefixArgs = @())
    if (-not $Exe) { return $false }
    try {
        $out = & $Exe @PrefixArgs -c "import sys;print(sys.version_info[0]*100+sys.version_info[1])" 2>$null
        if ($LASTEXITCODE -ne 0) { return $false }
        return ([int]$out.Trim() -ge 310)
    } catch {
        return $false
    }
}

function Find-DSQPython {
    $marker = Join-Path $ProjectRoot 'backend\.python-path'
    if (Test-Path $marker) {
        $saved = (Get-Content $marker -Raw).Trim()
        if (Test-PythonCandidate $saved) { return $saved }
    }

    $candidates = @()
    if ($env:DSQ_PYTHON) { $candidates += @{ Exe = $env:DSQ_PYTHON; Args = @() } }

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) { $candidates += @{ Exe = $pyLauncher.Source; Args = @('-3') } }

    foreach ($name in @('python', 'python3')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { $candidates += @{ Exe = $cmd.Source; Args = @() } }
    }

    # 这个项目最初是在 DSH 自带的 Python 上装的依赖，作为兜底
    $bundled = 'C:\Users\Lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
    if (Test-Path $bundled) { $candidates += @{ Exe = $bundled; Args = @() } }

    foreach ($item in $candidates) {
        if (Test-PythonCandidate $item.Exe $item.Args) {
            return $item.Exe
        }
    }
    return $null
}

function Invoke-DSQPython {
    param([string]$Exe, [string[]]$Arguments)
    # Python 在 Windows 控制台默认用 GBK，强制 UTF-8，免得中文变成乱码
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONPATH = "$ProjectRoot\backend\vendor;$ProjectRoot\backend"
    & $Exe @Arguments
}
