# Project X

Micropython project for GPIO control and atmospheric measurements over WiFi network.

![Project X](Project_X_small.jpg)

## Features
* easy configuration using webserver
* publishing measurements in Thingspeak
* NTP time synchronization
* time controlled relay switch and PWM outputs

## Hardware
ESP8266 NodeMCU v3 and dedicated PCB supporting:
* 4x PWM outputs, 12V/3A
* 1x relay output, 250VAC/8A
* DHT21 temperature and humidity sensor
* 3.3V analog input (*currently not supported by firmware*) 
* hardware watchdog for auto-reset

## Changelog

### v2.0

- added watchdog support
- added safety reboot
- updated BSP to current version of the board

### v1.1

- auto-reboot after multiple consecutive MQTT errors
- fixed local time in case of NTP synchronization error after reboot
- added simplified summertime detection

### v1.0

- finished main application
- added install and config instructions

## Installation
1. Install esptool:

```cmd
python -m pip install esptool
```

2. Open the watchdog jumper (JU1 on the board)
3. Flash the board with current version of the firmware (read COM port number in Device Manager):

```cmd
cd binaries
python -m esptool --port COMx erase_flash
python -m esptool --port COMx --baud 115200 write_flash --flash_size=detect 0 filename.bin
```

4. Open COM port in terminal (baudrate 115200) and reset the board using RST button on the ESP module. It should receive:
```
### Entering Bootloader ###
WebREPL daemon started on ws://192.168.4.1:8266
Started webrepl in manual override mode
[ERR] Missing configuration file: boot.conf. Forcing config mode.
[ERR] Missing webpage file: boot_index.html. Forcing config mode.
[CONFIG MODE]
Access Point started (PROJECT_X,projectx)
Network info: ('192.168.4.1', '255.255.255.0', '192.168.4.1', '208.67.222.222')
First run configuration in progress - upload necessary files and reset the board.
```

5. Close the watchdog jumper (JU1). From now on, watchdog and external pushbutton can reset the board. Red LED indicates watchdog clear signal, it should blink in order to stop the watchdog from resetting the board.
6. Connect a computer/smartphone to the WiFi created by the device:
   
```
SSID: PROJECT_X
PASS: projectx
```

7. Open webREPL page (`utils\webrepl-master\webrepl.html`) and connect to the device:

```
HOST: ws://192.168.4.1:8266/
PASS: projectx
```

8. Send main index file (`boot_index.html` from sources directory)
9. Send device configuration file (`boot.conf` from sources directory)
    *Note: You can manually edit the file, providing your local WiFi credentials and MQTT server login data. Then, you won't need to configure the device as described in the next section.*
10. Disconnect from the device.
11. Reset the board.
    ***Note: First connection to your local WiFi can take longer time, which could result in watchdog delay and cause the board to reset. If you see in the terminal that the board keeps rebooting, then you need to open the watchdog jumper (JU1) for the initial start-up. When the device saves the data, close the jumper again.***
12. From now on, the board is fully operational. When you look at the terminal, it should receive:

```
### Entering Bootloader ###
WebREPL daemon started on ws://0.0.0.0:8266
Started webrepl in manual override mode
Reading config file.
{'PWM3_DAY': '90', 'MQTT_WRITE_KEY': 'x', 'MQTT_CHANNEL_ID': '0', 'WIFI_PASS': 'x', 'LIGHT_ON': '06:00:00', 'PWM4_DAY': '90', 'LIGHT_OFF': '23:00:00', 'PWM2_DAY': '90', 'PWM1_DAY': '90', 'PWM4_NIGHT': '40', 'PWM3_NIGHT': '40', 'PWM2_NIGHT': '40', 'PWM1_NIGHT': '40', 'WIFI_SSID': 'x', 'MQTT_PUBLISH_PERIOD': '60', 'MQTT_SERVER': 'mqtt.thingspeak.com'}
[NORMAL MODE]


### Quitting Bootloader ###


### Entering Main Application ###
Reading config file.
{'PWM3_DAY': '90', 'MQTT_WRITE_KEY': 'x', 'MQTT_CHANNEL_ID': '0', 'WIFI_PASS': 'x', 'LIGHT_ON': '06:00:00', 'PWM4_DAY': '90', 'LIGHT_OFF': '23:00:00', 'PWM2_DAY': '90', 'PWM1_DAY': '90', 'PWM4_NIGHT': '40', 'PWM3_NIGHT': '40', 'PWM2_NIGHT': '40', 'PWM1_NIGHT': '40', 'WIFI_SSID': 'x', 'MQTT_PUBLISH_PERIOD': '60', 'MQTT_SERVER': 'mqtt.thingspeak.com'}
Connecting to WiFi (x,x)...
Connected: ('192.168.0.80', '255.255.255.0', '192.168.0.1', '192.168.0.1')
Synchronized to 2021.06.13 12:29:17
12:29:18 - DAY TIME
12:29:19 - DAY TIME
12:29:20 - DAY TIME
12:29:21 - DAY TIME
```

## Configuration
1. Reboot the board using RST button on ESP module, or external reset button.
2. While the blue LED is blinking, push the configuration button (FLASH button on ESP module, or external CONFIG button) to enter configuration mode.
3. If you have an active terminal session, you should see:

```
### Entering Bootloader ###
WebREPL daemon started on ws://192.168.4.1:8266
Started webrepl in manual override mode
Reading config file.
{'PWM3_DAY': '90', 'PWM1_NIGHT': '40', 'MQTT_SERVER': 'mqtt.thingspeak.com', 'MQTT_CHANNEL_ID': '0', 'LIGHT_ON': '06:00:00', 'MQTT_WRITE_KEY': 'YOURKEY', 'MQTT_PUBLISH_PERIOD': '60', 'PWM2_DAY': '90', 'PWM1_DAY': '90', 'PWM4_NIGHT': '40', 'PWM3_NIGHT': '40', 'PWM2_NIGHT': '40', 'WIFI_SSID': 'yourssid', 'WIFI_PASS': 'yourpass', 'PWM4_DAY': '90', 'LIGHT_OFF': '23:00:00'}
[CONFIG MODE]
Access Point started (PROJECT_X,projectx)
Network info: ('192.168.4.1', '255.255.255.0', '192.168.4.1', '208.67.222.222')
Loading webpage...
Page loaded, escaped 17 instances of '%s'.
Webserver started on 192.168.4.1:80
```

4. Connect a computer/smartphone to the WiFi created by the device:
   
```
SSID: PROJECT_X
PASS: projectx
```

5. Open the device configuration website: http://192.168.4.1/
6. Type in required configuration, especially your local WiFi credentials (and Thingspeak data, if you intend to use it).
7. After pushing Save button, there should be a message confirming that data has been saved. You can now restart te board either by using a web button or by pushing any of the reset buttons.
    ***Note: First connection to your local WiFi can take longer time, which could result in watchdog delay and cause the board to reset. If you see in the terminal that the board keeps rebooting, then you need to open the watchdog jumper (JU1) for the initial start-up. When the device saves the data, close the jumper again.***

## Modifying firmware

Follow the instructions described in ```build/README.md```.