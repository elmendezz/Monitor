import os
import time
import random
import subprocess
import requests
import json
from datetime import datetime

# Configuración
TOKEN = "8272026718:AAF8Zrd4Usetik-gWYbFX4NkGWJs-pz4mZU"
CHAT_ID = "5481932023"
API_URL = f"https://api.telegram.org/bot{TOKEN}"
MSG_FILE = "messages_id.txt"

# -------------------
# FUNCIONES AUXILIARES
# -------------------

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except:
        return "N/A"

def get_time():
    return datetime.now().strftime("%I:%M:%S %p")  # 12h con AM/PM

def get_battery_info():
    level = run_cmd("dumpsys battery | grep level").replace('level: ', '')
    status = run_cmd("dumpsys battery | grep status").replace('status: ', '')
    current = run_cmd("cat /sys/class/power_supply/battery/current_now")  # en µA
    voltage = run_cmd("cat /sys/class/power_supply/battery/voltage_now")  # en µV
    temp = run_cmd("dumpsys battery | grep temperature").replace('temperature: ', '')
    try:
        current_mA = int(current) / 1000
    except:
        current_mA = 0
    try:
        voltage_V = int(voltage) / 1_000_000
    except:
        voltage_V = 0
    return f"*Batería:* {level}%\n*Estado:* {status}\n*Corriente:* {current_mA:.0f} mA\n*Tensión:* {voltage_V:.2f} V\n*Temp:* {temp}°C"

def get_network_info():
    ssid = run_cmd("dumpsys wifi | grep SSID | head -n 1").replace('SSID: ', '')
    bssid = run_cmd("dumpsys wifi | grep BSSID | head -n 1").replace('BSSID: ', '')
    rx = run_cmd("cat /sys/class/net/wlan0/statistics/rx_bytes")
    tx = run_cmd("cat /sys/class/net/wlan0/statistics/tx_bytes")
    try:
        rx_MB = int(rx) / 1024 / 1024
        tx_MB = int(tx) / 1024 / 1024
    except:
        rx_MB, tx_MB = 0, 0
    return f"*WiFi SSID:* {ssid}\n*BSSID:* {bssid}\n*Descargado:* {rx_MB:.2f} MB\n*Subido:* {tx_MB:.2f} MB"

def get_hotspot_info():
    tether = run_cmd("dumpsys connectivity | grep 'Tethering' -A 10")
    if "Wi-Fi" in tether:
        return "*Hotspot:* Encendido ✅"
    return "*Hotspot:* Apagado ❌"

def get_bt_info():
    state = run_cmd("dumpsys bluetooth_manager | grep 'enabled'")
    if "true" in state:
        return "*Bluetooth:* Encendido ✅"
    return "*Bluetooth:* Apagado ❌"

def get_processes():
    procs = run_cmd("top -n 1 -m 5 | tail -n 5")
    return f"*Top procesos:*\n```\n{procs}\n```"

# -------------------
# TELEGRAM
# -------------------

def send_message(text):
    r = requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }).json()
    if "result" in r:
        return r["result"]["message_id"]
    return None

def edit_message(msg_id, text):
    requests.post(f"{API_URL}/editMessageText", data={
        "chat_id": CHAT_ID,
        "message_id": msg_id,
        "text": text,
        "parse_mode": "Markdown"
    })

def delete_messages():
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE) as f:
            ids = f.read().splitlines()
        for mid in ids:
            try:
                requests.post(f"{API_URL}/deleteMessage", data={"chat_id": CHAT_ID, "message_id": mid})
            except:
                pass
        os.remove(MSG_FILE)

# -------------------
# MAIN LOOP
# -------------------

def main():
    delete_messages()
    msg_ids = {}

    # Crear mensajes iniciales
    msg_ids["battery"] = send_message("*Cargando info batería...*")
    msg_ids["network"] = send_message("*Cargando info red...*")
    msg_ids["hotspot"] = send_message("*Cargando info hotspot...*")
    msg_ids["bt"] = send_message("*Cargando info bluetooth...*")
    msg_ids["proc"] = send_message("*Cargando procesos...*")

    with open(MSG_FILE, "w") as f:
        for mid in msg_ids.values():
            f.write(str(mid) + "\n")

    try:
        while True:
            now = get_time()
            edit_message(msg_ids["battery"], f"🕒 {now}\n{get_battery_info()}")
            time.sleep(random.randint(0, 10))
            edit_message(msg_ids["network"], f"🕒 {now}\n{get_network_info()}")
            time.sleep(random.randint(0, 10))
            edit_message(msg_ids["hotspot"], f"🕒 {now}\n{get_hotspot_info()}")
            time.sleep(random.randint(0, 10))
            edit_message(msg_ids["bt"], f"🕒 {now}\n{get_bt_info()}")
            time.sleep(random.randint(0, 10))
            edit_message(msg_ids["proc"], f"🕒 {now}\n{get_processes()}")
            time.sleep(random.randint(0, 10))

    except KeyboardInterrupt:
        delete_messages()
        print("Bot detenido y mensajes eliminados.")

if __name__ == "__main__":
    main()
