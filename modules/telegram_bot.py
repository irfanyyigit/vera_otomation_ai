import telebot
import os
import platform
import socket

# Telegram Bilgilerin
API_TOKEN = '8656070565:AAHQxJ9Ye_ru6NZ4zo2RQmJtfXG54tYBE1w'
CHAT_ID = '7621297112'  # Senin Telegram ID'n

bot = telebot.TeleBot(API_TOKEN)

def get_system_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return f"Sistem Açıldı!\nCihaz: {hostname}\nIP: {ip_address}\nİşletim Sistemi: {platform.system()}"

# /kapat Komutu Gelince
@bot.message_handler(commands=['kapat'])
def shutdown(message):
    if str(message.chat.id) == CHAT_ID: # Sadece senden gelen komutu dinle
        bot.reply_to(message, "Bilgisayar 10 saniye içinde kapatılıyor...")
        # Windows için kapatma komutu
        os.system("shutdown /s /t 10")
    else:
        bot.reply_to(message, "Bu komutu kullanma yetkiniz yok!")

# Başlangıç Bildirimi Gönder
try:
    bot.send_message(CHAT_ID, get_system_info())
except Exception as e:
    print(f"Hata: {e}")

# Botu Dinlemeye Başla
bot.infinity_polling()