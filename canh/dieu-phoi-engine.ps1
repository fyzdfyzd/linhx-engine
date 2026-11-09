# Điều phối LINHX ENGINE (repo riêng fyzdfyzd/linhx-engine) trên máy công ty: Claude canh, agy làm.
# Lịch ENGINE-DieuPhoi gọi mỗi 10 phút qua chay-an.vbs (ẩn hoàn toàn, luật 2/11). -Tho 0 = lượt chính: gọi từng thợ rồi ghi tổng hợp.
# Nhánh tích hợp: main ở D:\LINHX\LINHX-ENGINE. Mỗi thợ: worktree D:\LINHX\ENGINE-t<N>, nhánh tu-dong/engine-t<N>.
# Trạng thái ngoài repo: D:\LINHX\ENGINE-canh. Nhật ký agy từng phiếu: D:\LINHX\LINHX-ENGINE\.canh\log\<phieu>.jsonl (không commit).
# Cổng: K1 vùng (canh/rao.py), K2 trần CHUA_DAT liền thì lùi về mốc, K3 đọc nhật ký agy, K4 chấm bảo mật thêm cho feature nhạy cảm.
param([int]$Tho = 0, [switch]$ThuChon)  # -ThuChon: chỉ in feature sẽ giao cho thợ $Tho rồi thoát (không chấm, không gọi agy)
$ErrorActionPreference = "Continue"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false); $OutputEncoding = [Text.UTF8Encoding]::new($false)
$TichHop = "D:\LINHX\LINHX-ENGINE"; $NhanhTH = "main"
$Canh = "D:\LINHX\ENGINE-canh"
$LogDir = "$TichHop\.canh\log"
$LenhAgy = "$env:USERPROFILE\.gemini\bin\agy.exe"
$Proto = @("D:\LINHX\PROTO\03_OPC_OS", "D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG")
$CotPhieu = "luc_giao`tluc_xong`ttho`tphieu`tfeature`tloai`tdung`tket_luan`tphut`ttoken_vao`ttoken_ra"
New-Item -ItemType Directory -Force "$Canh\nhan", "$Canh\tac", $LogDir | Out-Null
function Ghi($s) { Add-Content -Encoding utf8 "$Canh\NHAT-KY.md" "- $(Get-Date -Format 'yyyy-MM-dd HH:mm') t${Tho}: $s" }
function DocJson($p) { Get-Content $p -Raw -Encoding utf8 | ConvertFrom-Json }
function KhoaTH { $m = New-Object System.Threading.Mutex($false, "Global\ENGINE-TichHop"); try { [void]$m.WaitOne(300000) } catch [System.Threading.AbandonedMutexException] {}; $m }
function CacFile($dk) { if ($dk.cac_file_features) { @($dk.cac_file_features) } else { @("features-dot1.json") } }
# Tìm feature trong các file features dưới thư mục $goc: trả @{ff = tên file; f = feature}
function TimF($dk, $goc, $id) {
  foreach ($ff in (CacFile $dk)) {
    if (-not (Test-Path "$goc\$ff")) { continue }
    $y = (DocJson "$goc\$ff").features | Where-Object id -eq $id
    if ($y) { return @{ ff = $ff; f = $y } }
  }
  $null
}
function TatCaF($dk, $goc) { foreach ($ff in (CacFile $dk)) { if (Test-Path "$goc\$ff") { (DocJson "$goc\$ff").features } } }
function SoTac($id) { [int]("0" + (Get-Content "$Canh\tac\$id.txt" -ErrorAction SilentlyContinue)) }
function KeoTH { git -C $TichHop pull -q --no-rebase --no-edit origin $NhanhTH 2>&1 | Out-Null }
# Đẩy main, 3 lần (kéo lại giữa các lần); hỏng thì ghi nhật ký (9/11: push hỏng bị Out-Null nuốt, trạng thái kẹt trên máy)
function DayTH { $ra = ""
  for ($i = 1; $i -le 3; $i++) { $ra = git -C $TichHop push -q origin $NhanhTH 2>&1 | Out-String; if ($LASTEXITCODE -eq 0) { return }; KeoTH; Start-Sleep -Seconds (5 * $i) }
  Ghi "đẩy $NhanhTH hỏng 3 lần: $($ra.Trim().Substring(0, [math]::Min(200, $ra.Trim().Length)))" }
# Gọi claude chấm; trả @{kl = DAT|CHUA_DAT; review = chữ}
function ChamClaude($de, $tep, $nhan) {
  $de | Set-Content -Encoding utf8 $tep
  $rel = ".canh-tho/" + (Split-Path $tep -Leaf)
  $raw = claude -p "Doc file $rel (UTF-8) va lam dung yeu cau trong do." --output-format json --max-turns 15 --allowedTools "Read" "Grep" "Glob" "Bash(git diff:*)" "Bash(git log:*)" "Bash(git show:*)" 2>&1 | Out-String
  try { $j = $raw | ConvertFrom-Json; $rv = $j.result
        Add-Content -Encoding utf8 "$Canh\token.tsv" "$(Get-Date -Format s)`t$Tho`t$nhan`t$fid`t$([int]$j.usage.input_tokens + [int]$j.usage.cache_read_input_tokens)`t$($j.usage.output_tokens)`t" } catch { $rv = $raw }
  $d1 = @("$rv" -split "`n" | Where-Object { $_.Trim().Trim('*', '#', ' ', [char]0xFEFF) -cmatch '^(DAT|CHUA_DAT)\b' }) | Select-Object -First 1
  @{ kl = $(if ("$d1".Trim().Trim('*', '#', ' ', [char]0xFEFF) -like 'DAT*') { "DAT" } else { "CHUA_DAT" }); review = "$rv" }
}

