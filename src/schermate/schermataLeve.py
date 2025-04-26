import tkinter


class SchermataLeve:
    def __init__(self, root, dati, x0, larghezza, altezza):
        self.root = root
        self.tela = root.tela
        self.dati = dati
        self.altezza = altezza
        self.x0 = x0
        self.larghezza = larghezza
        self.distanza = larghezza / 6
        self.r = 5
        self.xTesto = self.x0 + 15
        self.y_half = altezza / 2
        self.yTesto2 = altezza - 30
        self.yMargine1 = altezza - 65
        self.yTesto1= self.y_half - 30
        self.yMargine2 = self.y_half - 65

    def Mouse(self, event):
        xM = event.x - self.x0
        nColonne = 6
        for colonna in range(0, nColonne):
            if xM > colonna * self.distanza and xM < (colonna + 1) * self.distanza:
                if(event.y >= 0 and event.y <= self.yMargine2):
                    self.dati.SetAng(colonna, self.yToAng(colonna, event.y))
                    self.root.Aggiorna()
                    break
                elif(event.y >= self.y_half and event.y <= self.yMargine1):
                    self.dati.SetAng(colonna + 6, self.yToAng(colonna + 6, event.y))
                    self.root.Aggiorna()
                    break

    def yToAng(self, n, yMouse):
        # print(n)
        if n < 6:
            ang_base = yMouse / self.yMargine2
        else:
            ang_base = ((yMouse - (self.y_half)) / (self.yMargine1 - (self.y_half)))
        if n % 3 == 0:
            return ang_base * 180
        elif n % 3 - 1 == 0:
            return - ang_base * 135
        else:
            return 90 - ang_base * 180

    def AngToY(self, n, ang):
        if n < 6:
            y0 = 0
            y1 = self.yMargine2
            limite = self.yMargine2
        else:
            y0 = self.y_half
            y1 = self.yMargine1
            limite = self.yMargine1 - self.y_half
        if n % 3 == 0:
            return y0 + ang / 180 * limite
        elif n % 3 - 1 == 0:
            return y0 - ang / 135 * limite
        elif n % 3 - 2 == 0:
            return y1 - (ang + 90) / 180 * limite

    def Disegna(self):
        for i in range(0, 6):
            offsetcolonna = self.x0 + (self.distanza * i) + (self.distanza / 2)
            y_sopra = self.AngToY(i, self.dati.angles[i])
            y_sotto = self.AngToY(i + 6, self.dati.angles[i + 6])
            self.puntatori[i] = self.tela.create_oval(offsetcolonna - self.r, y_sopra - self.r, 
                                                      offsetcolonna + self.r, y_sopra + self.r)
            self.puntatori[i + 6] = self.tela.create_oval(offsetcolonna - self.r, y_sotto - self.r, 
                                                          offsetcolonna + self.r, y_sotto + self.r)
            self.text[i] = self.tela.create_text(
                self.xTesto + self.distanza * i, self.yTesto1, text=str(int(self.dati.angles[i])))
            self.text[i + 6] = self.tela.create_text(
                self.xTesto + self.distanza * i, self.yTesto2, text=str(int(self.dati.angles[i + 6])))

    def Elimina(self):
        for i in range(0, 12):
            self.tela.delete(self.text[i])
            self.tela.delete(self.puntatori[i])

    def Crea(self):
        self.linee = [None, None, None, None, None, None, None]
        for i in range(0, 7):
            offset = self.x0 + self.distanza * i
            self.linee[i] = self.tela.create_line(offset, 0, offset, self.altezza, width=3)
            
        self.margineBasso = self.tela.create_line(0, self.yMargine1, self.larghezza, self.yMargine1, width=3)
        
        self.puntatori = [None, None, None, None, None, None, None, None, None, None, None, None]
        self.text = [None, None, None, None, None, None, None, None, None, None, None, None]
        self.Disegna()


