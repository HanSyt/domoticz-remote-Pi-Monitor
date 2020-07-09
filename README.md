# PiRemoteMonitor
Python plugin to monitor temperature, memory usage, etc. from a Remote Raspberry Pi, sending it to an MQTT server in Domoticz format.
No plugin.py needed at Domoticz.

If you want to monitor disk usage, look at https://github.com/Xorfor/Domoticz-Disc-usage-Plugin

## Prerequisites
- Only works on Raspberry Pi
- Requires package python3
- Requires mosquitto mqtt server
- Requires paho.mqtt (pip3 install paho-mqtt)


## Instructions
- Install the python script in /usr/bin on remote server.
- Install piremotemonitor in /etc/init.d on remote server. 
- Make both scripts executable : chmod 755 
- Make the server autostart : sudo update-rc.d piremotemonitor defaults
- Make devices (hardware virtual-switch) in Domoticz (look at the python script for the device type)
- Adapt the python script for MQTT server and Domoticz device Indexes at top of the script.

## Devices
The following parameters are displayed:

| Name            | Description
| :---            | :---
| CPU temperature | Shows the current CPU temperature
| GPU temperature | Shows the current GPU temperature
| CPU memory      | Size of allocated memory for CPU
| GPU memory      | Size of allocated memory for GPU (specified with eg. raspi-config)
| Memory usage    | Percentage of CPU memory in use
| CPU usage       | Percentage of CPU usage
| CPU speed       | Current CPU speed
| CPU count       | Number of CPUs/cores
| Up time         | Up time of the Pi, in sec, minutes, hours or days
| Connections     | Number of active network connections
| Core voltage    | Core voltage
| SDRAM C voltage | SDRAM C voltage
| SDRAM I voltage | SDRAM I voltage
| SDRAM P voltage | SDRAM P voltage
| Domoticz memory | Amount of memory used by Domoticz
