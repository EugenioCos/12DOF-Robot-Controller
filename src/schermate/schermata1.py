import tkinter


class SchermataLeve:
    def __init__(self, tela, dati, wifi, x0, larghezza, altezza):
        self.tela = tela
        self.dati = dati
        self.wifi = wifi
        self.altezza = altezza
        self.x0 = x0
        self.larghezza = larghezza
        self.distanza = larghezza / 6
        self.r = 5
        self.yMargine1 = altezza - 65
        self.yTesto1 = self.yMargine1 + 35
        self.yMargine2 = (altezza / 2) - 65
        self.yTesto2 = self.yMargine2 + 35
        self.xTesto = self.x0 + 35

    def Mouse(self, event):
        xM = event.x - self.x0
        nColonne = 6
        for colonna in range(0, nColonne):
            if xM > colonna * self.distanza and xM < (colonna + 1) * self.distanza:
                if(event.y >= 0 and event.y <= self.yMargine2):
                    self.dati.SetAng(colonna + 6, self.yToAng(colonna, event.y))
                    self.wifi.Comunica(self.dati.angles)
                if(event.y >= self.altezza / 2 and event.y <= self.yMargine1):
                    self.dati.SetAng(colonna, self.yToAng(colonna + 6, event.y))
                    self.wifi.Comunica(self.dati.angles)
        self.Disegna()

    def yToAng(self, n, yMouse):
        # print(n)
        if n < 6:
            if n == 0 or n == 3:
                return (yMouse / self.yMargine2) * 180
            elif n == 2 or n == 5:
                return - (yMouse / self.yMargine2) * 135
            else:
                return 90 - (yMouse / self.yMargine2) * 180
        else:
            if n == 6 or n == 9:
                return ((yMouse - (self.altezza / 2)) / (self.yMargine1 - (self.altezza / 2))) * 180
            elif n == 8 or n == 11:
                return - ((yMouse - (self.altezza / 2)) / (self.yMargine1 - (self.altezza / 2))) * 135
            else:
                return 90 - ((yMouse - (self.altezza / 2)) / (self.yMargine1 - (self.altezza / 2))) * 180

    def AngToY(self, n, ang):
        if n < 6:
            if n == 0 or n == 3:
                return int(float(ang / 180) * self.yMargine2)
            elif n == 2 or n == 5:
                return - int(float(ang / 135) * self.yMargine2)
            else:
                return self.yMargine2 - int(float((ang + 90) / 180) * self.yMargine2)
        else:
            if n == 6 or n == 9:
                return (self.altezza / 2) + int(float(ang / 180) * (self.yMargine1 - (self.altezza / 2)))
            elif n == 8 or n == 11:
                return (self.altezza / 2) - int(float(ang / 135) * (self.yMargine1 - (self.altezza / 2)))
            else:
                return self.yMargine1 - int(float((ang + 90) / 180) * (self.yMargine1 - (self.altezza / 2)))

    def Disegna(self):
        self.Elimina()
        try:
            for i in range(0, 6):
                offsetcolonna = (self.distanza * i) + (self.distanza / 2)
                self.puntatori[i] = self.tela.create_oval(self.x0 + offsetcolonna - self.r, self.AngToY(
                    i, self.dati.angles[i + 6]) - self.r, self.x0 + offsetcolonna + self.r, self.AngToY(i, self.dati.angles[i + 6]) + self.r)
                self.puntatori[i + 6] = self.tela.create_oval((self.x0 + self.distanza*i+(self.distanza/2))-self.r, self.AngToY(
                    i + 6, self.dati.angles[i]) - self.r, self.x0 + (self.distanza*i+(self.distanza/2))+self.r, self.AngToY(i + 6, self.dati.angles[i])+self.r)
                self.text[i] = self.tela.create_text(
                    self.xTesto + self.distanza * i, self.yTesto1, text=str(int(self.dati.angles[i])))
                self.text[i + 6] = self.tela.create_text(
                    self.xTesto + self.distanza * i, self.yTesto2, text=str(int(self.dati.angles[i + 6])))
        except tkinter.TclError:
            pass
#        #self.tela.update()

    def Elimina(self):
        for i in range(0, 6):
            try:
                self.tela.delete(self.text[i])
                self.tela.delete(self.text[i + 6])
                self.tela.delete(self.puntatori[i])
                self.tela.delete(self.puntatori[i + 6])
            except tkinter.TclError:
                pass

    def Cancella(self):
        self.Elimina()
        self.tela.delete(self.margineBasso)
        for i in range(0, 5):
            self.tela.delete(self.linee[i])

    def Crea(self):
        self.text = [None, None, None, None, None,
                     None, None, None, None, None, None, None]
        for i in range(0, 6):
            self.text[i + 6] = self.tela.create_text(
                self.xTesto + self.distanza * i, self.yTesto2, text=str(int(self.dati.angles[i])))
            self.text[i] = self.tela.create_text(
                self.xTesto + self.distanza * i, self.yTesto1, text=str(int(self.dati.angles[i + 6])))

        self.linee = [None, None, None, None, None, None, None]
        for i in range(1, 7):
            self.linee[i] = self.tela.create_line(
                self.x0 + self.distanza * i, 0, self.x0 + self.distanza * i, self.altezza, width=3)

        self.puntatori = [None, None, None, None, None,
                          None, None, None, None, None, None, None]
        for i in range(0, 6):
            self.puntatori[i] = self.tela.create_oval((self.x0+self.distanza*i+(self.distanza/2))-self.r, self.AngToY(
                i, self.dati.angles[i + 6])-self.r, self.x0+(self.distanza*i+(self.distanza/2))+self.r, self.AngToY(i, self.dati.angles[i + 6])+self.r)
            self.puntatori[i + 6] = self.tela.create_oval((self.x0+self.distanza*i+(self.distanza/2))-self.r, self.AngToY(
                i + 6, self.dati.angles[i])-self.r, self.x0+(self.distanza*i+(self.distanza/2))+self.r, self.AngToY(i + 6, self.dati.angles[i])+self.r)

        self.margineBasso = self.tela.create_line(
                             0, self.yMargine1, self.larghezza, self.yMargine1, width=3)
