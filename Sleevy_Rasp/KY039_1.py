import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import matplotlib.pyplot as plt

# Create the I2C bus 
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channels
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

duree_max = 40
temps_debut = time.time()

if __name__ == '__main__':

   
    # initialization
    curState = 0
    thresh = 10000  # mid point in the waveform
    P = 10000
    T = 10000
    stateChanged = 0
    sampleCounter = 0
    lastBeatTime = 0
    firstBeat = True
    secondBeat = False
    Pulse = False
    IBI = 600
    rate = [0]*10
    amp = 100
    BPM_OLD = 0
    
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
    
    stable = False
    Valid = False

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
              #print(IBI_values)
              #plt.plot(IBI_values, color = 'r')
              
              if len(IBI_values) < 5 :
                  print('Initialisation')
              Last_values = IBI_values[-5:]
              deltaY = Last_values[-1] - Last_values[0]
              deltaX = len(Last_values)-1
              
              if not deltaX == 0 :
                  m = deltaY / deltaX
                  COEF_dir.append(m)
                  #print(m, 'coef dir')
              
              
              for m in COEF_dir[-5:] :
                  #print(m)
                  if -80 <= m <= 80 :
                      stable_count += 1
                      print('Calibration')
                      #print(stable_count, 'stable count')
                      if stable_count >= 5:
                          stable = True
                      
    
                  #else :
                      #stable_count = 0
                      #stable = False
                      
                  
                          
                  
              
              if stable :
                  print('Vérificiation')
                  #for m in COEF_dir[-2:]:
                  #print(COEF_dir, 'matrice coef dir')
                  #print(COEF_dir[-1])
                  #print(COEF_dir[-2])
                  diff = abs(COEF_dir[-1] - COEF_dir[-2])
                  #print(diff, 'diff')
                  if diff <= 120 :
                      print ('mesure stable')
                      Valid = True
                      stable_count = 0
                  if diff >= 120 :
                      erreur_count += 1
                      if erreur_count >= 5 :
                          print ('mesure pas stable')
                          Valid = False 
                          stable = False
                          stable_count = 0    
              
              if Valid :
              #print(runningTotal, 'IBI davant x 9 + nouveau IBI')
                  runningTotal /= 10;
              #print(runningTotal, 'IBI / 10')
                  BPM = int(60000/runningTotal);
                  BPM_values.append(BPM)
                  print(BPM_values)
                  plt.plot(BPM_values, color = 'r')
                  #if count == 15:
                        #print('go')
                    #BPM_OLD = BPM
              #if count > 15 :
                  
                  #if not BPM_OLD-5 <= BPM <= BPM_OLD+5 :
                      #print ('bypass')
                      #BPM = BPM_OLD
                  #else:
                      #BPM_OLD = BPM
                  print ('BPM: {}'.format(BPM))
                  count += 1
                  print(count)
                  
                  temps_ecoule = time.time() - temps_debut
                  if temps_ecoule >= duree_max :
                      plt.show()
                      break

        if Signal > thresh and Pulse == True :   # when the values are going down, the beat is over
            Pulse = False;                         
            amp = P - T;                           
            thresh = amp/2 + T;                    
            P = thresh;                            
            T = thresh;

        if N > 100000 :                          # if 2.5 seconds go by without a beat
            thresh = 512;                          # set thresh default
            P = 512;                               # set P default
            T = 512;                               # set T default
            lastBeatTime = sampleCounter;          # bring the lastBeatTime up to date        
            firstBeat = True;                      # set these to avoid noise
            secondBeat = False;                    # when we get the heartbeat back
            print ("no beats found")
        
        #if z == 1000 :
            #break

        time.sleep(0.005)
    plt.show()
        