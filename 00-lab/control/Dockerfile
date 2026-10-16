# Nœud de contrôle : Ansible + outils qualité
FROM python:3.12-slim
ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends \
      openssh-client git sshpass vim-tiny less curl jq iputils-ping ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash -u 1000 ansible
RUN pip install ansible ansible-lint yamllint jmespath netaddr passlib \
      molecule pytest-testinfra
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
USER ansible
WORKDIR /workspace
ENTRYPOINT ["/entrypoint.sh"]
CMD ["sleep", "infinity"]
