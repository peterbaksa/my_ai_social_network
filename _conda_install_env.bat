@echo off

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
:: Remove trailing backslash
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
:: Trim spaces
for /f "tokens=* delims= " %%a in ("%CONDA_ENV_NAME%") do set "CONDA_ENV_NAME=%%a"

if "%CONDA_ENV_NAME%"=="" (
    echo ERROR: File '%ENV_NAME_FILE%' is empty or does not contain a valid environment name.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: --- Read Python version ---
set "PYTHON_VERSION_FILE=%SCRIPT_DIR%\_python_version"

if not exist "%PYTHON_VERSION_FILE%" (
    echo ERROR: File '%PYTHON_VERSION_FILE%' not found.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

set /p PYTHON_VERSION=<"%PYTHON_VERSION_FILE%"
for /f "tokens=* delims= " %%a in ("%PYTHON_VERSION%") do set "PYTHON_VERSION=%%a"

if "%PYTHON_VERSION%"=="" (
    echo ERROR: File '%PYTHON_VERSION_FILE%' is empty or does not contain a valid Python version.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

echo Conda environment: %CONDA_ENV_NAME%
echo Python version:    %PYTHON_VERSION%
echo.

:: --- Check if conda is available ---
where conda >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda not found. Please make sure conda is installed and in your PATH.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: --- Check if environment already exists ---
conda env list | findstr /w "%CONDA_ENV_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo Environment '%CONDA_ENV_NAME%' already exists. No installation needed.
    echo.
    echo Press any key to close...
    pause >nul
    exit /b 0
)

:: --- Create the environment ---
echo Creating conda environment '%CONDA_ENV_NAME%' with Python %PYTHON_VERSION% ...
echo.

call conda create -n "%CONDA_ENV_NAME%" python="%PYTHON_VERSION%" -y
if errorlevel 1 (
    echo.
    echo ERROR: Failed to create environment '%CONDA_ENV_NAME%'.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

echo.
echo Environment '%CONDA_ENV_NAME%' was successfully created.
echo.
echo Press any key to close...
pause >nul
exit /b 0