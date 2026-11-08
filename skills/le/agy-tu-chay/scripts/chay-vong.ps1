# chay-vong.ps1 · một lượt tự chạy (máy công ty). Không cần Claude.
# Mỗi lượt: lấy phiếu kế tiếp → agy làm → máy kiểm → agy phiên MỚI chấm → ghi đạt/trượt → viết báo cáo quản trị.
# Gọi tay:   powershell -File chay-vong.ps1 -Viec D:\LINHX\LAB\LAB106...\chay-that\<du-an>
# Lịch 20 phút: powershell -File dang-ky-lich.ps1 -Viec <thu-muc>
param(
  [Parameter(Mandatory = $true)][string]$Viec,
  [string]$LenhAgy = "$env:USERPROFILE\.gemini\bin\agy.exe",
  [string]$ModelCham = "",          # model khác thợ cho người chấm "gemini" (trống = mặc định agy)
  [switch]$ToanQuyen                # chỉ bật khi Linh cho agy toàn quyền
)
$ErrorActionPreference = "Stop"
$KH = Join-Path $PSScriptRoot "ke_hoach.py"
$SKILLS = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent   # thư mục chứa các skill (.agents/skills)
Set-Location $Viec
New-Item -ItemType Directory -Force -Path ".vong\log", "cham" | Out-Null
$khoa = ".vong\luot.lock"
if (Test-Path $khoa) { if (((Get-Date) - (Get-Item $khoa).LastWriteTime).TotalMinutes -lt 60) { exit 0 } }
"$(Get-Date -Format s)" | Set-Content $khoa
function Ghi($s) { "$(Get-Date -Format 'MM-dd HH:mm') $s" | Add-Content -Encoding utf8 ".vong\NHAT-KY.md" }
function ChayAgy($tep, $nhan, $model) {
  $ts = @("-p", "`"Doc va lam theo dung file $tep (tieng Viet). Thu muc lam viec la thu muc hien tai.`"", "--output-format", "json")
  if ($ToanQuyen) { $ts += "--dangerously-skip-permissions" }
  if ($model) { $ts += @("--model", $model) }
  $p = Start-Process -FilePath $LenhAgy -WorkingDirectory $Viec -NoNewWindow -PassThru -Wait -ArgumentList $ts `
       -RedirectStandardOutput ".vong\log\$nhan.out" -RedirectStandardError ".vong\log\$nhan.err"
  return $p.ExitCode
}
try {
  $kh = Get-Content ke-hoach.json -Raw -Encoding utf8 | ConvertFrom-Json
  $phieu = $kh.phieu | Where-Object { $_.trang_thai -eq "dang" } | Select-Object -First 1
  if (-not $phieu) {
    $ra = & py -3 $KH tiep . 2>&1
    $ma = [regex]::Match(($ra -join "`n"), "PHIẾU (P\d+)").Groups[1].Value
    if (-not $ma) { Ghi ("không giao: " + ($ra | Select-Object -First 1)); & py -3 $KH bao-cao . | Out-Null; exit 0 }
    $kh = Get-Content ke-hoach.json -Raw -Encoding utf8 | ConvertFrom-Json
    $phieu = $kh.phieu | Where-Object { $_.ma -eq $ma }
    # 1. THỢ
    @"
# Phiếu $ma (bạn là THỢ)
$($ra -join "`n")

Luật: đọc skill linhx-chuan trước (luật 1–9). Chỉ làm đúng phiếu này, xong trong trần phút.
Mọi số gắn [BC-xxx]; câu trích phải có nguyên văn trong bang-chung/. Sửa STATUS.md sau mỗi file.
Không ghi đè file có sẵn trừ khi phiếu nói rõ. Không tự chấm mình đạt. Xong thì dừng.
"@ | Set-Content -Encoding utf8 ".vong\PHIEU.md"
    Ghi "giao thợ $ma"
    ChayAgy ".vong/PHIEU.md" "tho-$ma" "" | Out-Null
  }
  $ma = $phieu.ma
  # 2. MÁY KIỂM
  $lk = $phieu.lenh_kiem.Replace("{SKILLS}", $SKILLS); $mayDat = $true; $mayRa = ""
  if ($lk -match "^python (.+)$") { $mayRa = (& py -3 ($Matches[1] -split " ") 2>&1) -join "`n"; $mayDat = ($LASTEXITCODE -eq 0) }
  elseif ($lk -match "^có file (.+)$") { $mayDat = Test-Path $Matches[1]; $mayRa = "Test-Path $($Matches[1]) = $mayDat" }
  if (-not $mayDat) { & py -3 $KH xong . $ma --truot ("máy kiểm: " + ($mayRa -split "`n" | Select-Object -First 4) -join " | ") | Out-Null; Ghi "$ma trượt máy kiểm"; & py -3 $KH bao-cao . | Out-Null; exit 0 }
  # 3. NGƯỜI CHẤM (phiên mới, khác thợ)
  if ($phieu.nguoi_cham -eq "linh") { Ghi "$ma chờ Linh chấm"; & py -3 $KH bao-cao . | Out-Null; exit 0 }
  @"
# Chấm phiếu $ma (bạn là NGƯỜI CHẤM, không phải thợ, không sửa bài)
Việc của thợ: $($phieu.viec)
Đầu ra cần chấm: $($phieu.dau_ra -join ", ")
Tiêu chí: $($phieu.tieu_chi -join "; ")
Mở thang skill linhx-chuan/cham.md và tham chiếu trong THAM-CHIEU.md TRƯỚC khi đọc bài. Tự mở 5 số ngẫu nhiên đối chiếu bang-chung/.
Chỉ ghi lỗi chặn hoặc nặng, tối đa 3 lỗi.
Ghi đúng một file cham/$ma.json: {"nguoi_cham":"...","dat":true|false,"diem":{...},"loi":[{"muc":"...","muc_do":"chan|nang","sua":"..."}]}
"@ | Set-Content -Encoding utf8 ".vong\CHAM.md"
  $model = if ($phieu.nguoi_cham -eq "gemini") { $ModelCham } else { "" }
  Remove-Item "cham\$ma.json" -ErrorAction SilentlyContinue
  ChayAgy ".vong/CHAM.md" "cham-$ma" $model | Out-Null
  if (-not (Test-Path "cham\$ma.json")) { & py -3 $KH xong . $ma --truot "người chấm không ghi phiếu" | Out-Null; Ghi "$ma thiếu phiếu chấm"; exit 0 }
  $c = Get-Content "cham\$ma.json" -Raw -Encoding utf8 | ConvertFrom-Json
  Copy-Item "cham\$ma.json" "cham\$ma-v$($phieu.vong + 1).json" -Force
  if ($c.dat) { & py -3 $KH xong . $ma --dat | Out-Null; Ghi "$ma ĐẠT" }
  else {
    $loi = ($c.loi | Select-Object -First 3 | ForEach-Object { "$($_.muc): $($_.sua)" }) -join " | "
    & py -3 $KH xong . $ma --truot $loi | Out-Null; Ghi "$ma trượt chấm: $loi"
  }
  & py -3 $KH bao-cao . | Out-Null
}
finally { Remove-Item $khoa -ErrorAction SilentlyContinue }
