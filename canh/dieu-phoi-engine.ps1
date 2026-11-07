# Điều phối LINHX ENGINE đợt 1 trên máy công ty: Claude canh, agy làm.
# Lịch ENGINE-DieuPhoi gọi mỗi 10 phút qua chay-an.vbs (ẩn hoàn toàn, luật 2/11). -Tho 0 = lượt chính: gọi từng thợ rồi ghi tổng hợp.
# Mỗi thợ: worktree D:\LINHX\LINHX-OPC\ENGINE-t<N>, nhánh tu-dong/engine-t<N>, trạng thái ngoài repo ở D:\LINHX\LINHX-OPC\ENGINE-canh\t<N>.
# Nhánh tích hợp: claude/project-thread-imkbnt ở D:\LINHX\LINHX-OPC\CHIEMTINHSO-engine. Feature DAT mới được gộp vào đây.
param([int]$Tho = 0)
$ErrorActionPreference = "Continue"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false); $OutputEncoding = [Text.UTF8Encoding]::new($false)
$TichHop = "D:\LINHX\LINHX-OPC\CHIEMTINHSO-engine"; $NhanhTH = "claude/project-thread-imkbnt"
$Repo = "D:\LINHX\LINHX-OPC\CHIEMTINHSO"
$Canh = "D:\LINHX\LINHX-OPC\ENGINE-canh"
$LenhAgy = "$env:USERPROFILE\.gemini\bin\agy.exe"
$FF = "linhx-engine\features-dot1.json"
New-Item -ItemType Directory -Force "$Canh\nhan" | Out-Null
function Ghi($s) { Add-Content -Encoding utf8 "$Canh\NHAT-KY.md" "- $(Get-Date -Format 'yyyy-MM-dd HH:mm') t${Tho}: $s" }
function DocJson($p) { Get-Content $p -Raw -Encoding utf8 | ConvertFrom-Json }
function KhoaTH { $m = New-Object System.Threading.Mutex($false, "Global\ENGINE-TichHop"); try { [void]$m.WaitOne(300000) } catch [System.Threading.AbandonedMutexException] {}; $m }

# ---------- Lượt chính ----------
if ($Tho -eq 0) {
  $mx = KhoaTH
  git -C $TichHop pull -q --ff-only origin $NhanhTH 2>&1 | Out-Null
  $dk = DocJson "$TichHop\linhx-engine\canh\dieu-khien.json"
  if ($dk.trang_thai -eq "dung_han") {
    Get-ChildItem "$Canh\t*\phieu.txt" -ErrorAction SilentlyContinue | ForEach-Object { $id = ((Get-Content $_.FullName) -split ";")[0]; Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }
    Ghi "dung_han: đã dừng agy"
  } else {
    for ($i = 1; $i -le [int]$dk.so_tho; $i++) {
      Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"", "-Tho", "$i")
    }
  }
  # Tổng hợp cho Linh: linhx-engine/.canh/TRANG-THAI.md trên nhánh tích hợp
  $f = DocJson "$TichHop\$FF"
  $dat = @($f.features | Where-Object passes | ForEach-Object id)
  $bang = "# LINHX ENGINE đợt 1: trạng thái thợ`n`nCập nhật $(Get-Date -Format 'yyyy-MM-dd HH:mm') (giờ máy cty). Đạt: $($dat.Count)/$($f.features.Count) $(if ($dat) { '(' + ($dat -join ', ') + ')' })`n`n| Thợ | Đang làm | Phiếu | Kết luận lượt chấm gần nhất |`n|---|---|---|---|`n"
  for ($i = 1; $i -le [int]$dk.so_tho; $i++) {
    $S = "$Canh\t$i"
    $dang = if (Test-Path "$S\dang.txt") { (Get-Content "$S\dang.txt").Trim() } else { "-" }
    $ph = if (Test-Path "$S\phieu.txt") { $a = (Get-Content "$S\phieu.txt" -Encoding utf8) -split ";"; "$($a[2]) từ $($a[1])" } else { "rảnh" }
    $kl = if (Test-Path "$S\TRANG-THAI.md") { $l = @(Get-Content "$S\TRANG-THAI.md" -TotalCount 3 -Encoding utf8); "$($l[0]) · $($l[2])" } else { "-" }
    $bang += "| $i | $dang | $ph | $kl |`n"
  }
  $bang += "`n## Chờ`n" + (($dk.cho.PSObject.Properties | ForEach-Object { "- $($_.Name): $($_.Value)" }) -join "`n") + "`n"
  if (Test-Path "$Canh\CAN-LINH.md") { $bang += "`n## Cần Linh`n" + (Get-Content "$Canh\CAN-LINH.md" -Raw -Encoding utf8) }
  $bang += "`n## Nhật ký gần nhất`n" + ((Get-Content "$Canh\NHAT-KY.md" -Tail 12 -Encoding utf8 -ErrorAction SilentlyContinue) -join "`n") + "`n"
  New-Item -ItemType Directory -Force "$TichHop\linhx-engine\.canh\review" | Out-Null
  $bang | Set-Content -Encoding utf8 "$TichHop\linhx-engine\.canh\TRANG-THAI.md"
  Get-ChildItem "$Canh\t*\log\review-*.md" -ErrorAction SilentlyContinue | ForEach-Object { Copy-Item $_.FullName "$TichHop\linhx-engine\.canh\review\$($_.Directory.Parent.Name)-$($_.Name)" -Force }
  git -C $TichHop add linhx-engine/.canh 2>&1 | Out-Null
  git -C $TichHop diff --cached --quiet -- linhx-engine/.canh; if ($LASTEXITCODE -ne 0) {
    git -C $TichHop commit -q -m "canh: trạng thái thợ engine $(Get-Date -Format 'yyyy-MM-dd HH:mm')" -- linhx-engine/.canh 2>&1 | Out-Null
    git -C $TichHop push -q origin $NhanhTH 2>&1 | Out-Null
  }
  $mx.ReleaseMutex()
  exit 0
}

