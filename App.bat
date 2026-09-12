@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Imprest App Launcher (Multi-Station)
cd /d "%~dp0"

echo ============================================
echo      Railway Imprest Automator
echo      Multi-Station Edition
echo ============================================
echo.

echo Checking app structure...
echo.

if not exist "app.py" (
    echo [ERROR] Missing: app.py
    goto :error_structure
)

if not exist "config.py" (
    echo [ERROR] Missing: config.py
    goto :error_structure
)

if not exist "core\balance_store.py" (
    echo [ERROR] Missing folder/files: core\
    goto :error_structure
)

if not exist "core\validation.py" (
    echo [ERROR] Missing folder/files: core\
    goto :error_structure
)

if not exist "docx_engine\annexure1.py" (
    echo [ERROR] Missing folder/files: docx_engine\
    goto :error_structure
)

if not exist "docx_engine\labour.py" (
    echo [ERROR] Missing folder/files: docx_engine\
    goto :error_structure
)

if not exist "ui\tab_generate.py" (
    echo [ERROR] Missing folder/files: ui\
    goto :error_structure
)

if not exist "ui\tab_station.py" (
    echo [ERROR] Missing folder/files: ui\
    goto :error_structure
)

echo App structure OK.
echo.

echo Checking templates...
echo.

if not exist "templates\ANNEXURE_TEMPLATE.docx" (
    echo [ERROR] Missing:
    echo templates\ANNEXURE_TEMPLATE.docx
    goto :error_templates
)

if not exist "templates\LABOUR_TEMPLATE.docx" (
    echo [ERROR] Missing:
    echo templates\LABOUR_TEMPLATE.docx
    goto :error_templates
)

echo All templates found.
echo.
echo NOTE: Unlike the single-station app, this edition uses TWO
echo generic template files that are re-used for EVERY station
echo (the station's own name/officer/workers get filled in at
echo generate time from the Station Details tab^) - it does not
echo look for per-voucher-count template variants.
echo.

echo Checking Python installation...
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found on PATH.
    goto :error_python
)

python --version
echo.

echo Checking Python packages...
echo.

set NEED_INSTALL=0

python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] streamlit is not installed.
    set NEED_INSTALL=1
)

python -c "import docx" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] python-docx is not installed.
    set NEED_INSTALL=1
)

if "!NEED_INSTALL!"=="1" (
    if not exist "requirements.txt" (
        echo [ERROR] requirements.txt not found - cannot install
        echo missing packages automatically.
        goto :error_requirements
    )
    echo.
    echo Installing dependencies from requirements.txt...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] pip install failed. See the output above for details.
        goto :error_install
    )
    echo.
    echo Dependencies installed successfully.
    echo.
) else (
    echo All required packages are already installed.
    echo.
)

echo Starting application...
echo Close this window, or press Ctrl+C in it, to stop the app.
echo.

python -m streamlit run app.py
if errorlevel 1 (
    echo.
    echo ============================================
    echo Streamlit exited with an error - see the
    echo output above for details.
    echo ============================================
    echo.
    pause
)

goto :end

:error_structure
echo.
echo ============================================
echo The application cannot start because required
echo app files/folders are missing.
echo.
echo Make sure this .bat file sits directly inside
echo the railway_imprest folder, alongside app.py,
echo config.py, core\, docx_engine\, and ui\.
echo ============================================
echo.
pause
goto :end

:error_templates
echo.
echo ============================================
echo The application cannot start because one or
echo more required template files are missing.
echo.
echo Please copy both template files into:
echo.
echo templates\
echo.
echo   ANNEXURE_TEMPLATE.docx
echo   LABOUR_TEMPLATE.docx
echo.
echo See templates\README.txt for details, including
echo the required anchor text if you replace either
echo file, and the current 2-worker-slot limit on
echo LABOUR_TEMPLATE.docx.
echo ============================================
echo.
pause
goto :end

:error_python
echo.
echo ============================================
echo Python was not found on this computer's PATH.
echo.
echo Install Python 3.10 or later from python.org
echo and make sure "Add python.exe to PATH" is
echo checked during installation, then run this
echo launcher again.
echo ============================================
echo.
pause
goto :end

:error_requirements
echo.
echo ============================================
echo requirements.txt is missing from this folder,
echo so required packages cannot be installed
echo automatically.
echo.
echo Make sure this .bat file sits directly inside
echo the railway_imprest folder, alongside
echo requirements.txt.
echo ============================================
echo.
pause
goto :end

:error_install
echo.
echo ============================================
echo Failed to install required Python packages.
echo.
echo Check your internet connection, then try
echo running this launcher again. If the problem
echo continues, open a command prompt in this
echo folder and run:
echo.
echo   python -m pip install -r requirements.txt
echo.
echo to see the full error message.
echo ============================================
echo.
pause

:end
