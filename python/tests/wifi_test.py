import unittest
from unittest.mock import patch, Mock, MagicMock
import socket
import time

from src.wifi import Wifi

class TestWifi(unittest.TestCase):
    def setUp(self):
        self.wifi = Wifi(intervallo=1.0)

    #controllato
    @patch('socket.socket')
    def test_connetti_successo(self, mock_socket):
        mock_conn = Mock()
        mock_socket.return_value = mock_conn
        mock_conn.connect.return_value = None
        self.assertTrue(self.wifi.Connetti("127.0.0.1", 1234))
        mock_conn.connect.assert_called_once_with(("127.0.0.1", 1234))
        self.assertTrue(self.wifi.connesso)

    #controllato
    @patch('builtins.print')
    @patch('socket.socket')
    def test_connetti_fallimento(self, mock_socket, mock_print):
        mock_conn = Mock()
        mock_socket.return_value = mock_conn
        mock_conn.connect.side_effect = socket.error("error msg")
        self.assertFalse(self.wifi.Connetti("127.0.0.1", 1234))
        self.assertFalse(self.wifi.connesso)
        mock_print.assert_called_once_with('Server non creato: ', 'error msg')

    #controllato
    @patch('socket.socket')
    def test_disconnetti(self, mock_socket):
        mock_conn = Mock()
        self.wifi.s = mock_conn
        self.wifi.connesso = True
        self.assertTrue(self.wifi.Disconnetti())
        mock_conn.close.assert_called_once()
        self.assertFalse(self.wifi.connesso)

    # controllato
    @patch('builtins.print')
    @patch('socket.socket')
    def test_invia_success(self, mock_socket, mock_print):
        mock_conn = Mock()
        mock_conn.send.return_value = 4
        self.wifi.s = mock_conn
        self.assertEqual(self.wifi.Invia("test"), 4)
        mock_conn.send.assert_called_once_with("test".encode())

    # controllato
    @patch('builtins.print')
    @patch('socket.socket')
    def test_invia_fail(self, mock_socket, mock_print):
        mock_conn = Mock()
        mock_conn.send.side_effect = ConnectionResetError()
        self.wifi.s = mock_conn
        self.wifi.Invia("test")
        mock_print.assert_called_once_with("[Wifi] Invio Fallito")
        self.assertFalse(self.wifi.connesso)

    # controllato
    @patch('socket.socket')
    def test_ricevi_success(self, mock_socket):
        mock_conn = Mock()
        self.wifi.s = mock_conn
        self.wifi.connesso = True
        mock_conn.recv.return_value = b"dati"
        self.assertEqual(self.wifi.Ricevi(), "dati")

    # controllato  
    @patch('socket.socket')
    def test_ricevi_ConnReset_fail(self, mock_socket):
        mock_conn = Mock()
        mock_conn.recv.side_effect = ConnectionResetError()
        self.wifi.s = mock_conn
        self.wifi.connesso = True
        self.assertIsNone(self.wifi.Ricevi())
        self.assertFalse(self.wifi.connesso)

    # controllato
    @patch('socket.socket')
    def test_ricevi_timeout_fail(self, mock_socket):
        mock_conn = Mock()
        self.wifi.s = mock_conn
        self.wifi.connesso = True
        mock_conn.recv.side_effect = socket.timeout()
        self.assertIsNone(self.wifi.Ricevi())
        self.assertFalse(self.wifi.connesso)

    # controllato
    @patch('builtins.print')
    @patch('socket.socket')
    def test_check_gyro(self, mock_socket, mock_print):
        self.assertEqual(self.wifi.checkGyro("<123#456>"), [123.0, 456.0])
        self.assertIsNone(self.wifi.checkGyro("non_valid"))
        self.assertIsNone(self.wifi.checkGyro("<123#456#789>"))
        mock_print.assert_called_once_with("[Wifi] Parsing data error, data: [123.0, 456.0, 789.0]")

    # controllato
    @patch('socket.socket')
    def test_ang_to_cmd(self, mock_socket):
        angles = [90.0] * 12
        comando = self.wifi.AngToCmd(angles, withImg=False, resetDisplay=False)
        self.assertEqual("<1500#1500#-500#1500#1500#-500#1500#1500#-500#1500#1500#-500>", comando)
        comando = self.wifi.AngToCmd(angles, withImg=True, resetDisplay=False)
        self.assertEqual("<1500#1500#-500#1500#1500#-500#1500#1500#-500#1500#1500#-500P", comando)
        comando = self.wifi.AngToCmd(angles, withImg=True, resetDisplay=True)
        self.assertEqual("<1500#1500#-500#1500#1500#-500#1500#1500#-500#1500#1500#-500RP", comando)
        comando = self.wifi.AngToCmd(angles, withImg=False, resetDisplay=True)
        self.assertEqual("<1500#1500#-500#1500#1500#-500#1500#1500#-500#1500#1500#-500R>", comando)