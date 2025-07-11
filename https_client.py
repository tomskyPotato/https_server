import ssl
import socket

def run_https_client():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile="public/ca_public_rsa_weptech_iot_de.crt")
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED

    with socket.create_connection(("localhost", 5690)) as sock:
        with context.wrap_socket(sock, server_hostname="localhost") as ssock:
            print("🔐 TLS-Verbindung hergestellt:", ssock.version())
            ssock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            response = ssock.recv(4096).decode()
            print("📩 Antwort:\n", response)

if __name__ == "__main__":
    run_https_client()
