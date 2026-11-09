# Chạy trên MÁY CÔNG TY (DESKTOP-PVHR2CD), PowerShell "Run as Administrator".
# Linh duyệt 9/11: (2) loại thư mục engine khỏi Defender, (3) giới hạn RAM WSL 3 GB.

# (2) Defender bỏ quét thư mục engine, worktree thợ và trạng thái canh
$cac = @("D:\LINHX\LINHX-ENGINE", "D:\LINHX\ENGINE-canh") + (Get-ChildItem D:\LINHX -Directory -Filter "ENGINE-t*" | ForEach-Object FullName)
foreach ($d in $cac) { Add-MpPreference -ExclusionPath $d }
(Get-MpPreference).ExclusionPath

# (3) WSL tối đa 3 GB RAM + 4 GB swap (giữ vmIdleTimeout=-1 đang có)
$f = "$env:USERPROFILE\.wslconfig"
$cu = if (Test-Path $f) { Get-Content $f -Raw } else { "" }
Copy-Item $f "$f.cu-0911" -ErrorAction SilentlyContinue
if ($cu -notmatch '(?m)^\[wsl2\]') { $cu = "[wsl2]`r`n" + $cu }
$cu = $cu -replace '(?m)^memory=.*\r?\n?', '' -replace '(?m)^swap=.*\r?\n?', ''
$cu = $cu -replace '(?m)^\[wsl2\]\r?\n', "[wsl2]`r`nmemory=3GB`r`nswap=4GB`r`n"
Set-Content -Encoding ascii $f $cu
Get-Content $f
wsl --shutdown   # bench tự lên lại qua lịch ENGINE-BenchBen + linhx-bench.service
