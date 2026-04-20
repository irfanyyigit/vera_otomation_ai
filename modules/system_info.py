import streamlit as st
import psutil
import platform
import socket
import pandas as pd
import time
import platform

def render_system_info():
    st.title("Sistem Bilgisi")

    # ---- TEMEL BİLGİLER ----
    st.subheader("Cihaz Kimliği")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Bilgisayar Adı**")
        st.success(platform.node())

    with col2:
        st.write("**İşletim Sistemi**")
        st.success(f"{platform.system()} {platform.release()}")

    with col3:
        st.write("**İşlemci**")
        st.success(platform.processor())

    st.divider()

    # ---- DETAY BİLGİ ----
    boot_time = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(psutil.boot_time()))

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "Bulunamadı"

    col4, col5, col6 = st.columns(3)

    col4.metric("Açılış Zamanı", boot_time)
    col5.metric("CPU Çekirdek", f"{psutil.cpu_count()} adet")
    col6.metric("IP Adresi", ip)

    st.divider()

    # ---- RAM & DİSK ----
    st.subheader("Bellek & Depolama")

    mem = psutil.virtual_memory()
    if platform.system() == "Windows":
        disk = psutil.disk_usage('C:\\')
    else:
        disk = psutil.disk_usage('/')

    c1, c2, c3 = st.columns(3)

    c1.metric("Toplam RAM", f"{mem.total // (1024**3)} GB")
    c2.metric("Kullanılan RAM", f"%{mem.percent}")
    c3.metric("Disk Kullanımı", f"%{disk.percent}")

    st.divider()

    # ---- AĞ ARAYÜZLERİ ----
    st.subheader("Ağ Arayüzleri")

    net = psutil.net_if_addrs()
    st.write(", ".join(net.keys()))

    st.divider()

    # ---- CANLI CPU GRAFİK ----
    st.subheader("Canlı CPU Takibi")

    if "cpu_hist" not in st.session_state:
        st.session_state.cpu_hist = [0] * 20

    cpu = psutil.cpu_percent()
    st.session_state.cpu_hist.append(cpu)
    st.session_state.cpu_hist = st.session_state.cpu_hist[-20:]

    st.line_chart(st.session_state.cpu_hist)