# ---------- Lượt một thợ ----------
$Wt = "D:\LINHX\LINHX-OPC\ENGINE-t$Tho"; $Nhanh = "tu-dong/engine-t$Tho"; $S = "$Canh\t$Tho"
New-Item -ItemType Directory -Force "$S\log" | Out-Null
$lk = "$S\luot.lock"
if ((Test-Path $lk) -and ((Get-Date) - (Get-Item $lk).LastWriteTime).TotalMinutes -lt 15) { exit 0 }
New-Item -ItemType File -Force $lk | Out-Null
$dk = DocJson "$TichHop\linhx-engine\canh\dieu-khien.json"
$PhutToiDa = if ($dk.phut_toi_da) { [int]$dk.phut_toi_da } else { 40 }
if (-not (Test-Path $Wt)) {
  git -C $Repo worktree add -B $Nhanh $Wt $NhanhTH 2>&1 | Out-Null
  Ghi "tạo worktree $Wt nhánh $Nhanh"
}
Set-Location $Wt
$tamTho = "$Wt\linhx-engine\.canh-tho"; New-Item -ItemType Directory -Force $tamTho | Out-Null

# 1. Phiếu đang chạy: còn chạy, ngủ quên, quá giờ, hay xong
$dangChay = $false
if (Test-Path "$S\phieu.txt") {
  $pid0, $bd, $ten, $fid = (Get-Content "$S\phieu.txt" -Encoding utf8) -split ";", 4
  $p = Get-Process -Id $pid0 -ErrorAction SilentlyContinue
  if ($p -and $p.ProcessName -notmatch 'agy') { $p = $null }
  $phut = [int]((Get-Date) - [datetime]$bd).TotalMinutes
  $dau = (git status --porcelain | Out-String) + (git rev-parse HEAD) + ((Get-Item "$S\log\agy-$ten.out", "$S\log\agy-$ten.err" -ErrorAction SilentlyContinue | ForEach-Object { $_.Length }) -join ",")
  $nhip = "$S\nhip.txt"; $dauCu = if (Test-Path $nhip) { Get-Content $nhip -Raw -Encoding utf8 } else { "" }
  if ($dau -ne $dauCu) { $dau | Set-Content -Encoding utf8 -NoNewline $nhip }
  $ngu = $p -and ($dau -eq $dauCu) -and (((Get-Date) - (Get-Item $nhip).LastWriteTime).TotalMinutes -ge 15)
  if ($p -and $phut -lt $PhutToiDa -and -not $ngu) { $dangChay = $true }
  else {
    if ($p) { Stop-Process -Id $pid0 -Force; Ghi "dừng agy phiếu $ten ($fid): $(if ($ngu) { '15 phút không đổi gì' } else { "quá $PhutToiDa phút" })" }
    # Phần dở không cất stash (bài học Z01): commit lại để phiếu sau làm tiếp
    if (git status --porcelain) { git add -A 2>&1 | Out-Null; git commit -q -m "${fid}: phần dở cuối phiếu $ten" 2>&1 | Out-Null; Ghi "commit phần dở của $fid" }
    try { $j = Get-Content "$S\log\agy-$ten.out" -Raw -Encoding utf8 | ConvertFrom-Json; $tk = "$($j.usage.input_tokens)`t$($j.usage.output_tokens)" } catch { $tk = "khong-do-duoc`t" }
    if (-not (Test-Path "$Canh\token.tsv")) { "luc`ttho`tphieu`tfeature`ttoken_vao`ttoken_ra`tphut" | Set-Content -Encoding utf8 "$Canh\token.tsv" }
    Add-Content -Encoding utf8 "$Canh\token.tsv" "$(Get-Date -Format s)`t$Tho`t$ten`t$fid`t$tk`t$phut"
    "$fid;$ten" | Set-Content -Encoding utf8 "$S\can-cham.txt"
    Remove-Item "$S\phieu.txt" -Force
    Ghi "agy xong phiếu $ten ($fid) sau $phut phút"
  }
}

