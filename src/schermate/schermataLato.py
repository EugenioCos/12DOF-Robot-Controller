import numpy as np
import math

class SchermataLato:
    def __init__(self, root, dati, larghezza, altezza):
        self.dati = dati
        self.tela = root.tela
        self.root = root
        self.altezza = altezza
        self.larghezza = larghezza
        #
        self.lato = 60
        self.yMargineBasso = altezza - 65
        self.yTesto = self.yMargineBasso + 35
        self.XTesto = 35
        self.coord = [[larghezza / 5, 30], [0, 0], [0, 0], # FR: zero, femur, tibia
                      [larghezza / 5, 30 + altezza / 3], [0, 0], [0,0], # FL: zero, femur, tibia
                      [larghezza / 5 * 4, 30], [0, 0], [0,0], # BR: zero, femur, tibia
                      [larghezza / 5 * 4, 30 + altezza / 3], [0, 0], [0,0]] # BL: zero, femur, tibia
        self.AggiornaCoord()

    def MouseReleased(self, event):
        if event.y > self.yMargineBasso and event.x < 100:
            print("Cammina")
            self.dati.Cammina(self.root)  # V, angle, Wrot
        if event.y > self.yMargineBasso and event.x > 100 and event.x < 200:
            self.dati.Ferma()
        if event.y > self.yMargineBasso and event.x > 200:
            print("Cammina")
            self.dati.Gira(self.root)  # V, angle, Wrot

    def Mouse(self, event):
        x = event.x
        y = event.y
        # print(event.y)
        if (self.ElaboraZampa(x - self.coord[0][0], y - self.coord[0][1], "FR") or \
            self.ElaboraZampa(x - self.coord[3][0], y - self.coord[3][1], "FL") or \
            self.ElaboraZampa(x - self.coord[6][0], y - self.coord[6][1], "BR") or \
            self.ElaboraZampa(x - self.coord[9][0], y - self.coord[9][1], "BL")):
            self.root.Aggiorna()    

    def ElaboraZampa(self, x1, y1, zampa):
        if(y1 > 0):
            if(math.sqrt((x1 ** 2) + (y1 ** 2)) < (self.lato * 2)):
                self.dati.SetPos(self.MouseToM(x1, y1), zampa)
                return True
        return False

    def AggiornaCoord(self):
        for i in range(1, 12, 3):
            self.coord[i] = self.CalcolaFemur(self.coord[i-1], self.dati.angles[i])
            self.coord[i+1] = self.CalcolaTibia(self.coord[i], self.dati.angles[i], self.dati.angles[i+1])

    def MouseToM(self, x, y):
        newX = float(x / (self.lato * 10))
        newY = float(y / (self.lato * 10))
        return [newX, newY]

    def CalcolaFemur(self, coordZero, angle1):
        x = coordZero[0] + np.sin(np.deg2rad(angle1)) * self.lato
        y = coordZero[1] + np.cos(np.deg2rad(angle1)) * self.lato
        return [x, y]

    def CalcolaTibia(self, startCoord, angle1, angle2):
        ang = -90 + angle1 + angle2
        x = startCoord[0] + self.lato * np.cos(np.deg2rad(ang))
        y = startCoord[1] - self.lato * np.sin(np.deg2rad(ang))
        return [x, y]

    def Elimina(self):
        for femur in self.femurs:
            self.tela.delete(femur)

    def Disegna(self):
        self.AggiornaCoord()
        cood_indexes = [1, 2, 4, 5, 7, 8, 10, 11]
        for i, ndx in enumerate(cood_indexes):
            self.femurs[i] = self.tela.create_line(self.coord[ndx-1], self.coord[ndx], width=3)

    def Crea(self):
        self.femurs = [None, None, None, None, None, None, None, None]
        self.margineBasso = self.tela.create_line(0, self.yMargineBasso, self.larghezza, self.yMargineBasso, width=3)
        self.Disegna()
        for i in range(0, 12, 3):
            corner1 = (self.coord[i][0]-10, self.coord[i][1]-8)
            corner2 = (self.coord[i][0]+25, self.coord[i][1]+10)
            self.tela.create_rectangle(corner1[0], corner1[1], corner2[0], corner2[1], width=3)
            
        self.tasto1 = self.tela.create_text(35, self.yTesto, text=str("Cammina"))
        self.tasto2 = self.tela.create_text(100 + 35, self.yTesto, text=str("Fermati"))
        self.tasto3 = self.tela.create_text(200 + 35, self.yTesto, text=str("Gira"))
