# Python code
from src.dati import RobotController
from src.wifi import Wifi
from src.api import Api
import os

try:
    image_fd = os.fdopen(3, "wb")
except:
    print("UI connection failed")
    exit()

def sendImage(array, imgSize):
    image_fd.write(str(imgSize).encode()+b'S')
    image_fd.write(array)
    image_fd.flush()

wifi = Wifi(1 / 15, sendImage)

dati = RobotController(wifi)

api = Api(dati)
api.ReportAngles()
api.polling()
