#!/usr/bin/env python3
"""
MagicBridge — Main KVM Server

aiohttp HTTP + WebSocket server on 127.0.0.1:8080
nginx proxies all external traffic here.

Routes:
  GET  /          → KVM web UI (index.html)
  GET  /ws        → WebSocket (keyboard/mouse input)
  GET  /api/status           → system status JSON
  GET  /api/devices          → list V4L2 capture devices
  GET  /api/stream/settings  → current stream settings
  POST /api/stream/settings  → update stream settings (quality, resolution, fps)
"""
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

from aiohttp import web, WSMsgType
import aiohttp

# ── Local modules (same directory) ────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hid   import HIDKeyboard, HIDMouse
from video import VideoManager

# ── Config ─────────────────────────────────────────────────────────────────────
CONFIG_PATH = "/etc/magicbridge/config.json"
WEB_ROOT    = "/opt/magicbridge/web"
HOST        = "127.0.0.1"
PORT        = 8080
VERSION     = "1.0.0"

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(name)-24s %(levelname)s  %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("magicbridge")

# ── Global HID + Video instances ──────────────────────────────────────────────
keyboard = HIDKeyboard("/dev/hidg0")
mouse    = HIDMouse("/dev/hidg1")
video    = VideoManager()

# ── Connected WebSocket clients (for count tracking) ──────────────────────────
_ws_clients: set = set()


# ══════════════════════════════════════════════════════════════════════════════
# WebSocket — keyboard / mouse input handler
# ══════════════════════════════════════════════════════════════════════════════

async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(request)

    ip = request.headers.get("X-Real-IP") or request.remote or "?"
    _ws_clients.add(ws)
    log.info("WS connect  from %s  (total: %d)", ip, len(_ws_clients))

    loop = asyncio.get_running_loop()

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    d = json.loads(msg.data)
                    t = d.get("type", "")

                    if t == "keydown":
                        keyboard.key_down(d.get("code", ""))

                    elif t == "keyup":
                        keyboard.key_up(d.get("code", ""))

                    elif t == "release_all":
                        keyboard.release_all()
                        mouse.release_all()

                    elif t == "combo":
                        codes = list(d.get("codes", []))
                        if codes:
                            loop.run_in_executor(None, lambda c=codes: keyboard.combo(c))

                    elif t == "mousemove":
                        dx = int(d.get("dx", 0))
                        dy = int(d.get("dy", 0))
                        if dx or dy:
                            mouse.move(dx, dy)

                    elif t == "mousedown":
                        mouse.button_down(int(d.get("button", 0)))

                    elif t == "mouseup":
                        mouse.button_up(int(d.get("button", 0)))

                    elif t == "wheel":
                        mouse.scroll(int(d.get("dy", 0)))

                    elif t == "paste":
                        text = str(d.get("text", ""))
                        if text:
                            loop.run_in_executor(None, lambda tx=text: keyboard.send_text(tx))

                except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                    pass

            elif msg.type == WSMsgType.ERROR:
                log.debug("WS error from %s: %s", ip, ws.exception())
                break

    finally:
        _ws_clients.discard(ws)
        keyboard.release_all()
        mouse.release_all()
        log.info("WS disconnect %s  (total: %d)", ip, len(_ws_clients))

    return ws


# ══════════════════════════════════════════════════════════════════════════════
# HTTP handlers
# ══════════════════════════════════════════════════════════════════════════════

async def index_handler(request: web.Request) -> web.Response:
    path = Path(WEB_ROOT) / "index.html"
    if path.exists():
        return web.FileResponse(path, headers={"Cache-Control": "no-cache"})
    return web.Response(
        text="<h2>MagicBridge</h2><p>index.html missing from " + WEB_ROOT + "</p>",
        content_type="text/html",
        status=500,
    )


async def api_status(request: web.Request) -> web.Response:
    """Overall system status."""
    def _gather():
        import subprocess
        uptime = ""
        try:
            s = int(float(Path("/proc/uptime").read_text().split()[0]))
            d, r = divmod(s, 86400); h, r = divmod(r, 3600); m = r // 60
            uptime = "".join([f"{d}d " if d else "", f"{h}h " if h else "", f"{m}m"])
        except Exception:
            pass
        temp = None
        try:
            temp = round(int(Path("/sys/class/thermal/thermal_zone0/temp").read_text()) / 1000, 1)
        except Exception:
            pass
        local_ip = ""
        try:
            local_ip = subprocess.run(["hostname", "-I"], capture_output=True,
                                       text=True).stdout.strip().split()[0]
        except Exception:
            pass
        return uptime, temp, local_ip

    loop = asyncio.get_running_loop()
    uptime, temp, local_ip = await loop.run_in_executor(None, _gather)

    return web.json_response({
        "version":    VERSION,
        "clients":    len(_ws_clients),
        "hid_kb":     os.path.exists("/dev/hidg0"),
        "hid_ms":     os.path.exists("/dev/hidg1"),
        "stream":     video.status(),
        "uptime":     uptime,
        "temp_c":     temp,
        "local_ip":   local_ip,
    })


