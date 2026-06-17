@echo off
chcp 65001 >nul

:: --- Yonetici olarak calistir (oyuna giris gondermek icin gerekli) ---
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Yonetici izni isteniyor...
  powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [HATA] Once setup.bat dosyasini calistirin.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" translator.py
pause
