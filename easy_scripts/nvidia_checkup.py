import os
import subprocess
import logging
import sys
import getpass

def is_root():
    """Check if the current user is root."""
    return os.geteuid() == 0

def run_with_sudo(command, password):
    """Run a command with sudo using the provided password."""
    try:
        # Crear el comando con 'sudo -S'
        sudo_command = f'echo {password} | sudo -S ' + command
        result = subprocess.run(sudo_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f"Command '{command}' executed successfully.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command '{command}': {e.stderr}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def setup_logging():
    """Setup logging configuration."""
    try:
        # Obtener el nombre del script para usarlo como nombre del archivo de log
        script_name = os.path.basename(__file__)
        log_file_name = f"{os.path.splitext(script_name)[0]}.log"

        # Usar un archivo de log en el directorio del usuario si no es root
        if is_root():
            log_file = f"/var/log/{log_file_name}"
        else:
            log_file = os.path.expanduser(f"~/{log_file_name}")
        
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Logging initialized.")
    except PermissionError as e:
        print(f"PermissionError: {e}. Try running the script with sudo.")
        sys.exit(1)

def check_nvidia():
    """Check if an NVIDIA GPU is installed."""
    try:
        result = subprocess.run(['lspci'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if "NVIDIA" in result.stdout:
            logging.info("NVIDIA GPU detected.")
            return True
        else:
            logging.info("No NVIDIA GPU detected.")
            return False
    except Exception as e:
        logging.error(f"Error checking for NVIDIA GPU: {e}")
        return False

def check_and_install_linux_headers(password):
    """Check if Linux headers are installed and prompt to install them if not."""
    try:
        kernel_version = subprocess.run(['uname', '-r'], stdout=subprocess.PIPE, text=True).stdout.strip()
        headers_installed = subprocess.run(['dpkg', '-l', f'linux-headers-{kernel_version}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if "no packages found" in headers_installed.stderr:
            print("Linux headers are not installed.")
            install_confirm = input("Do you want to install the Linux headers now? (y/n): ").strip().lower()
            if install_confirm == 'y':
                run_with_sudo(f'apt update && apt install -y linux-headers-{kernel_version}', password)
                logging.info("Linux headers installed successfully.")
                print("Linux headers installed successfully.")
            else:
                logging.info("User opted not to install Linux headers.")
                print("Installation of Linux headers skipped by user.")
        else:
            logging.info("Linux headers are already installed.")
            print("Linux headers are already installed.")

    except Exception as e:
        logging.error(f"Error checking/installing Linux headers: {e}")
        print(f"Error checking/installing Linux headers: {e}")

def blacklist_nouveau(password):
    """Blacklist the nouveau driver."""
    try:
        blacklist_file = '/etc/modprobe.d/blacklist-nouveau.conf'
        blacklist_content = """
blacklist nouveau
options nouveau modeset=0
"""
        # Check if blacklist file exists using sudo privileges
        if not os.path.exists(blacklist_file):
            # Create blacklist file using sudo privileges
            run_with_sudo(f'echo "{blacklist_content}" | sudo tee {blacklist_file}', password)
            logging.info("Created blacklist file to disable nouveau driver.")
            print("Nouveau driver blacklisted successfully.")
        else:
            logging.info("Blacklist file already exists. No changes made.")
            print("Blacklist file already exists. Skipping creation.")

        # Confirmación del usuario antes de actualizar initramfs
        update_confirm = input("Do you want to update initramfs now? (y/n): ").strip().lower()
        if update_confirm == 'y':
            run_with_sudo('update-initramfs -u', password)
            logging.info("initramfs updated successfully.")
            print("initramfs updated successfully.")
        else:
            logging.info("initramfs update skipped by user.")
            print("initramfs update skipped.")

    except Exception as e:
        logging.error(f"Error blacklisting nouveau driver: {e}")
        print(f"Error blacklisting nouveau driver: {e}")

if __name__ == "__main__":
    # Verificar si el usuario es root
    if not is_root():
        print("This script requires root privileges. Please enter your sudo password.")
        sudo_password = getpass.getpass(prompt="Enter sudo password: ")

        # Configurar logging
        setup_logging()

        # Verificar e instalar headers de Linux
        check_and_install_linux_headers(sudo_password)

        if check_nvidia():
            blacklist_nouveau(sudo_password)
        else:
            print("No NVIDIA GPU detected or unable to detect.")
    else:
        # Si ya es root, solo configurar logging y continuar normalmente
        setup_logging()

        # Verificar e instalar headers de Linux
        check_and_install_linux_headers("")

        if check_nvidia():
            blacklist_nouveau("")
        else:
            print("No NVIDIA GPU detected or unable to detect.")

