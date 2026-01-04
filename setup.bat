@echo off
echo 🧸 Squishmallowdex Setup
echo ========================
echo.

set PY=
where py >nul 2>nul
if %errorlevel%==0 (
    set PY=py -3
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PY=python
    ) else (
        echo ❌ Python not found!
        echo.
        echo Please install Python from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during install.
        exit /b 1
    )
)

%PY% --version
if %errorlevel% neq 0 (
    echo ❌ Python is not working correctly.
    exit /b 1
)

echo.
echo 📦 Installing dependencies...
%PY% -m pip install --quiet requests beautifulsoup4 Pillow
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies.
    echo Try running this file again, or ask a helper for assistance.
    exit /b 1
)

echo.
echo 🎉 Setup complete! Run the collector with:
echo.
echo    %PY% squishmallowdex.py --limit 50
echo.
