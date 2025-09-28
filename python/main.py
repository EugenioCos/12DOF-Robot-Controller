# Python code
from src.dati import RobotController
from src.wifi import Wifi
from src.api import Api
import os

image_fd = os.fdopen(3, "wb")

def sendImage(array):
    image_fd.write(array)
    image_fd.flush()

wifi = Wifi(1 / 15, sendImage)

dati = RobotController(wifi)

api = Api(dati)
api.ReportAngles()
api.polling()
