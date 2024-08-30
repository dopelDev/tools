# Usar una imagen base de Debian Bookworm
FROM debian:bookworm

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    curl \
    systemd \
    systemd-sysv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Descargar Ollama
RUN curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama \
    && chmod +x /usr/bin/ollama

# Crear usuario y grupo para Ollama
RUN groupadd -r ollama && useradd --no-log-init -r -g ollama ollama

# Copiar el archivo de servicio
COPY ollama.service /etc/systemd/system/ollama.service

# Habilitar el servicio Ollama en tiempo de ejecución
RUN systemctl enable ollama

# Habilitar systemd en el contenedor
STOPSIGNAL SIGRTMIN+3

# Configurar el contenedor para usar systemd
RUN apt-get update && \
    apt-get install -y systemd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done); \
    rm -f /lib/systemd/system/multi-user.target.wants/*;\
    rm -f /etc/systemd/system/*.wants/*;\
    rm -f /lib/systemd/system/local-fs.target.wants/*; \
    rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
    rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
    rm -f /lib/systemd/system/basic.target.wants/*;\
    rm -f /lib/systemd/system/anaconda.target.wants/*;

VOLUME [ "/sys/fs/cgroup" ]

CMD ["/lib/systemd/systemd"]

