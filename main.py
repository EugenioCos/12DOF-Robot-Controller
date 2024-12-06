from src.dati import Robot
from src.wifi import Wifi
from src.finestra import Finestra

# Seriale
# /dev/cu.usbserial-0001   /dev/cu.usbmodem14101
portaDefault = '<1500#500#1500#1500#500#1500#1500#500#1500#1500#500#1500>'
wifi = Wifi(1 / 30)

# Dati Robot
dati = Robot(wifi)

# Finestra
altezza = 600
larghezza = 1100

finestra = Finestra(larghezza, altezza, wifi, portaDefault, dati)
finestra.creaFinestra(dati)
