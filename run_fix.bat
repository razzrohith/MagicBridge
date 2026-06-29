@echo off
set PYTHONIOENCODING=utf-8:replace
cd /d "E:\Startup\magicbridge"
python restore_pi.py > pi_fix_log.txt 2>&1
echo Done. Check pi_fix_log.txt
