import ssl
import socket

def run_https_client():
    context = ssl._create_unverified_context()

    with socket.create_connection(("localhost", 5690)) as sock:
        with context.wrap_socket(sock, server_hostname="localhost") as ssock:
            print("🔐 TLS-Verbindung hergestellt:", ssock.version())
            ssock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            response = ssock.recv(4096).decode()
            print("📩 Antwort:\n", response)

if __name__ == "__main__":
    run_https_client()
