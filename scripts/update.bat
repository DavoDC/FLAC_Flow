@echo off
cd /d "%~dp0.."
echo ================================
echo  FLAC Flow - Get Latest Version
echo ================================
echo.
echo Checking for updates...
echo.

git pull

if %errorlevel% equ 0 (
    echo.
    echo Done. Run scripts\run.bat to use the latest version.
) else (
    echo.
    echo Update failed. Check your internet connection and try again.
    echo If the problem persists, re-download FLAC Flow from the repo.
)

echo.
cmd /k
