import ssl
import socket
import sys
from datetime import datetime
from http_parser.parser import HttpParser

LOG_PATH = "/home/coder/projects/https_server/https_log.csv"

def log_transfer(timestamp, received_size, sent_size):
    with open(LOG_PATH, "a") as logfile:
        logfile.write(f"{timestamp},{received_size},{sent_size}\n")

def run_https_server(cert_type):
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.set_ciphers("ALL:@SECLEVEL=0")  # Nur für Debug!
    cert_path = f"/home/coder/projects/https_server/public/server_public_{cert_type}_weptech_iot_de.crt"
    key_path = f"/home/coder/projects/https_server/private/server_private_{cert_type}_weptech_iot_de.key"
    ssl_ctx.load_cert_chain(certfile=cert_path, keyfile=key_path)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", 5690))
        sock.listen(5)
        print("✅ HTTPS-Server läuft auf Port 5690...")

        with ssl_ctx.wrap_socket(sock, server_side=True) as ssock:
            while True:
                try:
                    conn, addr = ssock.accept()
                    print(f"\n🔗 Verbindung von {addr}")
                    print(f"🔐 Verwendete Cipher Suite: {conn.cipher()[0]}")
                    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
                    print(f"🔗 Verbindung erfolgreich aufgebaut um {timestamp}")

                    conn.settimeout(10)

                    request_as_bytes = conn.recv(10000)
                    received_size = len(request_as_bytes)
                    request_as_string = request_as_bytes.decode(errors="ignore")

                    parser = HttpParser()
                    parser.execute(request_as_bytes, received_size)

                    if parser.is_headers_complete():
                        print("📥 Header:\n", parser.get_headers())
                        if parser.is_message_complete():
                            body_as_string = parser.recv_body().decode(errors="ignore")
                            print("📦 Payload:\n", body_as_string)

                    response = "HTTPS-Server: " + request_as_string
                    conn.sendall(response.encode('utf-8'))
                    sent_size = len(response.encode('utf-8'))

                    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
                    print(f"✅ Daten erfolgreich zurückgesendet um {timestamp}")

                    conn.close()
                    log_transfer(timestamp, received_size, sent_size)

                except ssl.SSLError as e:
                    print(f"❌ SSL-Fehler bei Verbindung: {e}")
                except Exception as e:
                    print(f"❌ Allgemeiner Fehler: {e}")

if __name__ == "__main__":
    run_https_server("ecdsa")
