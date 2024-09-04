#!/usr/bin/env bats

# Ruta al script que vamos a probar
SCRIPT="./build_dependencies.sh"

# Prueba para verificar que el script existe y es ejecutable
@test "El script de instalación existe y es ejecutable" {
  [ -f "$SCRIPT" ]
  [ -x "$SCRIPT" ]
}

# Prueba para ejecutar el script y verificar que se ejecuta sin errores
@test "El script de instalación se ejecuta sin errores" {
  run bash "$SCRIPT"
  [ "$status" -eq 0 ]
}

# Lista de paquetes que deberían estar instalados después de ejecutar el script
PACKAGES=("build-essential" "gcc" "g++" "make" "ninja-build" "cmake" "linux-headers-$(uname -r)" "git" "pkg-config" "clang" "lld" "libssl-dev" "zlib1g-dev")

# Prueba para verificar que cada paquete está instalado
for package in "${PACKAGES[@]}"; do
  @test "El paquete $package está instalado" {
    run dpkg -s "$package" &> /dev/null
    [ "$status" -eq 0 ]
  }
done

