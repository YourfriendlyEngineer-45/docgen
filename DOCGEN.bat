@echo off
REM DOCGEN — Windows launcher
REM Double-click this file to run the invoice generator.

cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python is not installed.
    echo Download it from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

python docgen-gui.py
if errorlevel 1 (
    echo.
    echo Something went wrong. See the error above.
    pause
)
