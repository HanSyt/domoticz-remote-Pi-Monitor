#!/usr/bin/python3 

# -*- coding: utf-8 -*-
# PiReMonitor Server
#
# Author: Han Sytsma, based on JVaassen, based on Xorfor's PiMonitor

import os                       # read info from OS
# needs pip3 install paho-mqtt
import paho.mqtt.client as mqtt # MQTT Client
from datetime import timedelta  # Calculate System uptime
import time                     # sleep funtion

# MQTT
MQTThost = "192.168.2.8"        # Fill in the host 

# Send data every
period = "60"                   # Send data every 60 seconds

# Domoticz indexes, creating with remark which sensor should be made in Domoticx
idxcorevoltage = "169"          # Voltage sensor - Name: Core Voltage
idxsdram_c = "170"              # Voltage sensor
idxsdram_i = "171"              # Voltage sensor
idxsdram_p = "172"              # Voltage sensor
idxcpucount = "173"             # Custom sensor - axis Cores - NameL Amount Cores
idxcpucurrentspeed = "174"      # Custom sensor - axis MHz - Name: CPU Current Speed
idxcpumemory = "175"            # Custom sensor - axis MB - Name: CPU Memory
idxcputemperature = "176"       # Temperature sensor - Name CPU Temperature
idxcpuuse = "177"               # Percentage sensor - Nsme: CPU percentage
idxmemory = "178 "              # Custom sensor - axis: MB - Name: Total Memory
idxgpumemory = "179"            # Custom sensor - axis: MB - Name GPU Memory
idxgputemperature = "180"       # Temperature sensor - Name: GPU Temperature
idxraminfo = "181"              # Percentage sensor - Name: % Memory Used
idxnetworkconnections = "182"   # Custom Sensor - axis: Interfaces - Name Network Interfaces
idxcpuuptime = "183"            # Custom Sensor - axis: Days - Name System Uptime

# MQTT Publisher Activate
client = mqtt.Client("P1") # create new isntance
client.connect(MQTThost) #connect to broker
# client.publish(topic, message)

