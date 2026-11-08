# Cho thợ dùng Frappe bench trong WSL máy cty (dựng bằng canh/dung-bench.sh). Mọi lần gọi ghi log có thời điểm và mã thoát.
#   powershell -File canh/bench.ps1 gan -Tho 1           chép (rsync) apps linhx_core, linhx_worker từ worktree D:\LINHX\ENGINE-t1 vào ~/frappe-bench/apps (ổ Linux, không chạy từ /mnt/d), pip install -e, cài lên site test, migrate
#   powershell -File canh/bench.ps1 chay -- <lệnh bench>  vd: chay -- --site test migrate ; chay -- --site test console
#   powershell -File canh/bench.ps1 serve                 chạy bench serve ở cổng 8000 trong WSL (wsl.exe ẩn giữ distro sống; kiểm HTTP từ trong WSL: curl http://127.0.0.1:8000, vì cổng 8000 phía Windows đã có LINHX-Server8000), dừng: bench.ps1 dung
#   powershell -File canh/bench.ps1 dung
#   powershell -File canh/bench.ps1 th -Tho 1 th_b3.py    gắn app thợ 1 vào bench rồi chạy kiểm tích hợp tests/nghiem-thu/tich-hop/th_b3.py (bản main), mã thoát 0 = đạt
# Log: D:\LINHX\ENGINE-canh\bench\<yyyyMMdd>.log (mỗi lần: lúc bắt đầu, lệnh, toàn bộ đầu ra, lúc xong, mã thoát).
param([Parameter(Position = 0)][string]$Viec = "chay", [int]$Tho = 0, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Con)
$Distro = "Ubuntu"
$Log = "D:\LINHX\ENGINE-canh\bench"; New-Item -ItemType Directory -Force $Log | Out-Null
$tep = "$Log\$(Get-Date -Format yyyyMMdd).log"
function Wsl($lenh) {
  $bd = Get-Date -Format s
  Add-Content -Encoding utf8 $tep "`n=== $bd bắt đầu: $lenh"
  $ra = & wsl.exe -d $Distro -u frappe -- bash -lc "cd ~/frappe-bench && $lenh" 2>&1 | Out-String
  $ma = $LASTEXITCODE
  Add-Content -Encoding utf8 $tep $ra
  Add-Content -Encoding utf8 $tep "=== $(Get-Date -Format s) xong, mã thoát $ma"
  Write-Output $ra; Write-Output "[bench] $bd -> $(Get-Date -Format s) mã thoát $ma (log $tep)"
  $ma
}
$m = New-Object System.Threading.Mutex($false, "Global\ENGINE-Bench"); try { [void]$m.WaitOne(1800000) } catch [System.Threading.AbandonedMutexException] {}
try {
  switch ($Viec) {
    "gan" {
      if ($Tho -lt 1) { Write-Output "thiếu -Tho"; exit 2 }
      $wt = "/mnt/d/LINHX/ENGINE-t$Tho/apps"
      $kq = Wsl ("sudo service mariadb start >/dev/null; sudo service redis-server start >/dev/null; " +
        "for a in linhx_core linhx_worker; do [ -d $wt/`$a ] || continue; mkdir -p apps/`$a; rsync -a --delete --exclude __pycache__ --exclude node_modules $wt/`$a/ apps/`$a/ || exit 10; ./env/bin/pip install -q -e apps/`$a || exit 11; grep -qx `$a sites/apps.txt || echo `$a >> sites/apps.txt; done; " +
        "bench --site test list-apps | grep -q linhx_core || bench --site test install-app linhx_core; bench --site test migrate")
      exit ($kq | Select-Object -Last 1)
    }
    "th" {
      # Kiểm tích hợp (canh): gắn app của thợ vào bench rồi chạy tests/nghiem-thu/tich-hop/<file> bản của main, cùng khoá bench.
      if ($Tho -lt 1 -or -not $Con) { Write-Output "cần -Tho và tên file th_*.py"; exit 2 }
      $wt = "/mnt/d/LINHX/ENGINE-t$Tho/apps"
      $kq = Wsl ("sudo service mariadb start >/dev/null; sudo service redis-server start >/dev/null; " +
        "for a in linhx_core linhx_worker; do [ -d $wt/`$a ] || continue; mkdir -p apps/`$a; rsync -a --delete --exclude __pycache__ --exclude node_modules $wt/`$a/ apps/`$a/ || exit 10; ./env/bin/pip install -q -e apps/`$a || exit 11; grep -qx `$a sites/apps.txt || echo `$a >> sites/apps.txt; done; " +
        "bench --site test list-apps | grep -q linhx_core || bench --site test install-app linhx_core; bench --site test migrate || exit 12; bench --site test clear-cache; sleep 5; " +
        "cd /mnt/d/LINHX/LINHX-ENGINE/tests/nghiem-thu/tich-hop && PATH=`$HOME/.local/bin:`$PATH python3 $(@($Con | Where-Object { $_ -ne '--' })[0])")
      exit ($kq | Select-Object -Last 1)
    }
    "serve" {
      Start-Process wsl.exe -WindowStyle Hidden -ArgumentList @("-d", $Distro, "-u", "frappe", "--", "bash", "-lc", "cd ~/frappe-bench && sudo service mariadb start && sudo service redis-server start && exec bench serve --port 8000 > /tmp/bench-serve.log 2>&1")
      Add-Content -Encoding utf8 $tep "=== $(Get-Date -Format s) bench serve cổng 8000"
      Write-Output "bench serve: http://localhost:8000 (site test). Dừng: canh/bench.ps1 dung"
    }
    "dung" { $kq = Wsl "pkill -f 'bench serve' ; pkill -f 'frappe.utils.bench_helper' ; true"; exit 0 }
    default {
      $con = @($Con | Where-Object { $_ -ne "--" })
      $kq = Wsl ("sudo service mariadb start >/dev/null; sudo service redis-server start >/dev/null; bench " + ($con -join " "))
      exit ($kq | Select-Object -Last 1)
    }
  }
} finally { $m.ReleaseMutex() }
