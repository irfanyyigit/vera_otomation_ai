import psutil
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from modules.security import security_check

def render_dashboard():

    st.title("Sistem Kontrol Paneli")

    # ================= SYSTEM STATS =================
    st_autorefresh(interval=6000, key="global_refresh")

    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    #ag bağlantıları
    active_connections = len([conn for conn in psutil.net_connections(kind='inet') if conn.raddr])
    connections = psutil.net_connections(kind='inet')

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("CPU", f"%{cpu}")
    col2.metric("RAM", f"%{ram}")
    col3.metric("DISK", f"%{disk}")
    col4.metric("Ağ Bağlantıları", active_connections)

    st.divider()

    # ================= CLEAN THREAT UI =================

    st.subheader("Gerçek Zamanlı Tehdit İzleme")

    system_alerts = []
    network_alerts = []
    process_alerts = []

    threat_score = 0

    # ================= CPU / RAM =================
    cpu = psutil.cpu_percent(interval=0.3)
    ram = psutil.virtual_memory().percent

    if cpu > 85:
        system_alerts.append(f"CPU yüksek: %{cpu}")
        threat_score += 30

    if ram > 85:
        system_alerts.append(f"RAM yüksek: %{ram}")
        threat_score += 30

    # ================= PROCESS =================
    keywords = ["miner", "hack", "inject", "bot"]

    for p in psutil.process_iter(['name']):
        try:
            name = p.info['name'].lower()
            if any(k in name for k in keywords):
                process_alerts.append(name)
                threat_score += 40
        except:
            pass

    # ================= NETWORK =================
    seen_ips = set()

    for conn in connections:
        try:
            if conn.raddr:
                ip = conn.raddr.ip

                # zaten gördüklerini tekrar alma
                if ip in seen_ips:
                    continue

                seen_ips.add(ip)

                # BURASI EKLENECEK SECURITY KISMI
                allowed, risk, reasons = security_check(ip)

                if not allowed:
                    network_alerts.append(f"BLOCKED: {ip}")
                    continue

                # güvenli IP ise normal göster
                network_alerts.append(ip)

        except:
            pass

    # LIMIT
    threat_score = min(threat_score, 100)

    # ================= UI LAYOUT =================
    left, right = st.columns([1, 2])

    # ===== LEFT: SCORE =====
    with left:
        st.markdown("#### Risk Skoru")

        if threat_score > 70:
            st.error(f" {threat_score}")
        elif threat_score > 40:
            st.warning(f" {threat_score}")
        else:
            st.success(f" {threat_score}")


    # ===== RIGHT: ALERT PANELS =====
    with right:

        col1, col2 = st.columns(2)

        # SYSTEM
        with col1:
            st.markdown("####  Sistem")

            if system_alerts:
                for a in system_alerts:
                    st.warning(a)
            else:
                st.success("Normal")

        # PROCESS
        with col2:
            st.markdown("####  Process")

            if process_alerts:
                for p in process_alerts[:5]:
                    st.error(p)
            else:
                st.success("Temiz")


        # NETWORK
       # NETWORK
    st.markdown("#### Ağ Bağlantıları")

    if network_alerts:
        for i in range(0, min(len(network_alerts), 9), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(network_alerts):
                    ip = network_alerts[i + j]
                    
                    # Buradaki CSS güncellendi
                    cols[j].markdown(f"""
                    <div style="
                        background:#262730;
                        border: 1px solid #4cc9f0;
                        padding: 15px 10px;
                        border-radius: 8px;
                        text-align: center;
                        font-size: 16px;
                        color: #4cc9f0;
                        font-weight: bold;
                        margin-bottom: 10px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 50px;
                    ">
                        {ip}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.success("Şüpheli bağlantı yok")

    st.divider()

    # ================= RAM DETAILS =================
    mem = psutil.virtual_memory()

    st.subheader("Bellek Detayları")
    st.write(f"Toplam RAM: {mem.total // (1024**3)} GB")
    st.write(f"Kullanılan: {mem.used // (1024**3)} GB")
    st.write(f"Boş: {mem.available // (1024**3)} GB")

    st.progress(ram / 100)

    st.divider()

    # ================= CPU LIVE GRAPH =================
    st.subheader("CPU Canlı Grafik")

    if "cpu_history" not in st.session_state:
        st.session_state.cpu_history = [0] * 30

    st.session_state.cpu_history.append(cpu)
    st.session_state.cpu_history = st.session_state.cpu_history[-30:]

    st.line_chart(st.session_state.cpu_history)

    st.divider()

    # ================= NETWORK (FIXED) =================
    st.subheader("Ağ Trafik Grafiği")

    if "net_history" not in st.session_state:
        st.session_state.net_history = {
            "down": [],
            "up": []
        }

    if "net_prev" not in st.session_state:
        st.session_state.net_prev = psutil.net_io_counters()

    net_now = psutil.net_io_counters()

    down = (net_now.bytes_recv - st.session_state.net_prev.bytes_recv) / (1024 * 1024)
    up = (net_now.bytes_sent - st.session_state.net_prev.bytes_sent) / (1024 * 1024)

    st.session_state.net_prev = net_now

    st.session_state.net_history["down"].append(down)
    st.session_state.net_history["up"].append(up)

    for k in st.session_state.net_history:
        st.session_state.net_history[k] = st.session_state.net_history[k][-50:]

    st.line_chart(st.session_state.net_history)

    st.divider()

    # ================= PROCESS LIST (FIXED) =================
    st.subheader("En Çok Kaynak Tüketen Processler")

    # İlk çalıştırmada ölçümü başlat
    if "proc_initialized" not in st.session_state:
        for p in psutil.process_iter():
            try:
                p.cpu_percent(None)
            except:
                pass
        st.session_state.proc_initialized = True
        st.warning("Process verisi hazırlanıyor...")
        st.stop()  # BURASI KRİTİK

    # 2. çalıştırmada gerçek değerleri al
    processes = []

    for p in psutil.process_iter(['pid', 'name']):
        try:
            processes.append({
                "pid": p.pid,
                "name": p.name(),
                "cpu": p.cpu_percent(None),
                "mem": p.memory_percent()
            })
        except:
            pass

    # filtre etmek asagıda bulunan kodu ekledik bu sayede sadece cpu veya ram kullanımı yüksek olan processler gösterilecek
    processes = [p for p in processes if p["cpu"] > 0.1 or p["mem"] > 0.5]
    # sıralamak için burada cpu ve ram kullanımını toplayarak sıralama yapıyoruz böylece en çok kaynak tüketen processler en üstte gözükecek
    processes = sorted(processes, key=lambda x: (x["cpu"] + x["mem"]), reverse=True)

    # UI
    if processes:
        for proc in processes[:8]:
            col1, col2, col3 = st.columns([3, 2, 1])

            col1.write(proc["name"])
            col2.write(f"CPU: %{proc['cpu']:.1f} | RAM: %{proc['mem']:.1f}")

            if col3.button("Kapat", key=f"kill_{proc['pid']}"):
                try:
                    psutil.Process(proc["pid"]).terminate()
                    st.success("Kapatıldı")
                except:
                    st.error("Yetki yok")
    else:
        st.info("Aktif yüksek kaynak kullanan process bulunamadı")

    st.caption("VERA AI • Stable Monitoring System")

    st.divider()
    st.subheader("Security Monitor (Live)")

    for conn in connections:
        if conn.raddr:
            ip = conn.raddr.ip

            allowed, risk, reasons = security_check(ip)

            if not allowed:
                st.error(f"BLOCKED: {ip}")
                st.write(reasons)

            elif risk > 30:
                st.warning(f"SUSPICIOUS: {ip} | Risk: {risk}")

            else:
                st.success(f"SAFE: {ip}")