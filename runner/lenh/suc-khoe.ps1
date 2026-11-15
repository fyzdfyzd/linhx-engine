# Sức khoẻ máy: RAM, ổ đĩa, agy, git runner, 30 dòng log mới nhất. Chỉ đọc.
$ErrorActionPreference = "Continue"
$os = Get-CimInstance Win32_OperatingSystem
"may: $env:COMPUTERNAME"
"ram_trong_gb: {0:N1} / {1:N1}" -f ($os.FreePhysicalMemory/1MB), ($os.TotalVisibleMemorySize/1MB)
Get-PSDrive -PSProvider FileSystem | % { "o_{0}: trong {1:N1} GB" -f $_.Name, ($_.Free/1GB) }
$agy = Get-Command agy -ErrorAction SilentlyContinue
if ($agy) { "agy: " + (& $agy.Source --version 2>&1 | Select -First 1) } else { "agy: khong thay trong PATH" }
$goc = Split-Path -Parent $PSScriptRoot
"runner_head: " + (git -C (Split-Path -Parent $goc) log --oneline -1 2>&1)
"tien_trinh_agy: " + @(Get-Process -Name agy* -ErrorAction SilentlyContinue).Count
$tep = Get-ChildItem C:\linhx, D:\linhx -Recurse -Filter *.log -ErrorAction SilentlyContinue | Sort LastWriteTime | Select -Last 1
if ($tep) { "== log: $($tep.FullName)"; Get-Content $tep.FullName -Tail 30 }
