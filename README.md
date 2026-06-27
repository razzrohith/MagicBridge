# MagicBridge

Self-hosted KVM-over-IP for Raspberry Pi 4. Control any computer remotely via browser — keyboard, mouse, and video. Zero dependency on TinyPilot or any external service.

---

## Install

Flash Pi OS Bookworm (64-bit) on a Pi 4, then SSH in and run:

```bash
curl -fsSL https://raw.githubusercontent.com/razzrohith/MagicBridge/main/install.sh | sudo bash
sudo reboot
```

After reboot, plug the Pi's **USB-C port** into the target computer's USB port.

---

## Access

| | |
|---|---|
| KVM (remote control) | `https://raj.local/` |
| Admin panel | `https://raj.local/stealth/` |
| SSH | `ssh raj@raj.local` · password `lol` |
| Panel password | `lol` (change in panel → System) |

> Browser will warn about the self-signed certificate — click "Advanced → Proceed".

---

## Features

- **Video** — MJPEG stream via ustreamer; supports all UVC capture cards (MS2109, Elgato Cam Link, UGREEN, etc.)
- **Keyboard + mouse** — full HID gadget; Pi appears as a real USB keyboard + mouse
- **USB identity spoofing** — change manufacturer, product name, VID/PID, serial number
- **WiFi provisioning** — on first boot, Pi broadcasts `MagicBridge-Setup` AP with a captive portal to enter WiFi credentials
- **Stealth admin panel** — bcrypt-protected dashboard at `/stealth/` for USB, MAC, WiFi, Tailscale, DuckDNS, logs, backup
- **Tailscale + Funnel** — encrypted remote access from anywhere
- **DuckDNS** — free public hostname, updated every 5 min
- **MAC spoofing** — change and persist ethernet/WiFi MAC via systemd
- **Firewall** — default-deny iptables; ports 7777/8080/8081 blocked externally

---

## Capture card compatibility

Any UVC-compliant V4L2 device works out of the box, including:
- Generic MS2109 HDMI capture (common $10–20 USB dongle)
- Elgato Cam Link 4K
- UGREEN HDMI USB capture card

---

## First-time WiFi setup (no ethernet)

1. Power on Pi — it broadcasts an open WiFi network: **`MagicBridge-Setup`**
2. Connect your phone/laptop to it
3. Browser opens automatically (or go to `http://192.168.73.1/`)
4. Enter your WiFi credentials → Pi connects and the AP disappears
5. Access at `https://raj.local/`

---

## Terms & Conditions

**Personal use only.** MagicBridge is provided as-is for personal, non-commercial, educational, and homelab use.

- You are solely responsible for the security of your deployment
- Do not use this to access computers you do not own or have explicit permission to control
- Do not expose the admin panel (`/stealth/`) publicly without strong password protection
- The default password (`lol`) must be changed before exposing to any network you don't fully control
- The authors accept no liability for misuse, data loss, hardware damage, or unauthorized access resulting from use of this software

By installing and running MagicBridge, you agree to these terms.

---

## License

MIT — free to use, modify, and distribute with attribution.
