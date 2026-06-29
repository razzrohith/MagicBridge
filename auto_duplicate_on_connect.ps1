# MagicBridge — Auto-switch to Duplicate when second display connects
#
# Setup (run once as Admin in PowerShell):
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#   Then add this script to Task Scheduler:
#     - Trigger: On event — System log, Source: Display, Event ID 14 (monitor connected)
#     - Action: powershell.exe -WindowStyle Hidden -File "E:\Startup\magicbridge\auto_duplicate_on_connect.ps1"
#
# Or just double-click to switch NOW.

$monitors = Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorBasicDisplayParams
$count = ($monitors | Measure-Object).Count

Write-Host "Detected $count monitor(s)"

if ($count -ge 2) {
    Write-Host "Second display found — switching to Duplicate (Clone) mode"
    Start-Process "DisplaySwitch.exe" -ArgumentList "/clone" -NoNewWindow -Wait
    Write-Host "Done. Display is now cloned."
} else {
    Write-Host "Only one display detected — no action needed."
}
