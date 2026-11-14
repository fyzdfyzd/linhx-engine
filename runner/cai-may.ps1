# Cài máy công ty nhận việc qua hàng đợi GitHub (nhánh hang-doi).
# Ví dụ: powershell -ExecutionPolicy Bypass -File runner\cai-may.ps1 -May may-1
# - Clone repo vào D:\linhx\hang-doi (KHÔNG dùng D:\LINHX\LINHX-ENGINE vì trùng repo đang chạy thợ ENGINE trên Windows).
# - Tạo runner\tho.env (không ghi bí mật) và giới hạn agy tự chạy lệnh trong D:\linhx.
# - Đăng ký Task Scheduler chạy MỖI PHÚT, CHỈ KHI USER ĐÃ ĐĂNG NHẬP (Interactive), ẩn qua chay-an-tho.vbs.
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$May,

    [string]$ThuMuc = "D:\linhx\hang-doi",
    [string]$RepoUrl = "https://github.com/fyzdfyzd/linhx-engine.git",
    [string]$GocGioiHan = "D:\linhx",
    [string]$ThuMucDrive = "G:\My Drive\LINHX-VIEC",
    [string]$ThuMucLog = "D:\linhx\linhx-runner\log",
    [string]$TenLich = "LINHX-HangDoi",
    [string]$AgyCmd = "",
    [int]$SoPhieu = 1,
    [switch]$KhongChayNgay
)

$ErrorActionPreference = "Stop"

$mayChuan = $May.Trim().ToLowerInvariant()
if ($mayChuan -notmatch '^[a-z0-9][a-z0-9_-]*$' -or @("bat-ky", "all", "tat-ca") -contains $mayChuan) {
    throw "Tên máy không hợp lệ: '$May' (dùng may-1, may-2, may-3, ...; không dùng bat-ky)."
}
if ($SoPhieu -lt 1) {
    throw "SoPhieu phải >= 1 (nhận được: $SoPhieu)."
}

