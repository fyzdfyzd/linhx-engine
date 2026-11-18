# Nhật ký debug agy: kn-kiem-crawler-fb-m1

- trang_thai: xong
- ly_do: (khong)
- conversation_id: c1d91bc6-98e0-4d71-a75e-0bd596aeebf6
- nguon_buoc: hoi-thoai:transcript_full.jsonl
- so_buoc_ghi: 18

## 60 bước cuối

### 1. [2026-11-18T04:55:08Z] read_file
- lenh: `D:\linhx\hang-doi\runner\viec\lam-viec\viec\kn-thu\DE-BAI.md#L1-100`
- ma_thoat: `ERROR`
- dau_ra_cuoi:
```text
Created At: 2026-11-18T11:55:11+07:00
Completed At: 2026-11-18T11:55:11+07:00
Encountered error in step execution: file does not exist
```

### 2. [2026-11-18T04:55:08Z] read_file
- lenh: `D:\LINHX_CRAWLER\README.md#L1-100`
- ma_thoat: `-`
- dau_ra_cuoi:
```text
98:    * Cập nhật danh mục chỉ mục tổng tại `data/AI_VIETNAM_2026/_MASTER/scan_index.csv`.
99:
100: #### Luồng 2: Kích hoạt Social Extension Task Queue
```

### 3. [2026-11-18T04:55:08Z] run_command
- lenh: `rg -n "facebook|fb" D:\LINHX_CRAWLER --max-count 20`
- ma_thoat: `1`
- dau_ra_cuoi:
```text
+                                                                ~~
    + CategoryInfo          : ObjectNotFound: (rg:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
```

### 4. [2026-11-18T04:55:13Z] run_command
- lenh: `Get-ChildItem -Path D:\linhx\hang-doi\runner\viec\lam-viec -Filter "*DE-BAI*" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
Completed At: 2026-11-18T11:55:19+07:00
Command exited with code 0.
No output from the command.
```

### 5. [2026-11-18T04:55:13Z] run_command
- lenh: `Get-ChildItem -Path D:\LINHX_CRAWLER\server\api -File | Select-Object Name`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
routes.py
social_routes.py
__init__.py
```

### 6. [2026-11-18T04:55:13Z] run_command
- lenh: `Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction SilentlyContinue | ConvertTo-Json`
- ma_thoat: `1`
- dau_ra_cuoi:
```text
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRequest) [Invoke-RestMethod], WebExc
   eption
    + FullyQualifiedErrorId : WebCmdletWebResponseException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand
```

### 7. [2026-11-18T04:55:28Z] read_file
- lenh: `D:\linhx\hang-doi\runner\viec\kn-thu\DE-BAI.md#L1-100`
- ma_thoat: `ERROR`
- dau_ra_cuoi:
```text
Created At: 2026-11-18T11:55:31+07:00
Completed At: 2026-11-18T11:55:31+07:00
Encountered error in step execution: file does not exist
```

### 8. [2026-11-18T04:55:28Z] read_file
- lenh: `D:\LINHX_CRAWLER\server\api\social_routes.py#L1-120`
- ma_thoat: `-`
- dau_ra_cuoi:
```text
118:     await slog("info", "ingest_html", f"Article {url} ({len(text_content)} chars)")
119:     return {
120:         "status": "ok",
```

### 9. [2026-11-18T04:55:28Z] read_file
- lenh: `D:\LINHX_CRAWLER\server\main.py#L1-60`
- ma_thoat: `-`
- dau_ra_cuoi:
```text
58:                 scenario_json=json.dumps(scenario, ensure_ascii=False),
59:                 targets_json=json.dumps(targets, ensure_ascii=False),
60:             )
```

### 10. [2026-11-18T04:55:31Z] run_command
- lenh: `Get-ChildItem -Path D:\LINHX_CRAWLER\extension\modules -File | Select-Object Name`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
x.js
youtube.js
_template.js
```

### 11. [2026-11-18T04:55:31Z] run_command
- lenh: `Select-String -Path D:\LINHX_CRAWLER\server\api\*.py -Pattern "facebook" | Select-Object Filename, LineNumber, Line -First 15`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
cms_routes.py           1034         platforms = ["threads", "facebook", "linkedin", "tiktok", "youtube"]
cms_routes.py           1387             "Nền tảng / Loại": req.get("Nền tảng / Loại", "Facebook Group"),
project_routes.py         54         description="Engine type: web_direct, facebook, tiktok, tiktok_shop, youtube, t...
```

### 12. [2026-11-18T04:55:31Z] run_command
- lenh: `Test-Path D:\linhx\hang-doi\runner\viec\lam-viec\xong`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
False
```

### 13. [2026-11-18T04:55:39Z] run_command
- lenh: `Get-Process -Name python* -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, CommandLine`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
22640 python
22784 python
24908 python
```

### 14. [2026-11-18T04:55:39Z] run_command
- lenh: `Select-String -Path D:\LINHX_CRAWLER\server\api\social_routes.py -Pattern "@router\." | Select-Object LineNumber, Line`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
       311 @router.get("/data/target/{target_id}")
       316 @router.get("/logs")
       321 @router.post("/logs/clear")
```

### 15. [2026-11-18T04:55:39Z] run_command
- lenh: `New-Item -ItemType Directory -Force -Path "D:\linhx\hang-doi\runner\viec\lam-viec\xong\kn-kiem-crawler-fb-m1" | Out-Null; Test-Path "D:\linhx\hang-doi\runner\viec\lam-viec\xong\kn-kiem-crawler-fb-m1"`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
True
```

### 16. [2026-11-18T04:55:55Z] run_command
- lenh: `netstat -ano | findstr ":800" | findstr "LISTENING"`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
  TCP    127.0.0.1:8000         0.0.0.0:0              LISTENING       7608
  TCP    127.0.0.1:8000         0.0.0.0:0              LISTENING       6336
```

### 17. [2026-11-18T04:55:55Z] run_command
- lenh: `Test-Path D:\LINHX_CRAWLER\server\.env`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
True
```

### 18. [2026-11-18T04:55:55Z] run_command
- lenh: `Get-Process -Name chrome -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count`
- ma_thoat: `0`
- dau_ra_cuoi:
```text
39
```
