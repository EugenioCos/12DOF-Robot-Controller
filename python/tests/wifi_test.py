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

@pytest.fixture
def wifi_for_comunica(mocker):
    wifi = Wifi(intervallo=1.0)
    wifi.mock_AngToCmd = mocker.patch('src.wifi.Wifi.AngToCmd', return_value = "cmd1")
    wifi.mock_Invia = mocker.patch('src.wifi.Wifi.Invia', return_value = None)
    wifi.mock_RiceviImg = mocker.patch('src.wifi.Wifi.RiceviImg', return_value = "img_data")
    wifi.mock_RiceviRisposta = mocker.patch('src.wifi.Wifi.RiceviRisposta', return_value = "response")
    wifi.mock_checkGyro = mocker.patch('src.wifi.Wifi.checkGyro', return_value = {"gyro": 123})
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

def test_disconnetti_disconnesso(wifi_connected):
    """#controllato"""
    wifi_connected.connesso = False
    assert wifi_connected.Disconnetti() == False

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

def test_comunica_not_connected(wifi_for_comunica):
    wifi_for_comunica.connesso = False
    result = wifi_for_comunica.Comunica(angoli=[0, 0, 0], withImg=False, resetDisplay=True)
    wifi_for_comunica.mock_AngToCmd.assert_not_called()
    wifi_for_comunica.mock_Invia.assert_not_called()
    wifi_for_comunica.mock_RiceviImg.assert_not_called()
    wifi_for_comunica.mock_RiceviRisposta.assert_not_called()
    wifi_for_comunica.mock_checkGyro.assert_not_called()
    assert result is None

def test_comunica_connected_no_img(wifi_for_comunica):
    wifi_for_comunica.connesso = True
    result = wifi_for_comunica.Comunica(angoli=[0, 0, 0], withImg=False, resetDisplay=True)
    wifi_for_comunica.AngToCmd.assert_called_once_with([0, 0, 0], False, True)
    wifi_for_comunica.Invia.assert_called_once_with("cmd1")
    wifi_for_comunica.RiceviImg.assert_not_called()
    wifi_for_comunica.RiceviRisposta.assert_called_once()
    wifi_for_comunica.checkGyro.assert_called_once_with("response")
    assert result == {"gyro": 123}

def test_comunica_connected_with_img(wifi_for_comunica):
    wifi_for_comunica.connesso = True
    result = wifi_for_comunica.Comunica(angoli=[0, 0, 0], withImg=True, resetDisplay=True)
    wifi_for_comunica.AngToCmd.assert_called_once_with([0, 0, 0], True, True)
    wifi_for_comunica.Invia.assert_called_once_with("cmd1")
    wifi_for_comunica.RiceviImg.assert_called_once()
    wifi_for_comunica.RiceviRisposta.assert_called_once()
    wifi_for_comunica.checkGyro.assert_called_once_with("response")
    assert result == {"gyro": 123}

def test_ricevi_img_success(wifi_connected, mocker):
    wifi_connected.s.recv.side_effect = [b'fakeIm', b'ageDataa']  # Simulate receiving image data
    mock_RiceviImgSize = mocker.patch('src.wifi.Wifi.RiceviImgSize', return_value = 14)
    mock_sendImage = mocker.patch('src.api.Api.sendImage')

    # Instantiate the class
    wifi_connected.RiceviImg(mock_sendImage)
    mock_RiceviImgSize.assert_called_once()
    wifi_connected.s.recv.assert_any_call(14)
    wifi_connected.s.recv.assert_any_call(8)
    mock_sendImage.assert_called_once_with(b'fakeImageDataa', 14)

def test_ricevi_img_exception(wifi_connected, mocker):
    wifi_connected.s.recv.side_effect = Exception("Connection error")
    mock_RiceviImgSize = mocker.patch('src.wifi.Wifi.RiceviImgSize', return_value = 14)
    mock_sendImage = mocker.patch('src.api.Api.sendImage')

    # Instantiate the class
    assert wifi_connected.RiceviImg(sendImage=mock_sendImage) == None
    mock_sendImage.assert_not_called()
    assert wifi_connected.s.recv.called