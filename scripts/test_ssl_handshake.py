import socket
import ssl

host = 'surakarta.atcsindonesia.info'
port = 8086

print(f"Resolving {host}...")
ip = socket.gethostbyname(host)
print(f"IP: {ip}")

# Test different TLS versions and ciphers
versions = [
    ("TLS 1.2", ssl.PROTOCOL_TLS_CLIENT, ssl.TLSVersion.TLSv1_2),
    ("TLS 1.3", ssl.PROTOCOL_TLS_CLIENT, ssl.TLSVersion.TLSv1_3),
    ("Auto TLS", ssl.PROTOCOL_TLS_CLIENT, None),
]

for name, proto, ver in versions:
    print(f"\n--- Testing {name} ---")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((host, port))
        print("  TCP Socket connected!")

        ctx = ssl.SSLContext(proto)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_ciphers('DEFAULT:@SECLEVEL=0')
        if ver:
            ctx.minimum_version = ver
            ctx.maximum_version = ver

        # Wrap socket WITH SNI server_hostname
        print("  Wrapping SSL with SNI...")
        ssock = ctx.wrap_socket(sock, server_hostname=host)
        print(f"  [SUCCESS] Cipher: {ssock.cipher()}, Version: {ssock.version()}")
        
        # Try sending HTTP request
        req = f"GET /camera/Balapan01.flv HTTP/1.1\r\nHost: {host}:{port}\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
        ssock.sendall(req.encode())
        res = ssock.recv(256)
        print(f"  [RESPONSE] {res[:100]}")
        ssock.close()
    except Exception as e:
        print(f"  [FAILED] Error: {e}")
