import pytest
from src.api import Api

@pytest.fixture
def api(mocker):
    mock_UIRead = mocker.Mock()
    mock_UIWrite = mocker.Mock()
    mock_fd_image = mocker.Mock()
    mock_TextIOWrapper = mocker.patch('io.TextIOWrapper')
    mock_TextIOWrapper.readline = mock_UIRead
    mock_TextIOWrapper.write = mock_UIWrite
    mocker.patch('os.fdopen', side_effect = [mock_TextIOWrapper, mock_TextIOWrapper, mock_fd_image])
    mock_dati = mocker.Mock()
    api = Api(mock_dati)
    return api

def test_init_with_ui(mocker):
    mock_UIRead = mocker.Mock()
    mock_UIWrite = mocker.Mock()
    mock_fd_image = mocker.Mock()
    mock_TextIOWrapper = mocker.patch('io.TextIOWrapper')
    mock_TextIOWrapper.readline = mock_UIRead
    mock_TextIOWrapper.write = mock_UIWrite
    mocker.patch('os.fdopen', side_effect = [mock_TextIOWrapper, mock_TextIOWrapper, mock_fd_image])
    mock_dati = mocker.Mock()
    api = Api(mock_dati)
    assert api.UIRead == mock_UIRead
    assert api.UIWrite == mock_UIWrite
    assert api.image_fd == mock_fd_image
    assert api.dati == mock_dati
    assert api.thread == None

def test_init_without_ui(mocker):
    mocker.patch('os.fdopen', side_effect = [Exception()])
    mock_dati = mocker.Mock()
    api = Api(mock_dati)
    assert api.image_fd == None
    assert api.UIRead == input
    assert api.UIWrite == print
    assert api.dati == mock_dati
    assert api.thread == None

@pytest.mark.parametrize("n, input, expected", [
    (1, "cmd uno due", Exception()),
    (2, "cmd uno due", ["uno", "due"]),
    (None, "cmd uno due", Exception()),
    (1, None, Exception()),
])
def test_parseInput(api, mocker, n, input, expected):
    mock_print = mocker.patch("builtins.print")
    if isinstance(expected, Exception): 
        with pytest.raises(Exception):
            api.parseInput(n, input)
    else: assert api.parseInput(n, input) == expected
    if input is None: mock_print.assert_called_once()
    else: mock_print.assert_not_called()

def test_sendImage_no_fd_image(api, mocker):
    mock_print = mocker.patch("builtins.print")
    api.image_fd = None
    api.sendImage(b'to_write')
    mock_print.assert_not_called()

@pytest.mark.parametrize("array, calls, print", [
    (bytearray(b'to_write'), [b'8S', b'to_write'], False),
    (bytearray(b''), [], True),
    (b'to_write', [], True)
])
def test_sendImage(api, mocker, array, calls, print):
    mock_print = mocker.patch("builtins.print")
    api.sendImage(array)
    if print: mock_print.assert_called_once()
    else: mock_print.assert_not_called()
    if len(calls) == 0:
        api.image_fd.write.assert_not_called()
    else:
        for arg in calls:
            api.image_fd.write.assert_any_call(arg)
        api.image_fd.flush.assert_called_once()

def test_polling(api, mocker):
    api.UIRead.side_effect = ["Hello", "world", Exception()]
    mock_checkCommand = mocker.patch('src.api.Api.checkCommand')
    try: api.polling()
    except: pass
    assert api.UIRead.call_count == 3
    mock_checkCommand.assert_any_call("Hello")
    mock_checkCommand.assert_any_call("world")

@pytest.mark.parametrize("cmd, exp_calls_counts, exp_print, side", [
    ("cmd1", [1, 0], '', [None]),
    ("cmd2", [0, 1], '', [None]),
    ("invalid", [0, 0], 'invalid command: invalid\n', [None]),
    ("cmd1", [1, 0], 'Error in cmd1 \n', [Exception()]),
    ("cmd2", [0, 1], 'Error in cmd2 \n', [Exception()]),
])
def test_checkCommand(api, mocker, capsys, cmd, exp_calls_counts, exp_print, side):
    api.cmds=['cmd1', 'cmd2'] 
    api.handlers = [mocker.MagicMock(side_effect=side), mocker.MagicMock(side_effect=side)]
    api.checkCommand(cmd)
    for i, handler in enumerate(api.handlers):
        assert handler.call_count == exp_calls_counts[i]
    assert capsys.readouterr().out == exp_print

@pytest.mark.parametrize("input, exp_call_count", [
    ('setpos 3 45', 1),
    ('setpos 3', 0),
])
def test_setAngolo(api, mocker, input, exp_call_count):
    api.dati.SetAngolo.return_value = None
    mock_reportAngles = mocker.patch('src.api.Api.ReportAngles')
    api.SetAngolo(input)
    assert api.dati.SetAngolo.call_count == exp_call_count
    assert mock_reportAngles.call_count == exp_call_count

