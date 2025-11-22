@echo off
REM Quick Start Script for Telegram Media Downloader Bot (Windows)
REM This script automates the setup process

echo ========================================
echo Telegram Media Downloader Bot - Quick Start
echo ========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)
echo ✓ Python found
echo.

REM Check FFmpeg
echo Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg is not installed or not in PATH
    echo.
    echo FFmpeg is required for audio conversion and video processing.
    echo Download from: https://ffmpeg.org/download.html
    echo.
    echo After installation, add FFmpeg to your PATH:
    echo 1. Extract FFmpeg to a folder (e.g., C:\ffmpeg)
    echo 2. Add C:\ffmpeg\bin to your PATH environment variable
    echo.
    choice /C YN /M "Continue without FFmpeg"
    if errorlevel 2 exit /b 1
) else (
    echo ✓ FFmpeg found
)
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo ✓ Pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo ✓ Dependencies installed
echo.

REM Create .env file
if not exist ".env" (
    echo Creating .env configuration file...
    copy .env.example .env >nul
    echo ✓ .env file created
    echo.
    
    echo ========================================
    echo Bot Configuration
    echo ========================================
    echo.
    set /p BOT_TOKEN="Enter your Telegram Bot Token: "
    
    REM Update .env file
    powershell -Command "(Get-Content .env) -replace 'BOT_TOKEN=.*', 'BOT_TOKEN=%BOT_TOKEN%' | Set-Content .env"
    echo ✓ Bot token configured
) else (
    echo ✓ .env file already exists
)
echo.

REM Create downloads directory
echo Creating downloads directory...
if not exist "downloads" mkdir downloads
echo ✓ Downloads directory ready
echo.

REM Success message
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Verify your bot token in .env file
echo    notepad .env
echo.
echo 2. Start the bot:
echo    venv\Scripts\activate
echo    python telegram_media_bot.py
echo.
echo 3. Open Telegram and send /start to your bot
echo.
echo For more information, see:
echo   • README.md - Overview and features
echo   • SETUP_GUIDE.md - Detailed setup instructions
echo.
echo ========================================
echo.

REM Ask to start bot
choice /C YN /M "Would you like to start the bot now"
if not errorlevel 2 (
    echo.
    echo Starting bot...
    python telegram_media_bot.py
)

pause
