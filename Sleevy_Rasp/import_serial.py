import serial
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time

EMG_values = []
MOY = []
  # Ouvrir le port série (remplacez '/dev/ttyUSB0' par le bon port)
ser = serial.Serial('/dev/ttyACM0', 9600)  # Assurez-vous que le baud rate correspond à celui défini dans votre code Arduino
count = 0
ping = 0

duree_max = 40
temps_debut = time.time()

def function1 () :
    try:
        while True:
            # Lire une ligne de données série
            line = ser.readline().decode().strip()
            #print("Données reçues:", line)
            a = int(line)
            EMG_values.append(a)
            
            if len(EMG_values) < 5 :
                print('Erreur')
            
            if len(EMG_values) >= 5 :
                Last_values = EMG_values[-5:]
                somme = sum(Last_values)
                moyenne = somme/len(Last_values)
                MOY.append(moyenne)
                
                Last = EMG_values[-1]

                if Last < moyenne :
                    ping += 1
                    print(ping)
                
                    if ping == 10 :
                        print ('Fatigue detectee')
                else :
                    ping = 0

                temps_ecoule =  time.time() - temps_debut
                if temps_ecoule >= duree_max :
                    plt.plot(EMG_values, color = 'b')
                    plt.plot(MOY, color = 'r')
                    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    EMG = f"EMG : {timestamp}.png"
                    plt.savefig(EMG)
                    plt.show()
                    break

                #if temps_ecoule > duree_max :
                    #ser.close()

    except KeyboardInterrupt:
        # Fermer le port série lorsqu'on interrompt le programme
        ser.close()

def function2 () :
    try:
        while True:
            # Lire une ligne de données série
            line = ser.readline().decode().strip()
            #print("Données reçues:", line)
            a = int(line)
            EMG_values.append(a)
            print(EMG_values)

            somme = sum(EMG_values)
            moyenne = somme/len(EMG_values)
            
            pourcent = 0.1*moyenne

            inf = moyenne - pourcent
            sup = moyenne + pourcent

            #print(moyenne)

            
            
    except KeyboardInterrupt:
        # Fermer le port série lorsqu'on interrompt le programme
        ser.close()
        print(moyenne)
        print(inf)
        print(sup)
        plt.plot(EMG_values, color = 'b')
        plt.axhline(moyenne, color = 'r')
        plt.axhline(inf, color = 'r')
        plt.axhline(sup, color = 'r')
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        EMG = f"EMG : {timestamp}.png"
        plt.savefig(EMG)
        plt.show()

def function3 () :
    moyenne = 441
    inf = 397
    sup = 485
    count = 0
    ping = 0
    try:
        while True:
            # Lire une ligne de données série
            line = ser.readline().decode().strip()
            #print("Données reçues:", line)
            a = int(line)
            EMG_values.append(a)
            print(EMG_values)
            ping += 1

            if ping == 100:
                moy = sum(EMG_values)/len(EMG_values)
                if moy < moyenne :
                    count += 1
                    print(count)
                    ping == 0
        

    except KeyboardInterrupt:
        ser.close()
        plt.plot(EMG_values, color = 'b')
        plt.axhline(moyenne, color = 'r')
        plt.axhline(moy, color = 'g')
        plt.show()
            




if __name__ == '__main__':
    function2()