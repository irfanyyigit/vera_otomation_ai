import telebot
import os
import platform
import socket
import time

API_TOKEN = "8656070565:AAHQxJ9Ye_ru6NZ4zo2RQmJtfXG54tYBE1w"
CHAT_ID = "7621297112"

bot = telebot.TeleBot(API_TOKEN)


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "IP alınamadı"


def get_system_info():
    return f"""
Sistem Açıldı!
Cihaz: {platform.node()}
IP: {get_ip()}
OS: {platform.system()} {platform.release()}
"""


# Başlangıç mesajı (internet hazır olana kadar retry)
def send_startup_message():
    for _ in range(5):  # 5 kez dene
        try:
            bot.send_message(CHAT_ID, get_system_info())
            return
        except Exception as e:
            time.sleep(3)


send_startup_message()


# Güvenli kapatma komutu
@bot.message_handler(commands=['kapat'])
def shutdown(message):
    if str(message.chat.id) == CHAT_ID:
        bot.reply_to(message, "Bilgisayar 10 saniye içinde kapanıyor...")
        os.system("shutdown /s /t 10")
    else:
        bot.reply_to(message, "Yetkin yok!")


# Botu başlat
bot.infinity_polling()