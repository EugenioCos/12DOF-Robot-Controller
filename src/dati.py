import math
import time
import numpy as np
from src.modello.gaitPlanner import trotGait
from src.modello.kinematic_model import robotKinematics


class Robot:
    def __init__(self, wifi):
        self.wifi = wifi
        self.kinematics = robotKinematics()
        self.planner = trotGait()
        "initial foot position"
        # Ydist = 0.18 distanza tra i piedi lateralmente
        # Xdist = 0.25 distanza tra i piedi in lunghezza
        height = 0.16  # 0.16
        # distanza tra il centro del corpo e i piedi (0.08/-0.11 , -0.07 , -height)
        self.bodytoFeet1 = self.bodytoFeet0 = np.matrix([[0.09, -0.07, -height],  # FR posizione
                                      [0.09, 0.07, -height],   # FL iniziale
                                      [-0.125, -0.07, -height],   # BR dei passi
                                      [-0.125, 0.07, -height]])  # senza orn e senza pos
        self.orn = np.array([0., 0., 0.]) # pitch roll e yatch
        self.pos = np.array([0., 0., 0.]) # spostamenti xyz

        self.girando = False
        self.camminando = False
        self.tPlanner = 2  # period of time (in seconds) of every step
        self.angle = 0  # 0. direzione (0. avanti)
        self.Wrot = 0  # 0. rotazione (0. fermo)
        self.offsetPlanner = np.array([0., 0.5, 0.5, 0.]) #offset di inizio del movimento tra i passi
        self.angles = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.accXY = None # None | [accX, accY]
        self.Aggiorna()

    def Termina(self):
        print("Terminato")
        self.planner.phi = 1.
        self.Ferma()

    def Ferma(self):
        print("Fermo")
        self.girando = False
        self.camminando = False

    # Calcola nuovi angoli a partire dalle coordinate
    def Aggiorna(self):
        radsFR, radsFL, radsBR, radsBL, bodyToFeet = self.kinematics.solve(
            self.orn, self.pos, self.bodytoFeet1)
        for i in range(0, 3):
            self.angles[i] = np.rad2deg(radsFR[i])
            self.angles[i + 3] = np.rad2deg(radsFL[i])
            self.angles[i + 6] = np.rad2deg(radsBR[i])
            self.angles[i + 9] = np.rad2deg(radsBL[i])

    # fa camminare il robot
    def Cammina(self, root):
        self.camminando = True
        V = 0.35  # 0.5 velocità di movimento
        # il ciclo si interrompe solo se il passo è completo
        while self.camminando or (self.planner.phi < 0.99 and not (self.planner.phi > 0.499 and self.planner.phi < 0.51)):
            
            # Xacc e Yacc è l'accelerazione ricavata dall'mpu e compliant è un valore true o false (in accXY)
            # se compliantMode == False i valori calcolati sono tali da non alterare nulla (la stabilizzazione non avviene)
            # forceModule , forceAngle , Vcompliant , collision = control.bodyCompliant(Xacc , Yacc , True)
            # self.bodytoFeet1  = trot.loop(V + Vcompliant , self.angle + forceAngle , 0, self.tplanner, self.offsetplanner , bodytoFeet0)
            
            # print(self.planner.phi)
            # wrot = 0 in quanto il cammino non considera la rotazione
            self.bodytoFeet1 = self.planner.loop(V, self.angle, 0, self.tPlanner, self.offsetPlanner, self.bodytoFeet0)
            self.Aggiorna()
            self.accXY = self.wifi.Comunica(self.angles)
            root.Aggiorna()

    # fa girare il robot
    def Gira(self, root):
        self.girando = True
        print(self.Wrot)
        # il ciclo si interrompe solo se il passo è completo
        while self.girando or (self.planner.phi < 0.99 and not (self.planner.phi > 0.499 and self.planner.phi < 0.51)):
            self.bodytoFeet1 = self.planner.loop(0, 0, self.Wrot, self.tPlanner*3, self.offsetPlanner, self.bodytoFeet0)
            self.Aggiorna()
            self.accXY = self.wifi.Comunica(self.angles)
            root.Aggiorna()

    # Imposta un angolo (utilizzato da vista leve)
    def SetAng(self, n, angolo):
        self.angles[n] = int(angolo)
        if n in range(0, 3):
            self.bodytoFeet1[0] = self.bodytoFeet0[0] = self.kinematics.calcolaPiede("FR", self.angles[0:3])
        if n in range(3, 6):
            self.bodytoFeet1[1] = self.bodytoFeet0[1] = self.kinematics.calcolaPiede("FL", self.angles[3:6])
        if n in range(6, 9):
            self.bodytoFeet1[2] = self.bodytoFeet0[2] = self.kinematics.calcolaPiede("BR", self.angles[6:9])
        if n in range(9, 12):
            self.bodytoFeet1[3] = self.bodytoFeet0[3] = self.kinematics.calcolaPiede("BL", self.angles[9:12])
        self.wifi.Comunica(self.angles)

    # Imposta nuove coordinare (utilizzato da vista Lato)
    def SetPos(self, newXZ, feet):
        if "FR" in feet:
            self.bodytoFeet1[0, 0] = self.bodytoFeet0[0, 0] = self.kinematics.L / 2 - newXZ[0]
            self.bodytoFeet1[0, 2] = self.bodytoFeet0[0, 2] = -newXZ[1]
        if "FL" in feet:
            self.bodytoFeet1[1, 0] = self.bodytoFeet0[1, 0] = self.kinematics.L / 2 - newXZ[0]
            self.bodytoFeet1[1, 2] = self.bodytoFeet0[1, 2] = -newXZ[1]
        if "BR" in feet:
            self.bodytoFeet1[2, 0] = self.bodytoFeet0[2, 0] = -self.kinematics.L / 2 - newXZ[0]
            self.bodytoFeet1[2, 2] = self.bodytoFeet0[2, 2] = -newXZ[1]
        if "BL" in feet:
            self.bodytoFeet1[3, 0] = self.bodytoFeet0[3, 0] = -self.kinematics.L / 2 - newXZ[0]
            self.bodytoFeet1[3, 2] = self.bodytoFeet0[3, 2] = -newXZ[1]
        self.Aggiorna()
        self.accXY = self.wifi.Comunica(self.angles)
