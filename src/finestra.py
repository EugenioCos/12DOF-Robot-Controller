import tkinter as tk
import time
from src.schermate.schermata1 import SchermataLeve
from src.schermate.schermata2 import SchermataLato
from src.schermate.schermata3 import SchermataAlto


class Finestra:
    def __init__(self, larghezza, altezza, wifi, portaDefault, dati):
        self.dati = dati
        self.portaDefault = portaDefault
        self.altezza = altezza
        self.larghezza = larghezza
        self.wifi = wifi

    def MouseReleased(self, event):
        self.schermataLato.MouseReleased(event, self.schermataLeve)

    def Mouse(self, event):
        if event.x < self.larghezza / 3:
            self.schermataLato.Mouse(event)
            self.schermataLeve.Disegna()
        elif event.x < self.larghezza / 3 * 2:
            self.schermataLeve.Mouse(event)
            self.schermataLato.Disegna()
        else:
            self.schermataAlto.Mouse(event)
            self.schermataAlto.Disegna()
        # time.sleep(1/50)

    def Tasto(self, entryText):
        if self.wifi.connesso:
            self.wifi.Invia(entryText.get())
            entryText.set("")

    def TastoScreen(self, varTastoScreen):
        if varTastoScreen.get() == "Connetti":
            self.wifi.Avvia()
            if self.wifi.connesso:
                varTastoScreen.set("Disconnetti")
        else:
            self.wifi.Disconnetti()
            varTastoScreen.set("Connetti")

    def Termina(self):
        self.dati.Termina()
        self.screen.destroy()

    def creaFinestra(self, dati):
        # Finestra
        self.screen = tk.Tk()
        dimensioni = str(self.larghezza) + str("x") + str(self.altezza)
        self.screen.geometry(dimensioni)
        self.screen.resizable(False, False)
        self.screen.protocol("WM_DELETE_WINDOW", self.Termina)
#       # Variabili
        entryText = tk.StringVar()
        entryText.set(self.portaDefault)
        varTasto = tk.StringVar()
        varTasto.set("Invia")
        varTastoScreen = tk.StringVar()
        varTastoScreen.set("Connetti")
        self.screen.rowconfigure(1, weight=1)
#       # Entry
        entry = tk.Entry(self.screen, textvar=entryText,
                         width=60, justify=tk.CENTER)
        entry.grid(row=0, column=0, sticky=tk.EW)
#       # Tasto
        tasto = tk.Button(self.screen, textvar=varTasto,
                          command=lambda: self.Tasto(entryText))
        tasto.grid(row=0, column=1, sticky=tk.EW)
#       # TastoScreen
        tastoScreen = tk.Button(self.screen, textvar=varTastoScreen,
                                command=lambda: self.TastoScreen(varTastoScreen))
        tastoScreen.grid(row=0, column=2, sticky=tk.EW)
#       # Canvas
        self.tela = tk.Canvas(
            self.screen, width=self.larghezza, bd=0, highlightthickness=0)
        self.tela.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)
        self.tela.bind('<B1-Motion>', self.Mouse)
        self.tela.bind('<Button-1>', self.MouseReleased)

        self.screen.update()
#       # Schermate
        self.larghezzaTela = self.tela.winfo_width()
        self.altezzaTela = self.tela.winfo_height()
        width = self.larghezzaTela / 3
        self.schermataLeve = SchermataLeve(self.tela, dati, self.wifi, width, width, self.altezzaTela) # ... x0, larghezza, altezza)
        self.schermataLato = SchermataLato(self.tela, dati, self.wifi, width, self.altezzaTela) # ... larghezza, altezza)
        self.schermataAlto = SchermataAlto(self.tela, dati, tk.ARC, width * 2, width, self.altezzaTela) # ... x0, larghezza, altezza)
        self.schermataLeve.Crea()
        self.schermataLato.Crea()
        self.schermataAlto.Crea()

        self.screen.mainloop()
