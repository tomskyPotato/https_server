#!/bin/bash

# ausführbar machen mit chmod +x XXX.sh
# starte mit ./XXX.sh

echo "=== Create Customer Cert Header from PEM ==="

SERVER_NAME="server"
SAFE_NAME="${SERVER_NAME//[^a-zA-Z0-9]/_}"

# Funktion zur Erstellung eines gültigen PEM-Headers mit Byte-Länge
generate_pem_header() {
    local CERT_FILE="$1"
    local HEADER_FILE="$2"
    local VAR_NAME="$3"
    local SECTION="$4"

    echo "=== Erzeuge Header: $HEADER_FILE ==="
    {
        echo "const char ${VAR_NAME}[] ="
        awk '{ gsub(/"/, "\\\""); print "\"" $0 "\\r\\n\"" }' "$CERT_FILE"
        echo ";"
        LENGTH=$(awk '{ total += length($0) + 2 } END { print total + 1 }' "$CERT_FILE")
        echo "const size_t ${VAR_NAME}_len = ${LENGTH};"
    } > "$HEADER_FILE"
}

generate_pem_header "certs/${SAFE_NAME}.crt" "ca_${SAFE_NAME}.h" "ca_${SAFE_NAME}_crt" "credentials"
#generate_pem_header "${SAFE_NAME}.pem" "ca_rsa_${SAFE_NAME}.h" "ca_rsa_${SAFE_NAME}_crt" "credentials"

echo "Server-Zertifikate für ${SERVER_NAME} fertig."