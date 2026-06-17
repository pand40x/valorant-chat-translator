@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [HATA] Once setup.bat dosyasini calistirin.
  pause
  exit /b 1
)

echo PyInstaller kuruluyor...
".venv\Scripts\python.exe" -m pip install pyinstaller

echo Tek dosyalik exe olusturuluyor...
".venv\Scripts\pyinstaller.exe" --onefile --name ValorantTranslator translator.py

echo.
echo Tamam: dist\ValorantTranslator.exe
echo NOT: config.ini dosyasini exe ile AYNI klasore koymayi unutmayin.
echo NOT: exe'yi de "Yonetici olarak calistir" ile acin.
pause
