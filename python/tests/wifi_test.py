import pytest
import socket
import time

from src.wifi import Wifi


@pytest.fixture
def wifi():
    return Wifi(intervallo=1.0)

@pytest.fixture
def wifi_connected(mocker):
    wifi = Wifi(intervallo=1.0)
    mock_conn = mocker.patch('socket.socket').return_value
    wifi.s = mock_conn
    wifi.connesso = True
    return wifi

def test_connetti_success(wifi, mocker):
    """#controllato"""
    mock_conn = mocker.patch('socket.socket').return_value
    assert wifi.Connetti("127.0.0.1", 1234)
    mock_conn.connect.assert_called_once_with(("127.0.0.1", 1234))
    assert wifi.connesso

def test_connetti_fallimento(wifi, mocker, capsys):
    """#controllato"""
    mock_conn = mocker.patch('socket.socket').return_value
    mock_conn.connect.side_effect = socket.error("error msg")
    assert not wifi.Connetti("127.0.0.1", 1234)
    assert not wifi.connesso
    assert "Server non creato:  error msg" in capsys.readouterr().out

def test_disconnetti(wifi_connected):
    """#controllato"""
    assert wifi_connected.Disconnetti()
    wifi_connected.s.close.assert_called_once()
    assert not wifi_connected.connesso

def test_invia_success(wifi_connected):
    """# controllato"""
    wifi_connected.s.send.return_value = 4
    assert wifi_connected.Invia("test") == 4
    wifi_connected.s.send.assert_called_once_with("test".encode())

def test_invia_fail(wifi_connected, capsys):
    """# controllato"""
    wifi_connected.s.send.side_effect = ConnectionResetError()
    wifi_connected.Invia("test")
    assert "[Wifi] Invio Fallito" in capsys.readouterr().out
    assert not wifi_connected.connesso

def test_ricevi_success(wifi_connected):
    """#controllato"""
    wifi_connected.s.recv.return_value = b"dati"
    assert wifi_connected.Ricevi() == "dati"

def test_ricevi_ConnReset_fail(wifi_connected):
    """#controllato"""
    wifi_connected.s.recv.side_effect = ConnectionResetError()
    assert wifi_connected.Ricevi() is None
    assert not wifi_connected.connesso

def test_ricevi_timeout_fail(wifi_connected):
    """#controllato"""
    wifi_connected.s.recv.side_effect = socket.timeout()
    assert wifi_connected.Ricevi() is None
    assert not wifi_connected.connesso

@pytest.mark.parametrize("side_eff, exp_res, exp_calls", [
    (["some", ">", "data"], "some>", 2), # success 1
    (["some>", "data"], "some>", 1), # success 2
    ([None], "", 1), # disconnesso
    (["partial", None], "partial", 2) # ricevuto e disconnesso
])
def test_riceviRisposta(wifi_connected, mocker, side_eff, exp_res, exp_calls):
    """Test when Ricevi returns a string with '>'"""
    mock_recv = mocker.patch('src.wifi.Wifi.Ricevi', side_effect=side_eff)
    assert wifi_connected.RiceviRisposta() == exp_res
    assert mock_recv.call_count == exp_calls

@pytest.mark.parametrize("mock_recv, expected_size", [
    ([b"S"], 0),  # Only S received
    ([b"1", b"2", b"3", b"S"], 123),  # Valid size
    ([b"a", b"1", b"2", b"S"], 0),  # Invalid data
    ([b"1", b"2" b"S", b"1"], 0),  # data after S ignored
])
def test_RiceviImgSize_success(wifi_connected, mock_recv, expected_size):
    wifi_connected.s.recv.side_effect = mock_recv
    assert wifi_connected.RiceviImgSize() == expected_size

@pytest.mark.parametrize("mock_recv", [
    (ConnectionResetError()),
    (socket.timeout())
])
def test_RiceviImgSize_fail(wifi_connected, mocker, mock_recv):
    wifi_connected.s.recv.side_effect = mock_recv
    mock_disconnetti = mocker.patch('src.wifi.Wifi.Disconnetti', return_value=None)
    assert wifi_connected.RiceviImgSize() == 0
    assert mock_disconnetti.call_count == 1

def test_check_gyro(wifi):
    """#controllato"""
    assert wifi.checkGyro("<123#456>") == [123.0, 456.0]
    assert wifi.checkGyro("non_valid") is None
    assert wifi.checkGyro("<123#456#789>") is None
    assert wifi.checkGyro("<123#456#789>") is None

def test_ang_to_cmd(wifi):
    """#controllato"""
    angles = [90.0] * 12
    comando = wifi.AngToCmd(angles, withImg=False, resetDisplay=False)
    assert comando == "<1500#1500#-500#1500#1500#-500#1500#1500#-500#1500#1500#-500>"
    comando = wifi.AngToCmd(angles, withImg=True, resetDisplay=False)
    assert comando == "<1500#1500#-500#1500#1500#-500#1500#1500#-500#1500#1500#-500P"
    comando = wifi.AngToCmd(angles, withImg=True, resetDisplay=True)
    assert comando == "<1500#1500#-500#1500#1500#-500#1500#1500#-500#1500#1500#-500RP"
    comando = wifi.AngToCmd(angles, withImg=False, resetDisplay=True)
    assert comando == "<1500#1500#-500#1500#1500#-500#1500#1500#-500#1500#1500#-500R>"