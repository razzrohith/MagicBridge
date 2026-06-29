@echo off
:: MagicBridge — Switch display to Extend mode
:: Use this when you want the Pi to show a separate extended desktop instead of mirroring

echo Switching display to Extend mode...
DisplaySwitch.exe /extend
echo Done. Display is now extended — Pi capture card sees the second desktop.
timeout /t 2 /nobreak >nul
