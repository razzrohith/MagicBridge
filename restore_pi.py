"""Restore video.py to the Pi and restart magicbridge — no manual password needed."""
import subprocess
import sys
import os

# Install paramiko if missing
try:
    import paramiko
except ImportError:
    print("Installing paramiko...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko", "-q"])
    import paramiko

HOST = "172.16.20.197"
USER = "admin"
PASS = "lol"
LOCAL = os.path.join(os.path.dirname(__file__), "src", "core", "video.py")
REMOTE_TMP = "/tmp/video_restore.py"
REMOTE_DEST = "/opt/magicbridge/core/video.py"

print(f"Connecting to {HOST}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)
print("Connected.")

print("Uploading video.py...")
sftp = ssh.open_sftp()
sftp.put(LOCAL, REMOTE_TMP)
sftp.close()
print("Upload OK.")

cmds = [
    f"echo {PASS} | sudo -S cp {REMOTE_TMP} {REMOTE_DEST}",
    f"echo {PASS} | sudo -S systemctl restart magicbridge",
    "sleep 5",
    "curl -s -o /dev/null -w 'Stream HTTP %{http_code}\\n' http://127.0.0.1:8081/",
    f"echo {PASS} | sudo -S journalctl -u magicbridge -n 8 --no-pager",
]

for cmd in cmds:
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)

ssh.close()
print("\n=== Done ===")
input("Press Enter to close...")
