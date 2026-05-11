@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit
)

cd /d "%~dp0"
".venv\Scripts\python.exe" nte_auto_fishing.py
pause
