import numpy as np
import math


class SchermataLato:
    def __init__(self, tela, dati, wifi, larghezza, altezza):
        self.dati = dati
        self.tela = tela
        self.wifi = wifi
        self.altezza = altezza
        self.larghezza = larghezza
        #
        self.lato = 60
        self.yMargineBasso = altezza - 65
        self.yTesto = self.yMargineBasso + 35
        self.XTesto = 35
        self.coord = [[larghezza / 5, 30],
                      self.CalcolaFemur([larghezza / 5, 30], dati.angles[1]),
                      self.CalcolaTibia(self.CalcolaFemur(
                          [larghezza / 5, 30], dati.angles[1]), dati.angles[1], dati.angles[2]),
                      [larghezza / 5 * 4, 30],
                      self.CalcolaFemur(
                          [larghezza / 5 * 4, 30], dati.angles[4]),
                      self.CalcolaTibia(self.CalcolaFemur(
                          [larghezza / 5 * 4, 30], dati.angles[4]), dati.angles[4], dati.angles[5]),
                      [larghezza / 5, 30 + altezza / 2],
                      self.CalcolaFemur(
                          [larghezza / 5, 30 + altezza / 2], dati.angles[1]),
                      self.CalcolaTibia(self.CalcolaFemur(
                          [larghezza / 5, 30 + altezza / 2], dati.angles[1]), dati.angles[1], dati.angles[2]),
                      [larghezza / 5 * 4, 30 + altezza / 2],
                      self.CalcolaFemur(
                          [larghezza / 5 * 4, 30 + altezza / 2], dati.angles[4]),
                      self.CalcolaTibia(self.CalcolaFemur([larghezza / 5 * 4, 30 + altezza / 2], dati.angles[4]), dati.angles[4], dati.angles[5])]

    def Elabora(self, x, y):
        x1 = x - self.coord[0][0]
        y1 = y - self.coord[0][1]
        if y1 > 0:
            if(math.sqrt((x1 ** 2) + (y1 ** 2)) < (self.lato * 2)):
                self.dati.SetPos(self.MouseToM(x1, y1), "FL")
                return True
        x1 = x - self.coord[3][0]
        y1 = y - self.coord[3][1]
        if(y1 > 0):
            if(math.sqrt((x1 ** 2) + (y1 ** 2)) < (self.lato * 2)):
                self.dati.SetPos(self.MouseToM(x1, y1), "BL")
                return True
        x1 = x - self.coord[6][0]
        y1 = y - self.coord[6][1]
        if y1 > 0:
            if(math.sqrt((x1 ** 2) + (y1 ** 2)) < (self.lato * 2)):
                self.dati.SetPos(self.MouseToM(x1, y1), "FR")
                return True
        x1 = x - self.coord[9][0]
        y1 = y - self.coord[9][1]
        if(y1 > 0):
            if(math.sqrt((x1 ** 2) + (y1 ** 2)) < (self.lato * 2)):
                self.dati.SetPos(self.MouseToM(x1, y1), "BR")
                return True

    def AggiornaCoord(self):
        self.coord[1] = self.CalcolaFemur(self.coord[0], self.dati.angles[7])
        self.coord[2] = self.CalcolaTibia(
            self.coord[1], self.dati.angles[7], self.dati.angles[8])
        self.coord[4] = self.CalcolaFemur(self.coord[3], self.dati.angles[10])
        self.coord[5] = self.CalcolaTibia(
            self.coord[4], self.dati.angles[10], self.dati.angles[11])
        self.coord[7] = self.CalcolaFemur(self.coord[6], self.dati.angles[1])
        self.coord[8] = self.CalcolaTibia(
            self.coord[7], self.dati.angles[1], self.dati.angles[2])
        self.coord[10] = self.CalcolaFemur(self.coord[9], self.dati.angles[4])
        self.coord[11] = self.CalcolaTibia(
            self.coord[10], self.dati.angles[4], self.dati.angles[5])

    def MouseToM(self, x, y):
        newX = float(x / (self.lato * 10))
        newY = float(y / (self.lato * 10))
        return [newX, newY]

    def CalcolaFemur(self, coordZero, angle1):
        x = coordZero[0] + np.sin(np.deg2rad(angle1)) * self.lato
        y = coordZero[1] + np.cos(np.deg2rad(angle1)) * self.lato
        return [x, y]

    def CalcolaTibia(self, startCoord, angle1, angle2):
        ang = (-90 + angle1) + angle2
        x = startCoord[0] + self.lato * np.cos(np.deg2rad(ang))
        y = startCoord[1] - self.lato * np.sin(np.deg2rad(ang))
        return [x, y]

    def MouseReleased(self, event, schermata1):
        if event.y > self.yMargineBasso and event.x < 100:
            print("Cammina")
            self.dati.Cammina(self, schermata1)  # V, angle, Wrot
        if event.y > self.yMargineBasso and event.x > 100 and event.x < 200:
            self.dati.Ferma()
        if event.y > self.yMargineBasso and event.x > 200:
            print("Cammina")
            self.dati.Gira(self, schermata1)  # V, angle, Wrot

    def Mouse(self, event):
        # print(event.y)
        if(self.Elabora(event.x, event.y)):
            self.AggiornaCoord()
            self.wifi.Comunica(self.dati.angles)
            self.Disegna()

    def Elimina(self):
        self.tela.delete(self.femur1)
        self.tela.delete(self.tibia1)
        self.tela.delete(self.femur2)
        self.tela.delete(self.tibia2)
        self.tela.delete(self.femur3)
        self.tela.delete(self.tibia3)
        self.tela.delete(self.femur4)
        self.tela.delete(self.tibia4)

    def Disegna(self):
        self.Elimina()
        self.AggiornaCoord()
        self.femur1 = self.tela.create_line(
            self.coord[0], self.coord[1], width=3)
        self.tibia1 = self.tela.create_line(
            self.coord[1], self.coord[2], width=3)
        self.femur2 = self.tela.create_line(
            self.coord[3], self.coord[4], width=3)
        self.tibia2 = self.tela.create_line(
            self.coord[4], self.coord[5], width=3)
        self.femur3 = self.tela.create_line(
            self.coord[6], self.coord[7], width=3)
        self.tibia3 = self.tela.create_line(
            self.coord[7], self.coord[8], width=3)
        self.femur4 = self.tela.create_line(
            self.coord[9], self.coord[10], width=3)
        self.tibia4 = self.tela.create_line(
            self.coord[10], self.coord[11], width=3)
        self.tela.update()

    def Cancella(self):
        self.Elimina()
        self.tela.delete(self.margineBasso)

    def Crea(self):
        self.margineBasso = self.tela.create_line(
            0, self.yMargineBasso, self.larghezza, self.yMargineBasso, width=3)
        self.AggiornaCoord()
        self.femur1 = self.tela.create_line(
            self.coord[0], self.coord[1], width=3)
        self.tibia1 = self.tela.create_line(
            self.coord[1], self.coord[2], width=3)
        self.femur2 = self.tela.create_line(
            self.coord[3], self.coord[4], width=3)
        self.tibia2 = self.tela.create_line(
            self.coord[4], self.coord[5], width=3)
        self.femur3 = self.tela.create_line(
            self.coord[6], self.coord[7], width=3)
        self.tibia3 = self.tela.create_line(
            self.coord[7], self.coord[8], width=3)
        self.femur4 = self.tela.create_line(
            self.coord[9], self.coord[10], width=3)
        self.tibia4 = self.tela.create_line(
            self.coord[10], self.coord[11], width=3)
        self.tasto1 = self.tela.create_text(
            35, self.yTesto, text=str("Cammina"))
        self.tasto2 = self.tela.create_text(
            100 + 35, self.yTesto, text=str("Fermati"))
        self.tasto2 = self.tela.create_text(
            200 + 35, self.yTesto, text=str("Gira"))
#       #self.tela.update()
