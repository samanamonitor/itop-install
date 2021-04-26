#!/bin/bash

SERVER=$1
PORT=$2
USERNAME=$3
PASSWORD=$4

sudo postconf -e "relayhost = [${SERVER}]:${PORT}" \
"smtp_sasl_auth_enable = yes" \
"smtp_sasl_security_options = noanonymous" \
"smtp_sasl_password_maps = hash:/etc/postfix/sasl_password" \
"smtp_use_tls = yes" \
"smtp_tls_security_level = encrypt" \
"smtp_tls_note_starttls_offer = yes" \
"smtp_tls_CAfile = /etc/pki/tls/certs/ca-bundle.crt"

cat <<EOF >> /etc/postfix/sasl_password
[${SERVER}]:${PORT} ${USERNAME}:${PASSWORD}
EOF

sudo postmap hash:/etc/postfix/sasl_password
sudo chown root:root /etc/postfix/sasl_password
sudo chmod 0600 /etc/postfix/sasl_password

/etc/init.d/postfix restart
