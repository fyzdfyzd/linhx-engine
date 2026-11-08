@echo off
REM Radar LINHX hop nhat: cong dong, su kien, giai thuong, cuoc thi (LAB022), quy (LAB013). Mot lenh, mot ban tin.
set RADAR_HOME=D:\LINHX\LAB\LAB035-RADAR-CONG-DONG
cd /d "%RADAR_HOME%"
set PYTHONIOENCODING=utf-8
set PY=python
where py >nul 2>&1 && set PY=py -3
echo ===== %date% %time% ===== >> data\radar-log.txt
%PY% "%~dp0radar.py" all >> data\radar-log.txt 2>&1
if "%1"=="--mo" start "" "output\BAN-TIN-MOI-NHAT.md"
