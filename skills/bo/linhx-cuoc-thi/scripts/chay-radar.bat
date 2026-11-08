@echo off
REM Chay radar cuoc thi: quet nguon, cham diem, bang + lich .ics + digest. Dat file nay o bat ky dau.
set RADAR_HOME=D:\LINHX\LAB\LAB022-CUOC-THI-RADAR
cd /d "%RADAR_HOME%"
set PYTHONIOENCODING=utf-8
python "%~dp0contestscan.py" all >> data\radar-log.txt 2>&1
