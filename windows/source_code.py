import os
import ssl
import time
import smtplib
import keyboard
import datetime
import serial
import serial.tools.list_ports
from pathlib import Path
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def quit():
    keyboard.wait('Enter')
    exit(0)

def close_all(count):
    if log_write == True:
        logfile.close()
    for i in range(0, count):
        csv_file[i].close()

def date_time():
    d = str(datetime.datetime.now())
    d = d[:19]
    return d

def bm_read():
    try:
        bc16.reset_input_buffer()
        while(bc16.in_waiting != 17):
            time.sleep(.2)
        IN = bc16.read(17)
    except:
        print("BC16 disconnected, press Enter to Exit")
        quit()
    return IN

def file_begin():
    csv_file[i].write("Date and time;")
    csv_file[i].write("SOC (%);")
    csv_file[i].write("Total voltage (V);")
    csv_file[i].write("Capacity (Ah);")
    csv_file[i].write("Current (A);")
    csv_file[i].write("Power (W);\n")

def start_email():
    if send_emails == True:
         try:
            smtp = smtplib.SMTP(SMTP_IP, SMTP_PORT)
            if login == True:
                smtp.starttls(context=context)
                smtp.login(sender_email, password)
         except:
            print("Unable to login to email server, no emails will be sent.\nIf you want to resolve this issue, check your login information in config file")
            return 0
         return smtp
    return 0

def error_message(value):
    server = start_email()
    es_date = date_time()
    send_to = ""
    for i in range(len(receiver_emails)):
        send_to += receiver_emails[i] + ", "
    if server == 0:
        print("Sending emails is not available, check log file for more datails.")
        logmessage = "Sending emails is not available. Informations for sending emails are:\n                               Password: "
        if password == "None" or password == "":
            logmessage += "Password is not set in config file, trying to send emails without STARTTLS and any login request"
        else:
            logmessage += password
        logmessage += "\n                               Sender email: "
        if sender_email == "None" or sender_email == "":
            logmessage += "Sender email is not set in config file so it is impossible to send any email"
        else:
            logmessage += sender_email
        logmessage += "\n                               Receiver email: "
        if receiver_emails[0] == "None" or receiver_emails[0] == "":
            logmessage += "No receiver email adress is set in config file so it is impossible to send any email"
        else:
            for i in range(0,len(receiver_emails)):
                logmessage += receiver_emails[i] + " "
        logmessage += "\n                               SMTP_IP: "
        if SMTP_IP == "None" or SMTP_IP == "":
            logmessage += "SMTP IP is not set in config file so it is impossible to send any email"
        else:
            logmessage += SMTP_IP
        logmessage += "\n                               SMTP_PORT: "
        if SMTP_PORT == "None" or SMTP_PORT == "":
            logmessage += "SMTP PORT is not set in config file so it is impossible to send any email"
        else:
            logmessage += SMTP_PORT
        logmessage += "\n"
        logwrite(logmessage, 2)
        return
    logwrite("Sending email", 1)
    if value != 4 and value != 2:
        mess = "Error on BC16 board: "
    else:
        mess = ""
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = send_to
    if value != 2:
        message["Subject"] = subj + " ERROR " + es_date
        f_name = csv_file[all_files].name
        csv_file[all_files].close()
        csv_file[all_files] = open(f_name,"rb")
        part = MIMEBase("application", "octet-stream")
        part.set_payload(csv_file[all_files].read())
        encoders.encode_base64(part)
        part.add_header(
        "Content-Disposition",
        f"attachment; filename= {f_name}",
    )
    else:
        message["Subject"] = subj + " " + es_date
    if value == 0:
        mess += ".\nBC16 disconnected, program shutting down"
    elif value == 1:
        mess += ".\nNo BC16 found"
    elif value == 2:
        mess += ".\nConnected to: " + str(len(comm)) + " devices"
    elif value == 3:
        mess += ".\nData transfer error, program shutting down"
    elif value == 4:
        mess += ".\nPeak current:\nDischarge    " + daily_max_discharge + "A\n" + "Charge       " + daily_max_charge + "A"
    elif value == 5:
        mess += "Discharging current is: " + str(CUR) + "\nYour maximum value is: " + str(MAX_DISCH_CURR)
    elif value == 6:
        mess += "Charging current is: " + str(CUR) + "\nYour maximum value is: " + str(MAX_CHARGE_CURR)
    message.attach(MIMEText(mess, "plain"))
    if value != 2:
        message.attach(part)
    mess = message.as_string()
    return_code = server.sendmail(sender_email, receiver_emails, mess)
    if value != 2:
        csv_file[all_files].close()
        csv_file[all_files] = open(f_name, "a")

