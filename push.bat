@echo off
cd /d "E:\Startup\magicbridge"
git add -A
git commit -m "Fix firewall: add iptables to apt packages (not installed on Pi OS Lite)"
git push origin main --force
echo.
if %ERRORLEVEL% EQU 0 (echo SUCCESS!) else (echo FAILED)
pause
