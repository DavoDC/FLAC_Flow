@echo off
:: Human mode: no args (window stays open). Claude mode: --no-pause (clean exit).
cd /d "%~dp0.."
python src\flac_flow.py
if not "%1"=="--no-pause" cmd /k
exit /b 0
