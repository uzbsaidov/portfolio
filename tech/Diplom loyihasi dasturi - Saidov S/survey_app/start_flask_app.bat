@echo off
cd /d "%~dp0"
set PY_CMD=py -3
where py >nul 2>&1 || set PY_CMD=python
start "Flask App" cmd /k "%PY_CMD% app.py"
