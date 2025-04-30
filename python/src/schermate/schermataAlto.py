import math
import tkinter as tk

class SchermataAlto:
    def __init__(self, root, dati, x0, larghezza, altezza):
        self.dati = dati
        self.tela = root.tela
        self.altezza = altezza
        self.larghezza = larghezza
        self.x0 = x0
        #
        self.lato = 30
        self.xCorpo = x0 + (larghezza / 2)
        self.yCorpo = altezza / 3
        self.coord = [self.xCorpo - 100, self.altezza / 3 * 2,
                      self.xCorpo + 100, self.altezza / 3 * 2 + 100]
        self.direzione = 0
        self.AngWrot = 0

    def CoordFreccia(self):
        x = self.xCorpo + self.lato * \
            math.sin(math.radians((self.direzione))) * 4
        y = self.yCorpo - self.lato * \
            math.cos(math.radians(self.direzione)) * 4
        return self.xCorpo, self.yCorpo, x, y

    def SetWrot(self):
        if self.AngWrot in range(-60, 60):
            maxWrot = 1.0
            Wrot = (self.AngWrot * maxWrot) / 60.0
            if(Wrot <= 0.35 and Wrot >= -0.35):
                Wrot = 0
                self.AngWrot = 0
                self.dati.Wrot = 0
            else:
                self.dati.Wrot = Wrot
            self.tela.delete(self.puntatore)
            self.puntatore = self.tela.create_arc(
                self.coord, start=-(self.AngWrot-90)-5, extent=10, width=6, style=tk.ARC)

    def CalcolaDirezione(self, event):
        x = event.x - self.xCorpo
        y = self.yCorpo - event.y
        if x == 0:
            x = 1
        if y == 0:
            y = 1
        if(event.y < self.yCorpo):
            self.direzione = math.degrees(math.atan(float(x / y)))
        else:
            self.direzione = 180 - math.degrees(math.atan(float(x / (-y))))
        #print(self.direzione)
        if self.dati.angle != int(self.direzione):
            self.dati.angle = int(self.direzione)

    def CalcolaWrot(self, event):
        x = event.x - self.xCorpo
        y = (self.altezza / 3 * 2 + 50) - event.y + 30
        if x == 0:
            x = 1
        if y == 0:
            y = 1
        if(event.y < (self.altezza / 3 * 2 + 50 + 30)):
            self.AngWrot = int(math.degrees(math.atan(float(x / y))))
        else:
            self.AngWrot = 180 - int(math.degrees(math.atan(float(x / (-y)))))
        self.SetWrot()

    def Mouse(self, event):
        if(event.x in range(int(self.coord[0]), int(self.coord[2]))
           and event.y in range(int(self.coord[1]), int(self.coord[3]))):
            self.CalcolaWrot(event)
        else:
            self.CalcolaDirezione(event)

    def Elimina(self):
        self.tela.delete(self.freccia)

    def Disegna(self):
        self.Elimina()
        self.freccia = self.tela.create_line(self.CoordFreccia(), width=4)

    def Crea(self):
        self.tela.create_rectangle(self.xCorpo - self.lato, self.yCorpo - (2 * self.lato),
                                   self.xCorpo + self.lato, self.yCorpo + (2 * self.lato), width=3)
        self.tela.create_arc(self.coord, start=20, extent=140,
                             width=2, style=tk.ARC)
        self.puntatore = self.tela.create_arc(
            self.coord, start=85, extent=10, width=6, style=tk.ARC)
        self.freccia = self.tela.create_line(self.CoordFreccia(), width=4)
