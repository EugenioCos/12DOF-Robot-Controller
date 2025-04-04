import socket
import time


class Wifi:
    def __init__(self, intervallo):
        self.connesso = False
        self.intervallo = intervallo
        self.lastTime = time.time()

    def Avvia(self):
        try:
            self.s = socket.socket()
            self.s.settimeout(3)
            self.s.connect(('192.168.4.1', 80))
        except socket.error as exc:
            print("Server non creato: ", exc)
            return "Errore"
        self.connesso = True
        print("Connesso")

    def Invia(self, out):
        while(time.time() - self.lastTime < self.intervallo): # Invio
            pass
        self.lastTime = time.time()
        print("Sending... "+out)
        try:
            self.s.send(out.encode())
        except:
            print("[Wifi] Invio Fallito")
            return None
        
        risposta = self.Ricevi() # Ricezione risposta
        if risposta == None: return None
        while '>' not in risposta:
            if (time.time() >= self.lastTime + 3):
                self.Disconnetti()
                break
            tmp = self.Ricevi()
            if tmp != None: risposta += tmp
            else: return None
        print(str(risposta))
        # Ricavare dalla risposta i valori di accelerazioni (se mpu attivo)
            
        if '#' in risposta:
            risposta = risposta[1:-1]
            print("cutted: "+risposta)
            risposta.split('#');
            dati = []
            for dato in risposta:
                dati.append(float(dato))
            if len(dati) != 2:
                print("[Wifi] Parsing data error, data: "+str(dati))
            return dati
        else: return None

    def Disconnetti(self):
        print("disconnesso")
        self.s.close()
        self.connesso = False

    def Ricevi(self):
        try:
            return self.s.recv(1024).decode("utf-8").rstrip('\n\r')
        except ConnectionResetError:
            print("Non connesso")
            return None
        except socket.timeout:
            print("Nessuna Risposta")
            return None

    def Comunica(self, angoli):
        pulse = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if not self.connesso: return
        for i in range(0, 12):
            pulse[i] = angoli[i]
        pulse[2] = -pulse[2]
        pulse[5] = -pulse[5]
        pulse[8] = -pulse[8]
        pulse[11] = -pulse[11]
        for i in range(0, 12):
            pulse[i] = self.AngToPls(pulse[i])
        # Input
        comando = "<{0}#{1}#{2}#{3}#{4}#{5}#{6}#{7}#{8}#{9}#{10}#{11}>"
        command = comando.format(int(pulse[0]), int(pulse[1]), int(pulse[2]),
                                 int(pulse[3]), int(pulse[4]), int(pulse[5]),
                                 int(pulse[6]), int(pulse[7]), int(pulse[8]),
                                 int(pulse[9]), int(pulse[10]), int(pulse[11]))
        return self.Invia(command)

    def AngToPls(self, angle):
        return 500 + int((float(angle / 9) * 100))
