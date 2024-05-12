import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import matplotlib.pyplot as plt
import numpy as np

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channels
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

if __name__ == '__main__':

   
    # initialization
    curState = 0
    thresh = 525  # mid point in the waveform
    P = 512
    T = 512
    stateChanged = 0
    sampleCounter = 0
    lastBeatTime = 0
    firstBeat = True
    secondBeat = False
    Pulse = False
    IBI = 600
    rate = [0]*10
    amp = 100
    Signal_last = 0
    stable_zone = 0
    
    time_values = []
    signal_values = []
    signal_values_liss=[]

    lastTime = int(time.time()*1000)
    i = 0
    j = 0
    user_input = ('Entrer 0 pour arreter')

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
 
        if stable_zone == 0:
 
            if abs(Signal-Signal_last)<Signal*0.02:
                stable_count +=1
                print ("stable")
            else:
                stable_count = 0
                print ("non stable")
        
            Signal_last=Signal
            
            if stable_count == 5:
                stable_zone =1
        
        if stable_zone == 1:
 
            curTime = int(time.time()*1000)
        
            time_values.append(curTime)
            signal_values.append(Signal)
        
            i = i + 1
            print (i)
        
            lastTime = curTime

            if 	i == 200 :
                break
    
        time.sleep(0.01)
    
    print(j)
    
    signal_values_liss=lissage(signal_values, int(i/3))
    
    
    
    
    
    plt.plot(time_values, signal_values, color ='r')
    plt.plot(time_values, signal_values_liss, color ='g', linewidth=4)
    plt.xlabel('Time (ms)')
    plt.ylabel('Signal Value')
    plt.show()

