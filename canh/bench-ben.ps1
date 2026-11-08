# Giữ distro Ubuntu (WSL) sống để service systemd linhx-bench (bench serve cổng 8000) chạy bền.
# Gọi từ lịch ENGINE-BenchBen (lúc đăng nhập + mỗi 10 phút, bỏ qua nếu đang chạy) qua:
#   wscript.exe //B "D:\LINHX\LINHX-OPC\CHIEMTINHSO-chung\chay-an.vbs" "D:\LINHX\LINHX-ENGINE\canh\bench-ben.ps1"
# Script chặn ở "sleep infinity": còn tiến trình wsl.exe này thì WSL không tắt distro. Chết thì lượt lịch kế dựng lại.
$Log = "D:\LINHX\ENGINE-canh\bench"; New-Item -ItemType Directory -Force $Log | Out-Null
$tep = "$Log\$(Get-Date -Format yyyyMMdd).log"
Add-Content -Encoding utf8 $tep "=== $(Get-Date -Format s) bench-ben: giữ Ubuntu sống (linhx-bench.service)"
& wsl.exe -d Ubuntu -u root -- bash -c "systemctl start mariadb redis-server linhx-bench; exec sleep infinity"
Add-Content -Encoding utf8 $tep "=== $(Get-Date -Format s) bench-ben: wsl.exe thoát, mã $LASTEXITCODE"