@pytest.mark.parametrize("input, exp_call_count", [
    ('setpos 3 45', 1),
    ('setpos 3', 0),
])
def test_setPos(api, mocker, input, exp_call_count):
    api.dati.SetPos.return_value = None
    mock_reportAngles = mocker.patch('src.api.Api.ReportAngles')
    api.SetPos(input)
    assert api.dati.SetPos.call_count == exp_call_count
    assert mock_reportAngles.call_count == exp_call_count

@pytest.mark.parametrize("input, exp_call_count", [
    ('setpos 3 45', 1),
    ('setpos 3', 0),
])
def test_setOrn(api, mocker, input, exp_call_count):
    api.dati.SetOrn.return_value = None
    mock_reportAngles = mocker.patch('src.api.Api.ReportAngles')
    api.SetOrn(input)
    assert api.dati.SetOrn.call_count == exp_call_count
    assert mock_reportAngles.call_count == exp_call_count

@pytest.mark.parametrize("return_connetti, exp_UIWrite", [
    (True, 'Connesso\n\r'),
    (False, False),
])
def test_connetti_fail(api, return_connetti, exp_UIWrite):
    api.dati.wifi.Connetti.return_value = return_connetti
    api.Connect("connect 192.168.1.1 80")
    api.dati.wifi.Connetti.assert_called_once_with("192.168.1.1", 80)
    if exp_UIWrite: api.UIWrite.assert_called_once_with(exp_UIWrite)
    else: api.UIWrite.assert_not_called()

def test_connetti_success(api):
    api.dati.Connect.return_value = None
    api.Connect("connect ip")
    api.dati.Connect.assert_not_called()

@pytest.mark.parametrize("connesso, exp_UIWrite", [
    (True, 'Disconnesso\n\r'),
    (False, False),
])
def test_disconnetti(api, connesso, exp_UIWrite):
    api.dati.wifi.Disconnetti.return_value = connesso
    api.Disconnect("")
    api.dati.wifi.Disconnetti.assert_called_once()
    if exp_UIWrite: api.UIWrite.assert_called_once_with(exp_UIWrite)
    else: api.UIWrite.assert_not_called()

def test_reportAngles(api):
    api.dati.GetAngoli.return_value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    api.ReportAngles()
    api.UIWrite.assert_called_once_with("Angoli: 1 2 3 4 5 6 7 8 9 10 11 12\n\r")

def test_stop(api, mocker):
    api.dati.Ferma.return_value = None
    mock_reportAngles = mocker.patch('src.api.Api.ReportAngles')
    api.Stop("")
    api.dati.Ferma.assert_called_once()
    mock_reportAngles.assert_called_once()

def test_reset(api, mocker):
    api.dati.Reset.return_value = None
    mock_reportAngles = mocker.patch('src.api.Api.ReportAngles')
    api.Reset("")
    api.dati.Reset.assert_called_once()
    mock_reportAngles.assert_called_once()

def test_setWRot_invalid(api):
    api.dati.SetWRot.return_value = None
    api.SetWRot("invalid")
    api.dati.SetWRot.assert_not_called()

@pytest.mark.parametrize("input, expected", [
    ("setwrot 35", 1.),
    ("setwrot 7", 0.2),
])
def test_setWRot(api, input, expected):
    api.dati.SetWRot.return_value = None
    api.SetWRot(input)
    api.dati.SetWRot.assert_called_once_with(expected)

@pytest.mark.parametrize("input, expected", [
    ("setspeed 0", 0.2),
    ("setspeed 0.5", 0.5),
    ("setspeed 1", 0.8),
])
def test_setSpeed(api, input, expected):
    api.dati.SetSpeed.return_value = None
    api.SetSpeed(input)
    api.dati.SetSpeed.assert_called_once_with(expected)

def test_setFeetPos_invalid(api, mocker):
    api.dati.SetFeetPos.return_value = None
    mock_reportAngles = mocker.patch('src.api.Api.ReportAngles')
    api.SetFeetPos("invalid 1 2")
    api.dati.SetFeetPos.assert_not_called()
    mock_reportAngles.assert_not_called()

def test_setFeetPos_success(api, mocker):
    api.dati.SetFeetPos.return_value = None
    mock_reportAngles = mocker.patch('src.api.Api.ReportAngles')
    api.SetFeetPos("setfeetpos 1 2 FR")
    api.dati.SetFeetPos.assert_called_once_with([1.0, 2.0], "FR")
    mock_reportAngles.assert_called_once()

def test_setRecord_invalid(api):
    api.dati.SetRecord.return_value = None
    api.SetRecord("invalid")
    api.dati.SetRecord.assert_not_called()

@pytest.mark.parametrize("input, expected", [
    ("setrecord 1", True),
    ("setrecord true", True),
    ("setrecord 0", False),
    ("setrecord false", False),
])
def test_setRecord_success(api, input, expected):
    assert bool(0) == False
    api.dati.SetRecord.return_value = None
    api.SetRecord(input)
    api.dati.SetRecord.assert_called_with(expected)
