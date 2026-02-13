@echo off
REM AutoID Validator - Setup Script
REM Ini akan menginstall semua dependencies yang diperlukan

echo ============================================
echo   AutoID Validator - Setup Script
echo ============================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python 3.8+ dari https://python.org
    pause
    exit /b 1
)

echo [OK] Python terdeteksi
echo.

REM Install dependencies
echo [1/4] Menginstall dependencies Python...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Gagal menginstall dependencies
    echo Jalankan manual: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies terinstall
echo.

REM Install Playwright browsers
echo [2/4] Menginstall Playwright browsers...
python -m playwright install >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Gagal menginstall Playwright browsers
    echo Jalankan manual: python -m playwright install
)
echo [OK] Playwright browsers terinstall
echo.

REM Create .env file if not exists
echo [3/4] Membuat file konfigurasi...
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo [OK] File .env dibuat
    echo.
    echo [WARNING] HARAP EDIT FILE .env DAN ISI KREDENSIAL ANDA!
) else (
    echo [OK] File .env sudah ada
)
echo.

REM Create screenshots directory
echo [4/4] Membuat folder screenshot...
if not exist "screenshots" mkdir screenshots >nul
echo [OK] Folder screenshots dibuat
echo.

echo ============================================
echo   SETUP SELESAI!
echo ============================================
echo.
echo Langkah selanjutnya:
echo 1. Edit file .env dan isi kredensial Anda
echo 2. Jalankan: python main.py --demo (untuk test)
echo 3. Jalankan: python main.py (untuk produksi)
echo.
echo atau klik run_validator.bat untuk memulai
echo.
pause
