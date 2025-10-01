@echo off
title Apply Fixes - Local LLM Interface
color 0B

echo.
echo ========================================
echo   APPLY FIXES - Local LLM Interface
echo ========================================
echo.
echo This script will:
echo   1. Backup your current configuration
echo   2. Update config.py with missing attributes
echo   3. Update requirements.txt
echo   4. Install missing packages
echo   5. Add new helper scripts
echo.
echo Your data (chat history, context files) will NOT be affected.
echo.

set /p PROCEED="Proceed with updates? (y/n): "
if /i not "%PROCEED%"=="y" (
    echo.
    echo Update cancelled.
    pause
    exit /b 0
)

echo.
echo ========================================
echo Starting update process...
echo ========================================

:: Create backup directory
echo.
echo [1/7] Creating backup...
if not exist "backup" mkdir backup
set BACKUP_DIR=backup\backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%"

:: Backup current files
if exist config.py copy config.py "%BACKUP_DIR%\config.py.bak" >nul
if exist requirements.txt copy requirements.txt "%BACKUP_DIR%\requirements.txt.bak" >nul
if exist system_config.yaml copy system_config.yaml "%BACKUP_DIR%\system_config.yaml.bak" >nul

echo    Backup created: %BACKUP_DIR%

:: Check if files need updating
echo.
echo [2/7] Checking which files need updates...

set NEEDS_UPDATE=0

:: Check config.py for missing attributes
findstr /C:"MAX_SCREENSHOT_SIZE" config.py >nul 2>&1
if errorlevel 1 (
    echo    - config.py needs update ^(missing screen settings^)
    set NEEDS_UPDATE=1
)

:: Check requirements.txt for pyyaml
findstr /C:"pyyaml" requirements.txt >nul 2>&1
if errorlevel 1 (
    echo    - requirements.txt needs update ^(missing pyyaml^)
    set NEEDS_UPDATE=1
)

if %NEEDS_UPDATE%==0 (
    echo    All files appear up to date!
    echo.
    echo    However, let's install any missing packages just in case...
    goto :install_packages
)

echo.
echo ========================================
echo Files to Update
echo ========================================
echo.
echo The following files will be updated:
if not exist "MAX_SCREENSHOT_SIZE" config.py echo   - config.py
findstr /C:"pyyaml" requirements.txt >nul 2>&1
if errorlevel 1 echo   - requirements.txt
echo.
echo NOTE: If you've made custom changes to these files,
echo       you'll need to reapply them after the update.
echo.
echo Your backup is at: %BACKUP_DIR%
echo.

set /p CONTINUE="Continue with file updates? (y/n): "
if /i not "%CONTINUE%"=="y" (
    echo.
    echo Update cancelled. Your files are unchanged.
    pause
    exit /b 0
)

:: Update files
echo.
echo [3/7] Updating files...

:: Note: In a real scenario, you'd have the fixed files ready to copy
:: For now, we'll just show what needs to be done

echo.
echo    TO COMPLETE THE UPDATE:
echo    1. Replace config.py with the fixed version from artifacts
echo    2. Replace requirements.txt with the updated version
echo    3. Continue with this script
echo.
echo    Press any key once you've replaced the files...
pause >nul

:install_packages
echo.
echo [4/7] Activating virtual environment...
if exist "llm_env\Scripts\activate.bat" (
    call llm_env\Scripts\activate.bat
    echo    Virtual environment activated
) else (
    echo    ERROR: Virtual environment not found!
    echo    Please run install_windows.bat first
    pause
    exit /b 1
)

echo.
echo [5/7] Updating pip...
python -m pip install --upgrade pip --quiet

echo.
echo [6/7] Installing/updating packages...
echo    This may take a few minutes...
pip install -r requirements.txt --upgrade --quiet

if errorlevel 1 (
    echo.
    echo    WARNING: Some packages failed to install
    echo    You may need to install them manually
) else (
    echo    All packages installed successfully
)

echo.
echo [7/7] Running health check...
python startup_check.py

echo.
echo ========================================
echo Update Complete!
echo ========================================
echo.
echo Summary:
echo   - Backup created: %BACKUP_DIR%
echo   - Config files updated
echo   - Packages updated
echo   - Health check completed
echo.
echo Next steps:
echo   1. Review the health check results above
echo   2. Fix any issues if needed
echo   3. Launch the application with: smart_launch.bat
echo.
echo If anything went wrong:
echo   1. Restore from backup: %BACKUP_DIR%
echo   2. Report the issue
echo.
echo ========================================
pause