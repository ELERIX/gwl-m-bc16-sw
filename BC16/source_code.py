import os
import time
import keyboard
import datetime
import serial
import serial.tools.list_ports
from pathlib import Path

def bm_read():
    bc16.reset_input_buffer()
    while(bc16.in_waiting != 17):
        time.sleep(.2)
    IN = bc16.read(17)
    return IN

def file_begin():
    csv_file.write("Date and time;")
    csv_file.write("SOC;")
    csv_file.write("Total voltage (V);")
    csv_file.write("Capacity (Ah);")
    csv_file.write("Current (A);\n")

repeat = 1
while repeat == 1:
    repeat = 0
    ports = serial.tools.list_ports.comports()
    commPort = 'Nic'
    number_of_connections = len(ports)
    check = -1
    print("Scanning virtual COM ports for BC16...")
    for i in range(0,number_of_connections):
        port = ports[i]
        strPort = str(port) 
        print(strPort)
        splitPort = strPort.split(' ')
        commPort = (splitPort[0])
        try:
            bc16 = serial.Serial(commPort, 9600, timeout=0)
        except:
            continue
        time.sleep(1)
        check = time.time()
        bc16.reset_input_buffer()
        while(bc16.in_waiting != 17):
            time.sleep(.2)
            if (time.time() - check) > 8:
                check = -1
                break
        if check == -1:
            continue
        IN = bc16.read(17)
        data = bm_read()
        data = list(data)
        if data[0] != 0xA5:
            continue
        check = -2
        break
    if check != -2:
        print("Device not found, make sure it is connected and drivers are installed properly.\nPress Enter to try again\n")
        repeat = 1
        keyboard.wait('Enter')

print("BC16 found on", commPort)
date = str(datetime.datetime.now())
date = date[:10]
file_name = date
date += "_"
date += commPort
date += ".csv"
my_file = Path(date)
if my_file.is_file():
    csv_file = open(date, "a")
else:
    csv_file = open(date, "w")
    file_begin()
sample_count = 0
while 1:
    if(sample_count == 10):
        sample_count = 0
        csv_file.flush()
        os.fsync(csv_file.fileno())
    date = datetime.datetime.now()
    date = str(date)
    date = date[:10]
    if(file_name != date):
        csv_file.close()
        file_name = date
        date += "_"
        date += commPort
        date += ".csv"
        csv_file = open(date, "w")
        file_begin()
    data = bm_read()
    data = list(data)
    if(data[0] != 0xA5):
        print("Data transfer error, press Enter to exit the program")
        keyboard.wait('Enter')
        csv_file.close()
        exit(0)
    SOC = data[1]
    TBV = (data[2] << 8) + data[3]
    CAP = (data[4] << 24) + (data[5] << 16) + (data[6] << 8) + data[7]
    CUR = (data[8] << 24) + (data[9] << 16) + (data[10] << 8) + data[11]
    TIM = (data[12] << 16) + (data[13] << 8) + data[14]
    TBV = TBV / 100
    CAP = CAP / 1000
    CUR = CUR / 1000
    TIM = TIM / 60
    HOUR = int((TIM / 3600))
    MINUTE = int((TIM / 60) % 60)
    SECOND = int(TIM % 60)
    if (SOC < 0) or (SOC > 100) or (TBV < 0) or (CAP < 0):
        print("Data read error, press Enter to exit")
        keyboard.wait('Enter')
        csv_file.close()
        exit(0)
    print("SOC (%): ", SOC)
    print("Total battery voltage (V): ", TBV)
    print("Battery capacity (Ah): ", CAP)
    print("Current (A): ", CUR)
    print("Remaining time: ", HOUR , ":", MINUTE, ":", SECOND, "\n")
    date = datetime.datetime.now()
    SOC = str(SOC)
    TBV = str(TBV)
    CAP = str(CAP)
    CUR = str(CUR)
    date = str(date)
    csv_file.write(date[:20])
    csv_file.write(";")
    csv_file.write(SOC.replace('.',','))
    csv_file.write(";")
    csv_file.write(TBV.replace('.',','))
    csv_file.write(";")
    csv_file.write(CAP.replace('.',','))
    csv_file.write(";")
    csv_file.write(CUR.replace('.',','))
    csv_file.write(";\n")
    sample_count += + 1
csv_file.close();