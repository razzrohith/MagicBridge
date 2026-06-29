@echo off
:: MagicBridge — Force display to Duplicate (Clone) mode
:: Run this after connecting the Pi's HDMI capture card if Windows auto-extended
:: Can also be added to Startup folder for automatic behavior
::
:: To add to startup:
::   1. Press Win+R, type: shell:startup
::   2. Copy this .bat file into that folder
::   3. It will auto-run on every login
::
:: To switch back to Extend mode: Win+P -> Extend
:: Or run: set_extend.bat (see file in same folder)

echo Switching display to Duplicate (Clone) mode...
DisplaySwitch.exe /clone
echo Done. Display is now mirroring — Pi capture card sees same image as main screen.
timeout /t 2 /nobreak >nul