# 2. Chấm phiếu vừa xong: rào cứng + cổng kiểm + Claude đọc diff
if (-not $dangChay -and (Test-Path "$S\can-cham.txt")) {
  $fid, $ten = (Get-Content "$S\can-cham.txt" -Encoding utf8) -split ";"
  $goc = (Get-Content "$S\goc.txt").Trim()
  $loi = @()
  if ((git rev-parse HEAD).Trim() -eq $goc) { $loi += "agy không commit gì" }
  foreach ($f in @(git diff --name-only "$goc..HEAD")) {
    if ($f -like "linhx-engine/tests/nghiem-thu/*" -or $f -like "*.khoa" -or $f -eq "linhx-engine/pytest.ini") { $loi += "Sửa file cấm: $f" }
    elseif ($f -like "linhx-engine/canh/*" -or $f -like "linhx-engine/.canh/*") { $loi += "Sửa bộ điều phối: $f" }
    elseif (-not ($f -like "linhx-engine/*" -or $f -like ".github/workflows/linhx-engine*")) { $loi += "Sửa ngoài linhx-engine: $f" }
    if ($f -match '(^|/)(\.env|tho\.env)$' -or $f -match '(^|/)\.env\.(?!example$)' -or $f -match '\.(pem|key|p12)$') { $loi += "Commit file bí mật: $f" }
  }
  $them = git diff "$goc..HEAD" -U0 | Select-String '^\+'
  if ($them | Select-String -Pattern 'pytest\.mark\.skip|@skip|xfail|\.skip\(|pytest\.skip|importorskip') { $loi += "Có test bị skip/xfail" }
  if ($them | Select-String -Pattern '(sk-ant-|AIza[0-9A-Za-z_-]{20}|-----BEGIN [A-Z ]*PRIVATE KEY|ghp_[A-Za-z0-9]{30}|github_pat_)') { $loi += "Có thứ giống khoá trong diff" }
  $x = (DocJson $FF).features | Where-Object id -eq $fid
  if (-not $x.passes) { $loi += "$fid chưa đặt passes=true (thợ chưa báo xong)" }
  # cổng kiểm bản của nhánh tích hợp (thợ không sửa được), chạy lenh_kiem trong worktree thợ
  $ck = py -3.12 "$TichHop\scripts\cong_kiem.py" kiem "$Wt\$FF" 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) { $loi += "cong_kiem trượt:`n$ck" }
  git checkout -q -- $FF 2>&1 | Out-Null
  Remove-Item "$Wt\linhx-engine\KIEM-features-dot1.json" -Force -ErrorAction SilentlyContinue
  $tieuChi = ($x.tieu_chi | ForEach-Object { "  - $_" }) -join "`n"
  $de = @"
