import psutil

def get_connections():

    conns = []

    for c in psutil.net_connections(kind="inet"):
        try:
            if not c.raddr or not c.pid:
                continue

            try:
                p = psutil.Process(c.pid)
                name = p.name()
            except:
                name = "unknown"

            ip = c.raddr.ip

            # LOCAL FILTER
            if ip.startswith(("127.", "192.168.", "10.")) or ip == "::1":
                continue

            conns.append({
                "pid": c.pid,
                "process": name,
                "ip": ip,
                "port": c.raddr.port,
                "status": c.status
            })

        except:
            pass

    return conns