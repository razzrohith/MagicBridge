@echo off
cd /d "E:\Startup\magicbridge"
git add -A
git commit -m "Fix video: prefer USB capture card over Pi internal bcm2835 devices"
git push origin main --force
echo.
if %ERRORLEVEL% EQU 0 (echo SUCCESS!) else (echo FAILED)
pause
