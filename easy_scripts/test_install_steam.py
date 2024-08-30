import pytest
import subprocess
from unittest.mock import patch, mock_open
from install_steam import check_architecture, update_sources_list, install_steam, run_command

def test_run_command():
    """Test run_command with and without sudo."""
    with patch('subprocess.run') as mocked_run:
        run_command('echo test')
        mocked_run.assert_called_once_with('echo test', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Test run_command with sudo
    with patch('subprocess.run') as mocked_run:
        with patch('getpass.getpass', return_value='password'):
            run_command('apt update', use_sudo=True)
            mocked_run.assert_called_once_with('echo password | sudo -S apt update', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def test_check_architecture():
    """Test check_architecture function."""
    # Simulate that i386 architecture is not enabled
    with patch('subprocess.run') as mocked_run:
        mocked_run.return_value = subprocess.CompletedProcess(args='dpkg --print-foreign-architectures', returncode=0, stdout='')
        with patch('install_steam.run_command') as mocked_run_command:
            check_architecture()
            mocked_run.assert_called_once_with('dpkg --print-foreign-architectures', shell=True, text=True, stdout=subprocess.PIPE)
            mocked_run_command.assert_called_once_with('dpkg --add-architecture i386', use_sudo=True)

def test_update_sources_list():
    """Test update_sources_list function."""
    # Mock open function to simulate sources.list file content
    mock_open_obj = mock_open(read_data="deb http://deb.debian.org/debian/ stable main")
    
    with patch('builtins.open', mock_open_obj):
        update_sources_list()
        
        # Verificar que la función open sea llamada tanto para lectura ('r') como para escritura ('w')
        mock_open_obj.assert_any_call('/etc/apt/sources.list', 'r')
        mock_open_obj.assert_any_call('/etc/apt/sources.list', 'w')

def test_install_steam():
    """Test install_steam function."""
    with patch('install_steam.run_command') as mocked_run_command:
        with patch('os.remove') as mocked_remove:
            install_steam()
            mocked_run_command.assert_any_call('wget https://cdn.akamai.steamstatic.com/client/installer/steam.deb -O steam.deb')
            mocked_run_command.assert_any_call('dpkg -i steam.deb', use_sudo=True)
            mocked_run_command.assert_any_call('apt --fix-broken install -y', use_sudo=True)
            mocked_remove.assert_called_once_with('steam.deb')

