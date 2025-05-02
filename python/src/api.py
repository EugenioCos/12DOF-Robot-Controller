import threading

class Api:

    def __init__(self, dati):
        self.dati = dati
        self.cmds =     ["setang",    "setpos",    "setorn",    "walk",    "turn",    "connect",    "disconnect",    
                         "getang",     "stop",    "reset",    "sync"]
        self.handlers = [self.SetAng, self.SetPos, self.SetOrn, self.Walk, self.Turn, self.Connect, self.Disconnect,
                         self.GetAng, self.Stop, self.Reset, self.Sync]
        self.x = None


    def polling(self):
        while(True):
            tmp = input()
            self.checkCommand(tmp)
    
    def checkCommand(self, tmp):
        for i, cmd in enumerate(self.cmds):
            if cmd in tmp:
                try:
                    self.handlers[i](tmp)
                    print(" End", flush=True)
                except Exception as e:
                    print("Error in handler:", e)
                return
        print("[Python] invalid command: "+tmp)

    # input expected: 'setang [n] [angle]'
    def SetAng(self, input):
        words = input.split()
        if len(words) != 3:
            print("Invalid input")
            return
        n = int(words[1])
        angle = int(words[2])
        self.dati.SetAng(n, angle)
        self.ReportAngles()

    # input expected: 'setpos [n] [value]'
    def SetPos(self, input):
        words = input.split()
        if len(words) != 3:
            print("Invalid input")
            return
        n = int(words[1])
        value = float(words[2])
        self.dati.SetPos(n, value)
        self.ReportAngles()

    # input expected: 'setorn [n] [value]'
    def SetOrn(self, input):
        words = input.split()
        if len(words) != 3:
            print("Invalid input")
            return
        n = int(words[1])
        value = float(words[2])
        self.dati.SetOrn(n, value)
        self.ReportAngles()

    def Walk(self, input):
        if self.x is not None: self.x.join()
        self.x = threading.Thread(target=self.dati.Cammina, args=(self.Sync,))
        self.x.start()

    def Turn(self, input):
        self.dati.Gira(self.Sync)

    # input expected: 'connect [ip] [port]'
    def Connect(self, input):
        words = input.split()
        if len(words) != 3:
            print("Invalid input")
            return
        ip = words[1]
        port = int(words[2])
        self.dati.wifi.Avvia(ip, port)

    def Disconnect(self, input):
        self.dati.wifi.Disconnetti()

    def GetAng(self, input):
        pass

    def ReportAngles(self):
        angles = self.dati.GetAngles()
        string = "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} "
        string = string.format(int(angles[0]), int(angles[1]), int(angles[2]), 
                               int(angles[3]), int(angles[4]), int(angles[5]),
                               int(angles[6]), int(angles[7]), int(angles[8]),
                               int(angles[9]), int(angles[10]), int(angles[11]))
        print("Angoli: "+string, flush=True)

    def Stop(self, input):
        self.dati.Ferma()
        self.Sync()

    def Reset(self, input):
        self.dati.Reset()
        self.Sync()

    def Sync(self, input=""):
        self.ReportAngles()
# Operazioni:
"""
Setting angolo
Setting pos
Setting orn
cammina
gira
ferma
connetti
disconnetti

Getter angoli
"""

    