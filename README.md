# BC16 software
This software can read data from BC16 and save them in csv file that you can easily read. You can also set your email adress and get warnings in case something happens with your battery. You can set limits for charging and discharging overcurrent, overvoltage and undervoltage and SOC level.


To use this software you need to have USB to UART converter and drivers for it. We recomend using converters with CH340 chip. You can download driver for it in this repository in "driver" folder which is in windows and linux folder. You can find detailed information about driver installation in "driver_installation.txt" file.

Before you can start using the software, you have to set correct setting into the "config" file. Datailed information about these setting can be found in "config-help" file.

You can connect as many BC16 devices as you wish but if you disconnect any of them when the software is wokring, it will send you an error message and turn itself off.
