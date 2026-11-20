model: mac-dinh
phieu: yl19-staging
may: may-2
trang_thai: xong
tep_doi: KET-QUA.md, theo_doi/yl19-stg-00-git.log, theo_doi/yl19-stg-00-prod-before.log, theo_doi/yl19-stg-01-vm-before.log, theo_doi/yl19-stg-02-deploy.log, theo_doi/yl19-stg-03a-api.log, theo_doi/yl19-stg-03b-chromium.log, theo_doi/yl19-stg-03d-pdfinfo.log, theo_doi/yl19-stg-03d-pdftotext-sample.log, th...
drive: G:\My Drive\LINHX-VIEC\yl19-staging\theo_doi\yl19-stg-browser-download.pdf, G:\My Drive\LINHX-VIEC\yl19-staging\theo_doi\yl19-stg-pdf-run2.pdf, G:\My Drive\LINHX-VIEC\yl19-staging\theo_doi\yl19-stg-pdf-run3.pdf
phut: 11.72
token: vao=126971 ra=24331

Đang chạy bước 2 (`infra\deploy.bat lab --staging` trên nhánh `agy/yl19-tap-chi-pdf` commit `036ea544`) và kiểm tra Poppler cục bộ. Sẽ tự động tiếp tục bước 3 kiểm staging ngay khi tiến trình build & deploy hoàn tất.
Đã cài xong Poppler (`pdftoppm` 25.07.0-0) qua `winget` và xác nhận sẵn `playwright` cùng selector nút `[data-nut="pdf"]`. Đang chờ bước 2 (`infra\deploy.bat lab --staging`) hoàn tất để chạy ngay các bước kiểm staging.
Đang chạy Playwright kiểm màn tạp chí trên staging ở 360px/1280px, bấm thật nút "TẢI PDF A5" và xác minh file PDF tải về. Sẽ tổng hợp kết quả và commit bằng chứng ngay sau khi xong.
dat: co

- **Nhánh / SHA staging**: `agy/yl19-tap-chi-pdf` · `036ea544ec27` (`036ea544ec27f09e963712e865c33f1a7a4540ba`), `/healthz` HTTP `200` (`{"ok":true,"commit":"036ea544ec27","uptimeSec":33,"db":"ok"}`).
- **Ổ / RAM VM (`ifagent-event`)**:
  - Trước deploy: ổ `/` `28G/38G` (trống `11G`, `73%` — ≥ 5 GB nên không prune); 
...[cat bot]...
/ifagent-wt/yl19-tap-chi-pdf/bang-chung/yl19-staging/stg-pdf-8-trang.png) (`309,1 KB`, `1340×944`, từ `pdftoppm -png -r 100`).
- **Bằng chứng commit & push `agy/yl19-tap-chi-pdf` (`fe7d790f`)**: `bang-chung/yl19-staging/` (`stg-pdf-8-trang.png`, `stg-tap-chi-360.png`, `stg-tap-chi-1280.png`, `stg-mau-k1.pdf`, `kiem-staging.log`) · [KET-QUA.md](file:///C:/linhx/hang-doi/runner/viec/lam-viec/KET-QUA.md).
