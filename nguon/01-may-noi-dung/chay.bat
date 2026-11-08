@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PORT=8010

echo ============================================================================
echo [01_MAY_TAO_NOI_DUNG] Khoi dong Local tren cong co dinh %PORT% (May MSI)
echo   - Giao dien chinh  : http://127.0.0.1:%PORT%/web/index.html
echo   - Man tinh trang   : http://127.0.0.1:%PORT%/tinh-trang
echo   - Kiem tra suc khoe: http://127.0.0.1:%PORT%/health
echo ============================================================================

REM Chay sao luu hang ngay truoc khi mo server
python scripts\sao_luu_va_khoi_phuc.py --auto-daily

if "%1"=="--once" (
    python server_web.py --port %PORT%
    exit /b %ERRORLEVEL%
)

:LOOP
echo [%DATE% %TIME%] Dang chay server_web.py tren cong %PORT%...
python server_web.py --port %PORT%
set EXIT_CODE=%ERRORLEVEL%
if %EXIT_CODE% EQU 0 (
    echo [%DATE% %TIME%] Server dung chu dong (exit 0). Ket thuc.
    exit /b 0
)
echo [%DATE% %TIME%] CANH BAO: Server bi ngat (ma loi %EXIT_CODE%). Tu dong khoi dong lai sau 3 giay...
python -c "import json, time, pathlib; p=pathlib.Path('logs/bao_loi_he_thong.jsonl'); p.parent.mkdir(exist_ok=True); open(p,'a',encoding='utf-8').write(json.dumps({'ts':time.strftime('%%Y-%%m-%%dT%%H:%%M:%%S'),'muc':'ERROR','nguon':'chay.bat','thong_bao':'May chu bi ngat dot ngot (exit=' + str(%EXIT_CODE%) + '), da tu khoi dong lai.'},ensure_ascii=False)+'\n')"
timeout /t 3 /nobreak >nul
goto LOOP
