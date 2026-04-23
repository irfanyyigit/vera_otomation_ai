import streamlit as st
import psutil
import plotly.express as px
import pandas as pd
import platform
from datetime import datetime

def render_advanced_monitoring():
    st.title("📊 VERA AI - Sistem İzleme Paneli")
    
    # 1. Dashboard Tabs (Profesyonel yapı)
    tab1, tab2, tab3 = st.tabs(["Sistem Sağlığı", "Disk ve Depolama", "Canlı Süreçler"])

    with tab1:
        st.subheader("CPU & RAM Performansı")
        
        # CPU Verisi
        cpu_perc = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        
        # Plotly ile şık grafik
        df_stats = pd.DataFrame({
            "Kaynak": ["CPU", "RAM"],
            "Kullanım (%)": [cpu_perc, mem.percent]
        })
        
        fig = px.bar(df_stats, x="Kaynak", y="Kullanım (%)", color="Kaynak", 
                     range_y=[0, 100], text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

        # Metrikler
        c1, c2 = st.columns(2)
        c1.metric("CPU Kullanımı", f"%{cpu_perc}")
        c2.metric("RAM Kullanımı", f"%{mem.percent}", f"{mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB")

    with tab2:
        st.subheader("Disk Bölümleri (Linux/Cloud Uyumlu)")
        partitions = psutil.disk_partitions()
        for p in partitions:
            try:
                usage = psutil.disk_usage(p.mountpoint)
                st.write(f"**{p.device}** ({p.mountpoint})")
                st.progress(usage.percent / 100)
                st.caption(f"Toplam: {usage.total // (1024**3)} GB | Kullanılan: {usage.used // (1024**3)} GB")
            except:
                continue

    with tab3:
        st.subheader("Aktif Süreçler (İzleme Modu)")
        # Sadece en çok kaynak tüketen ilk 10'u göster
        procs = []
        for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except:
                continue
        
        df_procs = pd.DataFrame(procs)
        df_procs = df_procs.sort_values(by="memory_percent", ascending=False).head(10)
        
        st.dataframe(df_procs, use_container_width=True)

    st.sidebar.info(f"Sistem Zamanı: {datetime.now().strftime('%H:%M:%S')}")

                # Veriyi toplarken şunu yap:
    if "history_data" not in st.session_state:
        st.session_state.history_data = []

    # Her döngüde yeni veriyi ekle:
    new_data = {"CPU": cpu_perc, "RAM": mem.percent, "Time": datetime.now().strftime("%H:%M:%S")}
    st.session_state.history_data.append(new_data)


def render_report_section(history_data):
    st.divider()
    st.subheader("📋 Veri Raporlama")
    
    # Test et: Veri var mı?
    if history_data:
        df = pd.DataFrame(history_data)
        csv = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 CSV Olarak İndir (Raporla)",
            data=csv,
            file_name='vera_sistem_raporu.csv',
            mime='text/csv',
        )
    else:
        st.warning("Henüz raporlanacak veri toplanmadı.") # Veri yoksa neden gelmediğini burada görürsün

# Veri toplama fonksiyonunu güncelle
def update_history():
    # ÖNCE KONTROL ET: Bu anahtar var mı? Yoksa oluştur.
    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame(columns=["Zaman", "CPU", "RAM"])
    
    # Veri ekleme mantığı
    new_row = {
        "Zaman": datetime.now().strftime("%H:%M:%S"),
        "CPU": psutil.cpu_percent(),
        "RAM": psutil.virtual_memory().percent
    }
    
    # DataFrame güncelleme
    new_df = pd.DataFrame([new_row])
    st.session_state.history = pd.concat([st.session_state.history, new_df]).tail(20)  # Son 20 kaydı tut

def render_system_metadata():
    st.subheader("⚙️ Sistem Altyapısı")
    
    # Platform bilgisi
    uname = platform.uname()
    
    col1, col2 = st.columns(2)
    col1.metric("İşletim Sistemi", uname.system)
    col2.metric("Makine/Node", uname.node)
    
    # Detaylı tablo
    meta_data = {
        "Versiyon": uname.version,
        "İşlemci Mimarisi": uname.machine,
        "İşlemci Modeli": uname.processor,
        "Boot Zamanı": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    }
    st.table(pd.DataFrame(meta_data.items(), columns=["Özellik", "Değer"]))

def render_network_stats():
    st.subheader("🌐 Ağ ve Disk Trafiği")
    
    net = psutil.net_io_counters()
    disk = psutil.disk_io_counters()
    
    c1, c2 = st.columns(2)
    c1.metric("Gönderilen (Net)", f"{net.bytes_sent // 1024**2} MB")
    c1.metric("Alınan (Net)", f"{net.bytes_recv // 1024**2} MB")
    
    c2.metric("Okunan (Disk)", f"{disk.read_bytes // 1024**2} MB")
    c2.metric("Yazılan (Disk)", f"{disk.write_bytes // 1024**2} MB")




