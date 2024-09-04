#!/bin/bash

# Función para comprobar si un paquete está instalado
is_installed() {
    dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"
}

# Actualizar el sistema
echo "Actualizando el sistema..."
sudo apt update && sudo apt upgrade -y

# Lista de herramientas esenciales de compilación
TOOLS=("build-essential" "gcc" "g++" "make" "ninja-build" "cmake" "linux-headers-$(uname -r)" "git" "pkg-config" "clang" "lld" "libssl-dev" "zlib1g-dev")

# Instalar herramientas necesarias
for tool in "${TOOLS[@]}"; do
    if is_installed "$tool"; then
        echo "$tool ya está instalado."
    else
        echo "Instalando $tool..."
        sudo apt install -y "$tool"
    fi
done

# Limpiar el sistema
echo "Limpiando el sistema..."
sudo apt autoremove -y && sudo apt clean

echo "Instalación de dependencias de compilación completada."

