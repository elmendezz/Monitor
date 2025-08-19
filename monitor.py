import os
import random
import asyncio
import subprocess
import requests

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
def get_battery_info():
    try:
        cap = subprocess.check_output("cat /sys/class/power_supply/battery/capacity", shell=True).decode().strip()
        stat = subprocess.check_output("cat /sys/class/power_supply/battery/status", shell=True).decode().strip()
        volt = subprocess.check_output("cat /sys/class/power_supply/battery/voltage_now", shell=True).decode().strip()
        curr = subprocess.check_output("cat /sys/class/power_supply/battery/current_now", shell=True).decode().strip()
        return f"🔋 <b>Batería</b>\n{cap}% | {stat}\nVoltaje: {int(volt)/1e6:.2f} V\nCorriente: {int(curr)/1000} mA"
    except:
        return "🔋 Info batería no disponible"

def get_network_info():
    try:
        ssid = subprocess.getoutput("dumpsys wifi | grep 'SSID'")
        bssid = subprocess.getoutput("dumpsys wifi | grep 'BSSID'")
        rx = subprocess.getoutput("cat /proc/net/dev | grep wlan0 | awk '{print $2}'")
        tx = subprocess.getoutput("cat /proc/net/dev | grep wlan0 | awk '{print $10}'")
        return f"📶 <b>Red</b>\n{ssid}\n{bssid}\nRX: {rx} bytes\nTX: {tx} bytes"
    except:
        return "📶 Info red no disponible"

def get_bluetooth_info():
    try:
        bt = subprocess.getoutput("dumpsys bluetooth_manager | grep 'state'")
        return f"🔵 <b>Bluetooth</b>\n{bt}"
    except:
        return "🔵 Info BT no disponible"

def get_running_apps():
    try:
        apps = subprocess.getoutput("ps -A | grep u0_a | awk '{print $9}' | head -n 10")
        return f"📱 <b>Apps en segundo plano</b>\n{apps}"
    except:
        return "📱 Apps no disponibles"

# ========= MAIN LOOP =========
async def main():
    # limpiar mensajes viejos
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, "r") as f:
            for line in f:
                try:
                    delete_message(int(line.strip()))
                except:
                    pass
        os.remove(MSG_FILE)

    messages = {}
    with open(MSG_FILE, "w") as f:
        for title, func in {
            "bateria": get_battery_info,
            "red": get_network_info,
            "bt": get_bluetooth_info,
            "apps": get_running_apps,
        }.items():
            msg_id = send_message(func())
            if msg_id:
                messages[title] = msg_id
                f.write(str(msg_id) + "\n")

    # actualización aleatoria
    while True:
        for key, func in {
            "bateria": get_battery_info,
            "red": get_network_info,
            "bt": get_bluetooth_info,
            "apps": get_running_apps,
        }.items():
            try:
                edit_message(messages[key], func())
            except:
                pass
            await asyncio.sleep(random.randint(*UPDATE_INTERVAL))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # limpiar mensajes al salir
        if os.path.exists(MSG_FILE):
            with open(MSG_FILE, "r") as f:
                for line in f:
                    try:
                        delete_message(int(line.strip()))
                    except:
                        pass
            os.remove(MSG_FILE)
