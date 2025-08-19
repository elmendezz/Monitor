import os
import time
import random
import json
import psutil
import subprocess
import requests
from datetime import datetime

# ==== CONFIGURACIÓN ====
TOKEN = "8272026718:AAF8Zrd4Usetik-gWYbFX4NkGWJs-pz4mZU"
CHAT_ID = "5481932023"
MESSAGE_FILE = "messages_id.txt"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# ==== FUNCIONES ====
def load_messages():
    if os.path.exists(MESSAGE_FILE):
        with open(MESSAGE_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_messages(data):
    with open(MESSAGE_FILE, "w") as f:
        json.dump(data, f)

def delete_messages():
    ids = load_messages()
    for key, msg_id in ids.items():
        try:
            requests.post(f"{API_URL}/deleteMessage", data={"chat_id": CHAT_ID, "message_id": msg_id})
        except:
            pass
    if os.path.exists(MESSAGE_FILE):
        os.remove(MESSAGE_FILE)

def send_message(text):
    r = requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "MarkdownV2"
    }).json()
    return r.get("result", {}).get("message_id")

def edit_message(msg_id, text):
    requests.post(f"{API_URL}/editMessageText", data={
        "chat_id": CHAT_ID,
        "message_id": msg_id,
        "text": text,
        "parse_mode": "MarkdownV2"
    })

def escape_md(text):
    return str(text).replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

def get_time():
    return datetime.now().strftime("%I:%M:%S %p")

def get_battery():
    try:
        out = subprocess.check_output(["dumpsys", "battery"]).decode()
        data = {}
        for line in out.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
        return data
    except:
        return {}

def get_wifi():
    try:
        out = subprocess.check_output(["dumpsys", "wifi"]).decode()
        bssid = "?"
        ssid = "?"
        for line in out.splitlines():
            if "BSSID" in line:
                bssid = line.split(":", 1)[1].strip()
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":", 1)[1].strip()
        return ssid, bssid
    except:
        return "?", "?"

def get_net_speed():
    net1 = psutil.net_io_counters()
    time.sleep(1)
    net2 = psutil.net_io_counters()
    down = (net2.bytes_recv - net1.bytes_recv) / 1024
    up = (net2.bytes_sent - net1.bytes_sent) / 1024
    return f"{down:.1f} KB/s ↓ | {up:.1f} KB/s ↑"

def get_processes():
    try:
        out = subprocess.check_output(["ps"]).decode().splitlines()
        return len(out) - 1
    except:
        return 0

# ==== MAIN ====
if __name__ == "__main__":
    try:
        delete_messages()
        msgs = {}

        # Enviar mensajes iniciales
        msgs["info"] = send_message("*📊 Estado del Galaxy S3*")
        msgs["net"] = send_message("_Conectando información de red..._")
        msgs["bat"] = send_message("_Leyendo batería..._")
        msgs["apps"] = send_message("_Cargando procesos..._")

        save_messages(msgs)

        while True:
            now = get_time()
            ssid, bssid = get_wifi()
            net = escape_md(get_net_speed())
            bat = get_battery()
            procs = get_processes()

            text_info = f"*📱 Galaxy S3 Monitor*\n⏰ Hora: `{now}`"
            text_net = f"*🌐 Red*\nSSID: `{escape_md(ssid)}`\nBSSID: `{escape_md(bssid)}`\nVelocidad: `{net}`"
            text_bat = f"*🔋 Batería*\nNivel: `{bat.get('level', '?')}%`\nVoltaje: `{bat.get('voltage', '?')}` mV\nTemp: `{bat.get('temperature', '?')}`"
            text_apps = f"*⚙️ Procesos*\nApps en segundo plano: `{procs}`"

            edit_message(msgs["info"], text_info)
            edit_message(msgs["net"], text_net)
            edit_message(msgs["bat"], text_bat)
            edit_message(msgs["apps"], text_apps)

            time.sleep(random.randint(30, 60))

    except KeyboardInterrupt:
        delete_messages()
        print("Bot detenido y mensajes eliminados.")
