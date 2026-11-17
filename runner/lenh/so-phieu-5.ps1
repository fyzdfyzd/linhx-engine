# Đặt LINHX_SO_PHIEU=5 (số phiếu code chạy song song) trong runner\tho.env của máy này. Có hiệu lực từ lượt sau.
$tep = Join-Path (Split-Path -Parent $PSScriptRoot) "tho.env"
$nd = @(Get-Content $tep -Encoding UTF8)
if ($nd -match '^LINHX_SO_PHIEU=') { $nd = $nd -replace '^LINHX_SO_PHIEU=.*$', 'LINHX_SO_PHIEU=5' } else { $nd += 'LINHX_SO_PHIEU=5' }
[System.IO.File]::WriteAllLines($tep, $nd, (New-Object System.Text.UTF8Encoding $false))
"da_dat: " + ($nd -match '^LINHX_SO_PHIEU=')
$os = Get-CimInstance Win32_OperatingSystem
"ram_trong_gb: {0:N1}" -f ($os.FreePhysicalMemory/1MB)
"tien_trinh_agy: " + @(Get-Process -Name agy* -ErrorAction SilentlyContinue).Count
