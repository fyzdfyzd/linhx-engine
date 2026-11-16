# Xem thư mục việc C:\linhx\wt-* và C:\linhx\ifagent-wt\*: nhánh, commit cuối, file đổi. Chỉ đọc.
$ErrorActionPreference = "Continue"
$ds = @(Get-ChildItem C:\linhx\wt-*, D:\linhx\wt-*, C:\linhx\ifagent-wt\* -Directory -ErrorAction SilentlyContinue)
foreach ($d in $ds) {
  if (Test-Path (Join-Path $d.FullName ".git")) {
    "== $($d.FullName)  sua_luc: $($d.LastWriteTime.ToString('HH:mm'))"
    git -C $d.FullName log --oneline -1 2>&1
    git -C $d.FullName status --short 2>&1 | Select -First 10
  }
}
