import telebot
import os
import platform
import socket
import time
import threading
import psutil
import subprocess
import webbrowser


from telebot.types import BotCommand


API_TOKEN = "8656070565:AAEOg6jx6ZIVe5LsinV1As_LWc6jMLBuzDU"
CHAT_ID = "7621297112"

bot = telebot.TeleBot(API_TOKEN)

bot.set_my_commands([
    BotCommand("durum", "Sistem durumunu göster"),
    BotCommand("temizle", "Bilgisayarı temizle"),
    BotCommand("edge", "Edge aç"),
    BotCommand("chrome", "Chrome aç"),
    BotCommand("linkedin", "LinkedIn aç"),
    BotCommand("whatsapp", "WhatsApp Web aç"),
    BotCommand("youtube", "YouTube aç"),
    BotCommand("gmail", "Gmail aç"),
    BotCommand("github", "GitHub aç"),
])

# =========================
# SYSTEM INFO
# =========================
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "IP alınamadı"

def system_report():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    return f"""
VERA RAPOR
PC: {platform.node()}
IP: {get_ip()}

CPU: %{cpu}
RAM: %{ram}
DISK: %{disk}
"""

# =========================
# PERİYODİK RAPOR
# =========================
def periodic_report():
    while True:
        try:
            bot.send_message(CHAT_ID, system_report())
        except:
            pass
        time.sleep(600)  # 10 dk

threading.Thread(target=periodic_report, daemon=True).start()

# =========================
# GÜVENLİK KONTROL
# =========================
def is_authorized(message):
    return str(message.chat.id) == CHAT_ID

# =========================
# TEMİZLE KOMUTU
# =========================
@bot.message_handler(commands=['temizle'])
def clean_pc(message):
    if not is_authorized(message):
        return

    bot.reply_to(message, "Derin temizlik başlatılıyor...")

    # temp temizleme
    os.system("del /q/f/s %TEMP%\\*")
    os.system("del /q/f/s C:\\Windows\\Temp\\*")

    # disk cleanup
    os.system("cleanmgr /sagerun:1")

    bot.send_message(CHAT_ID, "Temizlik tamamlandı")

# =========================
# UYGULAMA AÇMA
# =========================

def open_app(name):
    
    apps = {
        "edge": "start msedge",
        "chrome": "start chrome",
        "notepad": "notepad",
        "calc": "calc",
        "cmd": "start cmd",
        "powershell": "start powershell",
    }

    sites = {
        "linkedin": "https://www.linkedin.com",
        "whatsapp": "https://web.whatsapp.com",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
    }

    if name in apps:
        # subprocess.Popen ile arka planda hızlıca çalıştır
        subprocess.Popen(apps[name], shell=True)
        return f"{name} tetiklendi."
    elif name in sites:
        webbrowser.open(sites[name])
        return f"{name} tarayıcıda açıldı."
    else:
        return "Uygulama bulunamadı."


@bot.message_handler(func=lambda message: message.text.startswith('/'))
def open_command(message):
    if not is_authorized(message):
        return

    cmd = message.text.lower().replace("/", "").replace("ı", "i")
    result = open_app(cmd)

    bot.send_message(CHAT_ID, result)

# =========================
# BAŞLANGIÇ MESAJI
# =========================
try:
    bot.send_message(CHAT_ID, f"VERA AKTİF\n{system_report()}")
except:
    pass

# =========================
# BOT ÇALIŞTIR
# =========================
bot.infinity_polling(non_stop=True, interval=1)