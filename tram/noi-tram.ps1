# Noi mot may vao tram giao viec tren may 2 (Tailscale). PowerShell "Run as administrator":
#   powershell -ExecutionPolicy Bypass -File noi-tram.ps1 -May may-3 -ThuMuc C:\linhx
#   (may-1 / may-3 / may-4; may-4 = MSI, chi nhan phieu dich danh)
param([Parameter(Mandatory)][ValidateSet("may-1","may-3","may-4")][string]$May,
      [Parameter(Mandatory)][string]$ThuMuc,
      [string]$QuaLan = "")   # vd -QuaLan 192.168.1.136: bo Tailscale, noi tram qua LAN van phong
$ErrorActionPreference = "Stop"
function Dat($m) { Write-Host "DAT   $m" -F Green }
function Loi($m) { Write-Host "LOI   $m" -F Red; exit 1 }
$ts = "C:\Program Files\Tailscale\tailscale.exe"
$Tram = if ($QuaLan) { "git://$QuaLan/linhx-engine.git" } else { "git://may-2/linhx-engine.git" }
$Repo = Join-Path $ThuMuc "hang-doi"

# 1. Cong cu
foreach ($c in "git","python") { if (-not (Get-Command $c -EA SilentlyContinue)) { Loi "Thieu $c, cai roi chay lai" } }
Dat "Co git va python"

# 2. Tailscale (bo qua khi -QuaLan)
if ($QuaLan) { Dat "Che do LAN: bo Tailscale, tram = $Tram" } else {
if (-not (Test-Path $ts) -and (Get-Command winget -EA SilentlyContinue)) {
  winget install --id Tailscale.Tailscale -e --silent --accept-package-agreements --accept-source-agreements
}
if (-not (Test-Path $ts)) {
  Write-Host "      winget khong cai duoc, tai thang ban MSI tu pkgs.tailscale.com"
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  $msi = Join-Path $env:TEMP "tailscale-setup.msi"
  Invoke-WebRequest -UseBasicParsing "https://pkgs.tailscale.com/stable/tailscale-setup-latest-amd64.msi" -OutFile $msi
  $p = Start-Process msiexec.exe -ArgumentList "/i `"$msi`" /qn /norestart" -Wait -PassThru
  if ($p.ExitCode -ne 0) { Loi "Cai MSI Tailscale loi (ma $($p.ExitCode))" }
  Start-Sleep 10
}
if (-not (Test-Path $ts)) { Loi "Chua cai duoc Tailscale" }
Dat "Da cai Tailscale"
Write-Host "      Trinh duyet se mo: dang nhap bang gmail da dung o may 2 (KHONG dung @urah.vn)"
& $ts up --hostname=$May --unattended
if ($LASTEXITCODE -ne 0) { Loi "tailscale up that bai" }
Dat "Tailscale da len, ten may $May, IP $((& $ts ip -4 | Select -First 1))"

# 3. Thay may 2
& $ts ping --c 3 may-2 | Out-Null
if ($LASTEXITCODE -ne 0) { Loi "Khong ping duoc may-2 qua Tailscale (may 2 da chay CAI-TRAM-MAY-2.ps1 chua?)" }
}
git ls-remote $Tram hang-doi | Out-Null
if ($LASTEXITCODE -ne 0) { Loi "Khong doc duoc tram $Tram" }
Dat "Thay may 2 va tram git"

# git daemon tren Windows treo khi push neu bat sideband: tat cho moi kho tren may nay
git config --global sendpack.sideband false
Dat "Tat sendpack.sideband (tranh treo khi push len tram Windows)"

# 4. Clone hang doi hoac them remote tram
if (-not (Test-Path "$Repo\.git")) {
  New-Item -ItemType Directory -Force $ThuMuc | Out-Null
  git clone -o tram -b claude/project-thread-jowxv1 $Tram $Repo
  if ($LASTEXITCODE -ne 0) { Loi "Clone tu tram loi" }
  git -C $Repo remote add origin https://github.com/fyzdfyzd/linhx-engine.git
  Dat "Da clone hang doi tu tram vao $Repo"
} else {
  if (-not (git -C $Repo remote | Select-String -SimpleMatch "tram")) { git -C $Repo remote add tram $Tram }
  git -C $Repo fetch tram
  if ($LASTEXITCODE -ne 0) { Loi "fetch tram loi" }
  Dat "Da them remote tram vao $Repo"
}

# 5. Cai runner neu chua co (lich LINHX-HangDoi), may-4 chi nhan phieu dich danh
$tepEnv = "$Repo\runner\tho.env"
if (-not (Test-Path $tepEnv)) {
  $a = @("-ExecutionPolicy","Bypass","-File","$Repo\runner\cai-may.ps1","-May",$May,"-ThuMuc",$Repo,"-GocGioiHan",$ThuMuc,
         "-ThuMucLog",(Join-Path $ThuMuc "linhx-runner\log"),"-KhongChayNgay")
  if ($May -eq "may-4") { $a += "-ChiDichDanh" }
  & powershell @a
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path $tepEnv)) { Loi "cai-may.ps1 loi" }
  Dat "Da cai runner $May"
} else { Copy-Item $tepEnv "$tepEnv.truoc-tram" -Force; Dat "Runner da co, luu ban cu tho.env.truoc-tram" }

# 6. Tro hang doi sang tram
$n = Get-Content $tepEnv | Where-Object { $_ -notmatch '^LINHX_REMOTE_HANG_DOI=' }
($n + "LINHX_REMOTE_HANG_DOI=tram") | Set-Content $tepEnv -Encoding utf8
Dat "tho.env: LINHX_REMOTE_HANG_DOI=tram"

# 7. Bat lich
schtasks /Change /TN LINHX-HangDoi /ENABLE | Out-Null
schtasks /Run /TN LINHX-HangDoi | Out-Null
Start-Sleep 70
$log = "$Repo\runner\tho.log"
if ((Test-Path $log) -and (Get-Content $log -Tail 20 | Select-String "tho=$May")) { Dat "Runner $May dang chay qua tram" }
else { Write-Host "CHUA RO Xem $log sau 1-2 phut" -F Yellow }
Write-Host "XONG $May" -F Green
