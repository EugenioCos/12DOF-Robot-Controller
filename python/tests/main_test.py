import pytest

def test_main_script(mocker):
    # Mock delle classi importate
    mock_wifi = mocker.patch("src.wifi.Wifi")
    mock_robot = mocker.patch("src.dati.RobotController")
    mock_api = mocker.patch("src.api.Api")

    import main

    # ✅ Verifica che Wifi sia istanziato con 1/15
    mock_wifi.assert_called_once_with(pytest.approx(1 / 15))

    # ✅ Verifica che RobotController riceva il wifi mockato
    mock_robot.assert_called_once_with(mock_wifi.return_value)

    # ✅ Verifica che Api riceva il controller mockato
    mock_api.assert_called_once_with(mock_robot.return_value)

    # ✅ Verifica che ReportAngles() e polling() vengano chiamati
    api_instance = mock_api.return_value
    api_instance.ReportAngles.assert_called_once()
    api_instance.polling.assert_called_once()
