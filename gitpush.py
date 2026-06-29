"""One-shot git commit + push for MagicBridge. Run from Windows Python."""
import os, subprocess, sys

REPO = r"E:\Startup\magicbridge"
LOCK = os.path.join(REPO, ".git", "index.lock")
LOG  = os.path.join(REPO, "git_push_log.txt")

# Redirect stdout/stderr to log file so output is visible even without a console
import io
_log = open(LOG, "w", encoding="utf-8")
sys.stdout = io.TextIOWrapper(_log.buffer, encoding="utf-8", write_through=True)
sys.stderr = sys.stdout
print("=== gitpush.py started ===")

# Step 1: remove stale lock
if os.path.exists(LOCK):
    try:
        os.unlink(LOCK)
        print("Removed stale index.lock")
    except Exception as e:
        print(f"WARNING: could not remove lock: {e}")

os.chdir(REPO)

def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    print("$", "git", *args)
    if r.stdout: print(r.stdout.rstrip())
    if r.stderr: print(r.stderr.rstrip())
    return r.returncode

# Step 2: unstage log file, stage everything else
git("restore", "--staged", "pi_fix_log.txt")
git("add", "auto_duplicate_on_connect.ps1", "autorun_fix.vbs", "run_fix.bat",
    "set_duplicate.bat", "set_extend.bat", "install.sh",
    "restore_pi.py", "src/core/video.py", ".gitignore", "push.bat", "gitpush.py")

# Step 3: commit
msg = (
    "fix: HID gadget working -- dtoverlay=dwc2 moved to [all] section\n\n"
    "- restore_pi.py: detect/fix dtoverlay in wrong config.txt section\n"
    "  Pi 4 Bookworm puts it in [cm5] by default; UDC never appears\n"
    "  sudobash()+awk avoids shell quoting bugs; fix SyntaxWarnings\n"
    "- install.sh: insert dtoverlay after [all] tag (Pi4+Pi5 compatible)\n"
    "- src/core/video.py: get_best_mjpeg_resolution() for auto resolution\n"
    "  detection; start() picks highest native MJPEG res automatically\n"
    "- set_duplicate.bat, set_extend.bat: Windows display mode switchers\n"
    "- auto_duplicate_on_connect.ps1: auto-clone on second monitor connect\n"
    "- run_fix.bat: one-click Pi fix runner with PYTHONIOENCODING fix\n\n"
    "Verified on Pi 4 Bookworm:\n"
    "  fe980000.usb in /sys/class/udc (UDC working)\n"
    "  /dev/hidg0 keyboard + /dev/hidg1 mouse both active\n"
    "  Logitech K120 USB identity VID=046d PID=c31c\n"
    "  ustreamer MJPEG stream HTTP 200\n"
    "  mb-gadget.service active and bound"
)
rc = git("commit", "-m", msg)

if rc == 0:
    # Step 4: push
    git("push", "origin", "main")
    print("\nDone!")
else:
    print("\nCommit failed — nothing to push or error above.")

_log.flush()
_log.close()
print("=== done ===")
