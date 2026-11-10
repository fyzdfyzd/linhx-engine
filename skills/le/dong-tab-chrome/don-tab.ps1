# don-tab.ps1: chot chan tab Chrome cua agent (skill dong-tab-chrome).
# Chi dong tab tren Chrome mo cong debug (--remote-debugging-port), tuc trinh duyet agent dieu khien.
# Chrome thuong cua Linh khong bi dong tab, chi ghi canh bao RAM.
# Chay duoc tren may cty DESKTOP-PVHR2CD va MSI, PowerShell 5+.
param(
  [int]$MaxTab = 8,
  [int]$MaxTabKhiThieu = 3,
  [int]$NguongMB = 1500,
  [switch]$ThuKhong,
  [switch]$CaiLich,
  [int]$PhutLich = 15,
  [string]$Log = ""
)
$ErrorActionPreference = "Continue"

if (-not $Log) {
  $Log = if (Test-Path "D:\linhx\.canh") { "D:\linhx\.canh\don-tab.log" } else { Join-Path $env:TEMP "don-tab.log" }
}
function Ghi($s) { $d = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm"), $s; Write-Host $d; Add-Content -Path $Log -Value $d -Encoding UTF8 }

if ($CaiLich) {
  $ps = $MyInvocation.MyCommand.Path
  $act = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ps`" -MaxTab $MaxTab -MaxTabKhiThieu $MaxTabKhiThieu -NguongMB $NguongMB"
  $trg = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $PhutLich)
  $set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 2) -MultipleInstances IgnoreNew
  Register-ScheduledTask -TaskName "LINHX-don-tab-chrome" -Action $act -Trigger $trg -Settings $set -Force | Out-Null
  Ghi "Da cai lich LINHX-don-tab-chrome moi $PhutLich phut ($ps)"
  exit 0
}

# RAM
$os = Get-CimInstance Win32_OperatingSystem
$trongMB = [int]($os.FreePhysicalMemory / 1024)
$chrome = @(Get-Process chrome -ErrorAction SilentlyContinue)
$chromeMB = [int](($chrome | Measure-Object WorkingSet64 -Sum).Sum / 1MB)
$tran = if ($trongMB -lt $NguongMB) { $MaxTabKhiThieu } else { $MaxTab }

# Tim cong debug tu dong lenh cac tien trinh chrome
$cong = @()
Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" -ErrorAction SilentlyContinue | ForEach-Object {
  if ($_.CommandLine -match '--remote-debugging-port=(\d+)') { $cong += [int]$Matches[1] }
}
$cong = @($cong | Where-Object { $_ -gt 0 } | Sort-Object -Unique)

$dong = 0; $tong = 0
foreach ($p in $cong) {
  try { $ds = Invoke-RestMethod -Uri "http://127.0.0.1:$p/json/list" -TimeoutSec 3 } catch { Ghi "cong $p khong doc duoc: $($_.Exception.Message)"; continue }
  # /json/list tra ve tab moi dung nhat truoc; giu $tran tab dau, dong phan con lai, luon chua it nhat 1 tab
  $tab = @($ds | Where-Object { $_.type -eq "page" -and $_.url -notmatch '^devtools://' })
  $tong += $tab.Count
  $giu = [Math]::Max(1, $tran)
  if ($tab.Count -le $giu) { continue }
  foreach ($t in $tab[$giu..($tab.Count - 1)]) {
    $ten = if ($t.url.Length -gt 80) { $t.url.Substring(0, 80) } else { $t.url }
    if ($ThuKhong) { Ghi "[thu] se dong cong $p : $ten"; $dong++; continue }
    try { Invoke-WebRequest -Uri "http://127.0.0.1:$p/json/close/$($t.id)" -UseBasicParsing -TimeoutSec 3 | Out-Null; $dong++; Ghi "dong cong $p : $ten" }
    catch { try { Invoke-WebRequest -Uri "http://127.0.0.1:$p/json/close/$($t.id)" -Method Put -UseBasicParsing -TimeoutSec 3 | Out-Null; $dong++; Ghi "dong cong $p : $ten" } catch { Ghi "khong dong duoc $ten" } }
  }
}

$canh = if ($trongMB -lt $NguongMB) { " CANH BAO RAM THAP" } else { "" }
Ghi ("RAM trong {0} MB, Chrome {1} MB ({2} tien trinh), cong debug [{3}], tab agent {4}, tran {5}, da dong {6}{7}{8}" -f $trongMB, $chromeMB, $chrome.Count, ($cong -join ','), $tong, $tran, $dong, $canh, $(if ($ThuKhong) { ' (thu khong)' } else { '' }))