class output:

  global _last_idle, _last_total
  _last_idle = _last_total = 0

  # Return % of CPU used by user
  # Based on: https://rosettacode.org/wiki/Linux_CPU_utilization#Python
  def getCPUuse(self):
   	global _last_idle, _last_total
   	try:
      	 with open('/proc/stat') as f:
              fields = [float(column) for column in f.readline().strip().split()[1:]]
      	 idle, total = fields[3], sum(fields)
      	 idle_delta, total_delta = idle - _last_idle, total - _last_total
      	 _last_idle, _last_total = idle, total
      	 res = round(100.0 * (1.0 - idle_delta / total_delta), 2 )
   	except:
      	 res = 0.0
   	return res

  def getCPUcount(self):
   	return os.cpu_count()

  def getCPUuptime(self):
   	try:
         with open('/proc/uptime','r') as f:
              uptime_seconds = float(f.readline().split()[0])
              res = str(timedelta(seconds = uptime_seconds))
   	except:
      	 res = 0.0
   	return res

  # Return number of network connections
  def getNetworkConnections(self,state):
   	res = 0
   	try:
      	 for line in os.popen("netstat -tun").readlines():
              if line.find(state) >= 0:
               	res += 1
   	except:
      	 res = 0
   	return res

  # Return GPU temperature
  def getGPUtemperature(self):
   	try:
      	 res = os.popen("/opt/vc/bin/vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", "")
      	 if (res==""):
         	 res = "0"
   	except:
      	 res = "0"
   	return float(res)

  def getGPUmemory(self):
   	try:
      	 res = os.popen("/opt/vc/bin/vcgencmd get_mem gpu").readline().replace("gpu=", "").replace("M\n", "")
      	 if (res==""):
         	 res = 0
   	except:
      	 res = "0"
   	return float(res)

  def getCPUmemory(self):
   	try:
      	 res = os.popen("/opt/vc/bin/vcgencmd get_mem arm").readline().replace("arm=", "").replace("M\n", "")
      	 if (res==""):
         	 res = 0
   	except:
      	 res = "0"
   	return float(res)

  # Return CPU temperature
  def getCPUtemperature(self):
   	try:
      	 res = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
      	 if (res==""):
         	 res = 0
   	except:
      	 res = "0"
   	return round(float(res)/1000,1)

  # Return CPU speed in Mhz
  def getCPUcurrentSpeed(self):
   	try:
      	 res = os.popen("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq").readline()
   	except:
      	 res = "0"
   	return round(int(res)/1000)

  # Return RAM information in a list
  # Based on: https://gist.github.com/funvill/5252169
  def getRAMinfo(self):
   	p = os.popen("free -b")
   	i = 0
   	while 1:
      	 i = i + 1
      	 line = p.readline()
      	 if i == 2:
              res = line.split()[1:4]
              # Index 0: total RAM
              # Index 1: used RAM
              # Index 2: free RAM
              return round(100 * int(res[1]) / int(res[0]), 2 )
  # http://www.microcasts.tv/episodes/2014/03/15/memory-usage-on-the-raspberry-pi/
  # https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=164787
  # https://stackoverflow.com/questions/22102999/get-total-physical-memory-in-python/28161352
  # https://stackoverflow.com/questions/17718449/determine-free-ram-in-python
  # https://www.reddit.com/r/raspberry_pi/comments/60h5qv/trying_to_make_a_system_info_monitor_with_an_lcd/

  # Get uptime of RPi
  # Based on: http://cagewebdev.com/raspberry-pi-showing-some-system-info-with-a-python-script/
  def getUpStats(self):
   	#Returns a tuple (uptime, 5 min load average)
   	try:
      	 s = os.popen("uptime").readline()
      	 load_split = s.split("load average: ")
      	 load_five = float(load_split[1].split(",")[1])
      	 up = load_split[0]
      	 up_pos = up.rfind(",", 0, len(up)-4)
      	 up = up[:up_pos].split("up ")[1]
      	 return up
   	except:
      	 return ""

  # Get voltage
  # Based on: https://www.raspberrypi.org/forums/viewtopic.php?t=30697
  def getVoltage(self,p):
   	if p in ["core", "sdram_c", "sdram_i", "sdram_p"]:
      	 try:
              res = os.popen(
               	"/opt/vc/bin/vcgencmd measure_volts {}".format(p)).readline().replace("volt=", "").replace("V", "")
              if (res==""):
                 res = 0
      	 except:
              res = "0"
   	else:
      	 res = "0"
   	return float(res)

  # ps aux | grep domoticz | awk '{sum=sum+$6}; END {print sum}'
  def getDomoticzMemory(self):
   	try:
      	 res = os.popen(
              "ps aux | grep domoticz | awk '{sum=sum+$6}; END {print sum}'").readline().replace("\n", "")
   	except:
      	 res = "0"
   	return float(res)


  def encodee(self):

      core = str(self.getVoltage("core"))
      print( "VoltageCore,"+ core )
      client.publish("domoticz/in",'{ "idx": ' + idxcorevoltage + ', "nvalue": 0, "svalue": "' + core + '" }' )
      #
      sdram_c = str(self.getVoltage("sdram_c"))
      print( "VoltageSdRam_C,"+ sdram_c )
      client.publish("domoticz/in",'{ "idx": ' + idxsdram_c + ', "nvalue": 0, "svalue": "' + sdram_c + '" }' )
      #
      sdram_i = str(self.getVoltage("sdram_i"))
      print( "VoltageSdRam_I,"+ sdram_i )
      client.publish("domoticz/in",'{ "idx": ' + idxsdram_i + ', "nvalue": 0, "svalue": "' + sdram_i + '" }' )
      #
      sdram_p = str(self.getVoltage("sdram_i"))
      print( "VoltageSdRam_P,"+ sdram_p )
      client.publish("domoticz/in",'{ "idx": ' + idxsdram_p + ', "nvalue": 0, "svalue": "' + sdram_p + '" }' )
      #
      cpucount = str(self.getCPUcount())
      print( "CPUcount,"+ cpucount )
      client.publish("domoticz/in",'{ "idx": ' + idxcpucount + ', "nvalue": 0, "svalue": "' + cpucount + '" }' )
      #
      cpucurrentspeed = str(self.getCPUcurrentSpeed())
      print( "CPUcurrentSpeed,"+ cpucurrentspeed )
      client.publish("domoticz/in",'{ "idx": ' + idxcpucurrentspeed + ', "nvalue": 0, "svalue": "' + cpucurrentspeed + '" }' )
      #
      cpumemory = str(self.getCPUmemory())
      print( "CPUmemory,"+ cpumemory )
      client.publish("domoticz/in",'{ "idx": ' + idxcpumemory + ', "nvalue": 0, "svalue": "' + cpumemory + '" }' )
      #
      cputemperature = str(self.getCPUtemperature())
      print( "CPUtemperature,"+ cputemperature )
      client.publish("domoticz/in",'{ "idx": ' + idxcputemperature + ', "nvalue": 0, "svalue": "' + cputemperature + '" }' )
      #
      cpuuse =  str(self.getCPUuse())
      print( "CPUuse,"+ cpuuse )
      client.publish("domoticz/in",'{ "idx": ' + idxcpuuse + ', "nvalue": 0, "svalue": "' + cpuuse + '" }' )
      #
      memory = str(self.getDomoticzMemory())
      print ("Memory,"+ memory )
      client.publish("domoticz/in",'{ "idx": ' + idxmemory + ', "nvalue": 0, "svalue": "' + memory + '" }' )
      #
      gpumemory = str(self.getGPUmemory())
      print ("GPUmemory,"+ gpumemory )
      client.publish("domoticz/in",'{ "idx": ' + idxgpumemory + ', "nvalue": 0, "svalue": "' + gpumemory + '" }' )
      #
      gputemperature = str(self.getGPUtemperature())
      print ("GPUtemperature,"+ gputemperature )
      client.publish("domoticz/in",'{ "idx": ' + idxgputemperature + ', "nvalue": 0, "svalue": "' + gputemperature + '" }' )
      #
      raminfo = str(self.getRAMinfo())
      print ("RAMinfo,"+ raminfo )
      client.publish("domoticz/in",'{ "idx": ' + idxraminfo + ', "nvalue": 0, "svalue": "' + raminfo  + '" }' )
      #
      networkconnections = str(self.getNetworkConnections("ESTABLISHED"))
      print ("NetworkConnections,"+ networkconnections )
      client.publish("domoticz/in",'{ "idx": ' + idxnetworkconnections + ', "nvalue": 0, "svalue": "' + networkconnections + '" }' )
      #
      cpuuptime = str(self.getCPUuptime())
      print ("CPUuptime,"+ cpuuptime )
      client.publish("domoticz/in",'{ "idx": ' + idxcpuuptime + ', "nvalue": 0, "svalue": "' + cpuuptime + '" }' )


      return

def sender():
     # Running as a deamon, comment out if you want to use crontab
     while True:
        MyO = output()
        print (MyO.encodee())
        time.sleep(float(period))
     # Running in crontab, uncomment
     #MyO = output()
     #print (MyO.encodee())
        

if __name__ == '__main__':
  sender()
