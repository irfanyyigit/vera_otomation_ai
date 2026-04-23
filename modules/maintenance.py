import streamlit as st
import psutil
import plotly.express as px
import pandas as pd
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


def render_report_section(history_data):
    st.divider()
    st.subheader("📋 Veri Raporlama")
    
    # Veriyi DataFrame'e çevir
    df = pd.DataFrame(history_data)
    
    # Raporu hazırlat
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 CSV Olarak İndir (Raporla)",
        data=csv,
        file_name='vera_sistem_raporu.csv',
        mime='text/csv',
    )
    st.info("Bu rapor, sistemin o anki performans verilerini analiz için saklamanı sağlar.")