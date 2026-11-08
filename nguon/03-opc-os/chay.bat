@echo off
chcp 65001 >nul
title 03_OPC_OS - He Dieu Hanh Doanh Nghiep Mot Nguoi (Cong 8300)
cd /d "%~dp0"

echo [03_OPC_OS] Dang chay sao luu hang ngay va kiem tra khoi phuc thu...
python scripts\sao_luu_va_khoi_phuc.py

echo [03_OPC_OS] Dang kiem tra khoang dich vu luong tien co lap (SePay che do thu)...
python services\payment_service_isolated.py

:loop
echo [03_OPC_OS] Khoi dong may chu tai http://127.0.0.1:8300/ (Health: /health , Tinh trang: /tinh-trang)...
python server_ui.py
echo [03_OPC_OS] May chu vua dung hoac gap su co (ExitCode=%ERRORLEVEL%). Tu dong khoi dong lai sau 3 giay...
timeout /t 3 /nobreak >nul
goto loop
