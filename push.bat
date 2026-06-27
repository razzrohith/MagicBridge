@echo off
echo ============================================
echo  MagicBridge — Push to GitHub
echo ============================================
echo.
cd /d "E:\Startup\magicbridge"

echo Removing stale git state...
if exist ".git" rmdir /s /q .git

echo Initializing fresh repo...
git init
git branch -M main
git config user.email "razzrohith@gmail.com"
git config user.name "razzrohith"

echo Staging all files...
git add -A

echo Committing...
git commit -m "Initial commit — MagicBridge KVM-over-IP"

echo Adding remote...
git remote add origin https://github.com/razzrohith/MagicBridge.git

echo.
echo ============================================
echo  Pushing to GitHub...
echo  (You may be prompted to sign into GitHub)
echo ============================================
git push -u origin main --force

echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! All files pushed to GitHub.
) else (
    echo FAILED. Check the error above.
)
pause
