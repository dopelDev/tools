import os
import difflib
import getpass
import subprocess

# Contenido esperado del archivo sources.list
expected_sources_list = """
#deb cdrom:[Debian GNU/Linux 12.5.0 _Bookworm_ - Official amd64 NETINST with firmware 20240210-11:27]/ bookworm contrib main non-free-firmware

deb http://deb.debian.org/debian/ bookworm main non-free-firmware non-free contrib
deb-src http://deb.debian.org/debian/ bookworm main non-free-firmware non-free contrib

deb http://security.debian.org/debian-security bookworm-security main non-free-firmware
deb-src http://security.debian.org/debian-security bookworm-security main non-free-firmware

# bookworm-updates, to get updates before a point release is made;
# see https://www.debian.org/doc/manuals/debian-reference/ch02.en.html#_updates_and_backports
deb http://deb.debian.org/debian/ bookworm-updates main non-free-firmware non-free contrib
deb-src http://deb.debian.org/debian/ bookworm-updates main non-free-firmware non-free contrib

deb http://deb.debian.org/debian/ bookworm-updates main contrib non-free
deb http://deb.debian.org/debian/ bookworm-backports main contrib non-free


# This system was installed using small removable media
# (e.g. netinst, live or single CD). The matching "deb cdrom"
# entries were disabled at the end of the installation process.
# For information about how to configure apt package sources,
# see the sources.list(5) manual.
"""

# Path al archivo sources.list
sources_list_path = "/etc/apt/sources.list"

def read_file(file_path):
    """Leer contenido de un archivo y devolverlo como una lista de líneas."""
    with open(file_path, 'r') as file:
        return file.readlines()

def write_file(file_path, content):
    """Escribir contenido en un archivo."""
    with open(file_path, 'w') as file:
        file.write(content)

def compare_sources_lists(current, expected):
    """Comparar dos listas de contenido y devolver las diferencias."""
    diff = list(difflib.unified_diff(current, expected, fromfile='current', tofile='expected'))
    return diff

def update_sources_list(sudo_password):
    """Actualizar el archivo sources.list con contenido esperado."""
    try:
        command = f"echo '{sudo_password}' | sudo -S cp /tmp/updated_sources.list {sources_list_path}"
        subprocess.run(command, shell=True, check=True)
        print("Archivo sources.list actualizado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"Error al actualizar el archivo: {e}")

def main():
    # Leer el archivo actual de sources.list
    try:
        current_sources_list = read_file(sources_list_path)
    except FileNotFoundError:
        print(f"Archivo {sources_list_path} no encontrado.")
        return
    
    # Comparar con el contenido esperado
    diff = compare_sources_lists(current_sources_list, expected_sources_list.splitlines(True))
    
    if diff:
        print("Se encontraron diferencias en el archivo sources.list:")
        for line in diff:
            print(line, end='')

        confirm = input("\n¿Deseas actualizar el archivo sources.list? (s/n): ").lower()
        if confirm == 's':
            sudo_password = getpass.getpass(prompt="Ingresa la contraseña de sudo: ")
            
            # Guardar el nuevo contenido en un archivo temporal
            tmp_file_path = "/tmp/updated_sources.list"
            write_file(tmp_file_path, expected_sources_list)
            
            # Actualizar el archivo sources.list con permisos de sudo
            update_sources_list(sudo_password)
        else:
            print("Actualización cancelada.")
    else:
        print("El archivo sources.list está actualizado y no requiere cambios.")

if __name__ == "__main__":
    main()