function ChuanHoaSoSanh([string]$p) {
    $s = ($p.Trim() -replace '/', '\')
    while ($s.Contains('\\')) { $s = $s.Replace('\\', '\') }
    if ($s.Length -gt 3) { $s = $s.TrimEnd('\') }
    return $s
}

$rawSoSanh = ChuanHoaSoSanh $ThuMuc
$camRaw = "D:\LINHX\LINHX-ENGINE"
if ($rawSoSanh.Equals($camRaw, [System.StringComparison]::OrdinalIgnoreCase) -or
    $rawSoSanh.StartsWith("$camRaw\", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "KHÔNG dùng '$ThuMuc': trùng '$camRaw' (Windows không phân biệt hoa thường, trùng repo đang chạy thợ ENGINE). Hãy dùng D:\linhx\hang-doi."
}

$thuMucChuan = [System.IO.Path]::GetFullPath($ThuMuc).TrimEnd('\', '/')
$gocChuan = [System.IO.Path]::GetFullPath($GocGioiHan).TrimEnd('\', '/')
$sep = [string][System.IO.Path]::DirectorySeparatorChar

$camFull = ChuanHoaSoSanh $thuMucChuan
if ($camFull.Equals($camRaw, [System.StringComparison]::OrdinalIgnoreCase) -or
    $camFull.StartsWith("$camRaw\", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "KHÔNG dùng '$ThuMuc': trùng '$camRaw' (Windows không phân biệt hoa thường, trùng repo đang chạy thợ ENGINE). Hãy dùng D:\linhx\hang-doi."
}

if ($thuMucChuan.Equals($gocChuan, [System.StringComparison]::OrdinalIgnoreCase) -or
    -not $thuMucChuan.StartsWith("$gocChuan$sep", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Thư mục cài '$thuMucChuan' phải nằm bên trong gốc giới hạn '$gocChuan' (ví dụ D:\linhx\hang-doi)."
}

New-Item -ItemType Directory -Force -Path $gocChuan | Out-Null
$thuMucCha = Split-Path -Parent $thuMucChuan
if ($thuMucCha) {
    New-Item -ItemType Directory -Force -Path $thuMucCha | Out-Null
}

$chamGit = Join-Path $thuMucChuan ".git"
$tepRunnerPy = Join-Path (Join-Path $thuMucChuan "runner") "linhx_runner.py"
if (Test-Path -LiteralPath $chamGit) {
    if (-not (Test-Path -LiteralPath $tepRunnerPy)) {
        throw "Thư mục '$thuMucChuan' đã có .git nhưng thiếu runner\linhx_runner.py."
    }
} else {
    if ((Test-Path -LiteralPath $thuMucChuan) -and (@(Get-ChildItem -Force -LiteralPath $thuMucChuan).Count -gt 0)) {
        throw "Thư mục '$thuMucChuan' đã tồn tại và không rỗng nhưng chưa phải git repo."
    }
    & git clone $RepoUrl $thuMucChuan
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $chamGit)) {
        throw "git clone '$RepoUrl' vào '$thuMucChuan' thất bại (mã $LASTEXITCODE)."
    }
    if (-not (Test-Path -LiteralPath $tepRunnerPy)) {
        throw "Repo vừa clone tại '$thuMucChuan' thiếu runner\linhx_runner.py."
    }
}

$thuMucRunner = Join-Path $thuMucChuan "runner"
$thuMucViecGoc = Join-Path $thuMucRunner "viec"
$thuMucLamViec = Join-Path $thuMucViecGoc "lam-viec"
New-Item -ItemType Directory -Force -Path $thuMucLamViec | Out-Null
New-Item -ItemType Directory -Force -Path $ThuMucLog | Out-Null

$utf8KhongBom = New-Object System.Text.UTF8Encoding($false)

$gocMacDinh = "D:\linhx"
$thuMucMacDinh = "D:\linhx\hang-doi"
$tepSettingsRepo = Join-Path $thuMucRunner "agy-settings.json"
$dungSettingsRepo = (
    (ChuanHoaSoSanh $gocChuan).Equals($gocMacDinh, [System.StringComparison]::OrdinalIgnoreCase) -and
    (ChuanHoaSoSanh $thuMucChuan).Equals($thuMucMacDinh, [System.StringComparison]::OrdinalIgnoreCase) -and
    (Test-Path -LiteralPath $tepSettingsRepo)
)

if ($dungSettingsRepo) {
    $tepSettings = $tepSettingsRepo
} else {
    $tepSettings = Join-Path $thuMucViecGoc "agy-settings.json"
    $gocPosix = $gocChuan.Replace('\', '/')
    $gocWin = $gocChuan.Replace('/', '\')
    $envPosix = (Join-Path $thuMucRunner "tho.env").Replace('\', '/')
    $envWin = (Join-Path $thuMucRunner "tho.env").Replace('/', '\')
    $cauHinhAgy = [ordered]@{
        agentMode   = "auto"
        permissions = [ordered]@{
            allow = @(
                "command(*)",
                "read_file($gocPosix)",
                "write_file($gocPosix)",
                "edit_file($gocPosix)",
                "read_file($gocWin)",
                "write_file($gocWin)",
                "edit_file($gocWin)",
                "mcp(browsentic/*)",
                "mcp(*)"
            )
            deny  = @(
                "read_file($envPosix)",
                "write_file($envPosix)",
                "edit_file($envPosix)",
                "read_file($envWin)",
                "write_file($envWin)",
                "edit_file($envWin)",
                "write_file(D:/LINHX/LINHX-ENGINE)",
                "edit_file(D:/LINHX/LINHX-ENGINE)",
                "write_file(D:\LINHX\LINHX-ENGINE)",
                "edit_file(D:\LINHX\LINHX-ENGINE)"
            )
        }
    }
    $jsonSettings = ($cauHinhAgy | ConvertTo-Json -Depth 5) + "`n"
    [System.IO.File]::WriteAllText($tepSettings, $jsonSettings, $utf8KhongBom)
}

function BaoThamSo([string]$giaTri) {
    if ($giaTri -match '\s') { return "`"$giaTri`"" }
    return $giaTri
}

$lenhAgy = ""
if ($AgyCmd -and $AgyCmd.Trim()) {
    $lenhAgy = $AgyCmd.Trim()
} elseif ($env:USERPROFILE) {
    $agyUngVien = Join-Path $env:USERPROFILE ".gemini\bin\agy.exe"
    if (Test-Path -LiteralPath $agyUngVien) {
        $lenhAgy = $agyUngVien
    }
}
if (-not $lenhAgy) {
    $lenhAgy = "agy"
}

$agyArgs = "--output-format json --mode auto --sandbox --add-dir $(BaoThamSo $gocChuan) --settings $(BaoThamSo $tepSettings) --print-timeout 2400s"
$tepThoEnv = Join-Path $thuMucRunner "tho.env"
$noiDungEnv = @(
    "# Cau hinh tho hang-doi GitHub (tao boi runner/cai-may.ps1). KHONG commit file nay.",
    "LINHX_NGUON=github",
    "LINHX_THO=$mayChuan",
    "LINHX_REPO_HANG_DOI=$thuMucChuan",
    "LINHX_NHANH_HANG_DOI=hang-doi",
    "LINHX_REMOTE_HANG_DOI=origin",
    "LINHX_THU_MUC=$thuMucLamViec",
    "LINHX_GIOI_HAN_THU_MUC=$gocChuan",
    "LINHX_DRIVE=$ThuMucDrive",
    "LINHX_LOG_DIR=$ThuMucLog",
    "LINHX_SO_PHIEU=$SoPhieu",
    "LINHX_TRAN_PHUT=40",
    "LINHX_KHONG_TIEN_PHUT=10",
    "LINHX_RAM_TOI_THIEU_GB=1.5",
    "AGY_CMD=$lenhAgy",
    "AGY_ARGS=$agyArgs"
) -join "`n"
[System.IO.File]::WriteAllText($tepThoEnv, $noiDungEnv + "`n", $utf8KhongBom)

$tepVbs = Join-Path $thuMucRunner "chay-an-tho.vbs"
if (-not (Test-Path -LiteralPath $tepVbs)) {
    throw "Thiếu file chạy ẩn: '$tepVbs'."
}

$nguoiDung = if ($env:USERNAME) { $env:USERNAME } elseif ($env:USER) { $env:USER } else { [Environment]::UserName }
$hanhDong = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "//B `"$tepVbs`" --mot-lan" -WorkingDirectory $thuMucRunner
$kichHoat = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$chuThe = New-ScheduledTaskPrincipal -UserId $nguoiDung -LogonType Interactive -RunLevel Limited
$caiDat = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask -TaskName $TenLich -Action $hanhDong -Trigger $kichHoat -Principal $chuThe -Settings $caiDat -Force | Out-Null
if (-not $KhongChayNgay) {
    Start-ScheduledTask -TaskName $TenLich
}

$tepPingMau = Join-Path (Join-Path $thuMucRunner "phieu-mau") "ping.md"
Write-Output "Đã cài $mayChuan tại $thuMucChuan (lịch $TenLich chạy mỗi 1 phút, Interactive, ẩn qua chay-an-tho.vbs). Phiếu mẫu: $tepPingMau"
