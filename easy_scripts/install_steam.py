import os
import subprocess
import getpass

def run_command(command, use_sudo=False):
    """Run a shell command with optional sudo."""
    if use_sudo:
        sudo_password = getpass.getpass("Introduce tu contraseña de sudo: ")
        command = f"echo {sudo_password} | sudo -S {command}"
    process = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        print(f"Error al ejecutar el comando: {command}\nError: {process.stderr}")
    else:
        print(process.stdout)

def check_architecture():
    """Check if i386 architecture is enabled."""
    print("Verificando si la arquitectura i386 está habilitada...")
    result = subprocess.run("dpkg --print-foreign-architectures", shell=True, text=True, stdout=subprocess.PIPE)
    if "i386" not in result.stdout:
        print("Habilitando la arquitectura i386...")
        run_command("dpkg --add-architecture i386", use_sudo=True)
    else:
        print("La arquitectura i386 ya está habilitada.")

def update_sources_list():
    """Update sources list with contrib and non-free repositories."""
    print("Actualizando la source list con repositorios contrib y non-free...")
    sources_list_path = "/etc/apt/sources.list"
    new_sources = """
deb http://deb.debian.org/debian/ $(lsb_release -cs) main contrib non-free
deb-src http://deb.debian.org/debian/ $(lsb_release -cs) main contrib non-free
deb http://deb.debian.org/debian/ $(lsb_release -cs)-updates main contrib non-free
deb-src http://deb.debian.org/debian/ $(lsb_release -cs)-updates main contrib non-free
deb http://deb.debian.org/debian-security/ $(lsb_release -cs)-security main contrib non-free
deb-src http://deb.debian.org/debian-security/ $(lsb_release -cs)-security main contrib non-free
"""
    with open(sources_list_path, "r") as file:
        current_sources = file.read()
    
    if "contrib" not in current_sources or "non-free" not in current_sources:
        with open(sources_list_path, "w") as file:
            file.write(new_sources)
        print("Sources list actualizada.")
    else:
        print("La sources list ya contiene los repositorios contrib y non-free.")

def install_steam():
    """Download and install Steam on Debian using a .deb file."""
    print("Descargando e instalando Steam...")
    steam_deb_url = "https://cdn.akamai.steamstatic.com/client/installer/steam.deb"
    steam_deb_file = "steam.deb"
    
    # Descargar el archivo .deb de Steam
    run_command(f"wget {steam_deb_url} -O {steam_deb_file}")

    # Instalar el archivo .deb descargado
    run_command(f"dpkg -i {steam_deb_file}", use_sudo=True)

    # Resolver dependencias rotas si las hay
    run_command("apt --fix-broken install -y", use_sudo=True)

    # Limpiar el archivo .deb después de la instalación
    os.remove(steam_deb_file)
    print("Instalación de Steam completada.")

if __name__ == "__main__":
    check_architecture()
    update_sources_list()
    install_steam()

