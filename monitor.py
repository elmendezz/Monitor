#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import asyncio
import subprocess
import requests
from datetime import datetime

# ========= CONFIG =========
BOT_TOKEN = "8272026718:AAF8Zrd4Usetik-gWYbFX4NkGWJs-pz4mZU"
CHAT_ID = 5481932023
MSG_FILE = "messages id.txt"   # nombre exacto con espacio
UPDATE_INTERVAL = (30, 60)     # segundos (min, max)

# ========= TELEGRAM =========
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def tg_send(text: str):
    try:
        r = requests.post(f"{BASE_URL}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }).json()
        return r["result"]["message_id"] if r.get("ok") else None
    except Exception:
        return None

def tg_edit(msg_id: int, text: str):
    try:
        requests.post(f"{BASE_URL}/editMessageText", data={
            "chat_id": CHAT_ID,
            "message_id": msg_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })
    except Exception:
        pass

def tg_delete(msg_id: int):
    try:
        requests.post(f"{BASE_URL}/deleteMessage", data={
            "chat_id": CHAT_ID,
            "message_id": msg_id
        })
    except Exception:
        pass

# ========= HELPERS =========
def sh(cmd: str) -> str:
    return subprocess.getoutput(cmd).strip()

def read_int(path: str, divisor: int = 1, default: int = 0) -> int:
    try:
        with open(path, "r") as f:
            v = int(f.read().strip())
            return v // divisor if divisor != 1 else v
    except Exception:
        return default

# ========= INFO FUNCTIONS =========
def get_device_info() -> str:
    model = sh("getprop ro.product.model")
    android = sh("getprop ro.build.version.release")
    codename = sh("getprop ro.product.device")
    return f"📱 <b>Dispositivo:</b> {model}\n🤖 <b>Android:</b> {android} ({codename})"

def get_battery_info() -> str:
    cap = sh("cat /sys/class/power_supply/battery/capacity")
    stat = sh("cat /sys/class/power_supply/battery/status")
    # voltage_now en µV → V (1e6). current_now en µA → mA (÷1000)
    volt_uV = read_int("/sys/class/power_supply/battery/voltage_now", 1, 0)
    curr_uA = read_int("/sys/class/power_supply/battery/current_now", 1, 0)
    volt_V = volt_uV / 1_000_000 if volt_uV else 0.0
    curr_mA = curr_uA / 1000 if curr_uA else 0
    # En muchos Samsung, corriente negativa = descargando
    signo = "−" if curr_mA < 0 else "+"
    return (
        f"🔋 <b>Batería:</b> {cap}% ({stat}, {signo}{abs(int(curr_mA))} mA)\n"
        f"🔌 <b>Voltaje:</b> {volt_V:.2f} V"
    )

def get_network_info() -> str:
    # Tomamos SSID y BSSID del dumpsys wifi
    ssid = sh(r"dumpsys wifi | grep -m1 -E 'SSID|mSSID'")
    bssid = sh(r"dumpsys wifi | grep -m1 -E 'BSSID|mBSSID'")
    if not ssid and not bssid:
        return "🌐 <b>WiFi:</b> No conectado"
    return f"🌐 <b>WiFi SSID:</b> {ssid}\n🛰 <b>BSSID:</b> {bssid}"

def get_bluetooth_info() -> str:
    state = sh("dumpsys bluetooth_manager | grep -i 'state' | head -n1")
    on = "ON" in state.upper() or "ENABLED" in state.upper()
    return f"🔵 <b>Bluetooth:</b> {'Activado' if on else 'Desactivado'}"

def get_screen_info() -> str:
    # Brillo 0-255 → %
    bri = sh("settings get system screen_brightness")
    try:
        bri_pct = int(bri) * 100 // 255
    except Exception:
        bri_pct = 0
    # Estado de pantalla
    power = sh("dumpsys power | grep -m1 -E 'Display Power|mHoldingDisplay'")
    on = ("ON" in power) or ("true" in power.lower())
    return f"💡 <b>Brillo:</b> {bri_pct}%\n🖥 <b>Pantalla:</b> {'Encendida' if on else 'Apagada'}"

def get_foreground_app() -> str:
    line = sh(r"dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp' | tail -n1")
    return f"📲 <b>App en primer plano:</b> {line if line else 'N/D'}"

def get_uptime() -> str:
    try:
        with open("/proc/uptime", "r") as f:
            seconds = float(f.readline().split()[0])
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d:
            return f"⏳ <b>Uptime:</b> {d}d {h}h {m}m {s}s"
        return f"⏳ <b>Uptime:</b> {h}h {m}m {s}s"
    except Exception:
        return "⏳ <b>Uptime:</b> N/D"

def now_time() -> str:
    return f"🕒 <b>Hora actual:</b> {datetime.now().strftime('%H:%M:%S')}"

# ========= PANEL =========
def build_panel() -> str:
    parts = [
        "🟢 <b>Estado del Dispositivo</b> 🟢",
        get_device_info(),
        get_battery_info(),
        get_network_info(),
        get_bluetooth_info(),
        get_screen_info(),
        get_foreground_app(),
        now_time(),
        get_uptime(),
    ]
    return "\n\n".join(parts)

# ========= CLEANUP =========
def cleanup():
    if os.path.exists(MSG_FILE):
        try:
            with open(MSG_FILE, "r") as f:
                ids = [x.strip() for x in f if x.strip().isdigit()]
            for mid in ids:
                tg_delete(int(mid))
        except Exception:
            pass
        try:
            os.remove(MSG_FILE)
        except Exception:
            pass

# ========= MAIN =========
async def main():
    # borrar restos previos
    cleanup()

    # mandar panel inicial y guardar id
    msg_id = tg_send(build_panel())
    if msg_id is None:
        return
    try:
        with open(MSG_FILE, "w") as f:
            f.write(str(msg_id) + "\n")
    except Exception:
        pass

    # loop de actualización aleatoria
    while True:
        tg_edit(msg_id, build_panel())
        await asyncio.sleep(random.randint(*UPDATE_INTERVAL))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
