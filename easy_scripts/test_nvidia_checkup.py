import pytest
import subprocess
import os
from unittest.mock import patch, mock_open
from nvidia_checkup import is_root, run_with_sudo, check_nvidia, blacklist_nouveau, setup_logging

@pytest.fixture
def mock_sudo_password():
    return "test_password"

def test_is_root():
    """Test is_root function."""
    with patch('os.geteuid', return_value=0):
        assert is_root() == True

    with patch('os.geteuid', return_value=1000):
        assert is_root() == False

@patch('subprocess.run')
def test_run_with_sudo(mock_subproc_run, mock_sudo_password):
    """Test run_with_sudo function."""
    mock_subproc_run.return_value = subprocess.CompletedProcess(args=['sudo'], returncode=0, stdout='success', stderr='')

    result = run_with_sudo('ls', mock_sudo_password)
    assert result == 'success'

    # Simulate error case
    mock_subproc_run.side_effect = subprocess.CalledProcessError(1, 'sudo', 'error')
    with pytest.raises(SystemExit):
        run_with_sudo('ls', mock_sudo_password)

@patch('subprocess.run')
def test_check_nvidia(mock_subproc_run):
    """Test check_nvidia function."""
    mock_subproc_run.return_value = subprocess.CompletedProcess(args=['lspci'], returncode=0, stdout='NVIDIA', stderr='')

    assert check_nvidia() == True

    mock_subproc_run.return_value = subprocess.CompletedProcess(args=['lspci'], returncode=0, stdout='', stderr='')

    assert check_nvidia() == False

@patch('builtins.open', new_callable=mock_open)
@patch('os.path.exists', return_value=False)
@patch('nvidia_checkup.run_with_sudo')
def test_blacklist_nouveau(mock_run_with_sudo, mock_exists, mock_open_file, mock_sudo_password):
    """Test blacklist_nouveau function."""
    mock_run_with_sudo.return_value = ""

    # Mock input to automatically provide 'y' response
    with patch('builtins.input', return_value='y'):
        blacklist_nouveau(mock_sudo_password)
        mock_run_with_sudo.assert_any_call('echo "\nblacklist nouveau\noptions nouveau modeset=0\n" | sudo tee /etc/modprobe.d/blacklist-nouveau.conf', mock_sudo_password)
        mock_run_with_sudo.assert_any_call('update-initramfs -u', mock_sudo_password)

@patch('os.path.exists', return_value=True)
@patch('nvidia_checkup.run_with_sudo')
def test_blacklist_nouveau_existing_file(mock_run_with_sudo, mock_exists, mock_sudo_password):
    """Test blacklist_nouveau function when file already exists."""
    with patch('builtins.input', return_value='n'):
        blacklist_nouveau(mock_sudo_password)
        mock_run_with_sudo.assert_not_called()

def test_setup_logging():
    """Test setup_logging function."""
    with patch('os.path.basename', return_value='nvidia_checkup.py'), \
         patch('os.path.expanduser', return_value='/home/user/nvidia_checkup.log'), \
         patch('logging.basicConfig') as mock_logging:
        setup_logging()
        mock_logging.assert_called_once()