def logwrite(input, severity, start = 0):
    if log_write == False:
        return
    buffer = ""
    if start == 1:
        buffer += "\n\n"
    buffer += date_time() + " "
    logfile.write(buffer)
    if severity == 0:
        buffer = " [INFO]           "
    elif severity == 1:
        buffer = " [WARNING]        "
    elif severity == 2:
        buffer = " [ERROR]          "
    elif severity == 3:
        buffer = " [CRITICAL ERROR] "
    buffer += input + "\n"
    logfile.write(buffer)
    logfile.flush()
    os.fsync(logfile)

sender_email = "None"
receiver_emails = ["None"]
password = "None"
context = ssl.create_default_context()
ERROR_interval = "None"
subj = "None"
SMTP_IP = "None"
SMTP_PORT = "None"
Email_name = "None"
my_file = Path("log.txt")
try:
    if my_file.is_file():
        logfile = open("log.txt", "a")
    else:
        logfile = open("log.txt", "w")
    log_write = True
    logwrite("Program started", 0, 1)
except:
    log_write = False
    print("Failed to open log file, nothing will be written in there...")
    time.sleep(5)
my_file = Path("config.txt")
send_emails = True
if my_file.is_file():
    config = open("config.txt","r")
    lines = config.readlines()
    config.close()
    print("Config file loaded")
else:
    print("Config file was not found")
    logwrite("Config file was not found", 2)
for line in lines:
    if "SMTP_IP" in line:
        SMTP_IP = line[8:]
        SMTP_IP = SMTP_IP.replace("\n", "")
    if "SMTP_PORT" in line:
        SMTP_PORT = line[10:]
        SMTP_PORT = SMTP_PORT.replace("\n", "")
    if "MAX_CHARGE_CURRENT" in line:
        MAX_CHARGE_CURR = line[19:]
        try:
            MAX_CHARGE_CURR = int(MAX_CHARGE_CURR)
        except:
            print("Maximum charging current is not written in config file")
            MAX_CHARGE_CURR = 0
    if "MAX_DISCH_CURRENT" in line:
        MAX_DISCH_CURR = line[18:]
        try:
            MAX_DISCH_CURR = int(MAX_DISCH_CURR)
        except:
            print("Maximum discharge current is not written in config file")
            MAX_DISCH_CURR = 0
    if "Email_send_to" in line:
        emails = line.split(";")
        emails[0] = emails[0][14:]
        First_time = True
        for i in range(0, len(emails)):
            check_buffer = ""
            check_email = False
            for y in (emails[i].replace("\n","")):
                if y == "@" or check_email == True:
                    check_email = True
                    if y == ".":
                        if First_time == True:
                            receiver_emails[0] = emails[i].replace("\n","")
                            First_time = False
                        else:
                            receiver_emails.append(emails[i].replace("\n",""))
                        break
    if "Email_send_from" in line:
        sender_email = "<" + line[16:].replace("\n", "") + ">"
    if "Email_subject" in line:
        subj = line[14:]
    if "Email_sender_name" in line:
        Email_name = line[18:].replace("\n", "")
    if "Password" in line:
        password = line[9:].replace("\n", "")
        login = True
    if "ERROR_interval" in line:
        ERROR_interval = line[15:]
        try:
            ERROR_interval = int(ERROR_interval)
        except:
            print("ERROR_interval is not properly written in config file, using default value 30 minutes")
            logwrite("ERROR_interval is not properly written in config file, using default value 30 minutes", 2)
            ERROR_interval = 30
if receiver_emails[0] == "None":
    print("Receiver email adress is not properly written in config file, no email will be sent.")
    logwrite("Receiver email adress is not properly written in config file, no email will be sent", 1)
    send_emails = False
if (sender_email == "None" or sender_email == "\n" or ("@" not in sender_email or "." not in sender_email)) and send_emails == True:
    print("No sender email found in config file, sending emails is not available")
    logwrite("No sender email found in config file, sending emails in not available", 1)
    send_emails = False
elif (password == "None" or password == "\n" or password == ""):
    print("Password to sender email adress is not defined in config file.Program will try to send emails without login command")
    logwrite("Password to sender email adress is not defined in config file. Program will try to send emails without login command", 1)
    login = False
if Email_name == "None" or Email_name == "":
    print("Using default sender email name (BC16)")
    Email_name = "BC16"

sender_email = Email_name + sender_email
comm = []
repeat = 1
while repeat == 1:
    repeat = 0
    ports = serial.tools.list_ports.comports()
    commPort = 'Nic'
    number_of_connections = len(ports)
    check = -1
    print("Scanning virtual COM ports for BC16")
    logwrite("Scanning virtual COM ports for BC16", 0)
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
            bc16.close()
            continue
        IN = bc16.read(17)
        data = bm_read()
        data = list(data)
        if data[0] != 0xA5:
            bc16.close()
            continue
        else:
            print("BC16 found on", commPort)
            logwrite("BC16 found on " + commPort, 0)
            comm.append(bc16)
        check = -2
    if check != -2:
        print("Device not found, make sure it is connected and drivers are installed properly.\nPress Enter to try again\n")
        logwrite("Device not found", 2)
        repeat = 1
        keyboard.wait('Enter')
