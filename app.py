import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from auth.login import login_page
from db.database import init_db
from modules.system_info import render_system_info
from modules.maintenance import render_maintenance
from modules.dashboard import render_dashboard
from modules.security import render_security
from modules.support import render_support
import threading
import telebot
import time


API_TOKEN = "8656070565:AAFgfOct8LXuFM1uAY-Z3eCQwck-2tbTpow"
CHAT_ID = "7621297112"

bot = telebot.TeleBot(API_TOKEN)

# =========================
# TELEGRAM BOT FONKSİYONU
# =========================
def start_telegram_bot():

    bot.send_message(CHAT_ID, "Sistem Uygulamanız Aktif Edilmiştir. İyi kullanımlar dileriz.")

    @bot.message_handler(commands=['durum'])
    def durum(message):
        if str(message.chat.id) != CHAT_ID:
            return
        bot.send_message(CHAT_ID, "Sistem aktif")

    @bot.message_handler(commands=['temizle'])
    def temizle(message):
        if str(message.chat.id) != CHAT_ID:
            return
        bot.send_message(CHAT_ID, "Temizlik başlatıldı")
        # buraya senin clean kodun

    # Bot başlat
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print("Bot hata verdi, yeniden başlatılıyor:", e)
            time.sleep(5)

# =========================
# SADECE 1 KEZ BAŞLAT
# =========================
if "bot_started" not in st.session_state:
    thread = threading.Thread(target=start_telegram_bot, daemon=True)
    thread.start()
    st.session_state.bot_started = True

# DB INIT
init_db()

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "username" not in st.session_state:
    st.session_state.username = None  



# ---------------- FLOW ----------------
if not st.session_state.logged_in:
    login_page()

else:
    st.sidebar.title("VERA Panel")

    role = st.session_state.user_role
    username = st.session_state.username  # 🔥 EKLENDİ

    # kullanıcı bilgisi göster
    st.sidebar.write(f"{username}")
    st.sidebar.write(f"Rol: {role}")

    # ---------------- MENU ----------------
    if role == "admin":
        menu = [
            "Dashboard",
            "Güvenlik",
            "Sistem Bilgisi",
            "Hızlı Bakım Merkezi",
            "Destek Talepleri"
        ]
    else:
        menu = [
            "Dashboard",
            "Sistem Bilgisi",
            "Hızlı Bakım Merkezi",
            "Destek Talebi Oluştur"
        ]

    choice = st.sidebar.selectbox("Menu", menu)

    # ---------------- ROUTING ----------------
    if choice == "Dashboard":
        render_dashboard()

    elif choice == "Güvenlik":
        render_security()

    elif choice in ["Destek Talepleri", "Destek Talebi Oluştur"]:
        # 🔥 kritik: role + username gönderiyoruz
        render_support(role=role, username=username)

    elif choice == "Sistem Bilgisi":
        render_system_info()

    elif choice == "Hızlı Bakım Merkezi":
        render_maintenance()

    # ---------------- LOGOUT ----------------
    st.sidebar.markdown("---")
    if st.sidebar.button("Çıkış"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None  # 🔥 EKLENDİ
        st.rerun()