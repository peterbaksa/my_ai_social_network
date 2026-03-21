@echo off

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: --- Read conda environment name ---
set "ENV_NAME_FILE=%SCRIPT_DIR%\_conda_env_name"

if not exist "%ENV_NAME_FILE%" (
    echo ERROR: File '%ENV_NAME_FILE%' not found.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

set /p CONDA_ENV_NAME=<"%ENV_NAME_FILE%"
for /f "tokens=* delims= " %%a in ("%CONDA_ENV_NAME%") do set "CONDA_ENV_NAME=%%a"

if "%CONDA_ENV_NAME%"=="" (
    echo ERROR: File '%ENV_NAME_FILE%' is empty or does not contain a valid environment name.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: --- Find requirements.txt ---
set "REQUIREMENTS_FILE=%SCRIPT_DIR%\requirements.txt"

if not exist "%REQUIREMENTS_FILE%" (
    echo ERROR: File '%REQUIREMENTS_FILE%' not found.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: Check if file is empty
for %%A in ("%REQUIREMENTS_FILE%") do (
    if %%~zA==0 (
        echo ERROR: File '%REQUIREMENTS_FILE%' is empty.
        echo Press any key to close...
        pause >nul
        exit /b 1
    )
)

echo Conda environment: %CONDA_ENV_NAME%
echo Requirements file: %REQUIREMENTS_FILE%
echo.

:: --- Check if conda is available ---
where conda >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda not found. Please make sure conda is installed and in your PATH.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: --- Activate the environment ---
echo Activating conda environment '%CONDA_ENV_NAME%'...

call conda activate "%CONDA_ENV_NAME%"
if errorlevel 1 (
    echo ERROR: Failed to activate environment '%CONDA_ENV_NAME%'.
    echo Make sure the environment exists. Run _conda_install_env.bat first.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

echo Environment '%CONDA_ENV_NAME%' activated.
echo.

:: --- Install requirements ---
echo Installing Python requirements from '%REQUIREMENTS_FILE%'...
echo.

pip install -r "%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some requirements.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

echo.
echo All requirements installed successfully.
echo.
echo Press any key to close...
pause >nul
exit /b 0