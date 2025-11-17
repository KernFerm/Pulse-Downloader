@echo off
cd /d "%~dp0"
echo.
echo ======================================================
echo  PulseDownloader - Launcher
echo ======================================================
echo.
echo When prompted, press Enter to see the menu. Type a number (1-4) and press Enter to select an option.
echo (Do not enter a file path or command.)
echo.

:start

echo.
echo ======================================================
echo  PulseDownloader - Launcher
echo ======================================================
echo.
echo Select launch method:
echo.
echo  [1] Launch PulseDownloader (GUI)
echo  [2] Run in Command Line (CLI)
echo  [3] Install/Update Dependencies
echo  [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto :launch_gui
if "%choice%"=="2" goto :launch_cli
if "%choice%"=="3" goto :install_deps
if "%choice%"=="4" goto :exit
echo Invalid choice. Please select 1-4.
pause
goto :start

:launch_gui
echo.
echo ========================================
echo  Launching PulseDownloader (GUI)
echo ========================================
echo.
if exist Pulse_Downloader.exe (
    start "PulseDownloader" Pulse_Downloader.exe
) else (
    python Pulse_Downloader.py
)
goto :end

:launch_cli
echo.
echo ========================================
echo  Running PulseDownloader in CLI mode
echo ========================================
echo.
set url=
set outdir=
:cli_prompt
set /p url="Enter video URL (or type 'menu' to return): "
if /I "%url%"=="menu" goto :start
if "%url%"=="" (
    echo.
    echo [ERROR] No URL provided. Please enter a valid video URL or type 'menu' to return.
    goto :cli_prompt
)
set /p outdir="Enter output directory (leave blank for default): "
if exist Pulse_Downloader.exe (
    if "%outdir%"=="" (
        start "PulseDownloader CLI" Pulse_Downloader.exe --no-gui "%url%"
    ) else (
        start "PulseDownloader CLI" Pulse_Downloader.exe --no-gui "%url%" -o "%outdir%"
    )
) else (
    if "%outdir%"=="" (
        python Pulse_Downloader.py --no-gui "%url%"
    ) else (
        python Pulse_Downloader.py --no-gui "%url%" -o "%outdir%"
    )
)
echo.
echo Press any key to return to the main menu...
pause >nul
goto :start

:install_deps
cd /d "%~dp0"
echo.
echo ========================================
echo  Installing/Updating Dependencies
echo ========================================
echo.
    REM Ensure working directory is the same as run.bat
    REM Create .venv if it doesn't exist in the batch file's folder
    if not exist "%~dp0.venv\Scripts\activate.bat" echo Creating virtual environment (.venv)...
    if not exist "%~dp0.venv\Scripts\activate.bat" python -m venv "%~dp0.venv"
    REM Activate .venv in the batch file's folder
    call "%~dp0.venv\Scripts\activate.bat"
    REM Install dependencies from requirements.txt in the batch file's folder
    if exist "%~dp0requirements.txt" python -m pip install --upgrade pip setuptools
    if exist "%~dp0requirements.txt" pip install -r "%~dp0requirements.txt"
    if exist "%~dp0requirements.txt" echo Dependencies installed/updated successfully in .venv.
    if not exist "%~dp0requirements.txt" echo Warning: requirements.txt not found.
    REM Deactivate .venv in the batch file's folder
    call "%~dp0.venv\Scripts\deactivate.bat" >nul 2>&1
pause
goto :start

:end
echo.
echo ========================================
echo  Session Ended
echo ========================================
echo.
pause
goto :start

:exit
echo.
echo Goodbye!
timeout /t 2 >nul
exit /b 0
