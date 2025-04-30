# lsof -ti tcp:5690

import ssl
import socket

def run_https_server():
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    ssl_ctx.load_cert_chain("/home/coder/projects/https_server/certs/server.crt",
                        "/home/coder/projects/https_server/certs/server.key")

    #ssl_ctx.verify_mode = ssl.CERT_NONE

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", 5690))
        sock.listen(5)
        print("✅ HTTPS-Server läuft auf Port 5690...")

        with ssl_ctx.wrap_socket(sock, server_side=True) as ssock:
            while True:
                try:
                    conn, addr = ssock.accept()
                    print(f"🔗 Verbindung von {addr}")
                    request = conn.recv(1024).decode()
                    print("📥 Anfrage:\n", request)

                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        "Content-Length: 13\r\n"
                        "\r\n"
                        "Hello, HTTPS!"
                    )
                    conn.sendall(response.encode())
                    conn.close()
                except ssl.SSLError as e:
                    print(f"❌ SSL-Fehler bei Verbindung: {e}")
                except Exception as e:
                    print(f"❌ Allgemeiner Fehler: {e}")

if __name__ == "__main__":
    run_https_server()