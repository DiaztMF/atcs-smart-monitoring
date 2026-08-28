import socket

host = 'surakarta.atcsindonesia.info'
port = 8086

print(f"Connecting raw TCP to {host}:{port}...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5.0)
s.connect((host, port))
print("Connected!")

# Test HTTP request
req = "GET /camera/Balapan01.flv HTTP/1.1\r\nHost: surakarta.atcsindonesia.info:8086\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n\r\n"
s.sendall(req.encode())

try:
    data = s.recv(1024)
    print(f"Received {len(data)} bytes: {data[:100]}")
except Exception as e:
    print(f"Recv error: {e}")

s.close()
