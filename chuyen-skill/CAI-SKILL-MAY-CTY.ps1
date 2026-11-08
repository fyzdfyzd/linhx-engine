# Cai goi skill/workflow tu MSI len MAY CTY (DESKTOP-PVHR2CD).
# Chay tren MAY CTY, PowerShell thuong (khong can Admin):
#   cd D:\linhx\linhx-engine ; git fetch origin chuyen/skill-0811 ; git checkout origin/chuyen/skill-0811 -- chuyen-skill
#   powershell -ExecutionPolicy Bypass -File chuyen-skill\CAI-SKILL-MAY-CTY.ps1
# Khong xoa gi. Chi chep file moi hon (robocopy /XO), roi tao lien ket (junction)
# cho tung skill vao thu muc skill toan cuc cua Antigravity.
param(
  [string]$Goi = "",
  [string]$DichLinhx = "D:\LINHX"
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Goi) {
  # Ghep cac mau goi-skill.zip.001.. roi giai bang Python (giu ten tieng Viet)
  $Goi = Join-Path $env:TEMP "goi-skill-0811"
  $zip = Join-Path $env:TEMP "goi-skill-0811.zip"
  $out = [IO.File]::Create($zip)
  Get-ChildItem $here -Filter "goi-skill.zip.*" | Sort-Object Name | ForEach-Object { $b=[IO.File]::ReadAllBytes($_.FullName); $out.Write($b,0,$b.Length) }
  $out.Close()
  python -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" $zip $Goi
  Write-Host "Da giai goi vao $Goi"
}
$log = Join-Path $env:TEMP "cai-skill-$(Get-Date -Format yyyyMMdd-HHmm).log"

# 1. Chep cay thu muc ve dung cho cu tren D:\LINHX (khong ghi de file moi hon o may cty)
foreach ($pair in @(@("LINHX", $DichLinhx), @("THU-MUC-CHUNG", "$DichLinhx\LAB\_TU-THU-MUC-CHUNG"))) {
  $src = Join-Path $Goi $pair[0]
  if (Test-Path $src) {
    robocopy $src $pair[1] /E /XO /R:1 /W:1 /NFL /NDL /NP /LOG+:$log | Out-Null
    Write-Host "Da chep $src -> $($pair[1])"
  }
}
# Luat + skill rieng cua agy tren MSI: de rieng, khong ghi de cau hinh may cty
$gh = Join-Path $Goi "GEMINI-HOME"
if (Test-Path $gh) {
  robocopy $gh "$DichLinhx\SKILLS\_tu-msi-gemini" /E /XO /R:1 /W:1 /NFL /NDL /NP /LOG+:$log | Out-Null
  Write-Host "Luat GEMINI.md cua MSI o $DichLinhx\SKILLS\_tu-msi-gemini\GEMINI.md (so voi ban may cty roi tu gop)"
}

# 2. Thu muc skill toan cuc cua Antigravity tren may cty
$agySkills = Join-Path $env:USERPROFILE ".gemini\antigravity\skills"
$it = Get-Item $agySkills -ErrorAction SilentlyContinue
if ($it -and $it.LinkType) { $agySkills = $it.Target | Select-Object -First 1 }
if (-not (Test-Path $agySkills)) { New-Item -ItemType Directory -Path $agySkills | Out-Null }
Write-Host "Thu muc skill agy: $agySkills"

# 3. Moi SKILL.md -> 1 junction <ten> trong thu muc skill agy (giu nguyen duong dan script tuong doi)
$moi = 0; $trung = 0
$roots = @("$DichLinhx\SKILLS", "$DichLinhx\LAB", "$DichLinhx\PROTO", "$DichLinhx\PRJ", "$DichLinhx\LINHX-OPC")
Get-ChildItem $roots -Recurse -Filter SKILL.md -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch '\\(node_modules|\.git|_cu|_tmp|IFAGENT-wt|_tam-lab043-nap)\\' } |
  Sort-Object LastWriteTime -Descending | ForEach-Object {
    $dir = $_.Directory.FullName
    $ten = $_.Directory.Name
    $m = Select-String -Path $_.FullName -Pattern '^name:\s*(.+)$' | Select-Object -First 1
    if ($m) { $ten = $m.Matches[0].Groups[1].Value.Trim().Trim('"',"'") -replace '[\\/:*?"<>|\s]','-' }
    $lk = Join-Path $agySkills $ten
    if (Test-Path $lk) { $trung++ } else {
      New-Item -ItemType Junction -Path $lk -Target $dir | Out-Null; $moi++
    }
  }
Write-Host "Xong: $moi skill moi duoc noi vao agy, $trung ten da co (giu ban moi nhat / ban san co)."
Write-Host "Log robocopy: $log"
