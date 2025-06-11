# sudo apt install lsof
# lsof -i :5690
# sudo kill -9 xxxxxx

import ssl
import socket
import sys
from datetime import datetime

LOG_PATH = "/home/coder/projects/https_server/https_log.csv"

def log_transfer(timestamp, received_size, sent_size):
    with open(LOG_PATH, "a") as logfile:
        logfile.write(f"{timestamp},{received_size},{sent_size}\n")

def parse_http_request(request_bytes):
    """
    Parst eine einfache HTTP-Anfrage (rudimentär).
    Gibt Methode, Pfad, Header und Body zurück.
    """
    request_str = request_bytes.decode('utf-8', errors='ignore')
    lines = request_str.split('\r\n')

    method = None
    path = None
    http_version = None
    headers = {}
    body = ""
    
    if not lines:
        return method, path, http_version, headers, body

    # Parse Request-Line (e.g., GET /index.html HTTP/1.1)
    request_line_parts = lines[0].split(' ')
    if len(request_line_parts) >= 3:
        method = request_line_parts[0]
        path = request_line_parts[1]
        http_version = request_line_parts[2]
    elif len(request_line_parts) == 2: # Sometimes HTTP/1.0 requests omit version
        method = request_line_parts[0]
        path = request_line_parts[1]
        http_version = "HTTP/1.0" # Assume HTTP/1.0 if not specified
    elif len(request_line_parts) == 1: # Only method
        method = request_line_parts[0]
        path = "/"
        http_version = "HTTP/1.0"

    # Parse Headers and Body
    header_end_index = -1
    for i, line in enumerate(lines[1:]):
        if not line: # Empty line signifies end of headers
            header_end_index = i + 1 # +1 because we started from lines[1:]
            break
        parts = line.split(':', 1)
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            headers[key] = value

    if header_end_index != -1:
        body = '\r\n'.join(lines[header_end_index + 1:])

    return method, path, http_version, headers, body


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
                    
                    method, path, http_version, headers, body = parse_http_request(request_as_bytes)

                    if method:
                        print(f"📥 Methode: {method}")
                        print(f"🌍 Pfad: {path}")
                        print(f"📜 HTTP-Version: {http_version}")
                        print("📥 Header:")
                        for key, value in headers.items():
                            print(f"    {key}: {value}")
                        if body:
                            print("📦 Payload:\n", body)
                    else:
                        print("⚠ Ungültige oder leere HTTP-Anfrage empfangen.")

                    # Manuelle Konstruktion der HTTP-Antwort
                    status_line = "HTTP/1.1 200 OK\r\n"
                    headers = {
                        "Content-Type": "text/plain; charset=utf-8",
                        "Connection": "close", # Keep-alive ist komplexer ohne Parser
                        "Date": datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
                    }
                    
                    response_body_content = f"Hallo von deinem HTTPS-Server!\n\nEmpfangene Anfrage:\n{request_as_bytes.decode('utf-8', errors='ignore')}"
                    headers["Content-Length"] = str(len(response_body_content.encode('utf-8')))

                    response_headers = "".join([f"{k}: {v}\r\n" for k, v in headers.items()])
                    
                    full_response = (status_line + 
                                     response_headers + 
                                     "\r\n" + # Leere Zeile zwischen Headern und Body
                                     response_body_content).encode('utf-8')
                    
                    conn.sendall(full_response)
                    sent_size = len(full_response)

                    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
                    print(f"✅ Daten erfolgreich zurückgesendet um {timestamp}")

                    conn.close()
                    log_transfer(timestamp, received_size, sent_size) # log_transfer ist jetzt aktiv

                except ssl.SSLError as e:
                    print(f"❌ SSL-Fehler bei Verbindung: {e}")
                except socket.timeout:
                    print("⌛ Verbindung aufgrund von Inaktivität geschlossen (Timeout).")
                except Exception as e:
                    print(f"❌ Allgemeiner Fehler: {e}")
                    # Hier könnte man detailliertere Fehlerbehandlung hinzufügen
                    try:
                        conn.close()
                    except:
                        pass # Verbindung war vielleicht schon geschlossen

if __name__ == "__main__":
    run_https_server("ecdsa")