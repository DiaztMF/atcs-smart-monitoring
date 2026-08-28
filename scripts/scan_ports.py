import socket

host = 'surakarta.atcsindonesia.info'
ports = [80, 443, 1935, 8000, 8080, 8086, 8443, 8888, 9000, 3000, 5000]

print(f"Scanning open ports on {host}...")
for p in ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        res = s.connect_ex((host, p))
        if res == 0:
            print(f"  [OPEN] Port {p}")
        else:
            print(f"  [CLOSED/FILTERED] Port {p} (code: {res})")
    except Exception as e:
        print(f"  [ERROR] Port {p}: {e}")
    finally:
        s.close()
