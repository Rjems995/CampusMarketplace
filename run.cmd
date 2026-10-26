@echo off
setlocal

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -c "import sys; sys.exit(sys.version_info[:2] != (3, 12))" >nul 2>&1
    if not errorlevel 1 goto existing_environment
)
py -3.12 -c "import sys; sys.exit(sys.version_info[:2] != (3, 12))" >nul 2>&1
if not errorlevel 1 goto python_launcher
python -c "import sys; sys.exit(sys.version_info[:2] != (3, 12))" >nul 2>&1
if not errorlevel 1 goto python_command

echo Python 3.12 is required. Install it with: py install 3.12
echo Then reopen your terminal and run this command again.
exit /b 1

:existing_environment
"%~dp0.venv\Scripts\python.exe" "%~dp0run.py" %*
exit /b %errorlevel%

:python_launcher
py -3.12 "%~dp0run.py" %*
exit /b %errorlevel%

:python_command
python "%~dp0run.py" %*
exit /b %errorlevel%
