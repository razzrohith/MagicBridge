@echo off
echo === MagicBridge: Restoring video.py to Pi ===
echo.
echo Step 1: Uploading video.py  (type 'lol' at password prompt)
scp -o StrictHostKeyChecking=no "E:\Startup\magicbridge\src\core\video.py" admin@172.16.20.197:/tmp/video_restore.py
if %ERRORLEVEL% NEQ 0 (echo UPLOAD FAILED & pause & exit /b 1)
echo Upload OK.
echo.
echo Step 2: Installing + restarting  (type 'lol' at password prompt)
ssh -o StrictHostKeyChecking=no admin@172.16.20.197 "echo lol | sudo -S cp /tmp/video_restore.py /opt/magicbridge/core/video.py && echo lol | sudo -S systemctl restart magicbridge && sleep 5 && curl -s -o /dev/null -w 'Stream HTTP %%{http_code}\n' http://127.0.0.1:8081/ && echo lol | sudo -S journalctl -u magicbridge -n 8 --no-pager"
echo.
echo === Done ===
pause
