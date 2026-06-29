@echo off
cd /d "E:\Startup\magicbridge"
git add -A
git commit -m "Fix ustreamer: use v4 flags (--resolution/--fps instead of --width/--desired-fps)"
git push origin main --force
echo.
if %ERRORLEVEL% EQU 0 (echo SUCCESS!) else (echo FAILED)
pause
