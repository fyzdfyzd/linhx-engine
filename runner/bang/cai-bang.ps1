# Cai bang theo doi web cho hang doi GitHub (nhanh hang-doi), chay thuong truc tren cong 8090.
# - Dang ky Task Scheduler chay khi dang nhap (AtLogOn), an qua chay-an-bang.vbs.
# - Mo cong 8090 tren tuong lua Windows cho mang noi bo (Private).
param(
    [int]$Cong = 8090,
    [string]$ThuMucClone = "C:\linhx\bang-hang-doi",
    [string]$RepoUrl = "https://github.com/fyzdfyzd/linhx-engine.git",
    [string]$TenLich = "LINHX-Bang",
    [string]$TenLuatTuongLua = "LINHX-Bang-8090",
    [string]$TepLog = "C:\linhx\bang-hang-doi.log",
    [switch]$KhongChayNgay,
    [switch]$KhongMoTuongLua
)

$ErrorActionPreference = "Stop"

if ($Cong -lt 1 -or $Cong -gt 65535) {
    throw "Cong khong hop le: $Cong (phai trong khoang 1..65535)."
}

$thuMucBang = Split-Path -Parent $MyInvocation.MyCommand.Path
$tepBangPy = Join-Path $thuMucBang "bang.py"
$tepVbs = Join-Path $thuMucBang "chay-an-bang.vbs"

if (-not (Test-Path -LiteralPath $tepBangPy)) {
    throw "Thieu file bang.py tai '$tepBangPy'."
}
if (-not (Test-Path -LiteralPath $tepVbs)) {
    throw "Thieu file chay an '$tepVbs'."
}

$chaClone = Split-Path -Parent ([System.IO.Path]::GetFullPath($ThuMucClone))
if ($chaClone) {
    New-Item -ItemType Directory -Force -Path $chaClone | Out-Null
}
$chaLog = Split-Path -Parent ([System.IO.Path]::GetFullPath($TepLog))
if ($chaLog) {
    New-Item -ItemType Directory -Force -Path $chaLog | Out-Null
}

# 1. Mo cong tren tuong lua cho mang noi bo (Private)
if (-not $KhongMoTuongLua) {
    try {
        Remove-NetFirewallRule -Name $TenLuatTuongLua -ErrorAction SilentlyContinue
        New-NetFirewallRule `
            -Name $TenLuatTuongLua `
            -DisplayName "LINHX Bang Web ($Cong)" `
            -Direction Inbound `
            -Protocol TCP `
            -LocalPort $Cong `
            -Profile Private `
            -Action Allow `
            -ErrorAction Stop | Out-Null
    } catch {
        $laQuanTri = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
            [Security.Principal.WindowsBuiltInRole]::Administrator
        )
        if (-not $laQuanTri) {
            $tenAnToan = $TenLuatTuongLua.Replace("'", "''")
            $lenhNangQuyen = "Remove-NetFirewallRule -Name '$tenAnToan' -ErrorAction SilentlyContinue; New-NetFirewallRule -Name '$tenAnToan' -DisplayName 'LINHX Bang Web ($Cong)' -Direction Inbound -Protocol TCP -LocalPort $Cong -Profile Private -Action Allow -ErrorAction Stop | Out-Null"
            $proc = Start-Process -FilePath "powershell.exe" -Verb RunAs -WindowStyle Hidden -Wait -PassThru -ArgumentList @(
                "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", $lenhNangQuyen
            )
            if ($proc.ExitCode -ne 0) {
                throw "Khong mo duoc cong tuong lua $Cong (ma thoat $($proc.ExitCode))."
            }
        } else {
            throw
        }
    }
}

# 2. Dang ky Task Scheduler chay khi dang nhap, an qua chay-an-bang.vbs
$nguoiDung = if ($env:USERNAME) { $env:USERNAME } elseif ($env:USER) { $env:USER } else { [Environment]::UserName }
$thamSoVbs = "//B `"$tepVbs`" --cong $Cong --clone `"$ThuMucClone`" --repo `"$RepoUrl`" --log `"$TepLog`""

$hanhDong = New-ScheduledTaskAction -Execute "wscript.exe" -Argument $thamSoVbs -WorkingDirectory $thuMucBang
$kichHoat = New-ScheduledTaskTrigger -AtLogOn -User $nguoiDung
$chuThe = New-ScheduledTaskPrincipal -UserId $nguoiDung -LogonType Interactive -RunLevel Limited
$caiDat = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 99 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $TenLich -Action $hanhDong -Trigger $kichHoat -Principal $chuThe -Settings $caiDat -Force | Out-Null

if (-not $KhongChayNgay) {
    if (Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue) {
        $dangNghe = Get-NetTCPConnection -LocalPort $Cong -State Listen -ErrorAction SilentlyContinue
        foreach ($ketNoi in @($dangNghe)) {
            if ($ketNoi.OwningProcess -and $ketNoi.OwningProcess -gt 4) {
                Stop-Process -Id $ketNoi.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
        if ($dangNghe) {
            Start-Sleep -Milliseconds 400
        }
    }
    Start-ScheduledTask -TaskName $TenLich
}

$ipNoiBo = "127.0.0.1"
if (Get-Command Get-NetIPAddress -ErrorAction SilentlyContinue) {
    $ungVienIp = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -ne "127.0.0.1" -and $_.IPAddress -notlike "169.254.*" -and $_.PrefixOrigin -ne "WellKnown" } |
        Select-Object -First 1 -ExpandProperty IPAddress
    if ($ungVienIp) {
        $ipNoiBo = $ungVienIp
    }
}

Write-Output "Da cai $TenLich chay khi dang nhap (an qua chay-an-bang.vbs), mo cong $Cong (Private). Dia chi: http://${ipNoiBo}:$Cong (log: $TepLog)"
