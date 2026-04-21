import streamlit as st
import psutil
import platform
import socket
import time
import subprocess
from streamlit_autorefresh import st_autorefresh

# 1. Otomatik Yenileme (Sayfa her 2 saniyede bir kendi kendine yenilenir)
st_autorefresh(interval=2000, key="globalrefresh")

def get_processor_name():
    # Windows'ta normal çalışsın, Linux'ta sistem dosyasından okusun
    if platform.system() == "Windows":
        return platform.processor()
    else:
        try:
            command = "cat /proc/cpuinfo | grep 'model name' | uniq"
            res = subprocess.check_output(command, shell=True).decode().strip()
            return res.split(":")[1].strip()
        except:
            return "Bilinmeyen CPU"

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
        # Yeni işlemci fonksiyonumuzu kullanıyoruz
        st.success(get_processor_name())

    st.divider()

    # ---- RAM & DİSK ----
    st.subheader("Bellek & Depolama")
    mem = psutil.virtual_memory()
    # Not: Sunucu kaynakları değişken olabilir, bu yüzden round ile temiz gösterelim
    ram_gb = round(mem.total / (1024**3), 2)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam RAM", f"{ram_gb} GB")
    c2.metric("Kullanılan RAM", f"%{mem.percent}")
    # ... (disk ve diğer kısımlar aynı kalabilir)

    # ---- CANLI CPU GRAFİK ----
    st.subheader("Canlı CPU Takibi")
    
    # Session state'i kullanarak grafiği koru
    if "cpu_hist" not in st.session_state:
        st.session_state.cpu_hist = [0] * 20

    cpu = psutil.cpu_percent()
    st.session_state.cpu_hist.append(cpu)
    st.session_state.cpu_hist = st.session_state.cpu_hist[-20:]

    st.line_chart(st.session_state.cpu_hist)