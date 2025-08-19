import os
import random
import asyncio
import subprocess
import requests
import time
from datetime import datetime

# ========= CONFIG =========
BOT_TOKEN = "8272026718:AAF8Zrd4Usetik-gWYbFX4NkGWJs-pz4mZU"
CHAT_ID = 5481932023
MSG_FILE = "messages_id.txt"
UPDATE_INTERVAL = (30, 60)  # segundos (min, max)

# ========= TELEGRAM =========
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(text):
    try:
        resp = requests.post(f"{BASE_URL}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }).json()
        if resp.get("ok"):
            return resp["result"]["message_id"]
    except:
        pass
    return None

def edit_message(msg_id, text):
    try:
        requests.post(f"{BASE_URL}/editMessageText", data={
            "chat_id": CHAT_ID,
            "message_id": msg_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })
    except:
        pass

def delete_message(msg_id):
    try:
        requests.post(f"{BASE_URL}/deleteMessage", data={
            "chat_id": CHAT_ID,
            "message_id": msg_id
        })
    except:
        pass

# ========= INFO FUNCTIONS =========
def get_device_info():
    try:
        model = subprocess.getoutput("getprop ro.product.model")
        android = subprocess.getoutput("getprop ro.build.version.release")
        codename = subprocess.getoutput("getprop ro.product.device")
        return f"📱 <b>Dispositivo:</b> {model}\n🤖 <b>Android:</b> {android} ({codename})"
    except:
        return "📱 Info dispositivo no disponible"

def get_battery_info():
    try:
        cap = subprocess.check_output("cat /sys/class/power_supply/battery/capacity", shell=True).decode().strip()
        stat = subprocess.check_output("cat /sys/class/power_supply/battery/status", shell=True).decode().strip()
        curr = subprocess.check_output("cat /sys/class/power_supply/battery/current_now", shell=True).decode().strip()
        curr_ma = int(curr) / 1000
        return f"🔋 <b>Batería:</b> {cap}% ({stat}, {curr_ma:+.0f} mA)"
    except:
        return "🔋 Info batería no disponible"

def get_network_info():
    try:
        ssid = subprocess.getoutput("dumpsys wifi | grep 'SSID'")
        bssid = subprocess.getoutput("dumpsys wifi | grep 'BSSID'")
        return f"🌐 <b>WiFi:</b> {ssid}, {bssid}"
    except:
        return "🌐 Info red no disponible"

def get_bluetooth_info():
    try:
        bt_state = subprocess.getoutput("dumpsys bluetooth_manager | grep 'state'")
        if "ON" in bt_state:
            return "🔵 <b>Bluetooth:</b> Activado"
        else:
            return "🔵 <b>Bluetooth:</b> Desactivado"
    except:
        return "🔵 Info BT no disponible"

def get_screen_info():
    try:
        brillo = subprocess.getoutput("settings get system screen_brightness")
        brillo_pct = int(brillo) * 100 // 255
        screen = subprocess.getoutput("dumpsys power | grep 'Display Power'")
        estado = "Encendida" if "ON" in screen else "Apagada"
        return f"💡 <b>Brillo:</b> {brillo_pct}%\n🖥 <b>Pantalla:</b> {estado}"
    except:
        return "💡 Pantalla/brillo no disponible"

def get_foreground_app():
    try:
        app = subprocess.getoutput("dumpsys window | grep mCurrentFocus")
        return f"📲 <b>App en primer plano:</b> {app}"
    except:
        return "📲 App no disponible"

def get_uptime():
    try:
        with open("/proc/uptime") as f:
            seconds = float(f.readline().split()[0])
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