async def api_devices(request: web.Request) -> web.Response:
    loop = asyncio.get_running_loop()
    devs = await loop.run_in_executor(None, video.detect_devices)
    return web.json_response(devs)


async def api_stream_settings(request: web.Request) -> web.Response:
    if request.method == "GET":
        loop = asyncio.get_running_loop()
        st = await loop.run_in_executor(None, video.status)
        return web.json_response(st)

    try:
        d = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "Invalid JSON"}, status=400)

    resolution = d.get("resolution")
    fps        = d.get("fps")
    quality    = d.get("quality")
    device     = d.get("device")
    mode       = d.get("mode")

    loop = asyncio.get_running_loop()
    ok = await loop.run_in_executor(None, lambda: video.start(
        device=device, resolution=resolution,
        fps=fps, quality=quality, mode=mode,
    ))

    # Persist settings to config.json
    if ok:
        try:
            cfg = json.loads(Path(CONFIG_PATH).read_text()) if Path(CONFIG_PATH).exists() else {}
            cfg.setdefault("video", {}).update({
                k: v for k, v in {
                    "device": device, "resolution": resolution,
                    "fps": fps, "quality": quality, "mode": mode,
                }.items() if v is not None
            })
            Path(CONFIG_PATH).write_text(json.dumps(cfg, indent=2))
        except Exception:
            pass

    return web.json_response({"ok": ok, "status": video.status()})


# ══════════════════════════════════════════════════════════════════════════════
# App factory
# ══════════════════════════════════════════════════════════════════════════════

def build_app() -> web.Application:
    app = web.Application(client_max_size=1024 * 1024)

    app.router.add_get("/",                      index_handler)
    app.router.add_get("/ws",                    ws_handler)
    app.router.add_get("/api/status",            api_status)
    app.router.add_get("/api/devices",           api_devices)
    app.router.add_get("/api/stream/settings",   api_stream_settings)
    app.router.add_post("/api/stream/settings",  api_stream_settings)

    # Serve static files if present (CSS, JS, images, etc.)
    web_static = Path(WEB_ROOT) / "static"
    if web_static.exists():
        app.router.add_static("/static", str(web_static), show_index=False)

    return app


# ══════════════════════════════════════════════════════════════════════════════
# Main entry point
# ══════════════════════════════════════════════════════════════════════════════

async def main():
    log.info("MagicBridge v%s starting…", VERSION)

    # ── Load config ───────────────────────────────────────────────────────────
    cfg = {}
    try:
        cfg = json.loads(Path(CONFIG_PATH).read_text())
        log.info("Config loaded from %s", CONFIG_PATH)
    except FileNotFoundError:
        log.info("No config at %s — using defaults", CONFIG_PATH)
    except Exception as e:
        log.warning("Config load error: %s — using defaults", e)

    # ── Start video stream ────────────────────────────────────────────────────
    vc  = cfg.get("video", {})
    loop = asyncio.get_running_loop()
    log.info("Starting video stream…")
    ok = await loop.run_in_executor(None, lambda: video.start(
        device     = vc.get("device"),
        resolution = vc.get("resolution", "1920x1080"),
        fps        = int(vc.get("fps", 30)),
        quality    = int(vc.get("quality", 80)),
        mode       = vc.get("mode", "mjpeg"),
    ))
    if ok:
        log.info("Stream started: %s", video.status())
        video.start_watchdog()
    else:
        log.warning("Stream not started — no capture device or streamer found")

    # ── Start HTTP server ──────────────────────────────────────────────────────
    app    = build_app()
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT, reuse_address=True)
    await site.start()
    log.info("HTTP+WS listening on %s:%d", HOST, PORT)

    # ── Run until killed ───────────────────────────────────────────────────────
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        log.info("Shutting down…")
        keyboard.release_all()
        mouse.release_all()
        video.stop()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