Bạn là Bàng Thống, người canh LINHX ENGINE đợt 1. Review phần agy làm cho feature $fid trên nhánh ${Nhanh}: git diff $goc..HEAD (chỉ phần này).
Feature $fid`: $($x.mo_ta)
Tiêu chí:
$tieuChi
Hợp đồng: linhx-engine/tests/nghiem-thu/HOP-DONG.md và linhx-engine/tests/nghiem-thu/test_$($fid.ToLower()).py.
Kết quả cổng kiểm (đã chạy ngoài tay thợ, không cần tự chạy lại): $ck
Chấm theo rủi ro: dữ liệu khách, quyền, tiền, bí mật là mức cao, lỗi là CHUA_DAT. Phần còn lại chỉ CHUA_DAT khi luồng chính sai hoặc làm cho qua test mà không làm thật
(ví dụ bằng chứng VM bịa: log/JSON không giống đầu ra thật, thời điểm vô lý; hàm trả cứng theo đúng dữ liệu test).
Lỗi nhỏ ghi mục "## Lưu ý" (file:dòng + việc), không chặn. Ý tưởng ngoài phạm vi để mục "## Ý tưởng".
Trả lời: dòng 1 chỉ là DAT hoặc CHUA_DAT. Sau đó tối đa 10 gạch đầu dòng, mỗi dòng file:dòng và việc phải sửa. Không sửa file nào, đọc ít file nhất có thể.
"@
  $de | Set-Content -Encoding utf8 "$tamTho\de-review.txt"
  $raw = claude -p "Doc file linhx-engine/.canh-tho/de-review.txt (UTF-8) va lam dung yeu cau trong do." --output-format json --max-turns 15 --allowedTools "Read" "Grep" "Glob" "Bash(git diff:*)" "Bash(git log:*)" "Bash(git show:*)" 2>&1 | Out-String
  try { $j = $raw | ConvertFrom-Json; $review = $j.result
        Add-Content -Encoding utf8 "$Canh\token.tsv" "$(Get-Date -Format s)`t$Tho`tcham-$ten`t$fid`t$([int]$j.usage.input_tokens + [int]$j.usage.cache_read_input_tokens)`t$($j.usage.output_tokens)`t" } catch { $review = $raw }
  $dong1 = @("$review" -split "`n" | Where-Object { $_.Trim().Trim('*', '#', ' ', [char]0xFEFF) -cmatch '^(DAT|CHUA_DAT)\b' }) | Select-Object -First 1
  $kl = if ($loi.Count -gt 0 -or "$dong1".Trim().Trim('*', '#', ' ', [char]0xFEFF) -notlike 'DAT*') { "CHUA_DAT" } else { "DAT" }
  $sha = (git rev-parse --short HEAD).Trim()
  if ($kl -eq "DAT") {
    # Gộp vào nhánh tích hợp (khoá chung giữa các thợ)
    $mx = KhoaTH
    git push -q -u origin $Nhanh 2>&1 | Out-Null
    git -C $TichHop pull -q --ff-only origin $NhanhTH 2>&1 | Out-Null
    git -C $TichHop merge -q --no-ff -m "canh: gộp $fid từ $Nhanh (DAT, commit $sha)" $Nhanh 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { git -C $TichHop merge --abort 2>&1 | Out-Null; $kl = "CHUA_DAT"; $loi += "Xung đột khi gộp vào ${NhanhTH}: gộp $NhanhTH vào nhánh này (git merge $NhanhTH), giải xung đột, chạy lại lệnh kiểm, commit" }
    else { git -C $TichHop push -q origin $NhanhTH 2>&1 | Out-Null; Remove-Item "$Canh\nhan\$fid.txt", "$S\dang.txt", "$S\tac-$fid.txt" -Force -ErrorAction SilentlyContinue; Ghi "$fid DAT, đã gộp vào $NhanhTH" }
    $mx.ReleaseMutex()
  }
  if ($kl -eq "CHUA_DAT") {
    $n = 1 + [int]("0" + (Get-Content "$S\tac-$fid.txt" -ErrorAction SilentlyContinue)); "$n" | Set-Content "$S\tac-$fid.txt"
    Ghi "$fid CHUA_DAT lần $n (commit $sha)"
    if ($n -ge 3) { Add-Content -Encoding utf8 "$Canh\CAN-LINH.md" "- $(Get-Date -Format s) $fid chưa đạt 3 lượt liền ở thợ $Tho, đã ngưng giao; cần Khổng Minh chia nhỏ hoặc Linh quyết" }
  }
  $nd = "$kl`n`nFeature $fid · commit $sha · nhánh $Nhanh · $(Get-Date -Format s)`n"
  if ($loi.Count) { $nd += "`n## Rào cứng`n" + (($loi | ForEach-Object { "- $_" }) -join "`n") + "`n" }
  $nd += "`n## Claude review`n$review"
  $nd | Set-Content -Encoding utf8 "$S\TRANG-THAI.md"
  Copy-Item "$S\TRANG-THAI.md" "$S\log\review-$ten-$fid.md" -Force
  Remove-Item "$S\can-cham.txt" -Force
}

