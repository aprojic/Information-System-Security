#!/bin/sh
# Flag se izvede iz studentovog matičnog broja (MB) i tajnog seeda (ISS_SECRET);
# čitljiv samo rootu → dokaz uspješne eskalacije. Isti flag daje nastavnikov checker.
HEX=$(printf '%s' "lab05:${MB}" | openssl dgst -sha256 -hmac "${ISS_SECRET}" | awk '{print $NF}' | cut -c1-6)
echo "ASPIRA{sis05_${HEX}}" > /root/flag.txt
chmod 600 /root/flag.txt
exec /usr/sbin/sshd -D -e
