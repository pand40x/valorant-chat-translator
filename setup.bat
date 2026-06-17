@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   Valorant Translator - Kurulum
echo ============================================

where python >nul 2>nul
if errorlevel 1 (
  echo [HATA] Python bulunamadi.
  echo https://www.python.org/downloads/ adresinden Python 3 kurun.
  echo Kurulumda "Add python.exe to PATH" kutusunu MUTLAKA isaretleyin.
  pause
  exit /b 1
)

echo [1/3] Sanal ortam olusturuluyor (.venv)...
python -m venv .venv

echo [2/3] pip guncelleniyor...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo [3/3] Bagimliliklar kuruluyor...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

if not exist config.ini (
  copy config.example.ini config.ini >nul
  echo.
  echo [ONEMLI] config.ini olusturuldu.
  echo Lutfen bu dosyayi acip DeepSeek API anahtarinizi yazin.
)

echo.
echo Kurulum tamam. Calistirmak icin run.bat dosyasini cift tiklayin.
pause
