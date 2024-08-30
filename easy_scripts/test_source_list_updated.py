import pytest
from unittest.mock import patch, mock_open, call
from source_list_updated import read_file, write_file, compare_sources_lists, main

# Contenido esperado para el archivo sources.list
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

@pytest.fixture
def mock_sources_list():
    """Fixture para simular el contenido del archivo sources.list"""
    return expected_sources_list.splitlines(True)

def test_read_file(mock_sources_list):
    """Prueba para la función read_file."""
    m = mock_open(read_data="".join(mock_sources_list))
    with patch('builtins.open', m):
        result = read_file('/etc/apt/sources.list')
        assert result == mock_sources_list

def test_write_file():
    """Prueba para la función write_file."""
    m = mock_open()
    with patch('builtins.open', m):
        write_file('/etc/apt/sources.list', expected_sources_list)
        m.assert_called_once_with('/etc/apt/sources.list', 'w')
        m().write.assert_called_once_with(expected_sources_list)

def test_compare_sources_lists(mock_sources_list):
    """Prueba para la función compare_sources_lists."""
    diff = compare_sources_lists(mock_sources_list, mock_sources_list)
    assert diff == []

def test_main_diff_detected():
    """Prueba para la función principal main con detección de diferencias."""
    # Mock del archivo actual
    current_sources_list = "# Different content\n"

    with patch('builtins.open', mock_open(read_data=current_sources_list)):
        with patch('builtins.input', return_value='n'):  # Mock de entrada del usuario para cancelar
            with patch('getpass.getpass', return_value='password'):
                with patch('subprocess.run') as mock_run:
                    main()
                    mock_run.assert_not_called()

def test_main_update_confirmed():
    """Prueba para la función principal main con actualización confirmada."""
    # Mock del archivo actual
    current_sources_list = "# Different content\n"

    with patch('builtins.open', mock_open(read_data=current_sources_list)):
        with patch('builtins.input', return_value='s'):  # Mock de entrada del usuario para confirmar
            with patch('getpass.getpass', return_value='password'):
                with patch('subprocess.run') as mock_run:
                    main()
                    mock_run.assert_called_once()

