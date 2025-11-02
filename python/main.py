# Python code
from src.dati import RobotController
from src.wifi import Wifi
from src.api import Api

wifi = Wifi(1 / 15)

dati = RobotController(wifi)

api = Api(dati)
api.ReportAngles()
api.polling()
