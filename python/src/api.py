import os, threading

class Api:
    """
        Questa classe è un'interfaccia da stdin per le seguenti operazioni:

        set angolo
        set pos
        set orn
        set feet pos
        set wrot
        set speed
        cammina
        gira
        ferma
        connetti
        disconnetti
        reset
        sync
    """

    def parseInput(self, n, input):
        if input is None:
            raise Exception("[parseInput] error parsing the input")
        words = input.split()
        words.pop(0)
        if len(words) == n: return words 
        else: raise Exception("[parseInput] error parsing the input")

    def sendImage(self, array):
        if self.image_fd is None:
            return
        if not isinstance(array, bytearray):
            print("[api.sendImage] array deve essere di tipo bytearray")
            return
        if len(array) == 0:
            print("[api.sendImage] array non deve essere vuoto")
            return
        imgSize = len(array)
        self.image_fd.write(str(imgSize).encode()+b'S')
        self.image_fd.write(array)
        self.image_fd.flush()
    
    def __init__(self, dati):
        try:
            self.UIRead = os.fdopen(3, "r").readline
            self.UIWrite = os.fdopen(4, "w", 1).write
            self.image_fd = os.fdopen(4, "wb")
        except:
            self.UIRead = input
            self.UIWrite = print
            self.image_fd = None
            print("UI connection failed")
        self.dati = dati
        self.cmds =     ["setang",    "setpos",    "setorn",    "walk",    "turn",    "disconnect",    "connect",    
                         "getang",     "stop",    "reset",    "sync", "setwrot", "setspeed", "setfeetpos", "setrecord"]
        self.handlers = [self.SetAngolo, self.SetPos, self.SetOrn, self.Walk, self.Turn, self.Disconnect, self.Connect,
                         self.GetAng, self.Stop, self.Reset, self.ReportAngles, self.SetWRot, self.SetSpeed, self.SetFeetPos, self.SetRecord]
        self.thread = None


    def polling(self):
        while(True):
            tmp = self.UIRead()
            self.checkCommand(tmp.rstrip("\n\r"))
    
    def checkCommand(self, tmp):
        for i, cmd in enumerate(self.cmds):
            if cmd in tmp:
                try:
                    self.handlers[i](tmp)
                except Exception as e:
                    print("Error in", cmd, e)
                return
        print("invalid command: "+tmp)

    # input expected: 'setang [n] [angle]'
    def SetAngolo(self, input):
        try: n, angle = self.parseInput(2, input)
        except: return
        self.dati.SetAngolo(int(n), int(angle))
        self.ReportAngles()

    # input expected: 'setpos [n] [value]'
    def SetPos(self, input):
        try: n, value = self.parseInput(2, input)
        except: return
        self.dati.SetPos(int(n), float(value))
        self.ReportAngles()

    # input expected: 'setorn [n] [value]'
    def SetOrn(self, input):
        try: n, value = self.parseInput(2, input)
        except: return
        self.dati.SetOrn(int(n), int(value))
        self.ReportAngles()

    def Walk(self, input):
        try:
            angle = self.parseInput(1, input)
            if not angle[0].isdigit(): return
            self.dati.SetAngle(int(angle[0]))
            self.ReportAngles()
        except:
            if self.thread is not None: self.thread.join()
            self.thread = threading.Thread(target=self.dati.Cammina, args=(self.ReportAngles,))
            self.thread.start()
            

    def Turn(self, input):
        if self.thread is not None: self.thread.join()
        self.thread = threading.Thread(target=self.dati.Gira, args=(self.ReportAngles,))
        self.thread.start()

    # input expected: 'connect [ip] [port]'
    def Connect(self, input):
        try: ip, port = self.parseInput(2, input)
        except: return
        if self.dati.wifi.Connetti(ip, int(port)):
            self.UIWrite("Connesso\n\r")

    def Disconnect(self, input):
        if self.dati.wifi.Disconnetti():
            self.UIWrite("Disconnesso\n\r")

    def GetAng(self, input):
        pass

    def ReportAngles(self, input=""):
        angles = self.dati.GetAngoli()
        string = "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}"
        string = string.format(int(angles[0]), int(angles[1]), int(angles[2]), 
                               int(angles[3]), int(angles[4]), int(angles[5]),
                               int(angles[6]), int(angles[7]), int(angles[8]),
                               int(angles[9]), int(angles[10]), int(angles[11]))
        self.UIWrite("Angoli: "+string+"\n\r")

    def Stop(self, input):
        self.dati.Ferma()
        self.ReportAngles()

    def Reset(self, input):
        self.dati.Reset()
        self.ReportAngles()

    def SetWRot(self, input):
        try: value = self.parseInput(1, input)[0]
        except: return
        max_angle = 35
        max_wrot = 1.
        scaled = int(value) * max_wrot/max_angle
        self.dati.SetWRot(scaled)

    def SetSpeed(self, input):
        min_speed = 0.2
        max_speed = 0.8
        scale = self.parseInput(1, input)[0]
        speed = min_speed + (max_speed - min_speed ) * float(scale)
        self.dati.SetSpeed(float(speed))

    def SetFeetPos(self, input):
        try: x, z, feet = self.parseInput(3, input)
        except: return
        self.dati.SetFeetPos([float(x), float(z)], feet)
        self.ReportAngles()

    def SetRecord(self, input):
        try: value = self.parseInput(1, input)[0]
        except: return
        record = bool(value)
        self.dati.SetRecord(record)