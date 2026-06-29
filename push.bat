@echo off
cd /d "E:\Startup\magicbridge"

:: Remove stale git lock if present
if exist .git\index.lock del /f .git\index.lock

:: Unstage log file, stage everything else
git restore --staged pi_fix_log.txt 2>nul
git add auto_duplicate_on_connect.ps