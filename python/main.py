# Python code
from src.dati import Robot
from src.wifi import Wifi
from src.api import Api

wifi = Wifi(1 / 30)

# Dati Robot
dati = Robot(wifi)

api = Api(dati)
api.ReportAngles()
api.polling()