# ---------- Lượt chính ----------
if ($Tho -eq 0) {
  $mx = KhoaTH
  KeoTH
  $dk = DocJson "$TichHop\canh\dieu-khien.json"
  if ($dk.trang_thai -eq "dung_han") {
    Get-ChildItem "$Canh\t*\phieu.txt" -ErrorAction SilentlyContinue | ForEach-Object { $id = ((Get-Content $_.FullName) -split ";")[0]; Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }
    Ghi "dung_han: đã dừng agy"
  } else {
    # Dọn mồ côi (Linh 9/11): lượt thợ treo quá 150 phút (gồm agy ≤40 + chấm), tiến trình chấm/kiểm của engine mất cha quá 60 phút,
    # claude chấm (.canh-tho) quá 60 phút. Chỉ đụng tiến trình có dòng lệnh trỏ vào engine; không đụng agy, phiên Claude khác.
    try {
      $bay = Get-CimInstance Win32_Process -ErrorAction Stop
      $song = @{}; foreach ($p in $bay) { $song[[int]$p.ProcessId] = $true }
      foreach ($p in $bay) {
        if ([int]$p.ProcessId -eq $PID -or -not $p.CommandLine -or -not $p.CreationDate) { continue }
        $tuoi = ((Get-Date) - $p.CreationDate).TotalMinutes; $cl = $p.CommandLine; $ly = $null
        if ($cl -match 'dieu-phoi-engine\.ps1' -and $cl -match '-Tho\s+[1-9]' -and $tuoi -gt 150) { $ly = "lượt thợ treo" }
        elseif ($cl -match 'Doc file \.canh-tho' -and $tuoi -gt 60) { $ly = "claude chấm treo" }
        elseif ($cl -match 'LINHX[\\-]ENGINE|ENGINE-t\d' -and $cl -match 'cong_kiem|pytest|next build|npm|node' -and -not $song[[int]$p.ParentProcessId] -and $tuoi -gt 60) { $ly = "kiểm mồ côi" }
        if ($ly) { & taskkill.exe /PID $p.ProcessId /T /F 2>&1 | Out-Null; Ghi "dọn mồ côi ($ly): PID $($p.ProcessId) $([int]$tuoi) phút: $($cl.Substring(0, [math]::Min(120, $cl.Length)))" }
      }
    } catch { Ghi "dọn mồ côi lỗi: $_" }
    # xoa_tac: ["ID@nhan"] xoá đếm CHUA_DAT một lần (Khổng Minh giao lại sau lỗi máy)
    foreach ($xt in @($dk.xoa_tac)) { if (-not $xt) { continue }; $id = ($xt -split "@")[0]; $dau = "$Canh\tac\da-xoa-$($xt -replace '[^A-Za-z0-9]', '_').txt"
      if (-not (Test-Path $dau)) { Remove-Item "$Canh\tac\$id.txt" -Force -ErrorAction SilentlyContinue; "1" | Set-Content $dau; Ghi "xoá đếm CHUA_DAT của $id ($xt)" } }
    # nhả giữ cũ: nhan\<ID>.txt trỏ tới thợ mà dang.txt của thợ đó không còn là ID (phiếu bị giao đè, lỗi 8/11 D1 giữ nhóm trang-bu)
    $mxG = New-Object System.Threading.Mutex($false, "Global\ENGINE-Giao"); try { [void]$mxG.WaitOne(120000) } catch [System.Threading.AbandonedMutexException] {}
    Get-ChildItem "$Canh\nhan\*.txt" -ErrorAction SilentlyContinue | ForEach-Object {
      $n = (Get-Content $_.FullName -Raw).Trim(); $dg = "$Canh\t$n\dang.txt"
      $dangN = if (Test-Path $dg) { (Get-Content $dg -Raw).Trim() } else { "" }
      if ($dangN -ne $_.BaseName -and -not (Test-Path "$Canh\t$n\can-cham.txt")) { Remove-Item $_.FullName -Force; Ghi "nhả giữ cũ $($_.BaseName) của t$n (thợ đang $dangN)" }
    }
    try { $mxG.ReleaseMutex() } catch {}
    # Thợ dư (số > so_tho, khi giảm thợ): dừng agy, nhả feature đang giữ để thợ khác nhận
    Get-ChildItem "$Canh\t*" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^t(\d+)$' -and [int]$Matches[1] -gt [int]$dk.so_tho } | ForEach-Object {
      $n = $_.Name.Substring(1)
      if (Test-Path "$($_.FullName)\phieu.txt") { $id = ((Get-Content "$($_.FullName)\phieu.txt") -split ";")[0]; Stop-Process -Id $id -Force -ErrorAction SilentlyContinue; Remove-Item "$($_.FullName)\phieu.txt" -Force; Ghi "t${n}: nghỉ (so_tho $($dk.so_tho)), đã dừng agy" }
      Remove-Item "$($_.FullName)\dang.txt" -Force -ErrorAction SilentlyContinue
      Get-ChildItem "$Canh\nhan\*.txt" -ErrorAction SilentlyContinue | Where-Object { (Get-Content $_.FullName -Raw).Trim() -eq $n } | ForEach-Object { Remove-Item $_.FullName -Force; Ghi "t${n}: nhả $($_.BaseName)" }
    }
    for ($i = 1; $i -le [int]$dk.so_tho; $i++) {
      Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"", "-Tho", "$i")
    }
  }
  # Tổng hợp cho Linh: .canh/TRANG-THAI.md, .canh/phieu.tsv, .canh/dang-chay.json trên main
  $tat = @(TatCaF $dk $TichHop)
  $dat = @($tat | Where-Object passes | ForEach-Object id)
  $bang = "# LINHX ENGINE: trạng thái thợ`n`nCập nhật $(Get-Date -Format 'yyyy-MM-dd HH:mm') (giờ máy cty). Đạt: $($dat.Count)/$($tat.Count) $(if ($dat) { '(' + ($dat -join ', ') + ')' })`n`n| Thợ | Đang làm | Phiếu | Kết luận lượt chấm gần nhất |`n|---|---|---|---|`n"
  $dangChay = @()
  for ($i = 1; $i -le [int]$dk.so_tho; $i++) {
    $S = "$Canh\t$i"
    $dang = if (Test-Path "$S\dang.txt") { (Get-Content "$S\dang.txt").Trim() } else { "-" }
    $ph = "rảnh"
    if (Test-Path "$S\phieu.txt") { $a = (Get-Content "$S\phieu.txt" -Encoding utf8) -split ";"; $ph = "$($a[2]) từ $($a[1])"; $dangChay += [ordered]@{ tho = $i; phieu = $a[2]; feature = $a[3]; tu = $a[1] } }
    $kl = if (Test-Path "$S\TRANG-THAI.md") { $l = @(Get-Content "$S\TRANG-THAI.md" -TotalCount 3 -Encoding utf8); "$($l[0]) · $($l[2])" } else { "-" }
    $bang += "| $i | $dang | $ph | $kl |`n"
  }
  $bang += "`n## Chờ`n" + (($dk.cho.PSObject.Properties | ForEach-Object { "- $($_.Name): $($_.Value)" }) -join "`n") + "`n"
  $tac = @(Get-ChildItem "$Canh\tac\*.txt" -ErrorAction SilentlyContinue | Where-Object { (SoTac $_.BaseName) -ge [int]$dk.tran_chua_dat } | ForEach-Object BaseName)
  if ($tac) { $bang += "`n## Chạm trần CHUA_DAT (đã lùi về mốc, ngưng giao)`n" + (($tac | ForEach-Object { "- $_" }) -join "`n") + "`n" }
  # K8: đối chiếu bằng chứng VM của feature đã đạt (2 lần liền sai thì hạ passes về false, ghi CAN-LINH)
  $dc = py -3.12 "$TichHop\canh\doi_chieu_vm.py" --goc $TichHop --trang-thai "$Canh\doi-chieu-vm.json" 2>&1 | Out-String
  if ($dc.Trim()) { $bang += "`n## Đối chiếu VM`n$($dc.Trim())`n" }
  if ($dc -match "HẠ VỀ") { Add-Content -Encoding utf8 "$Canh\CAN-LINH.md" "- $(Get-Date -Format s) đối chiếu VM: $(($dc -split "`n" | Where-Object { $_ -match 'HẠ VỀ' }) -join '; ')" }
  if (Test-Path "$Canh\CAN-LINH.md") { $bang += "`n## Cần Linh`n" + (Get-Content "$Canh\CAN-LINH.md" -Raw -Encoding utf8) }
  $bang += "`n## Nhật ký gần nhất`n" + ((Get-Content "$Canh\NHAT-KY.md" -Tail 12 -Encoding utf8 -ErrorAction SilentlyContinue) -join "`n") + "`n"
  New-Item -ItemType Directory -Force "$TichHop\.canh\review" | Out-Null
  $bang | Set-Content -Encoding utf8 "$TichHop\.canh\TRANG-THAI.md"
  if (Test-Path "$Canh\phieu.tsv") { Copy-Item "$Canh\phieu.tsv" "$TichHop\.canh\phieu.tsv" -Force }
  ConvertTo-Json -InputObject @($dangChay) -Depth 3 | Set-Content -Encoding utf8 "$TichHop\.canh\dang-chay.json"
  Get-ChildItem "$Canh\t*\log\review-*.md" -ErrorAction SilentlyContinue | ForEach-Object { Copy-Item $_.FullName "$TichHop\.canh\review\$($_.Directory.Parent.Name)-$($_.Name)" -Force }
  git -C $TichHop add .canh features-dot1.json features-dot1b.json 2>&1 | Out-Null
  git -C $TichHop diff --cached --quiet -- .canh features-dot1.json features-dot1b.json; if ($LASTEXITCODE -ne 0) {
    git -C $TichHop commit -q -m "canh: trạng thái thợ engine $(Get-Date -Format 'yyyy-MM-dd HH:mm')" -- .canh features-dot1.json features-dot1b.json 2>&1 | Out-Null
    DayTH
  } elseif ([int](git -C $TichHop rev-list --count "origin/$NhanhTH..$NhanhTH" 2>$null | Out-String).Trim() -gt 0) { DayTH }  # còn commit kẹt từ lượt trước
  $mx.ReleaseMutex()
  # Đẩy dữ liệu bảng thợ lên VM (container backend bind mount ~/linhx-engine/.canh). Ẩn, quá 90 giây hay lỗi mạng thì bỏ qua.
  # Chép vào .canh/moi/ trước rồi mv sang .canh/: scp đứt giữa chừng không để lại file cụt (bảng hiện 0 phiếu).
  function GoiGc($ten, $thamSo) {
    $p = Start-Process $gc -NoNewWindow -PassThru -RedirectStandardOutput "$Canh\scp-vm.out" -RedirectStandardError "$Canh\scp-vm.err" -ArgumentList $thamSo
    $null = $p.Handle
    if (-not $p.WaitForExit(90000)) { taskkill /PID $p.Id /T /F 2>&1 | Out-Null; Ghi "$ten bảng thợ lên VM quá 90 giây, bỏ qua"; return $false }
    $p.ExitCode -eq 0
  }
  try {
    $gc = (Get-Command gcloud.cmd -ErrorAction Stop).Source
    $tep = @("$TichHop\.canh\phieu.tsv", "$TichHop\.canh\dang-chay.json") | Where-Object { Test-Path $_ }
    $vm = @("--project", "linhx-engine", "--zone", "asia-southeast1-b", "--quiet")
    if ($tep -and (GoiGc "scp" (@("compute", "scp") + $vm + ($tep | ForEach-Object { "`"$_`"" }) + @("linhx-engine-1:linhx-engine/.canh/moi/")))) {
      [void](GoiGc "mv" (@("compute", "ssh", "linhx-engine-1") + $vm + @("--command", "`"cd linhx-engine/.canh && for f in phieu.tsv dang-chay.json; do test -s moi/`$f && mv -f moi/`$f `$f; done`"")))
    }
  } catch { Ghi "scp bảng thợ lên VM lỗi: $($_.Exception.Message)" }
  exit 0
}

# ---------- Lượt một thợ ----------
$Wt = "D:\LINHX\ENGINE-t$Tho"; $Nhanh = "tu-dong/engine-t$Tho"; $S = "$Canh\t$Tho"
New-Item -ItemType Directory -Force "$S\log" | Out-Null
# một lượt một thợ: mutex theo thợ (tự nhả khi tiến trình chết). Khoá file 15 phút cũ hỏng khi lượt chấm dài hơn 15 phút
# (chờ cong_kiem tuần tự): lượt sau chấm lại cùng phiếu và giao đè phiếu (lỗi 8/11 19:19-19:38)
$mxTho = New-Object System.Threading.Mutex($false, "Global\ENGINE-Tho$Tho")
$coTho = $false; try { $coTho = $mxTho.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $coTho = $true }
if (-not $coTho) { exit 0 }
$dk = DocJson "$TichHop\canh\dieu-khien.json"
$PhutToiDa = if ($dk.phut_toi_da) { [int]$dk.phut_toi_da } else { 40 }
$Tran = if ($dk.tran_chua_dat) { [int]$dk.tran_chua_dat } else { 3 }
if (-not (Test-Path $Wt)) {
  git -C $TichHop worktree add -B $Nhanh $Wt $NhanhTH 2>&1 | Out-Null
  Ghi "tạo worktree $Wt nhánh $Nhanh"
}
Set-Location $Wt
$tamTho = "$Wt\.canh-tho"; New-Item -ItemType Directory -Force $tamTho | Out-Null

# 1. Phiếu đang chạy: còn chạy, ngủ quên, quá giờ, hay xong
$dangChay = $false
if (-not $ThuChon -and (Test-Path "$S\phieu.txt")) {
  $pid0, $bd, $ten, $fid, $loai = (Get-Content "$S\phieu.txt" -Encoding utf8) -split ";", 5
  if (-not $loai) { $loai = "moi" }
  $p = Get-Process -Id $pid0 -ErrorAction SilentlyContinue
  if ($p -and $p.ProcessName -notmatch 'agy') { $p = $null }
  $phut = [int]((Get-Date) - [datetime]$bd).TotalMinutes
  $dau = (git status --porcelain | Out-String) + (git rev-parse HEAD) + ((Get-Item "$LogDir\$ten.jsonl", "$S\log\agy-$ten.err" -ErrorAction SilentlyContinue | ForEach-Object { $_.Length }) -join ",")
  $nhip = "$S\nhip.txt"; $dauCu = if (Test-Path $nhip) { Get-Content $nhip -Raw -Encoding utf8 } else { "" }
  if ($dau -ne $dauCu) { $dau | Set-Content -Encoding utf8 -NoNewline $nhip }
  $ngu = $p -and ($dau -eq $dauCu) -and (((Get-Date) - (Get-Item $nhip).LastWriteTime).TotalMinutes -ge 15)
  if ($p -and $phut -lt $PhutToiDa -and -not $ngu) { $dangChay = $true }
  else {
    $dung = "xong"
    if ($p) { Stop-Process -Id $pid0 -Force; $dung = if ($ngu) { "ngu" } else { "gio" }; Ghi "dừng agy phiếu $ten ($fid): $(if ($ngu) { '15 phút không đổi gì' } else { "quá $PhutToiDa phút" })" }
    # Phần dở không cất stash (bài học Z01): commit lại để phiếu sau làm tiếp
    if (git status --porcelain) { git add -A 2>&1 | Out-Null; git commit -q -m "${fid}: phần dở cuối phiếu $ten" 2>&1 | Out-Null; Ghi "commit phần dở của $fid" }
    "$fid;$ten;$loai;$dung;$bd;$phut" | Set-Content -Encoding utf8 "$S\can-cham.txt"
    Remove-Item "$S\phieu.txt" -Force
    Ghi "agy xong phiếu $ten ($fid) sau $phut phút"
  }
}

# 2. Chấm phiếu vừa xong: rào cứng (K1, K3) + cổng kiểm + Claude đọc diff (+ K4 bảo mật), K2 trần
if (-not $ThuChon -and -not $dangChay -and (Test-Path "$S\can-cham.txt")) {
  $fid, $ten, $loai, $dung, $bd, $phut = (Get-Content "$S\can-cham.txt" -Encoding utf8) -split ";"
  $goc = (Get-Content "$S\goc.txt").Trim()
  $tf = TimF $dk $Wt $fid; $FF = $tf.ff; $x = $tf.f
  $loi = @(); $luuY = @(); $loiMay = $false
  if ((git rev-parse HEAD).Trim() -eq $goc) { $loi += "agy không commit gì" }
  # K1 + K3: canh/rao.py bản của main (thợ không sửa được)
  $camNgoai = (@($TichHop, $Canh) + @(Get-ChildItem "D:\LINHX\ENGINE-t*" -Directory -ErrorAction SilentlyContinue | Where-Object FullName -ne $Wt | ForEach-Object FullName)) -join ";"
  $rao = $null
  try { $rao = py -3.12 "$TichHop\canh\rao.py" $Wt $goc $FF $fid --log "$LogDir\$ten.jsonl" --cam $camNgoai 2>&1 | Out-String | ConvertFrom-Json } catch {}
  if ($rao) { $loi += @($rao.loi); $luuY += @($rao.luu_y) } else { $loi += "rao.py không chạy được: không chấm vùng" }
  $tkV = if ($rao -and $null -ne $rao.token_vao) { $rao.token_vao } else { "" }; $tkR = if ($rao -and $null -ne $rao.token_ra) { $rao.token_ra } else { "" }
  if (-not (Test-Path "$Canh\token.tsv")) { "luc`ttho`tphieu`tfeature`ttoken_vao`ttoken_ra`tphut" | Set-Content -Encoding utf8 "$Canh\token.tsv" }
  Add-Content -Encoding utf8 "$Canh\token.tsv" "$(Get-Date -Format s)`t$Tho`t$ten`t$fid`t$tkV`t$tkR`t$phut"
  $them = git diff "$goc..HEAD" -U0 | Select-String '^\+'
  if ($them | Select-String -Pattern 'pytest\.mark\.skip|@skip|xfail|\.skip\(|pytest\.skip|importorskip') { $loi += "Có test bị skip/xfail" }
  if ($them | Select-String -Pattern '(sk-ant-|AIza[0-9A-Za-z_-]{20}|-----BEGIN [A-Z ]*PRIVATE KEY|ghp_[A-Za-z0-9]{30}|github_pat_)') { $loi += "Có thứ giống khoá trong diff" }
  if (-not $x.passes) { $loi += "$fid chưa đặt passes=true (thợ chưa báo xong)" }
  # môi trường của canh (không phải việc của agy): thư mục con có package.json (vd trang-bu) mà thiếu node_modules hoặc lock mới hơn thì cài trước khi chạy lệnh kiểm
  Get-ChildItem $Wt -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -notmatch '^(node_modules|\.git|\.canh.*)$' -and (Test-Path "$($_.FullName)\package.json") } | ForEach-Object {
    $d = $_.FullName; $lk = "$d\package-lock.json"; $nm = "$d\node_modules"
    $can = -not (Test-Path "$nm\.bin") -or ((Test-Path $lk) -and (Get-Item $lk).LastWriteTime -gt (Get-Item $nm).LastWriteTime)
    if ($can) {
      Push-Location $d
      # npm.cmd, không gọi npm (shim npm.ps1 đọc sai đối số khi chạy ẩn: "Unknown command: pm")
      $ra = if (Test-Path $lk) { & npm.cmd ci --no-audit --no-fund 2>&1 | Out-String } else { & npm.cmd install --no-audit --no-fund 2>&1 | Out-String }
      $maN = $LASTEXITCODE; Pop-Location
      Ghi "chuẩn bị node_modules $($_.Name) (mã $maN)"
      if ($maN -ne 0) { $loiMay = $true; $luuY += "npm cài $($_.Name) lỗi mã $maN`: $($ra.Substring([math]::Max(0, $ra.Length - 400)))" }
    }
  }
  # cổng kiểm bản của main, chạy lenh_kiem trong worktree thợ; một thợ một lúc (next build ăn RAM)
  $mxK = New-Object System.Threading.Mutex($false, "Global\ENGINE-CongKiem"); $coK = $false; try { $coK = $mxK.WaitOne(3600000) } catch [System.Threading.AbandonedMutexException] { $coK = $true }
  # không chạy cổng kiểm khi chưa giữ khoá (9/11: hết 20 phút rồi chạy chồng làm cạn RAM); can-cham.txt còn nên lượt sau chấm lại
  if (-not $coK) { Ghi "chờ khoá cổng kiểm quá 60 phút, để lượt sau chấm $fid"; exit 0 }
  # Linh 9/11: chỉ chạy lại lệnh kiểm của feature trùng vùng file đã sửa + feature vừa nộp; 12 giờ một lần chạy toàn bộ
  $dauDD = "$Canh\kiem-day-du.txt"
  if (-not (Test-Path $dauDD)) { "$(Get-Date -Format s) mốc đầu" | Set-Content $dauDD }
  if ((Test-Path $dauDD) -and ((Get-Date) - (Get-Item $dauDD).LastWriteTime).TotalHours -lt 12) {
    $mbK = (git merge-base HEAD $NhanhTH 2>$null | Out-String).Trim(); if (-not $mbK) { $mbK = $goc }
    git diff --name-only "$mbK..HEAD" 2>$null | Set-Content -Encoding utf8 "$tamTho\doi.txt"
    $env:CONG_KIEM_DOI = "$tamTho\doi.txt"; $env:CONG_KIEM_THEM = $fid
  } else { "$(Get-Date -Format s) $fid" | Set-Content $dauDD; Ghi "cổng kiểm chạy toàn bộ (12 giờ một lần)" }
  $ck =py -3.12 "$TichHop\canh\cong_kiem.py" kiem "$Wt\$FF" 2>&1 | Out-String
  Remove-Item Env:CONG_KIEM_DOI, Env:CONG_KIEM_THEM -ErrorAction SilentlyContinue
  $maCk = $LASTEXITCODE
  try { $mxK.ReleaseMutex() } catch {}
  if ($maCk -ne 0) { $loi += "cong_kiem trượt:`n$ck" }
  if ($ck -match 'Timeout \d+ms exceeded|TimeoutExpired|timed out after \d+ seconds|SIGTERM|page-data-collection-timeout|is not recognized as an internal|PageNotFoundError|Unknown command') { $loiMay = $true }
  git checkout -q -- $FF 2>&1 | Out-Null
  Remove-Item "$Wt\KIEM-*.json" -Force -ErrorAction SilentlyContinue
  $tieuChi = ($x.tieu_chi | ForEach-Object { "  - $_" }) -join "`n"
  $de = @"
Bạn là Bàng Thống, người canh LINHX ENGINE. Review phần agy làm cho feature $fid trên nhánh ${Nhanh}: git diff $goc..HEAD (chỉ phần này).
Feature $fid`: $($x.mo_ta)
Tiêu chí:
$tieuChi
Vùng được sửa: $(@($x.vung) -join ', ') (cổng vùng đã chạy bằng máy).
Hợp đồng: tests/nghiem-thu/HOP-DONG.md và tests/nghiem-thu/test_$($fid.ToLower()).py.
Kết quả cổng kiểm (đã chạy ngoài tay thợ, không cần tự chạy lại): $ck
Chấm theo rủi ro: dữ liệu khách, quyền, tiền, bí mật là mức cao, lỗi là CHUA_DAT. Phần còn lại chỉ CHUA_DAT khi luồng chính sai hoặc làm cho qua test mà không làm thật
(ví dụ bằng chứng VM bịa: log/JSON không giống đầu ra thật, thời điểm vô lý; hàm trả cứng theo đúng dữ liệu test).
Lỗi nhỏ ghi mục "## Lưu ý" (file:dòng + việc), không chặn. Ý tưởng ngoài phạm vi để mục "## Ý tưởng".
Trả lời: dòng 1 chỉ là DAT hoặc CHUA_DAT. Sau đó tối đa 10 gạch đầu dòng, mỗi dòng file:dòng và việc phải sửa. Không sửa file nào, đọc ít file nhất có thể.
"@
  $c = ChamClaude $de "$tamTho\de-review.txt" "cham-$ten"
  $review = $c.review
  $kl = if ($loi.Count -gt 0 -or $c.kl -ne "DAT") { "CHUA_DAT" } else { "DAT" }
  # K4: feature nhạy cảm qua thêm lượt chấm bảo mật trước khi gộp
  if ($kl -eq "DAT" -and @($dk.bao_mat) -contains $fid) {
    $deBM = @"
Bạn là người chấm bảo mật LINHX ENGINE. Feature $fid ($($x.mo_ta)) vừa đạt nghiệm thu. Đọc toàn bộ phần của feature: git diff $NhanhTH...HEAD.
Chỉ tìm lỗi bảo mật thật, có đường khai thác cụ thể: thiếu kiểm quyền hoặc kiểm khoá (webhook, API allow_guest), giá/số tiền nhận từ client,
chống trùng giao dịch sai, lộ dữ liệu khách (email, SĐT, hồ sơ) ra API công khai hoặc log, SQL/lệnh ghép chuỗi từ dữ liệu ngoài,
bí mật viết trong code, so khoá không hằng thời gian, đổi trạng thái tiền không trong giao dịch.
Trả lời: dòng 1 chỉ là DAT (không có lỗi mức cao) hoặc CHUA_DAT. Sau đó tối đa 8 gạch đầu dòng: file:dòng, cách khai thác, cách sửa. Không sửa file nào.
"@
    $bm = ChamClaude $deBM "$tamTho\de-bao-mat.txt" "baomat-$ten"
    $review += "`n`n## Bảo mật (K4): $($bm.kl)`n$($bm.review)"
    if ($bm.kl -ne "DAT") { $kl = "CHUA_DAT"; $loi += "Chấm bảo mật (K4) CHUA_DAT: sửa đúng các điểm ở mục Bảo mật" }
  }
  # K7: feature có kiểm tích hợp HTTP thật trên bench (dieu-khien.json tich_hop: {ID: "th_x.py"}) chạy sau khi đạt hộp đen
  $thTep = if ($dk.tich_hop) { $dk.tich_hop.$fid } else { $null }
  if ($kl -eq "DAT" -and $thTep) {
    $thRa = & powershell -NoProfile -ExecutionPolicy Bypass -File "$TichHop\canh\bench.ps1" th -Tho $Tho $thTep 2>&1 | Out-String
    $thMa = $LASTEXITCODE
    Ghi "kiểm tích hợp $fid ($thTep) mã $thMa"
    $review += "`n`n## Tích hợp bench (K7): mã $thMa`n``````n$($thRa.Substring([math]::Max(0, $thRa.Length - 1500)))`n``````"
    if ($thMa -ne 0) { $kl = "CHUA_DAT"; $loi += "Kiểm tích hợp trên bench trượt (tests/nghiem-thu/tich-hop/$thTep, đọc đầu file để biết hợp đồng): xem mục Tích hợp bench" }
  }
  $sha = (git rev-parse --short HEAD).Trim()
  if ($kl -eq "DAT") {
    # Gộp vào main (khoá chung giữa các thợ)
    $mx = KhoaTH
    git push -q -u origin $Nhanh 2>&1 | Out-Null
    KeoTH
    git -C $TichHop merge -q --no-ff -m "canh: gộp $fid từ $Nhanh (DAT, commit $sha)" $Nhanh 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { git -C $TichHop merge --abort 2>&1 | Out-Null; $kl = "CHUA_DAT"; $loi += "Xung đột khi gộp vào ${NhanhTH}: gộp $NhanhTH vào nhánh này (git merge $NhanhTH), giải xung đột, chạy lại lệnh kiểm, commit" }
    else { DayTH; Remove-Item "$Canh\nhan\$fid.txt", "$S\dang.txt", "$Canh\tac\$fid.txt", "$S\moc-$fid.txt" -Force -ErrorAction SilentlyContinue; Ghi "$fid DAT, đã gộp vào $NhanhTH" }
    $mx.ReleaseMutex()
  }
  if ($kl -eq "CHUA_DAT" -and $loiMay -and $c.kl -eq "DAT") {
    # lỗi máy (npm/next build/RAM), không phải lỗi thợ: không tính vào trần K2
    Ghi "$fid trượt do lỗi máy (commit $sha), không tính lần"
    $luuY += "Lượt này trượt do lỗi máy của canh (npm, next build, RAM), không tính vào trần. Không cần sửa gì vì lý do này."
  } elseif ($kl -eq "CHUA_DAT") {
    $n = 1 + (SoTac $fid); "$n" | Set-Content "$Canh\tac\$fid.txt"
    Ghi "$fid CHUA_DAT lần $n (commit $sha)"
    if ($n -ge $Tran) {
      # K2: lùi về mốc (giữ bản hỏng ở nhánh cục bộ), ngưng giao, báo Linh
      $moc = if (Test-Path "$S\moc-$fid.txt") { (Get-Content "$S\moc-$fid.txt").Trim() } else { $goc }
      $hong = "hong/$fid-$(Get-Date -Format 'yyyyMMdd-HHmm')"
      git branch -f $hong HEAD 2>&1 | Out-Null
      git reset -q --hard $moc 2>&1 | Out-Null
      Remove-Item "$Canh\nhan\$fid.txt", "$S\dang.txt", "$S\moc-$fid.txt" -Force -ErrorAction SilentlyContinue
      Add-Content -Encoding utf8 "$Canh\CAN-LINH.md" "- $(Get-Date -Format s) $fid CHUA_DAT $n lần liền (thợ $Tho): đã lùi $Nhanh về mốc $($moc.Substring(0, [math]::Min(8, $moc.Length))), bản hỏng giữ ở nhánh cục bộ $hong, ngưng giao. Cần Khổng Minh chia nhỏ hoặc Linh quyết; giao lại thì xoá D:\LINHX\ENGINE-canh\tac\$fid.txt"
      Ghi "$fid chạm trần $n lần CHUA_DAT: lùi về mốc, dừng"
    }
  }
  if (-not (Test-Path "$Canh\phieu.tsv")) { $CotPhieu | Set-Content -Encoding utf8 "$Canh\phieu.tsv" }
  Add-Content -Encoding utf8 "$Canh\phieu.tsv" "$bd`t$(Get-Date -Format s)`t$Tho`t$ten`t$fid`t$loai`t$dung`t$kl`t$phut`t$tkV`t$tkR"
  $nd = "$kl`n`nFeature $fid · commit $sha · nhánh $Nhanh · $(Get-Date -Format s)`n"
  if ($loi.Count) { $nd += "`n## Rào cứng`n" + (($loi | ForEach-Object { "- $_" }) -join "`n") + "`n" }
  if ($luuY.Count) { $nd += "`n## Lưu ý máy`n" + (($luuY | ForEach-Object { "- $_" }) -join "`n") + "`n" }
  $nd += "`n## Claude review`n$review"
  $nd | Set-Content -Encoding utf8 "$S\TRANG-THAI.md"
  Copy-Item "$S\TRANG-THAI.md" "$S\log\review-$ten-$fid.md" -Force
  if (Test-Path "$Wt\.canh-tho\anh") { New-Item -ItemType Directory -Force "$S\log\anh-$ten" | Out-Null; Copy-Item "$Wt\.canh-tho\anh\*" "$S\log\anh-$ten\" -Force -ErrorAction SilentlyContinue }
  Remove-Item "$S\can-cham.txt" -Force
}

# 3. Giao phiếu mới khi thợ rảnh
if (-not $dangChay -and ($dk.trang_thai -eq "chay" -or $ThuChon)) {
  # khoá giao: chọn + giữ feature là một bước, hai thợ chạy cùng lúc không nhận trùng (lỗi 8/11 06:39)
  $mxGiao = New-Object System.Threading.Mutex($false, "Global\ENGINE-Giao"); try { [void]$mxGiao.WaitOne(120000) } catch [System.Threading.AbandonedMutexException] {}
  $tatTH = @(TatCaF $dk $TichHop)
  $daDat = @{}; foreach ($y in $tatTH) { if ($y.passes) { $daDat[$y.id] = $true } }
  $coProto = -not (@($Proto | Where-Object { -not (Test-Path $_) }).Count)
  $cho = @($dk.cho.PSObject.Properties | ForEach-Object Name | Where-Object { -not ($_ -eq "N2" -and $coProto) })
  $nhomBan = @(); $giuBoi = @{}
  Get-ChildItem "$Canh\nhan\*.txt" -ErrorAction SilentlyContinue | ForEach-Object { $t = (Get-Content $_.FullName).Trim(); $giuBoi[$_.BaseName] = $t; if ($t -ne "$Tho") { $nhomBan += $(if ($dk.nhom.($_.BaseName)) { $dk.nhom.($_.BaseName) } else { $_.BaseName }) } }
  $dang = if (Test-Path "$S\dang.txt") { (Get-Content "$S\dang.txt").Trim() } else { "" }
  $tt = if (Test-Path "$S\TRANG-THAI.md") { (Get-Content "$S\TRANG-THAI.md" -TotalCount 1 -Encoding utf8).Trim() } else { "" }
  $them = ""; $loaiMoi = "moi"
  if ($dang -and -not $daDat[$dang] -and (SoTac $dang) -lt $Tran) {
    $chon = $dang
    if ($tt -eq "CHUA_DAT") { $loaiMoi = "sua"; $them = "`n## Lượt sửa: người canh chấm CHUA_DAT, sửa đúng các điểm dưới đây, không làm việc mới`n" + (Get-Content "$S\TRANG-THAI.md" -Raw -Encoding utf8) }
  } else {
    if ($dang) { Remove-Item "$S\dang.txt" -Force -ErrorAction SilentlyContinue }
    $chon = $dk.giao | Where-Object {
      $id = $_; $y = $tatTH | Where-Object id -eq $id; $nh = if ($dk.nhom.$id) { $dk.nhom.$id } else { $id }
      $y -and -not $daDat[$id] -and ($cho -notcontains $id) -and (SoTac $id) -lt $Tran -and (-not $giuBoi[$id] -or $giuBoi[$id] -eq "$Tho") -and
      (@($y.phu_thuoc | Where-Object { $_ -and -not $daDat[$_] }).Count -eq 0) -and ($nhomBan -notcontains $nh) -and
      (Test-Path "$TichHop\tests\nghiem-thu\test_$($id.ToLower()).py")
    } | Select-Object -First 1
  }
  $ram = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
  if ($ThuChon) { $mxGiao.ReleaseMutex(); Write-Output "tho $Tho se nhan: $(if ($chon) { $chon } else { '(khong co)' }); cho: $($cho -join ','); nhom ban: $($nhomBan -join ',')"; $mxTho.ReleaseMutex(); exit 0 }
  if ($chon -and $ram -lt 1.5) { Ghi "RAM trống $ram GB < 1,5 GB, chưa giao $chon"; $chon = $null }
  if ($chon) { "$Tho" | Set-Content "$Canh\nhan\$chon.txt"; $chon | Set-Content "$S\dang.txt" }
  $mxGiao.ReleaseMutex()
  if (-not $chon) { if (-not (Test-Path "$S\rong.txt")) { Ghi "không có feature giao được lúc này (chờ phụ thuộc, nhóm, trần, hoặc danh sách cho)"; "" | Set-Content "$S\rong.txt" } }
  else {
    Remove-Item "$S\rong.txt" -Force -ErrorAction SilentlyContinue
    # lấy phần đã tích hợp (feature thợ khác đã đạt) trước khi làm
    git merge -q --no-edit $NhanhTH 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { git merge --abort 2>&1 | Out-Null; $them += "`n## Trước khi làm`nChạy git merge $NhanhTH, giải xung đột, giữ phần đã đạt của cả hai bên, commit `"${chon}: gộp tích hợp`"." }
    # K2: mốc = trạng thái nhánh lúc giao lần đầu feature này
    if (-not (Test-Path "$S\moc-$chon.txt")) { (git rev-parse HEAD).Trim() | Set-Content "$S\moc-$chon.txt" }
    $tf = TimF $dk $TichHop $chon; $y = $tf.f; $FF = $tf.ff
    $ten = "$(Get-Date -Format 'yyyyMMdd-HHmm')-t$Tho"
    $rieng = switch ($chon) {
      "N1" { "- Riêng N1: được ``git push -u origin $Nhanh`` để CI GitHub chạy. Máy không có gh: đọc kết quả lượt chạy qua API GitHub (lấy quyền bằng git credential, KHÔNG in hay ghi token ra file). Workflow đặt ở .github/workflows/linhx-engine.yml, chạy py canh/cong_kiem.py kiem cho từng features-dot1*.json." }
      "N2" { "- Riêng N2: chép từ D:\LINHX\PROTO\03_OPC_OS và D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG. Bỏ .env*, khoá, token, file phiên, cơ sở dữ liệu, dữ liệu khách, node_modules, ảnh/video nặng." }
      default { "- VM thật: linhx-engine-1 (gcloud project linhx-engine, zone asia-southeast1-b). gcloud scp trên Windows dùng /home/ADMIN/ (không dùng ~). Bí mật chỉ ở /root/linhx-bi-mat.env trên VM: không chép về máy, không in ra log, không đưa vào bằng chứng." }
    }
    @"
# Phiếu $ten · LINHX ENGINE · feature $chon
Repo: $Wt (repo riêng linhx-engine), nhánh $Nhanh (thợ $Tho). Mọi đường dẫn tính từ gốc repo. Chỉ làm theo phiếu này.

## Việc
$chon`: $($y.mo_ta)
Tiêu chí:
$(($y.tieu_chi | ForEach-Object { "- $_" }) -join "`n")
Lệnh kiểm (chạy ở gốc repo): ``$($y.lenh_kiem)``
Hợp đồng đường dẫn, tên hàm, dạng bằng chứng: tests/nghiem-thu/HOP-DONG.md và tests/nghiem-thu/test_$($chon.ToLower()).py. Đọc, không sửa.
$them

## Luật
- Vùng được sửa của ${chon}: $(@($y.vung) -join ', '), cộng bang-chung/$chon/. Sửa hay ghi file ngoài vùng (kể cả ghi rồi xoá) là CHUA_DAT máy, không ai đọc diff.
- Cấm sửa: tests/nghiem-thu/, *.khoa, pytest.ini, canh/, .canh/.
- Không skip/xfail test. Không commit .env, khoá, mật khẩu, dữ liệu khách. Không gọi SePay thật.
- Bằng chứng phải từ lần chạy thật; không tự viết tay số liệu. Người canh đối chiếu lại.
$rieng
- Xong: trong $FF chỉ đổi 2 trường của $chon`: "passes": true và "bang_chung": "<đường dẫn tương đối từ gốc repo tới file bằng chứng>".
- Trước commit chạy lệnh kiểm và ``py -3.12 canh/cong_kiem.py kiem $FF``, rồi ``git checkout -- $FF`` nếu cổng kiểm hạ passes về false; xoá KIEM-*.json.
- Commit trên nhánh hiện tại, thông điệp bắt đầu bằng ``${chon}: ``. Không tạo nhánh. Tắt server, tiến trình nền đã mở trước khi kết thúc.
- Hộp giờ $PhutToiDa phút. Làm phần nhỏ nhất cho lệnh kiểm xanh. Hết giờ mà chưa xong thì commit phần đã chạy được.
- Chưa đạt $Tran lượt liền thì nhánh bị lùi về mốc và feature dừng: mỗi lượt sửa đúng điểm người canh nêu.
$(if ($dk.ghi_chu_cho_agy) { "- Ghi chú của Linh: $($dk.ghi_chu_cho_agy)" })

## Cuối lượt
Thêm vào cuối .canh-tho/CAI-TIEN-AGY.md, dưới tiêu đề ``### $ten``, đúng 3 dòng: Tri thức, Tránh, Cải thiện.
Ý tưởng ngoài phạm vi: KHÔNG tự làm, thêm một dòng vào .canh-tho/Y-TUONG.md.
"@ | Set-Content -Encoding utf8 "$tamTho\PHIEU.md"
    Copy-Item "$tamTho\PHIEU.md" "$S\log\phieu-$ten.md"
    (git rev-parse HEAD).Trim() | Set-Content "$S\goc.txt"
    $dd = if ($dk.agy_dinh_dang) { $dk.agy_dinh_dang } else { "stream-json" }
    $ts = @("-p", '"Doc va lam theo dung file .canh-tho/PHIEU.md (tieng Viet). Thu muc lam viec la thu muc hien tai."', "--output-format", $dd)
    if ($dk.agy_toan_quyen) { $ts += "--dangerously-skip-permissions" }
    if ($dk.agy_model) { $ts += @("--model", $dk.agy_model) }
    if ($dk.agy_effort) { $ts += @("--effort", $dk.agy_effort) }
    $p = Start-Process -FilePath $LenhAgy -WorkingDirectory $Wt -NoNewWindow -PassThru -ArgumentList $ts `
          -RedirectStandardOutput "$LogDir\$ten.jsonl" -RedirectStandardError "$S\log\agy-$ten.err"
    "$($p.Id);$(Get-Date -Format s);$ten;$chon;$loaiMoi" | Set-Content -Encoding utf8 "$S\phieu.txt"
    Remove-Item "$S\nhip.txt" -Force -ErrorAction SilentlyContinue
    # agy thoát là chấm ngay (lịch 10 phút vẫn là lưới an toàn)
    Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command",
      "Wait-Process -Id $($p.Id) -ErrorAction SilentlyContinue; Start-Sleep 5; & '$PSCommandPath' -Tho $Tho")
    Ghi "giao agy phiếu $ten`: $chon$(if ($loaiMoi -eq 'sua') { ' (lượt sửa)' })"
  }
}
try { $mxTho.ReleaseMutex() } catch {}
