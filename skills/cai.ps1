# Noi moi skill trong repo vao thu muc skill cua Antigravity va Claude Code tren may nay.
# Chay duoc tren CA HAI may (MSI va may cty DESKTOP-PVHR2CD), PowerShell thuong:
#   cd <repo linhx-engine> ; git pull ; powershell -ExecutionPolicy Bypass -File skills\cai.ps1
# Khong xoa thu muc that nao. Chi tao/sua junction. Ten da co ma la thu muc that thi bo qua va bao.
param([switch]$ChiAgy, [switch]$ChiClaude)
$ErrorActionPreference = "Stop"
$goc = Split-Path -Parent $MyInvocation.MyCommand.Path

$dich = @()
if (-not $ChiClaude) { $dich += Join-Path $env:USERPROFILE ".gemini\antigravity\skills" }
if (-not $ChiAgy)    { $dich += Join-Path $env:USERPROFILE ".claude\skills" }

$skills = Get-ChildItem (Join-Path $goc "bo"), (Join-Path $goc "le") -Recurse -Filter SKILL.md | ForEach-Object {
  $m = Select-String -Path $_.FullName -Pattern '^name:\s*["'']?([^"''\r\n]+)' | Select-Object -First 1
  $ten = if ($m) { $m.Matches[0].Groups[1].Value.Trim() } else { $_.Directory.Name }
  [pscustomobject]@{ Ten = ($ten -replace '[\\/:*?"<>|\s]', '-'); Dir = $_.Directory.FullName }
}

foreach ($d in $dich) {
  $it = Get-Item $d -ErrorAction SilentlyContinue
  if ($it -and $it.LinkType) { $d = @($it.Target)[0] }
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
  $moi = 0; $sua = 0; $bo = @()
  foreach ($s in $skills) {
    $lk = Join-Path $d $s.Ten
    $cu = Get-Item $lk -ErrorAction SilentlyContinue
    if ($cu -and -not $cu.LinkType) { $bo += $s.Ten; continue }
    if ($cu -and @($cu.Target)[0] -eq $s.Dir) { continue }
    if ($cu) { [IO.Directory]::Delete($lk); $sua++ } else { $moi++ }   # xoa junction, khong dung ruot
    New-Item -ItemType Junction -Path $lk -Target $s.Dir | Out-Null
  }
  Write-Host "$d : $moi moi, $sua cap nhat, $($skills.Count) skill trong repo"
  if ($bo) { Write-Host "  Bo qua (dang la thu muc that, so tay roi xoa neu thua): $($bo -join ', ')" }
}
