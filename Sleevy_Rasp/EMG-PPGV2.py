import serial
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time

import time
import max30102
import hrcalc
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import filtfilt, iirfilter, butter, lfilter, wiener, medfilt
from scipy import fftpack
#arange
from scipy.signal import find_peaks
import heartpy as hp
# import pywt
from sklearn.ensemble import IsolationForest

import threading

from multiprocessing import Process

EMG_values = []
MOY = []
  # Ouvrir le port série (remplacez '/dev/ttyUSB0' par le bon port)
ser = serial.Serial('/dev/ttyACM0', 9600)  # Assurez-vous que le baud rate correspond à celui défini dans votre code Arduino
count = 0
ping = 0

duree_max = 40
temps_debut = time.time()

def EMG () :
    start_time=time.time()
    try:
        while True:
            # Lire une ligne de données série
            line = ser.readline().decode().strip()
            #print("Données reçues:", line)
            a = int(line)
            EMG_values.append(a)
            #print(EMG_values)

            somme = sum(EMG_values)
            moyenne = somme/len(EMG_values)
            
            pourcent = 0.1*moyenne

            inf = moyenne - pourcent
            sup = moyenne + pourcent

            #print(moyenne)

            if (time.time()-start_time>=40):
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


def PPG () :
    
    BPM_values = []
    bpm=[]
    bpmt=[]
    BPM_values_liss =[]
    brut_serie=[]
    moy=[]
    temps=[]
    count = 1
    megacount = 0
    ping = 0

    moyenne = 65
    heart_rate_bpm = moyenne
    bpm = moyenne
    bpm2= moyenne
    bpm3=moyenne
    bpm5=moyenne




    def lissage(signal_brut,L):
            res = np.copy(signal_brut) # duplication des valeurs
            for i in range (1,len(signal_brut)-1): # toutes les valeurs sauf la première et la dernière
                L_g = min(i,L) # nombre de valeurs disponibles à gauche
                L_d = min(len(signal_brut)-i-1,L) # nombre de valeurs disponibles à droite
                Li=min(L_g,L_d)
                res[i]=np.sum(signal_brut[i-Li:i+Li+1])/(2*Li+1)
            return res

    def filtrage(data, threshold):
        mean = np.mean(data)
        std_dev = np.std(data)
        filtered_data = [x for x in data if abs(x - mean) < threshold * std_dev]
        return filtered_data

    def filtrage2(BPM_reference) :
        reference_BPM = np.array(BPM_reference)
                    
        if len(reference_BPM.shape) ==1 :
            reference_BPM = reference_BPM.reshape(-1, 1)
        
        outlier_detector = IsolationForest()
        outlier_detector.fit(reference_BPM)
        
        outlier_mask = outlier_detector.predict(reference_BPM) == -1
        
    #                 cleaned_BPM = reference_BPM[~outlier_mask]
    #                 cleaned_BPM_list = [tuple(row) for row in cleaned_BPM]
        cleaned_BPM_list = [data for data, is_outlier in zip(reference_BPM, outlier_mask) if not is_outlier]
        return cleaned_BPM_list

    m = max30102.MAX30102()

    hr2 = 0
    sp2 = 0
    next = 0
    Amorce = 5
    Duree = 5
    Interval = 0.03

    start_time=time.time()

    while True:
        time.sleep(Interval)
        red, ir = m.read_fifo()
    #    print (red,ir)
        
        if (count==int(Amorce/Interval)):
            print ("Fin de l'amorçage")

        if (count>=int(Amorce/Interval)):
            if (next==1):
                BPM_values[count-int(Amorce/Interval)]=red
            else:
                BPM_values.append(red)

        count += 1

        
        if (count==int(Duree/Interval+Amorce/Interval)):
            
            ppg_signal = lissage(BPM_values,1)
            ppg_signal2 = lissage(BPM_values,int((Duree/Interval)/5))
            drift = ppg_signal[0] - ppg_signal2
            ppg_signal3 =ppg_signal+drift-ppg_signal[0]
            ppg_signal4 = lissage(ppg_signal3,int((Duree/Interval)/50))
            
            

            # Calcul de la transformée de Fourier rapide (FFT) du signal PPG
            fft_result = np.fft.fft(ppg_signal4)
            frequencies = np.fft.fftfreq(len(ppg_signal4),Interval)  # Fréquences correspondantes
            
            fft_result = [nombre.real for nombre in fft_result]
            
            tableau = list(zip(fft_result, frequencies))
            tableau_trie = sorted(tableau, key=lambda x: x[0], reverse=True)
            tableau_trie[:] = [element for element in tableau_trie if element[0] >= 0]
            tableau_trie[:] = [element for element in tableau_trie if element[1] >= 0.9 and element[1]<=3]        
            
            heart_rate_bpm=tableau_trie[0][1]*60
            
        
            count = int(Amorce/Interval)
            next = 1
    
    #         bpm.append(heart_rate_bpm)
            bpmt.append(time.time()-start_time)
            
    #        print ("BOB :", heart_rate_bpm)
            
            
            peaks, _=find_peaks(ppg_signal4, height=0) #Nombre de pics dans singal
            peak_periods=np.diff(peaks)/(1/Interval) #Calcule de la période entre les pics en seconde
            bpm2 = 60/np.mean(peak_periods) #BPM
    #        print('Diff_pics :', bpm2)
            
            #calcule du BPM grapjiquement
            filtered = hp.filter_signal(ppg_signal4, cutoff=[0.5,5], sample_rate = 1/Interval, order = 3, filtertype = 'bandpass') #filtre passe bande avec frequence de coupure 0.5 et 5 
            try:
                working_data, measures = hp.process(hp.scale_data(filtered), sample_rate=1/Interval)
            except:
                bpm = moyenne
            else:
            #working_data, measures = hp.process(ppg_signal4, sample_rate = 1/Interval)
                bpm = measures['bpm']
    #        print("Passe-bande :", bpm)
            
            filtered2 = wiener(ppg_signal4)
            try:
                working_data, measures = hp.process(hp.scale_data(filtered2), sample_rate=1/Interval)
            except:
                bpm3 = moyenne
            else:
                bpm3 = measures['bpm']
    #        print("Wiener:", bpm3)
            
                
            wiener_filtered = wiener(ppg_signal4, mysize = 10)
            try:
                working_data, measures = hp.process(hp.scale_data(wiener_filtered), sample_rate=1/Interval)
            except:
                bpm5 = moyenne
            else:
                bpm5 = measures['bpm']
    #        print("Wiener+ :", bpm5)
            
    # array time et 5 valkaurs et valeur moyenne de ts ceux avec ecartype à moins de 10%
    # visualiser les 6 tracés
    # ajoer dérivée de la valeur moyenne sur écartype des 3 valeurs les plu sregourpées

            
            if (50 <= heart_rate_bpm <= 200):
                brut_serie.append(heart_rate_bpm)
            if (50 <= bpm <= 200):
                brut_serie.append(bpm2)
            if (50 <= bpm2 <= 200):
                brut_serie.append(bpm2)
            if (50 <= bpm3 <= 200):
                brut_serie.append(bpm3)
            if (50 <= bpm5 <= 200):
                brut_serie.append(bpm5)
                
            
            variation = 2
            
            for i in range(variation):
                brut_serie.append(moyenne)
            
            threshold = 1  # seuil tolérance ecarttype

            filtered_serie = filtrage(brut_serie, threshold)

    #         filtered_serie = filtrage2(brut_serie)
            print("Série de mesures brutes:", brut_serie)
            print("Série de mesures filtrées:", filtered_serie)
    
            brut_serie=[]
            
            moyenne = int(sum(filtered_serie) / len(filtered_serie))
            
            print ("BPM retenu = ", moyenne)
            
            moy.append(moyenne)
            
            temps.append(time.time()-start_time)
            
            
            megacount+=1
            
            if (time.time()-start_time>=40):
            
                        
                moy =moy[1:]
                temps = temps[1:]
                # Calcul de la courbe de tendance d'ordre n
                coefficients = np.polyfit(temps, moy, deg=2)  # deg=3 pour un polynôme d'ordre 3
                polynome = np.poly1d(coefficients)

                # Génération de données pour la courbe de tendance
                x_tendance = np.linspace(min(temps), max(temps), 100)
                y_tendance = polynome(x_tendance)

                coefficients2 = np.polyfit(temps, moy, deg=3)  # deg=3 pour un polynôme d'ordre 3
                polynome2 = np.poly1d(coefficients2)

                # Génération de données pour la courbe de tendance
                x_tendance2 = np.linspace(min(temps), max(temps), 100)
                y_tendance2 = polynome2(x_tendance2)

                moy_liss=lissage(moy,5)
                

                # Tracé des données et de la courbe de tendance

                plt.scatter(temps, moy, label='BPM')
                plt.plot(x_tendance, y_tendance, color='red', label='Courbe de tendance (ordre 2)')
                plt.plot(x_tendance2, y_tendance2, color='green', label='Courbe de tendance (ordre 3)')
                plt.plot(temps, moy_liss, color='blue', label='lissage')
                plt.xlabel('Temps')
                plt.ylabel('BPM')
                plt.title('Courbe de tendance')
                plt.legend()
                plt.grid(True)
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                TEST = f"PPG : {timestamp}.png"
                plt.savefig(TEST)
                plt.show()

            

                
                        
                        
            



if __name__ == '__main__': 
    #results = [None, None]
    #thread1 = threading.Thread(target = EMG)
    #thread2 = threading.Thread(target = PPG, args = (results, 1))

    #thread1.start()
    #thread2.start()

    #thread1.join()
    #thread2.join()

    process1 = Process(target=EMG)
    process2 = Process(target = PPG)
    process2.start()
    process1.start()
    process1.join()
    process2.join()

    
