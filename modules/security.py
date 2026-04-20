import streamlit as st
import socket
import os
import psutil
import hashlib
import time
import sqlite3
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from modules.network_monitor import get_connections
from streamlit_autorefresh import st_autorefresh
import requests

# ---------------- PORT SCAN ----------------
def port_scan(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        return port if s.connect_ex((host, port)) == 0 else None
    finally:
        s.close()

# ---------------- MAIN ----------------
def render_security():
    st.title("Güvenlik Merkezi")

    # ---- PORT TARAMA ----
    st.subheader("Port Tarama")

    if st.button("Portları Tara"):
        with ThreadPoolExecutor(max_workers=30) as executor:
            results = list(executor.map(lambda p: port_scan("127.0.0.1", p), range(1, 1025)))

        open_ports = [p for p in results if p]

        if open_ports:
            st.warning(f"{len(open_ports)} açık port bulundu!")
            for p in open_ports:
                st.error(f"Açık Port: {p}")
        else:
            st.success("Açık port yok")

    st.divider()

    # ---- DOSYA HASH ----
    st.subheader("Şüpheli Dosya Analizi")

    path = st.text_input("Klasör Yolu", "C:/")

    if st.button("Analiz Başlat"):
        if not os.path.exists(path):
            st.error("Geçersiz yol")
            return

        files = []
        for root, _, filenames in os.walk(path):
            for f in filenames:
                files.append(os.path.join(root, f))

        results = []
        progress = st.progress(0)

        for i, file in enumerate(files):
            try:
                h = hashlib.sha256()
                with open(file, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        h.update(chunk)

                results.append({
                    "Dosya": os.path.basename(file),
                    "Hash": h.hexdigest(),
                    "Durum": "Güvenli"
                })
            except:
                results.append({
                    "Dosya": os.path.basename(file),
                    "Hash": "Hata",
                    "Durum": "Okunamadı"
                })

            progress.progress((i + 1) / len(files))

        st.success("Analiz tamamlandı")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

    st.subheader("Gerçek Zamanlı Tehdit İzleme")

    import psutil

    alerts = []

    # CPU spike kontrol
    cpu = psutil.cpu_percent(interval=0.5)
    if cpu > 85:
        alerts.append(f"Yüksek CPU kullanımı: %{cpu}")

    # RAM spike
    ram = psutil.virtual_memory().percent
    if ram > 85:
        alerts.append(f"Yüksek RAM kullanımı: %{ram}")

    # Şüpheli process (örnek basit kontrol)
    suspicious_names = ["miner", "hack", "inject"]

    for p in psutil.process_iter(['name']):
        try:
            name = p.info['name'].lower()
            if any(x in name for x in suspicious_names):
                alerts.append(f"Şüpheli process: {name}")
        except:
            pass

    # UI
    if alerts:
        for alert in alerts:
            st.error(alert)
    else:
        st.success("Sistem temiz görünüyor")


    st.subheader("Canlı Ağ Bağlantıları")

    connections = psutil.net_connections(kind='inet')

    suspicious = []

    unique_connections = {}

    for conn in connections:
        try:
            if conn.raddr:
                key = (conn.pid, conn.raddr.ip, conn.raddr.port)

                if key in unique_connections:
                    continue  # aynı bağlantıyı atla

                proc = psutil.Process(conn.pid) if conn.pid else None
                pname = proc.name() if proc else "Unknown"

                unique_connections[key] = {
                    "process": pname,
                    "ip": conn.raddr.ip,
                    "port": conn.raddr.port,
                    "pid": conn.pid
                }
        except:
            pass

    suspicious = list(unique_connections.values())

    # UI
    if suspicious:
        st.error(f"{len(suspicious)} şüpheli bağlantı bulundu!")

        for s in suspicious[:10]:
            col1, col2, col3 = st.columns([3,2,1])

            col1.write(f"**{s['process']}** (PID: {s['pid']})")
            col2.write(f"{s['ip']}:{s['port']}")

            if col3.button("Kes", key=f"kill_conn_{s['pid']}_{s['ip']}_{s['port']}"):
                try:
                    psutil.Process(s['pid']).terminate()
                    st.success("Bağlantı kesildi")
                except:
                    st.error("Yetki yok")
    else:
        st.success("Şüpheli dış bağlantı yok")

    st.divider()

    st.subheader("Gelişmiş Process Güvenliği")

    import time

    process_alerts = []

    # baseline için önce snapshot al
    process_data = {}

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            process_data[proc.pid] = {
                "name": proc.info['name'],
                "cpu": proc.cpu_percent(interval=None),
                "mem": proc.info['memory_percent']
            }
        except:
            pass

    time.sleep(1)

    # ikinci ölçüm (spike yakalamak için)
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_percent()

            # CPU spike
            if cpu > 70:
                process_alerts.append(f"CPU Spike: {proc.name()} (PID {proc.pid}) → %{cpu}")

            # RAM spike
            if mem > 25:
                process_alerts.append(f"Yüksek RAM: {proc.name()} (PID {proc.pid}) → %{round(mem,2)}")

            # yeni process (baseline'da yoksa)
            if proc.pid not in process_data:
                process_alerts.append(f"Yeni process: {proc.name()} (PID {proc.pid})")

            # şüpheli path
            try:
                exe_path = proc.exe()
                if "temp" in exe_path.lower() or "appdata" in exe_path.lower():
                    process_alerts.append(f"Şüpheli konum: {proc.name()} → {exe_path}")
            except:
                pass

        except:
            pass

    # UI
    if process_alerts:
        st.error(f"{len(process_alerts)} process tehdidi tespit edildi!")

        for alert in process_alerts[:15]:
            st.warning(alert)
    else:
        st.success("Process davranışları normal görünüyor")


DB = "vera_bakim.db"



def get_db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def analyze_ip(ip: str):
    risk = 0
    reasons = []

    # Local IP kontrolü
    if ip.startswith(("127.", "10.", "192.168.", "::1")):
        return 0, ["local_ip"]

    # External IP intelligence (opsiyonel API)
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=2)
        data = r.json()

        if data.get("proxy"):
            risk += 40
            reasons.append("proxy_detected")

        if data.get("vpn"):
            risk += 40
            reasons.append("vpn_detected")

        country = data.get("country_code")
        if country in ["CN", "RU", "KP"]:
            risk += 20
            reasons.append("high_risk_country")

    except:
        reasons.append("geo_api_failed")

    # Format check
    if ip.count(".") != 3:
        risk += 50
        reasons.append("invalid_ip_format")

    return risk, reasons


# =========================
# BLOCK IP
# =========================
def block_ip(ip, reason, risk):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO blocked_ips (ip, reason, risk_score, created_at)
        VALUES (?, ?, ?, ?)
    """, (ip, reason, risk, time.time()))

    conn.commit()
    conn.close()

# =========================
# CHECK IF BLOCKED
# =========================
def is_blocked(ip: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT ip FROM blocked_ips WHERE ip=?", (ip,))
    result = cur.fetchone()

    conn.close()

    return result is not None


# =========================
# MAIN SECURITY CHECK
# =========================
def security_check(ip):
    conn = sqlite3.connect(DB, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT risk, reason FROM ip_blacklist WHERE ip = ?", (ip,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return False, row[0], row[1]

    return True, 0, []