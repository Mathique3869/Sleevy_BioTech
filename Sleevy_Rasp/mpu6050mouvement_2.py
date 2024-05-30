import smbus
import time
import math
import matplotlib.pyplot as plt

# Adresse I2C du MPU6050
MPU6050_ADDR = 0x68

# Registres MPU6050
REG_ACCEL_XOUT_H = 0x3B
REG_PWR_MGMT_1 = 0x6B

# Seuil de mouvement
SEUIL_MOUVEMENT = 0.7  # Réglage du seuil selon vos besoins

# Initialisation du bus I2C
bus = smbus.SMBus(1)

# Réveil du MPU6050
bus.write_byte_data(MPU6050_ADDR, REG_PWR_MGMT_1, 0)

nb = 0

list = []
start_time=time.time()

def read_acceleration(bus, address, type):
    high_byte = bus.read_byte_data(address, type)
    low_byte = bus.read_byte_data(address, type + 1)
    value = (high_byte << 8) | low_byte
    if value > 32767:
        value -= 65536
    return value / 16384.0  # Convertit la valeur brute en g

def read_temperature(bus, address, type):
    high_byte = bus.read_byte_data(address, type)
    low_byte = bus.read_byte_data(address, type + 1)
    value = (high_byte << 8) | low_byte
    temp_c=(value-521)/340+35
    return temp_c

def detect_movement_threshold(accel_values, threshold):
    for value in accel_values:
        if abs(value) > threshold:
            return True
    return False

try:
    accel_values = [0, 0, 0]  # Initialisation des valeurs d'accélération précédentes
    while True:
        # Lire les données d'accélération actuelles
        accel_x = read_acceleration(bus, MPU6050_ADDR,0x3b)
        accel_y = read_acceleration(bus, MPU6050_ADDR,0x3d)
        accel_z = read_acceleration(bus, MPU6050_ADDR,0x3f)
#        temperature = read_temperature(bus, MPU6050_ADDR,0x41)
#        print(temperature)
       
        # Calculer les changements d'accélération
        accel_changes = [abs(accel_x - accel_values[0]), abs(accel_y - accel_values[1]), abs(accel_z - accel_values[2])]
        
        # Mettre à jour les valeurs d'accélération précédentes
        accel_values = [accel_x, accel_y, accel_z]
        
        # Vérifier si un mouvement au-dessus du seuil est détecté
        if detect_movement_threshold(accel_changes, SEUIL_MOUVEMENT):
            print("Mouvement du bras détecté!")
            nb = 0
            list.append(1)
        else:
            if nb == 0:
                print("Pas de mouvement du bras détecté.")
                nb = 1
                list.append(0)
            list.append(0)      
        time.sleep(0.05)  # Attend 0.1 seconde avant de lire à nouveau les données
        if (time.time()-start_time>=60) :
            plt.plot(list, marker = 'o', linestyle = 'None')
            plt.show()
except KeyboardInterrupt:
    pass