csv_file = []
for i in range(0, len(comm)):
    date = str(datetime.datetime.now())
    date = date[:10]
    file_name = date
    date += "_"
    date += comm[i].name
    date += ".csv"
    my_file = Path(date)
    try:
        if my_file.is_file():
            csv_file.append(open(date, "a"))
        else:
            csv_file.append(open(date, "w"))
            file_begin()
    except:
        print("Cannot open file:", date, ", maybe it is being used by another program so you need to close it first.\nPress Enter to exit")
        logwrite("Cannot open file: " + date + ", maybe it is being used by another program so you need to close it first.", 3)
        quit()
error_message(2)
daily_max_charge = 0.
daily_max_discharge = 0.
e_date = datetime.datetime.now() - datetime.timedelta(seconds = ERROR_interval * 60)
while 1:
    for all_files in range(0, len(comm)):
        data = bm_read()
        data = list(data)
        if(data[0] != 0xA5):
            print("Data transfer error, press Enter to exit the program")
            logwrite("Data transfer error", 3)
            error_message(3)
            close_all(len(comm))
            quit()
        SOC = data[1]
        TBV = (data[2] << 8) + data[3]
        CAP = (data[4] << 24) + (data[5] << 16) + (data[6] << 8) + data[7]
        CUR = (data[8] << 24) + (data[9] << 16) + (data[10] << 8) + data[11]
        TIM = (data[12] << 16) + (data[13] << 8) + data[14]
        if data[8] == 255:
            CUR = CUR - (1 << 32)
        TBV = TBV / 100
        CAP = CAP / 1000
        CUR = CUR / 1000
        TIM = TIM / 60
        HOUR = int((TIM / 3600))
        MINUTE = int((TIM / 60) % 60)
        SECOND = int(TIM % 60)
        if (SOC < 0) or (SOC > 100) or (TBV < 0) or (CAP < 0):
            print("Data read error, press Enter to exit")
            logwrite("Data read error, press Enter to exit", 3)
            error_message(3)
            close_all(len(comm))
            quit
        CAP = round(CAP, 2)
        CUR = round(CUR, 1)
        print("SOC (%): ", SOC)
        print("Total battery voltage (V): ", TBV)
        print("Battery capacity (Ah): ", CAP)
        print("Current (A): ", CUR)
        print("Power (W)", round(CUR*TBV,1))
        print("Remaining time: ", HOUR , ":", MINUTE, ":", SECOND, "\n")
        if CUR > MAX_CHARGE_CURR:
            print("Charging current is too high!")
            if (datetime.datetime.now() - e_date).seconds >= ERROR_interval * 60:
                logwrite("Charging current is too high", 1)
                error_message(6)
                e_date = datetime.datetime.now()
        
        elif CUR < 0 and abs(CUR) > MAX_DISCH_CURR:
            print("Discharging current is too high!")
            if (datetime.datetime.now() - e_date).seconds >= ERROR_interval * 60:
                logwrite("Discharging current is too high", 1)
                error_message(5)
                e_date = datetime.datetime.now()
        if CUR < 0:
            if daily_max_discharge < abs(CUR) or daily_max_discharge == 0:
                daily_max_discharge = abs(CUR)
        elif CUR > 0:
            if daily_max_charge < CUR or daily_max_charge == 0:
                daily_max_charge = CUR
        date = datetime.datetime.now()
        date = str(date)
        csv_file[all_files].write(date[:20])
        csv_file[all_files].write(";")
        csv_file[all_files].write(str(SOC).replace('.',','))
        csv_file[all_files].write(";")
        csv_file[all_files].write(str(TBV).replace('.',','))
        csv_file[all_files].write(";")
        csv_file[all_files].write(str(CAP).replace('.',','))
        csv_file[all_files].write(";")
        csv_file[all_files].write(str(CUR).replace('.',','))
        csv_file[all_files].write(";")
        csv_file[all_files].write(str(round(CUR*TBV,1)))
        csv_file[all_files].write(";\n")
        csv_file[all_files].flush()
        os.fsync(csv_file[all_files].fileno())
        date = datetime.datetime.now()
        date = str(date)
        date = date[:10]
        if(file_name != date):
            error_message(4)
            daily_max_discharge = 0.
            daily_max_charge = 0.
            logwrite("Beginning new files")
            for i in range(0, len(comm)):
                csv_file[i].close()
                date = str(datetime.datetime.now())
                date = date [:10]
                file_name = date
                date += "_"
                date += comm[i].name
                date += ".csv"
                csv_file[i] = open(date, "w")
                file_begin()