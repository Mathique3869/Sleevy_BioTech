import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# pour ajouter des nouvelles broches sda sdc sur un bus I2C
# cd /boot, puis éditer le fichier config.txt
# ajouter une ligne (ou la trouver et la modifier)
# dtoverlay=i2c-gpio, bus=5,i2c_gpio_delay_us=1, i2c_gpio_sda=5, i2c_gpio_scl=6
# pour définir que le bus numéro 5 utilise les broches 5 pour sda et 6 pour scl
# voir un schéma pour trouver les briches GPIO5 et GPIO6

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channels
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

duree_max = 120
temps_debut = time.time()

if __name__ == '__main__':

   
    # initialization
    curState = 0
    thresh = 10000  # mid point in the waveform
    P = 512
    T = 512
    P_old = 10000
    T_old = 10000
    thresh_old=10000
    stateChanged = 0
    sampleCounter = 0
    lastBeatTime = 0
    firstBeat = True
    secondBeat = False
    Pulse = False
    IBI = 600
    rate = [0]*10
    amp = 100
    BPM_last = 0
    
    time_values = []
    signal_values = []

    lastTime = int(time.time()*1000)
    
    z = 0
    count = 0
    stable_count = 0
    erreur_count = 0
    IBI_values = []
    COEF_dir = []
    BPM_values = []
    BPM_values_liss =[]
    stable_zone = 0
    precision = 20
    
    stable = False
    Valid = False

    def lissage(signal_brut,L):
        res = np.copy(signal_brut) # duplication des valeurs
        for i in range (1,len(signal_brut)-1): # toutes les valeurs sauf la première et la dernière
            L_g = min(i,L) # nombre de valeurs disponibles à gauche
            L_d = min(len(signal_brut)-i-1,L) # nombre de valeurs disponibles à droite
            Li=min(L_g,L_d)
            res[i]=np.sum(signal_brut[i-Li:i+Li+1])/(2*Li+1)
        return res

    # Main loop. use Ctrl-c to stop the code
    while True:
        # read from the ADC
        Signal = chan0.value   #TODO: Select the correct ADC channel. I have selected A0 here
        curTime = int(time.time()*1000)
        
        time_values.append(curTime)
        signal_values.append(Signal)
        
        #plt.plot(time_values, signal_values, color ='b')
        #plt.xlabel('Time (ms)')
        #plt.ylabel('Signal Value')
        #plt.pause(0.05)
        z = z + 1
        
        
        
        sampleCounter += curTime - lastTime;      ## keep track of the time in mS with this variable
        lastTime = curTime
        N = sampleCounter - lastBeatTime;     #  # monitor the time since the last beat to avoid noise
       

        ##  find the peak 
        if Signal < thresh and N > (IBI/5.0)*3.0 :  #       # avoid dichrotic noise by waiting 3/5 of last IBI
            if Signal < T :                        # T is the trough
              T = Signal;
              #print ('toto', Signal, thresh)						# keep track of lowest point in pulse wave 

        if Signal > thresh and  Signal > P:           # thresh condition helps avoid noise
            P = Signal;
            #print('gros')# P is the peak
                                                # keep track of highest point in pulse wave

         
          # signal surges up in value every time there is a pulse
        
        if N > 333 :                                   # avoid high frequency noise
            if  (Signal > thresh) and  (Pulse == False) and  (N > (IBI/5.0)*3.0)  :       
              Pulse = True;                               # set the Pulse flag when we think there is a pulse
              IBI = sampleCounter - lastBeatTime;
              #print(IBI)
              
              
              #print(IBI, 'valeur du IBI')# measure time between beats in mS
              #print(secondBeat)
              lastBeatTime = sampleCounter;               # keep track of time for next pulse

              if secondBeat :                        # if this is the second beat, if secondBeat == TRUE
                secondBeat = False;
                #print('toto')# clear secondBeat flag
                for i in range(0,10):             # seed the running total to get a realisitic BPM at startup
                  rate[i] = IBI;
                  #print(IBI, 'test')

              if firstBeat :
                #print('rat')
                firstBeat = False;                   
                secondBeat = True;
                continue                              


              # keep a running total of the last 10 IBI values
              runningTotal = 0;                  # clear the runningTotal variable    

              for i in range(0,9):                # shift data in the rate array
                rate[i] = rate[i+1];                   
                runningTotal += rate[i];
                #print(runningTotal, 'IBI de avant x 9')

              rate[9] = IBI;
              #print(IBI, 'ecart entre 2 beat juste calculé')
              runningTotal += rate[9];
              IBI_values.append(runningTotal)
              runningTotal /= 10;
              BPM = int(60000/runningTotal);
              
              if stable_zone == 0:
 
                  if abs(BPM-BPM_last)<BPM*0.05:
                    stable_count +=1
                    print ("stable")
                  else:
                    stable_count = 0
                    print ("non stable")
                  BPM_last=BPM
        
            
              if stable_count == 7:
                  stable_zone =1
        
              if stable_zone == 1:
#                   print ('BPM: {}'.format(BPM-BPM_last))
#                   if abs(BPM-BPM_last)>int(BPM*0.1):
#                       print ("valeur forcée",BPM_last)
#                       BPM_values.append(BPM_last)
#                       
#                   else:
#                       BPM_values.append(BPM)
#                       BPM_last=BPM
                  BPM_values.append(BPM)
                  BPM_last=BPM
                  print(BPM_values)
                  print ('BPM: {}'.format(BPM))
                  count += 1
                  print(count)
              temps_ecoule = time.time()-temps_debut
              if temps_ecoule >= duree_max :
                  precision = min(int(count/4),40)
                  BPM_values_liss = lissage (BPM_values, precision)
                  plt.plot(BPM_values, color = 'r')
                  plt.plot(BPM_values_liss, color = 'g')
                  timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                  TEST = f"Test{timestamp}.png"
                  plt.savefig(TEST)
                  plt.show()
                  break

        if Signal > thresh and Pulse == True :   # when the values are going down, the beat is over
            Pulse = False;                         
            amp = P - T;                           
            thresh = amp/2 + T;                    
            P = thresh;                            
            T = thresh;

        if N > 2500 :                          # if 2.5 seconds go by without a beat
            thresh = 10000;                          # set thresh default
            P = 512;                               # set P default
            T = 512;                               # set T default
            lastBeatTime = sampleCounter;          # bring the lastBeatTime up to date        
            firstBeat = True;                      # set these to avoid noise
            secondBeat = False;                    # when we get the heartbeat back
            print ("no beats found")
#            stable_zone = 0
        
        #if z == 50 :
            #break

#        time.sleep(0.005)
    plt.show()
        
