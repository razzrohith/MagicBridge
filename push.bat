@echo off
cd /d "E:\Startup\magicbridge"
git add -A
git commit -m "Fix installer: install git first, use network-manager (lowercase) for Lite"
git push origin main --force
echo.
if %ERRORLEVEL% EQU 0 (echo SUCCESS!) else (echo FAILED)
pause
