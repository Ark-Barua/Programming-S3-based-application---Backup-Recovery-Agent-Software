@echo off
title AWS S3 Automation Setup

echo Setting up environment...
cd /d "%~dp0"

:: Step 1: Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

:: Step 2: Create virtual environment
python -m venv venv

:: Step 3: Activate venv
call venv\Scripts\activate

:: Step 4: Upgrade pip
python -m pip install --upgrade pip

:: Step 5: Install required packages
pip install boto3 watchdog customtkinter

:: Step 6: Create required folders
mkdir sync_folder
mkdir backup_files
mkdir zip_source

:: Step 7: Run the GUI
echo Setup complete. Starting app...
python s3_gui.py

pause
