# Nœud géré : Ubuntu 24.04 avec systemd + SSH + Python (prérequis minimum d'Ansible)
FROM ubuntu:24.04
ENV container=docker DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      systemd systemd-sysv openssh-server python3 python3-apt sudo ca-certificates \
      iproute2 iputils-ping curl procps cron rsyslog \
    && rm -rf /var/lib/apt/lists/* \
    && systemctl enable ssh \
    && (userdel -r ubuntu 2>/dev/null || true) \
    && useradd -m -s /bin/bash -u 1000 ansible \
    && echo 'ansible ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/ansible \
    && chmod 440 /etc/sudoers.d/ansible \
    && mkdir -p /home/ansible/.ssh /run/sshd \
    && chown -R ansible:ansible /home/ansible/.ssh \
    && printf 'StrictModes no\nPasswordAuthentication no\n' > /etc/ssh/sshd_config.d/lab.conf \
    && systemctl mask getty.target systemd-logind.service 2>/dev/null || true
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
STOPSIGNAL SIGRTMIN+3
EXPOSE 22 80
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/lib/systemd/systemd"]
