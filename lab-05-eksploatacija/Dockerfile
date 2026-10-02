# Lab 05 — namjerno ranjiva meta: SSH sa slabom lozinkom + sudo misconfig (privesc).
# Isključivo za lab okruženje. Nije za izlaganje na mrežu.
FROM debian:12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server sudo openssl procps iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Nisko-privilegirani korisnik sa slabom lozinkom (u passwords.txt).
RUN useradd -m -s /bin/bash flicker && echo 'flicker:summer2024' | chpasswd

# Namjerna pogreška u konfiguraciji: flicker smije pokrenuti `find` kao root bez lozinke.
RUN echo 'flicker ALL=(root) NOPASSWD: /usr/bin/find' > /etc/sudoers.d/flicker \
    && chmod 440 /etc/sudoers.d/flicker

# sshd: dopuštena lozinka za flickera, root login zabranjen.
RUN mkdir -p /run/sshd && ssh-keygen -A \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 22
CMD ["/entrypoint.sh"]
