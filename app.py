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


# DB INIT
init_db()

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "username" not in st.session_state:
    st.session_state.username = None  # 🔥 EKLENDİ

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