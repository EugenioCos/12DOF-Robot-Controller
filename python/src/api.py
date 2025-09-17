import threading

class Api:
    """
        Questa classe è un'interfaccia da stdin per le seguenti operazioni:

        Set angolo
        Set pos
        Set orn
        cammina
        gira
        ferma
        connetti
        disconnetti
        reset
        sync
    """

    def parseInput(self, n, input):
        words = input.split()
        words.pop(0)
        return (words if len(words) == n else None)
    
    def __init__(self, dati):
        self.dati = dati
        self.cmds =     ["setang",    "setpos",    "setorn",    "walk",    "turn",    "disconnect",    "connect",    
                         "getang",     "stop",    "reset",    "sync"]
        self.handlers = [self.SetAngolo, self.SetPos, self.SetOrn, self.Walk, self.Turn, self.Disconnect, self.Connect,
                         self.GetAng, self.Stop, self.Reset, self.Sync]
        self.thread = None


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
                    print("Error in ", cmd, e)
                return
        print("[Python] invalid command: "+tmp)

    # input expected: 'setang [n] [angle]'
    def SetAngolo(self, input):
        n, angle = self.parseInput(2, input)
        self.dati.SetAngolo(int(n), int(angle))

    # input expected: 'setpos [n] [value]'
    def SetPos(self, input):
        n, value = self.parseInput(2, input)
        self.dati.SetPos(int(n), float(value))
        self.ReportAngles()

    # input expected: 'setorn [n] [value]'
    def SetOrn(self, input):
        n, value = self.parseInput(2, input)
        self.dati.SetOrn(int(n), int(value))
        self.ReportAngles()

    def Walk(self, input):
        angle = self.parseInput(1, input)
        if angle == None: # walk
            if self.thread is not None: self.thread.join()
            self.thread = threading.Thread(target=self.dati.Cammina, args=(self.Sync,))
            self.thread.start()
        else: # set direction
            if not angle[0].isdigit(): return
            self.dati.SetAngle(int(angle[0]))
            self.ReportAngles()

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
        self.dati.wifi.Connetti(ip, port)

    def Disconnect(self, input):
        self.dati.wifi.Disconnetti()

    def GetAng(self, input):
        pass

    def ReportAngles(self):
        angles = self.dati.GetAngoli()
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


    