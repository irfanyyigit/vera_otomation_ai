import streamlit as st
import psutil
import os
import shutil
import time

# -------- AĞIR PROCESS BUL --------
def get_heavy_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['cpu_percent'] > 1 or proc.info['memory_percent'] > 1:
                processes.append(proc.info)
        except:
            pass
    return sorted(processes, key=lambda x: x['memory_percent'], reverse=True)

# -------- ANA MODÜL --------
def render_maintenance():
    st.title("Hızlı Bakım Merkezi")

    # ---- TEMİZLİK ----
    st.subheader("Sistem Temizliği")

    if st.button("Geçici Dosyaları Temizle"):
        total_deleted = 0

        temp_paths = [
            os.environ.get('TEMP'),
            "C:\\Windows\\Temp"
        ]

        for path in temp_paths:
            if path and os.path.exists(path):
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            total_deleted += 1
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            total_deleted += 1
                    except:
                        pass

        st.success(f"{total_deleted} dosya temizlendi")

    st.divider()

    # ---- ZOMBİ AVCISI ----
    st.subheader("Zombi Avcısı (RAM Temizleme)")

    if "proc_list" not in st.session_state:
        st.session_state.proc_list = []

    if st.button("Ağır Süreçleri Tara"):
        st.session_state.proc_list = get_heavy_processes()

    if st.session_state.proc_list:
        for p in st.session_state.proc_list[:10]:
            col1, col2, col3 = st.columns([2, 2, 1])

            col1.write(f"{p['name']} (PID: {p['pid']})")
            col2.write(f"RAM: %{p['memory_percent']:.1f} | CPU: %{p['cpu_percent']:.1f}")

            if col3.button("Kapat", key=p['pid']):
                try:
                    psutil.Process(p['pid']).terminate()
                    st.success(f"{p['name']} kapatıldı")
                    st.rerun()
                except:
                    st.error("Kapatılamadı (yetki gerekli olabilir)")