# 3. Giao phiếu mới khi thợ rảnh
if (-not $dangChay -and $dk.trang_thai -eq "chay") {
  $ftH = DocJson "$TichHop\$FF"
  $daDat = @{}; foreach ($y in $ftH.features) { if ($y.passes) { $daDat[$y.id] = $true } }
  $cho = @($dk.cho.PSObject.Properties | ForEach-Object Name)
  $vungBan = @(); $giuBoi = @{}
  Get-ChildItem "$Canh\nhan\*.txt" -ErrorAction SilentlyContinue | ForEach-Object { $t = (Get-Content $_.FullName).Trim(); $giuBoi[$_.BaseName] = $t; if ($t -ne "$Tho") { $vungBan += $dk.vung.($_.BaseName) } }
  $dang = if (Test-Path "$S\dang.txt") { (Get-Content "$S\dang.txt").Trim() } else { "" }
  $tt = if (Test-Path "$S\TRANG-THAI.md") { (Get-Content "$S\TRANG-THAI.md" -TotalCount 1 -Encoding utf8).Trim() } else { "" }
  $them = ""
  if ($dang -and -not $daDat[$dang]) {
    if ([int]("0" + (Get-Content "$S\tac-$dang.txt" -ErrorAction SilentlyContinue)) -ge 3) { $chon = $null; Ghi "$dang đã tắc 3 lượt, không giao lại" }
    else { $chon = $dang; if ($tt -eq "CHUA_DAT") { $them = "`n## Lượt sửa: người canh chấm CHUA_DAT, sửa đúng các điểm dưới đây, không làm việc mới`n" + (Get-Content "$S\TRANG-THAI.md" -Raw -Encoding utf8) } }
  } else {
    $chon = $dk.giao | Where-Object {
      $id = $_; $y = $ftH.features | Where-Object id -eq $id
      $y -and -not $daDat[$id] -and ($cho -notcontains $id) -and (-not $giuBoi[$id] -or $giuBoi[$id] -eq "$Tho") -and
      (@($y.phu_thuoc | Where-Object { $_ -and -not $daDat[$_] }).Count -eq 0) -and ($vungBan -notcontains $dk.vung.$id) -and
      (Test-Path "$TichHop\linhx-engine\tests\nghiem-thu\test_$($id.ToLower()).py")
    } | Select-Object -First 1
  }
  $ram = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
  if ($chon -and $ram -lt 1.5) { Ghi "RAM trống $ram GB < 1,5 GB, chưa giao $chon"; $chon = $null }
  if (-not $chon) { if (-not (Test-Path "$S\rong.txt")) { Ghi "không có feature giao được lúc này (chờ phụ thuộc, vùng, hoặc danh sách cho)"; "" | Set-Content "$S\rong.txt" } }
  else {
    Remove-Item "$S\rong.txt" -Force -ErrorAction SilentlyContinue
    "$Tho" | Set-Content "$Canh\nhan\$chon.txt"; $chon | Set-Content "$S\dang.txt"
    # lấy phần đã tích hợp (feature thợ khác đã đạt) trước khi làm
    git merge -q --no-edit $NhanhTH 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { git merge --abort 2>&1 | Out-Null; $them += "`n## Trước khi làm`nChạy git merge $NhanhTH, giải xung đột, giữ phần đã đạt của cả hai bên, commit `"${chon}: gộp tích hợp`"." }
    $y = $ftH.features | Where-Object id -eq $chon
    $ten = "$(Get-Date -Format 'yyyyMMdd-HHmm')-t$Tho"
    $rieng = switch ($chon) {
      "N1" { "- Riêng N1: được ``git push -u origin $Nhanh`` để CI GitHub chạy. Máy không có gh: đọc kết quả lượt chạy qua API GitHub (lấy quyền bằng git credential, KHÔNG in hay ghi token ra file). Workflow đặt ở .github/workflows/linhx-engine.yml, chỉ chạy phần linhx-engine." }
      "N2" { "- Riêng N2: chép từ D:\LINHX\PROTO\03 OPC OS và D:\LINHX\PROTO\01 Máy tạo nội dung. Bỏ .env*, khoá, token, file phiên, cơ sở dữ liệu, dữ liệu khách, node_modules, ảnh/video nặng." }
      default { "- VM thật: linhx-engine-1 (gcloud project linhx-engine, zone asia-southeast1-b). gcloud scp trên Windows dùng /home/ADMIN/ (không dùng ~). Bí mật chỉ ở /root/linhx-bi-mat.env trên VM: không chép về máy, không in ra log, không đưa vào bằng chứng." }
    }
    @"
# Phiếu $ten · LINHX ENGINE đợt 1 · feature $chon
Repo: $Wt, nhánh $Nhanh (thợ $Tho). AGENTS.md và CLAUDE.md ở gốc repo là luật của Chiêm Tinh Số: KHÔNG áp cho phiếu này, chỉ làm theo phiếu này.

## Việc
$chon`: $($y.mo_ta)
Tiêu chí:
$(($y.tieu_chi | ForEach-Object { "- $_" }) -join "`n")
Lệnh kiểm (chạy trong thư mục linhx-engine): ``$($y.lenh_kiem)``
Hợp đồng đường dẫn, tên hàm, dạng bằng chứng: linhx-engine/tests/nghiem-thu/HOP-DONG.md và test_$($chon.ToLower()).py. Đọc, không sửa.
$them

## Luật
- Chỉ sửa trong linhx-engine/ (N1 thêm .github/workflows/linhx-engine.yml). Cấm sửa: linhx-engine/tests/nghiem-thu/, *.khoa, linhx-engine/pytest.ini, linhx-engine/canh/, linhx-engine/.canh/, scripts/.
- Không skip/xfail test. Không commit .env, khoá, mật khẩu, dữ liệu khách. Không gọi SePay thật.
- Bằng chứng phải từ lần chạy thật; không tự viết tay số liệu. Người canh đối chiếu lại.
$rieng
- Xong: trong linhx-engine/features-dot1.json chỉ đổi 2 trường của $chon`: "passes": true và "bang_chung": "<đường dẫn tương đối từ linhx-engine tới file bằng chứng>".
- Trước commit chạy lệnh kiểm và ``py -3.12 scripts/cong_kiem.py kiem linhx-engine/features-dot1.json``, rồi ``git checkout -- linhx-engine/features-dot1.json`` nếu cổng kiểm hạ passes về false; xoá KIEM-*.json.
- Commit trên nhánh hiện tại, thông điệp bắt đầu bằng ``${chon}: ``. Không tạo nhánh. Tắt server, tiến trình nền đã mở trước khi kết thúc.
- Hộp giờ $PhutToiDa phút. Làm phần nhỏ nhất cho lệnh kiểm xanh. Hết giờ mà chưa xong thì commit phần đã chạy được.
$(if ($dk.ghi_chu_cho_agy) { "- Ghi chú của Linh: $($dk.ghi_chu_cho_agy)" })

## Cuối lượt
Thêm vào cuối linhx-engine/.canh-tho/CAI-TIEN-AGY.md, dưới tiêu đề ``### $ten``, đúng 3 dòng: Tri thức, Tránh, Cải thiện.
Ý tưởng ngoài phạm vi: KHÔNG tự làm, thêm một dòng vào linhx-engine/.canh-tho/Y-TUONG.md.
"@ | Set-Content -Encoding utf8 "$tamTho\PHIEU.md"
    Copy-Item "$tamTho\PHIEU.md" "$S\log\phieu-$ten.md"
    (git rev-parse HEAD).Trim() | Set-Content "$S\goc.txt"
    $ts = @("-p", '"Doc va lam theo dung file linhx-engine/.canh-tho/PHIEU.md (tieng Viet). Thu muc lam viec la thu muc hien tai."', "--output-format", "json")
    if ($dk.agy_toan_quyen) { $ts += "--dangerously-skip-permissions" }
    if ($dk.agy_model) { $ts += @("--model", $dk.agy_model) }
    if ($dk.agy_effort) { $ts += @("--effort", $dk.agy_effort) }
    $p = Start-Process -FilePath $LenhAgy -WorkingDirectory $Wt -NoNewWindow -PassThru -ArgumentList $ts `
          -RedirectStandardOutput "$S\log\agy-$ten.out" -RedirectStandardError "$S\log\agy-$ten.err"
    "$($p.Id);$(Get-Date -Format s);$ten;$chon" | Set-Content -Encoding utf8 "$S\phieu.txt"
    Remove-Item "$S\nhip.txt" -Force -ErrorAction SilentlyContinue
    # agy thoát là chấm ngay (lịch 10 phút vẫn là lưới an toàn)
    Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command",
      "Wait-Process -Id $($p.Id) -ErrorAction SilentlyContinue; Start-Sleep 5; & '$PSCommandPath' -Tho $Tho")
    Ghi "giao agy phiếu $ten`: $chon$(if ($tt -eq 'CHUA_DAT' -and $chon -eq $dang) { ' (lượt sửa)' })"
  }
}
Remove-Item $lk -Force -ErrorAction SilentlyContinue
