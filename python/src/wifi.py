import socket
import time
import numpy as np

# Questa classe permette le seguenti operazioni:
# - connessione
# - disconnessione
# - invio
# - ricezione
# - invio degli angoli e ricezione dei dati del giroscopio

class Wifi:
    def __init__(self, intervallo, sendImage):
        self.connesso = False
        self.intervallo = intervallo
        self.lastTime = time.time()
        self.sendImage = sendImage
        self.imgSize = 42240

    def Connetti(self, ip, port):
        try:
            self.s = socket.socket()
            self.s.settimeout(3)
            self.s.connect((ip, port))
        except socket.error as exc:
            print("Server non creato: ", exc)
            self.connesso = False
            return
        self.connesso = True
        print("Connesso")
    
    def Disconnetti(self):
        if not self.connesso: return
        print("disconnesso")
        self.s.close()
        self.connesso = False

    def Invia(self, out):
        #print("Sending... "+out)
        try:
            return self.s.send(out.encode())
        except:
            print("[Wifi] Invio Fallito")
            self.Disconnetti()

    def Ricevi(self):
        try:
            return self.s.recv(1024).decode("utf-8").rstrip('\n\r')
        except ConnectionResetError:
            self.Disconnetti()
        except socket.timeout:
            self.Disconnetti()
        return None
    
    def RiceviImg(self):
        received = 0
        chunk_size = 4096
        array_from_client = bytearray()
        while received < self.imgSize:
            try:
                to_recv = self.imgSize - received if self.imgSize - received < chunk_size else chunk_size
                data = self.s.recv(to_recv)
            except Exception as e: 
                print(e)
                return
            received += len(data)
            array_from_client.extend(data)
        self.sendImage(array_from_client)

    def Comunica(self, angoli, withImg):
        if not self.connesso: return
        while(time.time() - self.lastTime < self.intervallo):
            time.sleep(self.intervallo/20)
        self.lastTime = time.time()

        command = self.AngToCmd(angoli, withImg)
        self.Invia(command)
        if(withImg): self.RiceviImg()
        risposta = self.RiceviRisposta()
        gyroData = self.checkGyro(risposta)
        return gyroData

    def RiceviRisposta(self):
        risposta = ""
        while '>' not in risposta:
            tmp = self.Ricevi()
            if tmp == None: break
            else: risposta += tmp
        return risposta
        #print(str(risposta))

    def checkGyro(self, risposta):
        if risposta != None and '#' in risposta:
            risposta = risposta[1:-1]
            dati = [float(tmp) for tmp in risposta.split('#')]
            if len(dati) == 2:
                return dati
            print("[Wifi] Parsing data error, data: "+str(dati))
        return None
    
    def AngToCmd(self, angles, withImg):
        pulse = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for i in range(0, 12):
            pulse[i] = angles[i] 
            pulse[i] *= (-1 if (i-2)%3==0 else 1)
            pulse[i] = self.AngToPls(pulse[i])
        # Input
        comando = "<{0}#{1}#{2}#{3}#{4}#{5}#{6}#{7}#{8}#{9}#{10}#{11}" + ("P" if withImg else ">")
        return comando.format(int(pulse[0]), int(pulse[1]), int(pulse[2]),
                                 int(pulse[3]), int(pulse[4]), int(pulse[5]),
                                 int(pulse[6]), int(pulse[7]), int(pulse[8]),
                                 int(pulse[9]), int(pulse[10]), int(pulse[11]))

    def AngToPls(self, angle):
        return 500 + int((float(angle / 9) * 100))
